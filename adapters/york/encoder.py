from __future__ import annotations

import re
from typing import Any

from adapters.york.errors import YorkFrameError, YorkProtocolNotReady

_HEX_CLEAN_RE = re.compile(r"[^0-9a-fA-F]")


class YorkPacketEncoder:
    """Encodes only protocol frames backed by validated captures.

    Sprint 2.3 deliberately accepts a state request only when the operator has
    supplied its captured hexadecimal bytes. Climate Bridge never invents or
    guesses authentication, sequence, checksum, or payload fields.
    """

    def __init__(self, state_request_hex: str = "") -> None:
        self._state_request_hex = state_request_hex.strip()

    @staticmethod
    def parse_captured_hex(value: str) -> bytes:
        compact = _HEX_CLEAN_RE.sub("", value)
        if not compact:
            raise YorkProtocolNotReady(
                "direct_device.state_request_hex is required for a native probe"
            )
        if len(compact) % 2:
            raise YorkFrameError("Captured York request contains an incomplete hex byte")
        try:
            frame = bytes.fromhex(compact)
        except ValueError as error:
            raise YorkFrameError("Captured York request is not valid hexadecimal") from error
        if len(frame) < 4:
            raise YorkFrameError("Captured York request is too short")
        if frame[0] != 0xBB:
            raise YorkFrameError(
                f"Captured York request header is 0x{frame[0]:02X}; expected 0xBB"
            )
        return frame

    def encode_state_request(self) -> bytes:
        return self.parse_captured_hex(self._state_request_hex)

    def encode_command(self, changes: dict[str, Any]) -> bytes:
        raise YorkProtocolNotReady(
            "York command encoding is awaiting validated protocol fields"
        )
