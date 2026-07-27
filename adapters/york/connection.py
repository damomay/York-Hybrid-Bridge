from __future__ import annotations

import socket
from dataclasses import dataclass


@dataclass(frozen=True)
class YorkEndpoint:
    host: str
    port: int


class YorkConnection:
    """Owns the UDP socket for one York Wi-Fi module.

    Opening a UDP socket does not prove the HVAC module is responsive. Device
    availability is only established after a valid protocol response arrives.
    """

    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.endpoint = YorkEndpoint(host=host, port=port)
        self.timeout = timeout
        self._socket: socket.socket | None = None

    @property
    def opened(self) -> bool:
        return self._socket is not None

    def open(self) -> None:
        if self._socket is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        sock.connect((self.endpoint.host, self.endpoint.port))
        self._socket = sock

    def send(self, payload: bytes) -> int:
        self.open()
        assert self._socket is not None
        return self._socket.send(payload)

    def receive(self, max_bytes: int = 4096) -> bytes:
        self.open()
        assert self._socket is not None
        return self._socket.recv(max_bytes)

    def exchange(self, payload: bytes, max_bytes: int = 4096) -> bytes:
        self.send(payload)
        return self.receive(max_bytes=max_bytes)

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
