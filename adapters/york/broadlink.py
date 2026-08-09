from __future__ import annotations

import hashlib
import socket
import time
from dataclasses import dataclass
from typing import Callable

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from adapters.york.errors import YorkFrameError, YorkProtocolError
from adapters.york.captured_temperature_command import (
    build_captured_heat_high_vertical_temperature_command,
    validate_captured_heat_high_vertical_temperature_command,
)
from adapters.york.low_vertical_temperature_command import (
    build_captured_heat_low_vertical_temperature_command,
    validate_captured_heat_low_vertical_temperature_command,
)
from adapters.york.power_on_command import (
    QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS,
)
from adapters.york.power_off_command import (
    QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS,
)
from adapters.york.official_sdk_mode_transitions import (
    QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS,
    validate_official_sdk_mode_command,
)
from adapters.york.fan_command import (
    build_qualified_heat_vertical_fan_command,
    validate_qualified_heat_vertical_fan_command,
)
from adapters.york.fan_off_qualification import (
    build_heat_22_5_fan_off_qualification_command,
    validate_heat_22_5_fan_off_qualification_command,
)
from adapters.york.cool_fan_off_qualification import (
    build_cool_22_5_fan_off_qualification_command,
    validate_cool_22_5_fan_off_qualification_command,
)
from adapters.york.swing_command import (
    build_qualified_heat_low_swing_command,
)
from adapters.york.swing_matrix_qualification import (
    build_heat_22_5_low_swing_matrix_command,
    validate_heat_22_5_low_swing_matrix_command,
)
from adapters.york.temperature_command import (
    build_qualified_temperature_command,
    validate_qualified_temperature_command,
)
from adapters.york.cool_fan_auto_temperature_qualification import (
    COOL_20_5_TO_20_FAN_AUTO_COMMAND,
    COOL_20_TO_20_5_FAN_AUTO_COMMAND,
    COOL_23_TO_21_FAN_AUTO_COMMAND,
    validate_general_cool_fan_auto_temperature_command,
    validate_general_cool_qualified_fan_temperature_command,
)

