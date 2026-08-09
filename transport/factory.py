from __future__ import annotations

import logging

from configuration import Config
from transport.base import TransportBase
from transport.native_command_boundary import NativeCommandBoundaryTransport
from transport.york_direct_transport import YorkDirectTransport

LOG = logging.getLogger("climate_bridge.transport")


def create_transport(config: Config) -> TransportBase:
    transport_type = config.transport_type.strip().lower()
    if transport_type in {"relay", "tablet_relay"}:
        LOG.warning(
            "Legacy transport.type=%s is ignored; using native LAN runtime",
            transport_type,
        )
        transport_type = "native"

    if transport_type in {"native", "york_native"}:
        if not config.direct_read_enabled:
            raise ValueError("native transport requires direct_read.enabled")
        return NativeCommandBoundaryTransport(config)
    if transport_type in {"york", "york_direct"}:
        return YorkDirectTransport(config)
    raise ValueError(f"Unsupported transport type: {config.transport_type}")
