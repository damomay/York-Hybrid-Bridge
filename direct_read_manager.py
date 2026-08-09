from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from configuration import Config
from transport.york_direct_transport import YorkDirectTransport

COMPARABLE_FIELDS = (
    "power",
    "mode",
    "temperature",
    "fan",
    "swing",
    "turbo",
    "eco",
    "health",
    "display",
)


@dataclass(frozen=True)
class DirectReadResult:
    state: dict[str, Any]
    comparison: str
    matched_fields: int
    compared_fields: int
    response_length: int
    udp_sends: int
    raw_frame_hex: str
    fan_status_byte: int | None
    fan_status_nibble: int | None


class DirectReadManager:
    """Read normalized York state directly from the authenticated LAN session."""

    def __init__(
        self,
        config: Config,
        *,
        transport_factory: Callable[[Config], YorkDirectTransport] = YorkDirectTransport,
    ) -> None:
        self.interval = config.direct_read_poll_seconds
        self.transport = transport_factory(config)
        self.next_due_monotonic = 0.0

    def due(self, now: float | None = None) -> bool:
        moment = time.monotonic() if now is None else now
        return moment >= self.next_due_monotonic

    def observe(
        self,
        relay_state: dict[str, Any],
        *,
        now: float | None = None,
    ) -> DirectReadResult | None:
        moment = time.monotonic() if now is None else now
        if not self.due(moment):
            return None

        # Advance the schedule before the network operation. A timeout is a
        # completed observation attempt, not a trigger for an immediate retry.
        self.next_due_monotonic = moment + self.interval
        direct_state = self.transport.get_state()
        compared = [
            key
            for key in COMPARABLE_FIELDS
            if key in relay_state and key in direct_state
        ]
        mismatches = [
            key for key in compared if relay_state[key] != direct_state[key]
        ]
        if not compared:
            comparison = "no comparable fields"
        elif mismatches:
            comparison = "mismatch: " + ", ".join(mismatches)
        else:
            comparison = f"match ({len(compared)}/{len(compared)})"

        return DirectReadResult(
            state=direct_state,
            comparison=comparison,
            matched_fields=len(compared) - len(mismatches),
            compared_fields=len(compared),
            response_length=self.transport.last_response_length,
            udp_sends=self.transport.last_send_count,
            raw_frame_hex=getattr(self.transport, "last_raw_frame_hex", ""),
            fan_status_byte=getattr(self.transport, "last_fan_status_byte", None),
            fan_status_nibble=getattr(
                self.transport, "last_fan_status_nibble", None
            ),
        )

    def read_authoritative(self) -> DirectReadResult:
        """Return one fresh direct state without consulting Relay v2.

        Alpha.55 uses this path for normal Home Assistant polling and command
        guards.  The older scheduled ``observe`` method remains available for
        historical shadow-comparison tests and diagnostic tooling.
        """

        direct_state = self.transport.get_state()
        decoded_fields = [key for key in COMPARABLE_FIELDS if key in direct_state]
        return DirectReadResult(
            state=direct_state,
            comparison=f"authoritative ({len(decoded_fields)} decoded fields)",
            matched_fields=len(decoded_fields),
            compared_fields=len(decoded_fields),
            response_length=self.transport.last_response_length,
            udp_sends=self.transport.last_send_count,
            raw_frame_hex=getattr(self.transport, "last_raw_frame_hex", ""),
            fan_status_byte=getattr(self.transport, "last_fan_status_byte", None),
            fan_status_nibble=getattr(
                self.transport, "last_fan_status_nibble", None
            ),
        )

    def close(self) -> None:
        self.transport.close()