MAGIC = bytes.fromhex("5AA5AA555AA5AA55")
INITIAL_KEY = bytes.fromhex("097628343FE99E23765C1513ACCF8B02")
INITIAL_IV = bytes.fromhex("562E17996D093D28DDB3BA695A2E6F58")
YORK_STATE_QUERY = bytes.fromhex("BB000104020100BD")
# Exact command produced by the official Android York/TCL SDK and captured by
# Relay v2 transaction 2. It changes the fully qualified Cool/22/Low/Off state
# to Cool/25/Low/Off. Alpha.25 cannot generate or alter command frames.
YORK_QUALIFICATION_COOL_22_TO_25 = bytes.fromhex(
    "BB0001031901004403060200000000000000000000000000000000000000E2"
)
# Exact command produced by the official Android York/TCL SDK and captured by
# Relay v2 transaction 25. It changes Heat/23/Low/Off to Heat/24/Low/Off.
YORK_QUALIFICATION_HEAT_23_TO_24 = bytes.fromhex(
    "BB0001031901004401070200000000000000000000000000000000000000E1"
)
# Exact power commands produced by the official Android York/TCL SDK. Fresh
# Relay v2 transaction 46 qualified the 31-byte Power Off frame from
# Cool/25/High/Vertical. The retained Power On command remains historical.
# Alpha.32 separately locks the fresh combined Power On + Heat command from
# Off/Cool/25/High/Vertical to On/Heat/25/High/Vertical. Alpha.33 locks the
# fresh combined Power On + Cool command from Off/Heat/25/High/Vertical to
# On/Cool/25/High/Vertical. Alpha.35 separately locks Power Off from
# Heat/25/High/Vertical, captured by Relay v2 transaction 7 on 2026-07-30.
YORK_QUALIFICATION_POWER_OFF = bytes.fromhex(
    "BB0001031901004003063D00000000000000000000000000000000000000D9"
)
YORK_QUALIFICATION_POWER_OFF_HEAT = bytes.fromhex(
    "BB0001031901004001063D00000000000000000000000000000000000000DB"
)
YORK_QUALIFICATION_POWER_ON = bytes.fromhex(
    "BB0001031901004403090200000000000000000000000000000000000000ED"
)
YORK_QUALIFICATION_POWER_ON_HEAT = bytes.fromhex(
    "BB0001031901004401063D00000000000000000000000000000000000000DF"
)
YORK_QUALIFICATION_POWER_ON_COOL = bytes.fromhex(
    "BB0001031901004403063D00000000000000000000000000000000000000DD"
)
YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_24 = bytes.fromhex(
    "BB0001031901004401073D00000000000000000000000000000000000000DE"
)
YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_26 = bytes.fromhex(
    "BB0001031901004401053D00000000000000000000000000000000000000DC"
)
YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_16 = bytes.fromhex(
    "BB00010319010044010F3D00000000000000000000000000000000000000D6"
)
YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_31 = bytes.fromhex(
    "BB0001031901004401003D00000000000000000000000000000000000000D9"
)
YORK_QUALIFICATION_HEAT_LOW_VERTICAL_24 = bytes.fromhex(
    "BB0001031901004401073A00000000000000000000000000000000000000D9"
)
YORK_QUALIFICATION_HEAT_LOW_VERTICAL_25 = bytes.fromhex(
    "BB0001031901004401063A00000000000000000000000000000000000000D8"
)
# Alpha.49's inferred status-bit candidate is retained only as rejected
# evidence. It commanded Swing Off and must never enter the write allowlist.
YORK_REJECTED_ALPHA49_HEAT_LOW_HORIZONTAL_21_5 = bytes.fromhex(
    "BB00010319010044010A0222000000000000000000000000000000000000CE"
)
# Alpha.50 uses exact Relay v2 command evidence for independent axes. The
# command keeps Vertical enabled (0x3A) and adds the command-side Horizontal
# flag 0x08 to byte 11, alongside the 0x02 half-degree flag: 0x0A.
YORK_QUALIFICATION_HEAT_LOW_BOTH_21_5 = bytes.fromhex(
    "BB00010319010044010A3A0A000000000000000000000000000000000000DE"
)
YORK_QUALIFICATION_HEAT_LOW_VERTICAL_21_5 = bytes.fromhex(
    "BB00010319010044010A3A02000000000000000000000000000000000000D6"
)
# Alpha.53 qualifies the independent Horizontal-only axis at the physically
# observable Heat/21.5/Low state. Relay v2 captured byte 11 as 0x0A for
# Horizontal (0x08 axis flag plus 0x02 half-degree flag) and 0x02 for Off.
YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5 = bytes.fromhex(
    "BB00010319010044010A020A000000000000000000000000000000000000E6"
)
YORK_QUALIFICATION_HEAT_LOW_OFF_21_5 = bytes.fromhex(
    "BB00010319010044010A0202000000000000000000000000000000000000EE"
)
# Alpha.51 uses the exact Relay v2 frames physically qualified in Dry mode.
# Horizontal remains an independent command-side 0x08 flag. Dry normalises the
# reported setpoint to 21.0 °C and uses no half-degree flag in byte 11.
YORK_QUALIFICATION_DRY_LOW_BOTH_21 = bytes.fromhex(
    "BB00010319010044020A3A08000000000000000000000000000000000000DF"
)
YORK_QUALIFICATION_DRY_LOW_VERTICAL_21 = bytes.fromhex(
    "BB00010319010044020A3A00000000000000000000000000000000000000D7"
)
YORK_QUALIFICATION_COMMANDS = frozenset(
    {
        YORK_QUALIFICATION_COOL_22_TO_25,
        YORK_QUALIFICATION_HEAT_23_TO_24,
        YORK_QUALIFICATION_POWER_OFF,
        YORK_QUALIFICATION_POWER_OFF_HEAT,
        YORK_QUALIFICATION_POWER_ON,
        YORK_QUALIFICATION_POWER_ON_HEAT,
        YORK_QUALIFICATION_POWER_ON_COOL,
        YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_24,
        YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_26,
        YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_16,
        YORK_QUALIFICATION_HEAT_HIGH_VERTICAL_31,
        YORK_QUALIFICATION_HEAT_LOW_VERTICAL_24,
        YORK_QUALIFICATION_HEAT_LOW_VERTICAL_25,
        YORK_QUALIFICATION_HEAT_LOW_BOTH_21_5,
        YORK_QUALIFICATION_HEAT_LOW_VERTICAL_21_5,
        YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5,
        YORK_QUALIFICATION_HEAT_LOW_OFF_21_5,
        YORK_QUALIFICATION_DRY_LOW_BOTH_21,
        YORK_QUALIFICATION_DRY_LOW_VERTICAL_21,
        COOL_20_TO_20_5_FAN_AUTO_COMMAND,
        COOL_20_5_TO_20_FAN_AUTO_COMMAND,
        COOL_23_TO_21_FAN_AUTO_COMMAND,
    }
)
YORK_DEVICE_TYPE = 20014
AUTH_COMMAND = 0x65
AUTH_REPLY = 0xE9
QUERY_COMMAND = 0x6A
QUERY_REPLY = 0xEE

SocketFactory = Callable[..., socket.socket]


def broadlink_checksum(data: bytes) -> int:
    return sum(data, 0xBEAF) & 0xFFFF


