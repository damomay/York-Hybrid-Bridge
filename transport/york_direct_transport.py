from __future__ import annotations

import ipaddress
import logging
import re
from typing import Any

from adapters.york import YorkConnection, YorkProtocolSession
from adapters.york.encoder import YorkPacketEncoder
from adapters.york.decoder import YorkFrame
from configuration import Config
from transport.base import TransportBase

LOG = logging.getLogger("climate_bridge.york")
_MAC_RE = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$", re.IGNORECASE)


class YorkDirectTransport(TransportBase):
    """Native York/TCL transport backed by a per-device protocol session."""

    name = "york_direct"
    display_name = "York Direct (Experimental)"

    def __init__(self, config: Config) -> None:
        self.config = config
        if not config.direct_enabled:
            raise ValueError(
                "York-direct transport is disabled; set "
                "direct_device.enabled only for an approved native test"
            )
        self.host = config.direct_host
        self.port = config.direct_port
        self.mac = config.direct_mac
        self.timeout = config.direct_connect_timeout
        self._validate_endpoint()
        self.session = YorkProtocolSession(
            YorkConnection(self.host, self.port, self.timeout),
            encoder=YorkPacketEncoder(config.direct_state_request_hex),
            frame_observer=self._observe_frame,
        )

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

    def connect(self) -> None:
        self.session.open()

    @property
    def connected(self) -> bool:
        return self.session.opened

    def inspect_captured_frame(self, data: bytes) -> YorkFrame:
        """Developer hook used to validate real captures during Sprint 2.2."""
        return self.session.inspect_captured_frame(data)

    def get_state(self) -> dict[str, Any]:
        return self.session.poll_state().to_dict()

    def command(self, **changes: Any) -> dict[str, Any]:
        return self.session.command(changes).to_dict()

    def close(self) -> None:
        self.session.close()
