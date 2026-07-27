from __future__ import annotations

import logging
from typing import Any

import requests

from configuration import Config
from transport.base import TransportBase


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

    def _request_json(
        self,
        method: str,
        endpoint: str,
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

        return payload

    def get_state(self) -> dict[str, Any]:
        """Retrieve the current air-conditioner state."""
        return self._request_json("GET", "state")

    def command(self, **changes: Any) -> dict[str, Any]:
        """Send state changes to the air conditioner."""
        if not changes:
            raise RelayError("Relay command must contain at least one change.")

        LOG.debug("Sending relay command with fields: %s", sorted(changes))
        return self._request_json("POST", "command", json=changes)

    def close(self) -> None:
        """Close the persistent HTTP session."""
        self.session.close()