def york_xor(data: bytes) -> int:
    value = 0
    for byte in data:
        value ^= byte
    return value


def parse_mac(value: str) -> bytes:
    compact = value.replace(":", "").replace("-", "").strip()
    if len(compact) != 12:
        raise YorkProtocolError("MAC address must contain exactly six bytes")
    try:
        return bytes.fromhex(compact)
    except ValueError as error:
        raise YorkProtocolError("MAC address is not valid hexadecimal") from error


def _crypt(key: bytes, payload: bytes, *, encrypt: bool) -> bytes:
    if len(payload) % 16:
        raise YorkProtocolError("Broadlink AES payload is not block aligned")
    cipher = Cipher(algorithms.AES(key), modes.CBC(INITIAL_IV))
    worker = cipher.encryptor() if encrypt else cipher.decryptor()
    return worker.update(payload) + worker.finalize()


def validate_state_query(frame: bytes) -> None:
    if frame != YORK_STATE_QUERY:
        raise YorkProtocolError("Safety interlock rejected a non-state York request")
    if york_xor(frame):
        raise YorkProtocolError("York state-query XOR checksum is invalid")


def _auth_payload() -> bytes:
    payload = bytearray(0x50)
    payload[0x04:0x14] = bytes([0x31] * 16)
    payload[0x1E] = 0x01
    payload[0x2D] = 0x01
    payload[0x30:0x36] = b"Test 1"
    return bytes(payload)


def _query_payload() -> bytes:
    validate_state_query(YORK_STATE_QUERY)
    return len(YORK_STATE_QUERY).to_bytes(2, "little") + YORK_STATE_QUERY


