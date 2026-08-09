from __future__ import annotations

from typing import Any

from configuration import Config
from transport.base import TransportBase


class NativeCommandBoundaryTransport(TransportBase):
    """Fail-closed runtime boundary for direct-authority installations.

    DirectReadManager owns authenticated state reads and the guarded direct
    managers own qualified writes.  This transport deliberately has no HTTP
    client, fallback endpoint, socket creation, or retry behavior.
    """

    name = "york_native_boundary"
    display_name = "Native LAN"
    command_fallback_enabled = False

    def __init__(self, _config: Config) -> None:
        pass

    def get_state(self) -> dict[str, Any]:
        raise RuntimeError(
            "native command boundary does not provide state; use direct LAN authority"
        )

    def command(self, **_changes: Any) -> dict[str, Any]:
        raise RuntimeError(
            "command is outside the qualified native allowlist"
        )
