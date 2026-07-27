from __future__ import annotations

from typing import Any, Callable

from adapters.york.connection import YorkConnection
from adapters.york.decoder import YorkFrame, YorkPacketDecoder
from adapters.york.encoder import YorkPacketEncoder
from adapters.york.state import YorkState


class YorkProtocolSession:
    """Coordinates one York device's connection and protocol components."""

    def __init__(
        self,
        connection: YorkConnection,
        encoder: YorkPacketEncoder | None = None,
        decoder: YorkPacketDecoder | None = None,
        frame_observer: Callable[[YorkFrame], None] | None = None,
    ) -> None:
        self.connection = connection
        self.encoder = encoder or YorkPacketEncoder()
        self.decoder = decoder or YorkPacketDecoder()
        self.frame_observer = frame_observer

    @property
    def opened(self) -> bool:
        return self.connection.opened

    def open(self) -> None:
        self.connection.open()

    def inspect_captured_frame(self, data: bytes) -> YorkFrame:
        """Parse a real captured response without guessing its state fields."""
        frame = self.decoder.parse_frame(data)
        if self.frame_observer is not None:
            self.frame_observer(frame)
        return frame

    def poll_state(self) -> YorkState:
        request = self.encoder.encode_state_request()
        response = self.connection.exchange(request)
        frame = self.decoder.parse_frame(response)
        if self.frame_observer is not None:
            self.frame_observer(frame)
        return self.decoder.decode_state(response)

    def command(self, changes: dict[str, Any]) -> YorkState:
        request = self.encoder.encode_command(changes)
        response = self.connection.exchange(request)
        frame = self.decoder.parse_frame(response)
        if self.frame_observer is not None:
            self.frame_observer(frame)
        return self.decoder.decode_state(response)

    def close(self) -> None:
        self.connection.close()