@dataclass
class _SessionEnvelope:
    mac: bytes
    counter: int
    device_id: int = 0
    key: bytes = INITIAL_KEY

    def build_packet(self, command: int, payload: bytes) -> bytes:
        if command not in {AUTH_COMMAND, QUERY_COMMAND}:
            raise YorkProtocolError(
                f"Safety interlock rejected Broadlink command 0x{command:02X}"
            )
        if command == QUERY_COMMAND and payload != _query_payload():
            raise YorkProtocolError("Safety interlock rejected a non-state payload")

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = command
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(_crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True))
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_qualification_write_packet(self, frame: bytes) -> bytes:
        if frame not in YORK_QUALIFICATION_COMMANDS:
            raise YorkProtocolError(
                "Safety interlock rejected a non-qualification York command"
            )
        if york_xor(frame):
            raise YorkProtocolError("York qualification-command XOR checksum is invalid")
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(_crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True))
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_cool_fan_auto_temperature_write_packet(self, frame: bytes) -> bytes:
        """Build only a canonical Cool command for a qualified fan state."""

        validate_general_cool_qualified_fan_temperature_command(frame)
        if york_xor(frame):
            raise YorkProtocolError(
                "York Cool Fan Auto qualification-command XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_temperature_write_packet(self, frame: bytes) -> bytes:
        validate_qualified_temperature_command(frame)
        if york_xor(frame):
            raise YorkProtocolError(
                "York dynamic temperature-command XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(_crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True))
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_parameterised_power_on_write_packet(self, frame: bytes) -> bytes:
        if frame not in QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS:
            raise YorkProtocolError(
                "Safety interlock rejected a non-canonical parameterised "
                "power-on command"
            )
        if york_xor(frame):
            raise YorkProtocolError(
                "York parameterised power-on XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_parameterised_power_off_write_packet(self, frame: bytes) -> bytes:
        if frame not in QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS:
            raise YorkProtocolError(
                "Safety interlock rejected a non-canonical parameterised "
                "power-off command"
            )
        if york_xor(frame):
            raise YorkProtocolError(
                "York parameterised power-off XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_official_sdk_mode_write_packet(self, frame: bytes) -> bytes:
        """Build one write from the consolidated five-edge SDK allowlist."""

        validate_official_sdk_mode_command(frame)
        if york_xor(frame):
            raise YorkProtocolError(
                "York official-SDK mode command XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_captured_temperature_write_packet(self, frame: bytes) -> bytes:
        validate_captured_heat_high_vertical_temperature_command(frame)
        if york_xor(frame):
            raise YorkProtocolError(
                "York captured temperature-command XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(_crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True))
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_low_vertical_temperature_write_packet(self, frame: bytes) -> bytes:
        validate_captured_heat_low_vertical_temperature_command(frame)
        if york_xor(frame):
            raise YorkProtocolError(
                "York Low/Vertical temperature-command XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_fan_write_packet(self, frame: bytes, target_fan: str) -> bytes:
        validate_qualified_heat_vertical_fan_command(frame, target_fan)
        if york_xor(frame):
            raise YorkProtocolError(
                "York fan-command XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_fan_off_qualification_write_packet(
        self,
        frame: bytes,
        target_fan: str,
    ) -> bytes:
        validate_heat_22_5_fan_off_qualification_command(frame, target_fan)
        if york_xor(frame):
            raise YorkProtocolError(
                "York Alpha.63 Fan Off qualification XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_cool_fan_off_qualification_write_packet(
        self,
        frame: bytes,
        target_fan: str,
    ) -> bytes:
        validate_cool_22_5_fan_off_qualification_command(frame, target_fan)
        if york_xor(frame):
            raise YorkProtocolError(
                "York Alpha.64 Cool Fan Off qualification XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def build_swing_matrix_qualification_write_packet(
        self,
        frame: bytes,
        target_swing: str,
    ) -> bytes:
        validate_heat_22_5_low_swing_matrix_command(frame, target_swing)
        if york_xor(frame):
            raise YorkProtocolError(
                "York Alpha.65 swing qualification XOR checksum is invalid"
            )
        payload = len(frame).to_bytes(2, "little") + frame

        self.counter = ((self.counter + 1) | 0x8000) & 0xFFFF
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = QUERY_COMMAND
        packet[0x28:0x2A] = self.counter.to_bytes(2, "little")
        packet[0x2A:0x30] = self.mac[::-1]
        packet[0x30:0x34] = self.device_id.to_bytes(4, "little")
        packet[0x34:0x36] = broadlink_checksum(payload).to_bytes(2, "little")
        packet.extend(
            _crypt(self.key, payload + bytes((-len(payload)) % 16), encrypt=True)
        )
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def parse_reply(self, packet: bytes, expected_command: int) -> bytes:
        if len(packet) < 0x38 or packet[:8] != MAGIC:
            raise YorkProtocolError("Broadlink reply header or length is invalid")
        expected_checksum = int.from_bytes(packet[0x20:0x22], "little")
        actual_checksum = (
            sum(packet, 0xBEAF) - sum(packet[0x20:0x22])
        ) & 0xFFFF
        if expected_checksum != actual_checksum:
            raise YorkProtocolError("Broadlink outer checksum is invalid")
        if packet[0x26] != expected_command:
            raise YorkProtocolError(
                f"Unexpected Broadlink reply 0x{packet[0x26]:02X}; "
                f"expected 0x{expected_command:02X}"
            )
        if int.from_bytes(packet[0x28:0x2A], "little") != self.counter:
            raise YorkProtocolError("Broadlink reply counter does not match the request")
        error = int.from_bytes(packet[0x22:0x24], "little")
        if error:
            raise YorkProtocolError(f"Broadlink device returned error 0x{error:04X}")

        encrypted = packet[0x38:]
        if not encrypted or len(encrypted) % 16:
            raise YorkProtocolError("Broadlink encrypted reply length is invalid")
        clear = _crypt(self.key, encrypted, encrypt=False)
        if int.from_bytes(packet[0x34:0x36], "little") != broadlink_checksum(clear):
            raise YorkProtocolError("Broadlink payload checksum is invalid")
        return clear


class BroadlinkYorkReadClient:
    """Authenticate and perform one fixed York state read.

    Every call creates one fresh UDP session, sends authentication once and
    sends the fixed state query once. There is no discovery, retry loop or
    control encoder.
    """

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        self.endpoint = (host, port)
        self.mac = parse_mac(mac)
        self.timeout = timeout
        self.socket_factory = socket_factory
        self.last_send_count = 0
        self.last_session_id = 0

    def _exchange_once(self, sock: socket.socket, packet: bytes) -> bytes:
        sent = sock.sendto(packet, self.endpoint)
        if sent != len(packet):
            raise YorkProtocolError("UDP send was incomplete")
        self.last_send_count += 1
        reply, source = sock.recvfrom(2048)
        if source[0] != self.endpoint[0] or source[1] != self.endpoint[1]:
            raise YorkProtocolError(
                f"Reply came from unexpected endpoint {source[0]}:{source[1]}"
            )
        return reply

    @staticmethod
    def _parse_state_payload(payload: bytes) -> bytes:
        if len(payload) < 3:
            raise YorkFrameError("York state reply payload is too short")
        length = int.from_bytes(payload[:2], "little")
        if length < 4 or length > len(payload) - 2:
            raise YorkFrameError("York state reply length prefix is invalid")
        frame = payload[2 : 2 + length]
        if frame[0] != 0xBB:
            raise YorkFrameError("York state reply does not begin with 0xBB")
        if york_xor(frame):
            raise YorkFrameError("York state reply XOR checksum is invalid")
        return frame

    def read_state_frame(self) -> bytes:
        validate_state_query(YORK_STATE_QUERY)
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            auth_request = session.build_packet(AUTH_COMMAND, _auth_payload())
            auth_reply = self._exchange_once(sock, auth_request)
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")

            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            query_request = session.build_packet(QUERY_COMMAND, _query_payload())
            query_reply = self._exchange_once(sock, query_request)
            query_clear = session.parse_reply(query_reply, QUERY_REPLY)
            return self._parse_state_payload(query_clear)


@dataclass(frozen=True)
class YorkOneShotWriteResult:
    before_frame: bytes
    command_reply_frame: bytes
    after_frame: bytes
    send_count: int
    session_id: int
    verification_read_count: int = 1


class BroadlinkYorkOneShotWriteClient(BroadlinkYorkReadClient):
    """Run one exact captured qualification command inside one fresh session.

    The fixed sequence is auth, state read, one exact captured command, then one
    state read. The caller must approve the decoded precondition before the
    command packet is constructed. There is no retry or general command API.
    """

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        qualification_command: bytes = YORK_QUALIFICATION_COOL_22_TO_25,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        if qualification_command not in YORK_QUALIFICATION_COMMANDS:
            raise YorkProtocolError(
                "Safety interlock rejected a non-qualification York command"
            )
        super().__init__(
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        self.qualification_command = qualification_command

    def _build_write_packet(self, session: _SessionEnvelope) -> bytes:
        return session.build_qualification_write_packet(
            self.qualification_command
        )

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
        postcondition_verifier: Callable[[bytes], bool] | None = None,
        verification_window_seconds: float = 0.0,
        verification_poll_interval_seconds: float = 5.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            auth_request = session.build_packet(AUTH_COMMAND, _auth_payload())
            auth_reply = self._exchange_once(sock, auth_request)
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_request = session.build_packet(QUERY_COMMAND, _query_payload())
            before_reply = self._exchange_once(sock, before_request)
            before_clear = session.parse_reply(before_reply, QUERY_REPLY)
            before_frame = self._parse_state_payload(before_clear)

            # This callback must raise on any mismatch. The command packet is
            # deliberately not constructed until the live precondition passes.
            approve_precondition(before_frame)

            write_request = self._build_write_packet(session)
            write_reply = self._exchange_once(sock, write_request)
            write_clear = session.parse_reply(write_reply, QUERY_REPLY)
            command_reply_frame = self._parse_state_payload(write_clear)

            elapsed = max(0.0, float(post_write_delay_seconds))
            if elapsed > 0:
                time.sleep(elapsed)

            verification_read_count = 0
            while True:
                after_request = session.build_packet(QUERY_COMMAND, _query_payload())
                after_reply = self._exchange_once(sock, after_request)
                after_clear = session.parse_reply(after_reply, QUERY_REPLY)
                after_frame = self._parse_state_payload(after_clear)
                verification_read_count += 1

                if postcondition_verifier is None or postcondition_verifier(after_frame):
                    break
                if elapsed >= verification_window_seconds:
                    break
                delay = min(
                    max(0.1, float(verification_poll_interval_seconds)),
                    verification_window_seconds - elapsed,
                )
                time.sleep(delay)
                elapsed += delay

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
            verification_read_count=verification_read_count,
        )


class BroadlinkYorkPowerWriteClient(BroadlinkYorkOneShotWriteClient):
    """Write an immutable capture or a canonical parameterised power state."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        qualification_command: bytes,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        if qualification_command in YORK_QUALIFICATION_COMMANDS:
            super().__init__(
                host,
                port,
                mac,
                timeout,
                qualification_command,
                socket_factory=socket_factory,
            )
            return
        if qualification_command not in (
            QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS
            | QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS
            | QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS
        ):
            raise YorkProtocolError(
                "Safety interlock rejected a non-canonical power command"
            )
        BroadlinkYorkReadClient.__init__(
            self,
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        self.qualification_command = qualification_command

    def _build_write_packet(self, session: _SessionEnvelope) -> bytes:
        if self.qualification_command in YORK_QUALIFICATION_COMMANDS:
            return session.build_qualification_write_packet(
                self.qualification_command
            )
        if self.qualification_command in QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS:
            return session.build_parameterised_power_on_write_packet(
                self.qualification_command
            )
        if self.qualification_command in QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS:
            return session.build_parameterised_power_off_write_packet(
                self.qualification_command
            )
        return session.build_official_sdk_mode_write_packet(
            self.qualification_command
        )


class BroadlinkYorkCoolFanAutoTemperatureWriteClient(
    BroadlinkYorkOneShotWriteClient
):
    """Transport canonical Cool commands for Auto, Low, or High fan.

    The historical class name is retained for compatibility with the
    Alpha.83–91 test and integration boundary.
    """

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        qualification_command: bytes,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        validate_general_cool_qualified_fan_temperature_command(
            qualification_command
        )
        BroadlinkYorkReadClient.__init__(
            self,
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        self.qualification_command = qualification_command

    def _build_write_packet(self, session: _SessionEnvelope) -> bytes:
        return session.build_cool_fan_auto_temperature_write_packet(
            self.qualification_command
        )


# Compatibility alias retained for Alpha.60 imports and external test harnesses.
BroadlinkYorkPowerOnWriteClient = BroadlinkYorkPowerWriteClient


class BroadlinkYorkTemperatureWriteClient(BroadlinkYorkReadClient):
    """Execute one generated temperature command under qualification guards.

    The caller must approve the live pre-read before the canonical command is
    generated. The sequence is fixed to authentication, pre-read, one write,
    and post-read. There is no retry, restore, MQTT, or startup integration.
    """

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        mode: str,
        target_temperature: float,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        # Validate inputs without retaining a caller-supplied packet.
        build_qualified_temperature_command(mode, target_temperature)
        self.mode = mode
        self.target_temperature = target_temperature

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            auth_request = session.build_packet(AUTH_COMMAND, _auth_payload())
            auth_reply = self._exchange_once(sock, auth_request)
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_request = session.build_packet(QUERY_COMMAND, _query_payload())
            before_reply = self._exchange_once(sock, before_request)
            before_clear = session.parse_reply(before_reply, QUERY_REPLY)
            before_frame = self._parse_state_payload(before_clear)

            approve_precondition(before_frame)

            command = build_qualified_temperature_command(
                self.mode, self.target_temperature
            )
            write_request = session.build_temperature_write_packet(command)
            write_reply = self._exchange_once(sock, write_request)
            write_clear = session.parse_reply(write_reply, QUERY_REPLY)
            command_reply_frame = self._parse_state_payload(write_clear)

            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)

            after_request = session.build_packet(QUERY_COMMAND, _query_payload())
            after_reply = self._exchange_once(sock, after_request)
            after_clear = session.parse_reply(after_reply, QUERY_REPLY)
            after_frame = self._parse_state_payload(after_clear)

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )


class BroadlinkYorkCapturedTemperatureWriteClient(BroadlinkYorkReadClient):
    """Execute one boundary-qualified Heat/High/Vertical temperature command."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        target_temperature: float,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        build_captured_heat_high_vertical_temperature_command(target_temperature)
        self.target_temperature = float(target_temperature)

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            auth_request = session.build_packet(AUTH_COMMAND, _auth_payload())
            auth_reply = self._exchange_once(sock, auth_request)
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_request = session.build_packet(QUERY_COMMAND, _query_payload())
            before_reply = self._exchange_once(sock, before_request)
            before_clear = session.parse_reply(before_reply, QUERY_REPLY)
            before_frame = self._parse_state_payload(before_clear)

            approve_precondition(before_frame)

            command = build_captured_heat_high_vertical_temperature_command(
                self.target_temperature
            )
            write_request = session.build_captured_temperature_write_packet(command)
            write_reply = self._exchange_once(sock, write_request)
            write_clear = session.parse_reply(write_reply, QUERY_REPLY)
            command_reply_frame = self._parse_state_payload(write_clear)

            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)

            after_request = session.build_packet(QUERY_COMMAND, _query_payload())
            after_reply = self._exchange_once(sock, after_request)
            after_clear = session.parse_reply(after_reply, QUERY_REPLY)
            after_frame = self._parse_state_payload(after_clear)

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )


class BroadlinkYorkLowVerticalTemperatureWriteClient(BroadlinkYorkReadClient):
    """Execute one qualified parameterised Heat/Low/Vertical command."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        target_temperature: float,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        build_captured_heat_low_vertical_temperature_command(target_temperature)
        self.target_temperature = float(target_temperature)

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            auth_request = session.build_packet(AUTH_COMMAND, _auth_payload())
            auth_reply = self._exchange_once(sock, auth_request)
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_request = session.build_packet(QUERY_COMMAND, _query_payload())
            before_reply = self._exchange_once(sock, before_request)
            before_clear = session.parse_reply(before_reply, QUERY_REPLY)
            before_frame = self._parse_state_payload(before_clear)

            approve_precondition(before_frame)

            command = build_captured_heat_low_vertical_temperature_command(
                self.target_temperature
            )
            write_request = session.build_low_vertical_temperature_write_packet(command)
            write_reply = self._exchange_once(sock, write_request)
            write_clear = session.parse_reply(write_reply, QUERY_REPLY)
            command_reply_frame = self._parse_state_payload(write_clear)

            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)

            after_request = session.build_packet(QUERY_COMMAND, _query_payload())
            after_reply = self._exchange_once(sock, after_request)
            after_clear = session.parse_reply(after_reply, QUERY_REPLY)
            after_frame = self._parse_state_payload(after_clear)

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )


class BroadlinkYorkFanWriteClient(BroadlinkYorkReadClient):
    """Execute one qualified Heat/Vertical Low or High fan command."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        target_fan: str,
        target_temperature: float,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        build_qualified_heat_vertical_fan_command(
            target_fan,
            target_temperature,
        )
        self.target_fan = str(target_fan).strip().lower()
        self.target_temperature = float(target_temperature)

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            auth_request = session.build_packet(AUTH_COMMAND, _auth_payload())
            auth_reply = self._exchange_once(sock, auth_request)
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError(
                    "Authentication reply payload is too short"
                )
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError(
                    "Authentication returned a zero session ID"
                )
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError(
                    "Authentication returned an invalid session key"
                )
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_request = session.build_packet(QUERY_COMMAND, _query_payload())
            before_reply = self._exchange_once(sock, before_request)
            before_clear = session.parse_reply(before_reply, QUERY_REPLY)
            before_frame = self._parse_state_payload(before_clear)

            approve_precondition(before_frame)

            command = build_qualified_heat_vertical_fan_command(
                self.target_fan,
                self.target_temperature,
            )
            write_request = session.build_fan_write_packet(
                command,
                self.target_fan,
            )
            write_reply = self._exchange_once(sock, write_request)
            write_clear = session.parse_reply(write_reply, QUERY_REPLY)
            command_reply_frame = self._parse_state_payload(write_clear)

            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)

            after_request = session.build_packet(QUERY_COMMAND, _query_payload())
            after_reply = self._exchange_once(sock, after_request)
            after_clear = session.parse_reply(after_reply, QUERY_REPLY)
            after_frame = self._parse_state_payload(after_clear)

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )


class BroadlinkYorkFanOffQualificationClient(BroadlinkYorkReadClient):
    """Execute one exact Alpha.63 Heat/22.5/Swing Off fan qualification."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        target_fan: str,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(host, port, mac, timeout, socket_factory=socket_factory)
        self.command = build_heat_22_5_fan_off_qualification_command(target_fan)
        self.target_fan = str(target_fan).strip().lower()

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            auth_reply = self._exchange_once(
                sock,
                session.build_packet(AUTH_COMMAND, _auth_payload()),
            )
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_reply = self._exchange_once(
                sock,
                session.build_packet(QUERY_COMMAND, _query_payload()),
            )
            before_frame = self._parse_state_payload(
                session.parse_reply(before_reply, QUERY_REPLY)
            )
            approve_precondition(before_frame)

            write_reply = self._exchange_once(
                sock,
                session.build_fan_off_qualification_write_packet(
                    self.command,
                    self.target_fan,
                ),
            )
            command_reply_frame = self._parse_state_payload(
                session.parse_reply(write_reply, QUERY_REPLY)
            )
            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)
            after_reply = self._exchange_once(
                sock,
                session.build_packet(QUERY_COMMAND, _query_payload()),
            )
            after_frame = self._parse_state_payload(
                session.parse_reply(after_reply, QUERY_REPLY)
            )

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )


class BroadlinkYorkCoolFanOffQualificationClient(BroadlinkYorkReadClient):
    """Execute one exact Alpha.64 Cool/22.5/Swing Off fan qualification."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        target_fan: str,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(host, port, mac, timeout, socket_factory=socket_factory)
        self.command = build_cool_22_5_fan_off_qualification_command(target_fan)
        self.target_fan = str(target_fan).strip().lower()

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            auth_reply = self._exchange_once(
                sock,
                session.build_packet(AUTH_COMMAND, _auth_payload()),
            )
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_reply = self._exchange_once(
                sock,
                session.build_packet(QUERY_COMMAND, _query_payload()),
            )
            before_frame = self._parse_state_payload(
                session.parse_reply(before_reply, QUERY_REPLY)
            )
            approve_precondition(before_frame)

            write_reply = self._exchange_once(
                sock,
                session.build_cool_fan_off_qualification_write_packet(
                    self.command,
                    self.target_fan,
                ),
            )
            command_reply_frame = self._parse_state_payload(
                session.parse_reply(write_reply, QUERY_REPLY)
            )
            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)
            after_reply = self._exchange_once(
                sock,
                session.build_packet(QUERY_COMMAND, _query_payload()),
            )
            after_frame = self._parse_state_payload(
                session.parse_reply(after_reply, QUERY_REPLY)
            )

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )


class BroadlinkYorkSwingMatrixQualificationClient(BroadlinkYorkReadClient):
    """Execute one exact Alpha.65 Heat/22.5/Low swing qualification."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        target_swing: str,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(host, port, mac, timeout, socket_factory=socket_factory)
        self.command = build_heat_22_5_low_swing_matrix_command(target_swing)
        self.target_swing = str(target_swing).strip().lower()

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            auth_reply = self._exchange_once(
                sock, session.build_packet(AUTH_COMMAND, _auth_payload())
            )
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError("Authentication reply payload is too short")
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError("Authentication returned a zero session ID")
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError("Authentication returned an invalid session key")
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_reply = self._exchange_once(
                sock, session.build_packet(QUERY_COMMAND, _query_payload())
            )
            before_frame = self._parse_state_payload(
                session.parse_reply(before_reply, QUERY_REPLY)
            )
            approve_precondition(before_frame)

            write_reply = self._exchange_once(
                sock,
                session.build_swing_matrix_qualification_write_packet(
                    self.command, self.target_swing
                ),
            )
            command_reply_frame = self._parse_state_payload(
                session.parse_reply(write_reply, QUERY_REPLY)
            )
            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)
            after_reply = self._exchange_once(
                sock, session.build_packet(QUERY_COMMAND, _query_payload())
            )
            after_frame = self._parse_state_payload(
                session.parse_reply(after_reply, QUERY_REPLY)
            )

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )


class BroadlinkYorkSwingWriteClient(BroadlinkYorkReadClient):
    """Execute one qualified Heat/Low Swing Off or Vertical command."""

    def __init__(
        self,
        host: str,
        port: int,
        mac: str,
        timeout: float,
        target_swing: str,
        target_temperature: float,
        *,
        socket_factory: SocketFactory = socket.socket,
    ) -> None:
        super().__init__(
            host,
            port,
            mac,
            timeout,
            socket_factory=socket_factory,
        )
        build_qualified_heat_low_swing_command(
            target_swing,
            target_temperature,
        )
        self.target_swing = str(target_swing).strip().lower()
        self.target_temperature = float(target_temperature)

    def execute(
        self,
        approve_precondition: Callable[[bytes], None],
        *,
        post_write_delay_seconds: float = 2.0,
    ) -> YorkOneShotWriteResult:
        self.last_send_count = 0
        self.last_session_id = 0
        seed = int.from_bytes(
            hashlib.sha256(self.mac + str(time.time_ns()).encode()).digest()[:2],
            "little",
        )
        session = _SessionEnvelope(mac=self.mac, counter=0x8000 | seed)

        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            auth_request = session.build_packet(AUTH_COMMAND, _auth_payload())
            auth_reply = self._exchange_once(sock, auth_request)
            auth_clear = session.parse_reply(auth_reply, AUTH_REPLY)
            if len(auth_clear) < 20:
                raise YorkProtocolError(
                    "Authentication reply payload is too short"
                )
            device_id = int.from_bytes(auth_clear[:4], "little")
            session_key = auth_clear[4:20]
            if device_id == 0:
                raise YorkProtocolError(
                    "Authentication returned a zero session ID"
                )
            if len(session_key) != 16 or session_key == bytes(16):
                raise YorkProtocolError(
                    "Authentication returned an invalid session key"
                )
            session.device_id = device_id
            session.key = session_key
            self.last_session_id = device_id

            before_request = session.build_packet(QUERY_COMMAND, _query_payload())
            before_reply = self._exchange_once(sock, before_request)
            before_clear = session.parse_reply(before_reply, QUERY_REPLY)
            before_frame = self._parse_state_payload(before_clear)

            approve_precondition(before_frame)

            command = build_qualified_heat_low_swing_command(
                self.target_swing,
                self.target_temperature,
            )
            if self.target_swing == "off":
                write_request = session.build_temperature_write_packet(command)
            else:
                write_request = session.build_low_vertical_temperature_write_packet(
                    command
                )
            write_reply = self._exchange_once(sock, write_request)
            write_clear = session.parse_reply(write_reply, QUERY_REPLY)
            command_reply_frame = self._parse_state_payload(write_clear)

            if post_write_delay_seconds > 0:
                time.sleep(post_write_delay_seconds)

            after_request = session.build_packet(QUERY_COMMAND, _query_payload())
            after_reply = self._exchange_once(sock, after_request)
            after_clear = session.parse_reply(after_reply, QUERY_REPLY)
            after_frame = self._parse_state_payload(after_clear)

        return YorkOneShotWriteResult(
            before_frame=before_frame,
            command_reply_frame=command_reply_frame,
            after_frame=after_frame,
            send_count=self.last_send_count,
            session_id=self.last_session_id,
        )
