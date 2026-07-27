"""York UDP XML discovery and status broadcast support."""
from __future__ import annotations

import socket
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class YorkXmlMessage:
    message_id: str
    message_type: str
    sequence: str
    state: dict[str, Any]
    raw_xml: str
    sender: tuple[str, int]


def _fahrenheit_to_celsius(value: str) -> float:
    fahrenheit = float(value)
    return round((fahrenheit - 32.0) * 5.0 / 9.0, 1)


def parse_xml_payload(payload: bytes, sender: tuple[str, int] = ("", 0)) -> YorkXmlMessage:
    text = payload.decode("utf-8", errors="strict").strip("\x00\r\n ")
    root = ET.fromstring(text)
    message_id = root.attrib.get("msgid", "")
    message_type = root.attrib.get("type", "")
    sequence = root.attrib.get("seq", "")

    state: dict[str, Any] = {}
    status = root.find("statusUpdateMsg") if root.tag == "msg" else None
    if status is not None:
        mode = status.findtext("BaseMode")
        power = status.findtext("TurnOn")
        set_temp = status.findtext("SetTemp")
        fan = status.findtext("WindSpeed")
        indoor_temp = status.findtext("IndoorTemp")
        if mode:
            state["mode"] = mode.strip().lower().replace(" ", "_")
        if power:
            state["power"] = power.strip().lower() == "on"
        if set_temp:
            state["temperature_f"] = float(set_temp)
            state["temperature"] = _fahrenheit_to_celsius(set_temp)
        if fan:
            state["fan"] = fan.strip().lower().replace(" ", "_")
        if indoor_temp:
            state["current_temperature_f"] = float(indoor_temp)
            state["current_temperature"] = _fahrenheit_to_celsius(indoor_temp)

    return YorkXmlMessage(
        message_id=message_id,
        message_type=message_type,
        sequence=sequence,
        state=state,
        raw_xml=text,
        sender=sender,
    )


class YorkXmlBroadcastListener:
    """Listen for York module XML broadcasts on UDP port 10074."""

    def __init__(self, port: int = 10074, timeout: float = 10.0) -> None:
        self.port = port
        self.timeout = timeout
        self._socket: socket.socket | None = None

    def open(self) -> None:
        if self._socket is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", self.port))
        sock.settimeout(0.5)
        self._socket = sock

    def wait_for_status(self, device_ip: str = "") -> YorkXmlMessage:
        self.open()
        assert self._socket is not None
        deadline = time.monotonic() + self.timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                payload, sender = self._socket.recvfrom(4096)
            except socket.timeout:
                continue
            if device_ip and sender[0] != device_ip:
                continue
            try:
                message = parse_xml_payload(payload, sender)
            except (UnicodeDecodeError, ET.ParseError, ValueError) as exc:
                last_error = exc
                continue
            if message.message_id == "statusUpdateMsg" and message.state:
                return message
        suffix = f"; last parse error: {last_error}" if last_error else ""
        raise TimeoutError(f"No York statusUpdateMsg received within {self.timeout:.1f}s{suffix}")

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def __enter__(self) -> "YorkXmlBroadcastListener":
        self.open()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
