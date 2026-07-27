from __future__ import annotations

from dataclasses import dataclass

from adapters.york.errors import YorkFrameError
from adapters.york.state import YorkState


@dataclass(frozen=True)
class YorkFrame:
    raw: bytes
    header: int
    payload: bytes
    checksum: int

    @property
    def hex(self) -> str:
        return self.raw.hex(" ").upper()


class YorkPacketDecoder:
    """Decode York TFIAC status frames backed by captured observations.

    The mappings enabled here are limited to fields repeatedly isolated in the
    Protocol Explorer logs. Unknown or unresolved fields remain ``None``.
    """

    FRAME_HEADER = 0xBB
    STATUS_FRAME_LENGTH = 21
    STATUS_MESSAGE_TYPE = (0x01, 0x00, 0x03)

    _MODE_MAP = {
        0x01: "cool",
        0x02: "fan_only",
        0x03: "dry",
        0x04: "heat",
        0x05: "auto",
    }
    _FAN_MAP = {
        0x00: "low",
        0x10: "auto",
        0x20: "medium",
        0x30: "high",
    }

    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """Return the XOR checksum used by captured 21-byte status frames."""
        checksum = 0
        for value in data:
            checksum ^= value
        return checksum

    def parse_frame(self, data: bytes) -> YorkFrame:
        if not data:
            raise YorkFrameError("Received an empty York frame")
        if data[0] != self.FRAME_HEADER:
            raise YorkFrameError(
                f"Unsupported York frame header 0x{data[0]:02X}; expected 0xBB"
            )
        if len(data) != self.STATUS_FRAME_LENGTH:
            raise YorkFrameError(
                f"York status frame length is {len(data)} bytes; "
                f"expected {self.STATUS_FRAME_LENGTH}"
            )
        if tuple(data[1:4]) != self.STATUS_MESSAGE_TYPE:
            message_type = " ".join(f"{value:02X}" for value in data[1:4])
            raise YorkFrameError(
                f"Unsupported York message type {message_type}; expected 01 00 03"
            )

        expected = self.calculate_checksum(data[:-1])
        actual = data[-1]
        if actual != expected:
            raise YorkFrameError(
                f"York checksum mismatch: received 0x{actual:02X}, "
                f"calculated 0x{expected:02X}"
            )

        return YorkFrame(
            raw=bytes(data),
            header=data[0],
            payload=bytes(data[1:-1]),
            checksum=actual,
        )

    def decode_state(self, data: bytes) -> YorkState:
        frame = self.parse_frame(data)
        raw = frame.raw

        flags = raw[7]
        fan_byte = raw[8]
        option_byte = raw[9]
        swing_byte = raw[10]

        power = bool(flags & 0x10)
        mode = self._MODE_MAP.get(flags & 0x0F)
        fan = self._FAN_MAP.get(fan_byte & 0x30)

        horizontal = bool(swing_byte & 0x20)
        vertical = bool(swing_byte & 0x40)
        if horizontal and vertical:
            swing = "both"
        elif horizontal:
            swing = "horizontal"
        elif vertical:
            swing = "vertical"
        else:
            swing = "off"

        return YorkState(
            power=power,
            mode=mode,
            fan=fan,
            swing=swing,
            turbo=bool(flags & 0x80),
            eco=bool(flags & 0x40),
            health=bool(option_byte & 0x04),
            display=bool(flags & 0x20),
        )
