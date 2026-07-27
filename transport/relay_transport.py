from __future__ import annotations

import logging
import time
from typing import Any, Callable

import requests

from configuration import Config
from transport.base import TransportBase
from transport.relay_extraction_logger import RelayExtractionLogger


LOG = logging.getLogger("york_bridge.relay")


class RelayError(RuntimeError):
    """Raised when the tablet relay returns an invalid response."""


class RelayTransport(TransportBase):
    """Compatibility transport using the proven Android tablet HTTP relay."""

    name = "tablet_relay"
    display_name = "Relay (Legacy)"

    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "York-Hybrid-Bridge",
            }
        )
        self.extraction_logger = (
            RelayExtractionLogger()
            if config.debug_relay_extraction
            else None
        )

    def _request_json(
        self,
        method: str,
        endpoint: str,
        response_observer: Callable[
            [requests.Response, dict[str, Any]],
            None,
        ] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a relay request and return a validated JSON object."""
        url = f"{self.config.transport_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method,
                url,
                timeout=self.config.transport_timeout,
                **kwargs,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise RelayError(
                "Relay request timed out after "
                f"{self.config.transport_timeout:g} seconds: {endpoint}"
            ) from exc
        except requests.ConnectionError as exc:
            raise RelayError(
                f"Unable to connect to tablet relay: {url}"
            ) from exc
        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else "unknown"
            )
            raise RelayError(
                f"Tablet relay returned HTTP {status_code}: {endpoint}"
            ) from exc
        except requests.RequestException as exc:
            raise RelayError(
                f"Tablet relay request failed: {exc}"
            ) from exc

        try:
            payload = response.json()
        except requests.JSONDecodeError as exc:
            raise RelayError(
                f"Tablet relay returned invalid JSON: {endpoint}"
            ) from exc

        if not isinstance(payload, dict):
            raise RelayError(
                "Tablet relay returned an unexpected JSON type for "
                f"{endpoint}: {type(payload).__name__}"
            )

        if response_observer is not None:
            response_observer(response, payload)
        return payload

    def get_state(self) -> dict[str, Any]:
        """Retrieve the current air-conditioner state."""
        return self._request_json("GET", "state")

    def command(self, **changes: Any) -> dict[str, Any]:
        """Send state changes to the air conditioner."""
        if not changes:
            raise RelayError("Relay command must contain at least one change.")

        LOG.debug("Sending relay command with fields: %s", sorted(changes))
        if self.extraction_logger is None:
            return self._request_json("POST", "command", json=changes)

        endpoint = f"{self.config.transport_url}/command"
        correlation_id = self.extraction_logger.next_id()
        record = self.extraction_logger.pending(
            correlation_id=correlation_id,
            endpoint=endpoint,
            payload=dict(changes),
        )
        started = time.monotonic()
        logged = False

        def record_response(
            response: requests.Response,
            payload: dict[str, Any],
        ) -> None:
            nonlocal logged
            self.extraction_logger.complete(
                record,
                response_status=response.status_code,
                response_json=payload,
                response_text=response.text,
                elapsed_ms=round((time.monotonic() - started) * 1000),
                result="success",
            )
            logged = True

        try:
            return self._request_json(
                "POST",
                "command",
                response_observer=record_response,
                json=changes,
                headers={
                    "X-Climate-Bridge-Correlation-ID": correlation_id
                },
            )
        except Exception as exc:
            if not logged:
                self.extraction_logger.complete(
                    record,
                    response_status=None,
                    response_json=None,
                    response_text=str(exc),
                    elapsed_ms=round(
                        (time.monotonic() - started) * 1000
                    ),
                    result="transport_error",
                )
            raise

    def close(self) -> None:
        """Close the persistent HTTP session."""
        self.session.close()
