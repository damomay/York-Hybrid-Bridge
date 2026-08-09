from __future__ import annotations

import ipaddress
import logging
import re
from typing import Any

from adapters.york.broadlink import BroadlinkYorkReadClient
from adapters.york.decoder import YorkFrame
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.errors import YorkProtocolNotReady
from configuration import Config
from transport.base import TransportBase

LOG = logging.getLogger("climate_bridge.york")
_MAC_RE = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$", re.IGNORECASE)


class YorkDirectTransport(TransportBase):
    """Read-only York/TCL transport using the qualified Broadlink LAN session."""

    name = "york_direct_read"
    display_name = "York Direct Read (Phase 2)"

    def __init__(self, config: Config) -> None:
        self.config = config
        self.host = config.direct_host
        self.port = config.direct_port
        self.mac = config.direct_mac
        self.timeout = config.direct_connect_timeout
        self._validate_endpoint()
        self.client = BroadlinkYorkReadClient(
            self.host,
            self.port,
            self.mac,
            self.timeout,
        )
        self.decoder = YorkPacketDecoder()
        self.last_response_length = 0
        self.last_raw_frame_hex = ""
        self.last_fan_status_byte: int | None = None
        self.last_fan_status_nibble: int | None = None

    def _validate_endpoint(self) -> None:
        if not self.host:
            raise ValueError("direct_device.host is required for york_direct transport")
        try:
            ipaddress.ip_address(self.host)
        except ValueError as error:
            raise ValueError(f"direct_device.host must be a valid IP address: {self.host}") from error
        if not 1 <= self.port <= 65535:
            raise ValueError("direct_device.port must be between 1 and 65535")
        if not _MAC_RE.fullmatch(self.mac):
            raise ValueError("direct_device.mac must use aa:bb:cc:dd:ee:ff format")

    def _observe_frame(self, frame: YorkFrame) -> None:
        LOG.debug("York RX frame (%d bytes): %s", len(frame.raw), frame.hex)

    @property
    def connected(self) -> bool:
        return False

    @property
    def last_send_count(self) -> int:
        return self.client.last_send_count

    def inspect_captured_frame(self, data: bytes) -> YorkFrame:
        return self.decoder.parse_frame(data)

    def get_state(self) -> dict[str, Any]:
        frame = self.client.read_state_frame()
        self.last_response_length = len(frame)
        parsed = self.decoder.parse_frame(frame)
        self.last_raw_frame_hex = frame.hex().upper()
        self.last_fan_status_byte = frame[8]
        self.last_fan_status_nibble = (frame[8] >> 4) & 0x0F
        self._observe_frame(parsed)
        state = self.decoder.decode_state(frame).to_dict()
        state["indoor_temperature"] = self.decoder.decode_indoor_temperature(frame)
        # Native Dry and Fan-only have no selectable setpoint. Their status
        # temperature nibbles are protocol/status values, so never expose them
        # as Home Assistant target temperatures. The independently decoded
        # indoor_temperature remains the measured room temperature.
        if state.get("mode") in {"dry", "fan_only"}:
            state.pop("temperature", None)
        return state

    def command(self, **changes: Any) -> dict[str, Any]:
        raise YorkProtocolNotReady(
            "York direct LAN integration is read-only; control writes are disabled"
        )

    def close(self) -> None:
        return None
