"""Backward-compatible relay imports for existing runtime and tools."""

from transport.relay_transport import RelayError, RelayTransport


RelayManager = RelayTransport

__all__ = ["RelayError", "RelayManager"]
