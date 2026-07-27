from __future__ import annotations

from configuration import Config
from transport.base import TransportBase
from transport.relay_transport import RelayTransport
from transport.york_direct_transport import YorkDirectTransport


def create_transport(config: Config) -> TransportBase:
    transport_type = config.transport_type.strip().lower()
    if transport_type in {"relay", "tablet_relay"}:
        return RelayTransport(config)
    if transport_type in {"york", "york_direct"}:
        return YorkDirectTransport(config)
    raise ValueError(f"Unsupported transport type: {config.transport_type}")
