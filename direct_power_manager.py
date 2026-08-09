from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Callable

from adapters.york.broadlink import (
    BroadlinkYorkPowerWriteClient,
    YORK_QUALIFICATION_POWER_OFF,
    YORK_QUALIFICATION_POWER_OFF_HEAT,
    YORK_QUALIFICATION_POWER_ON_COOL,
    YORK_QUALIFICATION_POWER_ON_HEAT,
    york_xor,
)
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.errors import YorkProtocolError
from adapters.york.mode_command import (
    build_parameterised_running_mode_command,
    validate_parameterised_running_mode_command,
)
from adapters.york.power_on_command import (
    build_parameterised_power_on_command,
    validate_parameterised_power_on_command,
)
from adapters.york.power_off_command import (
    build_parameterised_power_off_command,
    validate_parameterised_power_off_command,
)
from adapters.york.official_sdk_mode_transitions import (
    MODE_FIELDS,
    NON_SETPOINT_MODE_FIELDS,
    OFFICIAL_SDK_MODE_TRANSITIONS,
    OfficialSdkModeTransition,
    select_official_sdk_mode_transition,
    state_mismatches,
    validate_official_sdk_mode_command,
)
from configuration import Config

LOG = logging.getLogger("climate_bridge.direct_power")

QUALIFIED_FIELDS = MODE_FIELDS
FAN_ONLY_APPLICABLE_FIELDS = NON_SETPOINT_MODE_FIELDS


class DirectPowerSafeStop(RuntimeError):
    """Stop a direct power write before transmission when a guard fails."""


class DirectPowerVerificationError(RuntimeError):
    """The one-shot power write completed but its post-read did not match."""


class DirectPowerCriticalVerificationError(DirectPowerVerificationError):
    """A post-write read observed a dangerous unexpected power transition."""


@dataclass(frozen=True)
class DirectPowerCase:
    name: str
    requested: dict[str, Any]
    command: bytes
    before: dict[str, Any]
    after: dict[str, Any]
    expected_sha256: str


@dataclass(frozen=True)
class ParameterisedPowerOnCase:
    name: str
    requested: dict[str, Any]
    command: bytes
    before: dict[str, Any]
    after: dict[str, Any]


@dataclass(frozen=True)
class ParameterisedPowerOffCase:
    name: str
    requested: dict[str, Any]
    command: bytes
    before: dict[str, Any]
    after: dict[str, Any]


@dataclass(frozen=True)
class ParameterisedRunningModeCase:
    name: str
    requested: dict[str, Any]
    command: bytes
    before: dict[str, Any]
    after: dict[str, Any]


@dataclass(frozen=True)
class OfficialSdkModeCase:
    name: str
    requested: dict[str, Any]
    command: bytes
    before: dict[str, Any]
    after: dict[str, Any]
    source_fields: tuple[str, ...]
    target_fields: tuple[str, ...]
    dynamic_target_temperature: bool


def _official_case(key: str) -> OfficialSdkModeCase:
    transition = next(
        item for item in OFFICIAL_SDK_MODE_TRANSITIONS if item.key == key
    )
    return OfficialSdkModeCase(
        name=transition.key,
        requested={"power": True, "mode": transition.requested_mode},
        command=transition.frame,
        before=dict(transition.source),
        after=dict(transition.target),
        source_fields=transition.source_fields,
        target_fields=transition.target_fields,
        dynamic_target_temperature=transition.dynamic_target_temperature,
    )


# Evidence-facing aliases retained for historical test/report consumers. The
# runtime selector below uses only the consolidated transition registry.
OFFICIAL_SDK_FAN_ONLY_CASE = _official_case("mode-dry-to-fan-only")
OFFICIAL_SDK_FAN_ONLY_HEAT_CASE = _official_case("mode-fan-only-to-heat-23")
OFFICIAL_SDK_HEAT_AUTO_CASE = _official_case("mode-heat-23-to-auto-feel")
OFFICIAL_SDK_AUTO_COOL_CASE = _official_case("mode-auto-feel-21-to-cool-21")
OFFICIAL_SDK_AUTO_23_COOL_CASE = _official_case(
    "mode-auto-feel-23-to-cool-23"
)
OFFICIAL_SDK_AUTO_20_COOL_CASE = _official_case(
    "mode-auto-feel-20-to-cool-20"
)
OFFICIAL_SDK_COOL_DRY_CASE = _official_case("mode-cool-21-to-dry")

# Historical tests and evidence reports may still inspect this name. No
# legacy matrix case is executable or used by the runtime selector.
REMAINING_MODE_MATRIX_CASES: tuple[object, ...] = ()


COMMON_DISABLED = {
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}

DIRECT_POWER_CASES = (
    DirectPowerCase(
        name="off",
        requested={"power": False},
        command=YORK_QUALIFICATION_POWER_OFF,
        before={
            "power": True,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": False,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        expected_sha256=(
            "46b8d41444e8363bf591b41c4334386fe509b2063a42863bd143900c0cbfc629"
        ),
    ),
    DirectPowerCase(
        name="off-heat",
        requested={"power": False},
        command=YORK_QUALIFICATION_POWER_OFF_HEAT,
        before={
            "power": True,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": False,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        expected_sha256=(
            "6be1093e8fb776faf047513d3b0bd6b9cca2166fac49d60346ce1f3575707b58"
        ),
    ),
    DirectPowerCase(
        name="on-heat",
        requested={"power": True, "mode": "heat"},
        command=YORK_QUALIFICATION_POWER_ON_HEAT,
        before={
            "power": False,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": True,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        expected_sha256=(
            "a499631892d2f17255351c7fd8ff2974532d508c01f1e589a49e49bd9a891515"
        ),
    ),
    DirectPowerCase(
        name="on-cool",
        requested={"power": True, "mode": "cool"},
        command=YORK_QUALIFICATION_POWER_ON_COOL,
        before={
            "power": False,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": True,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        expected_sha256=(
            "41fc632383cbbe62b9db91e018f9b9f73eaac3315e218439fa4e6f93c01e667c"
        ),
    ),
    DirectPowerCase(
        name="heat-to-cool",
        requested={"power": True, "mode": "cool"},
        command=YORK_QUALIFICATION_POWER_ON_COOL,
        before={
            "power": True,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": True,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        expected_sha256=(
            "41fc632383cbbe62b9db91e018f9b9f73eaac3315e218439fa4e6f93c01e667c"
        ),
    ),
    DirectPowerCase(
        name="cool-to-heat",
        requested={"power": True, "mode": "heat"},
        command=YORK_QUALIFICATION_POWER_ON_HEAT,
        before={
            "power": True,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": True,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        expected_sha256=(
            "a499631892d2f17255351c7fd8ff2974532d508c01f1e589a49e49bd9a891515"
        ),
    ),
)


MODE_VERIFICATION_WINDOW_SECONDS = 30.0
MODE_VERIFICATION_POLL_SECONDS = 5.0
AUTO_FEEL_QUALIFIED_PROGRAM_TEMPERATURES = frozenset(
    {18.0, 20.0, 21.0, 23.0}
)


def _is_valid_auto_program_temperature(value: Any) -> bool:
    """Accept only observed or manual-defined latched Auto/FEEL programs."""

    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    return float(value) in AUTO_FEEL_QUALIFIED_PROGRAM_TEMPERATURES


def _is_valid_auto_ambient_temperature(value: Any) -> bool:
    """Compatibility alias for historical qualification consumers."""

    return _is_valid_auto_program_temperature(value)


class DirectPowerManager:
    """Guarded native path for captured and parameterised York power writes."""

    def __init__(
        self,
        config: Config,
        *,
        client_factory: Callable[..., BroadlinkYorkPowerWriteClient] = (
            BroadlinkYorkPowerWriteClient
        ),
    ) -> None:
        self.config = config
        self.client_factory = client_factory
        self.decoder = YorkPacketDecoder()
        self.last_udp_sends = 0
        for case in DIRECT_POWER_CASES:
            self._validate_case(case)

    @staticmethod
    def _validate_case(case: DirectPowerCase) -> None:
        if len(case.command) != 31:
            raise DirectPowerSafeStop(
                f"{case.name} fixture is not the qualified 31-byte frame"
            )
        if york_xor(case.command):
            raise DirectPowerSafeStop(f"{case.name} fixture checksum is invalid")
        if hashlib.sha256(case.command).hexdigest() != case.expected_sha256:
            raise DirectPowerSafeStop(f"{case.name} fixture fingerprint is invalid")

    @staticmethod
    def _mismatches(
        expected: dict[str, Any],
        observed: dict[str, Any],
    ) -> list[str]:
        return [
            key
            for key in QUALIFIED_FIELDS
            if observed.get(key) != expected.get(key)
        ]

    @staticmethod
    def _official_mode_mismatches(
        case: OfficialSdkModeCase,
        observed: dict[str, Any],
        *,
        target: bool,
    ) -> list[str]:
        expected = case.after if target else case.before
        fields = case.target_fields if target else case.source_fields
        mismatches = state_mismatches(expected, observed, fields)
        if (
            target
            and case.dynamic_target_temperature
            and not _is_valid_auto_program_temperature(
                observed.get("temperature")
            )
        ):
            mismatches.append("temperature")
        return mismatches

    @staticmethod
    def _select_case(command: dict[str, Any]) -> DirectPowerCase:
        matching_requests = [
            case for case in DIRECT_POWER_CASES if command == case.requested
        ]
        if len(matching_requests) == 1:
            return matching_requests[0]
        if matching_requests:
            raise DirectPowerSafeStop(
                "qualified power request requires live-state case selection"
            )
        raise DirectPowerSafeStop(
            "request is not an exact qualified power command"
        )

    @classmethod
    def _select_case_for_state(
        cls,
        command: dict[str, Any],
        authoritative_state: dict[str, Any],
    ) -> DirectPowerCase:
        matching_requests = [
            case for case in DIRECT_POWER_CASES if command == case.requested
        ]
        if not matching_requests:
            raise DirectPowerSafeStop(
                "request is not an exact qualified power command"
            )
        matching_states = [
            case
            for case in matching_requests
            if not cls._mismatches(case.before, authoritative_state)
        ]
        if len(matching_states) == 1:
            return matching_states[0]
        if not matching_states:
            raise DirectPowerSafeStop(
                "authoritative direct state is outside every qualified power shape"
            )
        raise DirectPowerSafeStop(
            "authoritative direct state ambiguously matches multiple qualified "
            "power cases"
        )

    @classmethod
    def _build_parameterised_power_on_case(
        cls,
        command: dict[str, Any],
        authoritative_state: dict[str, Any],
    ) -> ParameterisedPowerOnCase:
        if set(command) != {"power", "mode"} or command.get("power") is not True:
            raise DirectPowerSafeStop(
                "request is not an exact parameterised power-on command"
            )
        if authoritative_state.get("power") is not False:
            raise DirectPowerSafeStop(
                "parameterised power-on requires an authoritative Off state"
            )
        missing = [
            field
            for field in QUALIFIED_FIELDS
            if field not in authoritative_state
        ]
        if missing:
            raise DirectPowerSafeStop(
                "authoritative direct state is incomplete: " + ", ".join(missing)
            )
        disabled_mismatches = [
            field
            for field, expected in COMMON_DISABLED.items()
            if authoritative_state.get(field) != expected
        ]
        if disabled_mismatches:
            raise DirectPowerSafeStop(
                "authoritative direct state has unqualified feature flags: "
                + ", ".join(disabled_mismatches)
            )

        mode = str(command["mode"]).strip().lower()
        temperature = float(authoritative_state["temperature"])
        fan = str(authoritative_state["fan"]).strip().lower()
        swing = str(authoritative_state["swing"]).strip().lower()
        try:
            frame = build_parameterised_power_on_command(
                mode,
                temperature,
                fan,
                swing,
            )
            validate_parameterised_power_on_command(
                frame,
                mode,
                temperature,
                fan,
                swing,
            )
        except (TypeError, ValueError, YorkProtocolError) as error:
            raise DirectPowerSafeStop(str(error)) from error
        if len(frame) != 31 or york_xor(frame):
            raise DirectPowerSafeStop(
                "parameterised power-on frame failed canonical validation"
            )

        before = dict(authoritative_state)
        after = dict(authoritative_state)
        after.update({"power": True, "mode": mode})
        return ParameterisedPowerOnCase(
            name=f"parameterised-on-{mode}-{fan}-{swing}",
            requested={"power": True, "mode": mode},
            command=frame,
            before=before,
            after=after,
        )

    @classmethod
    def _build_parameterised_power_off_case(
        cls,
        command: dict[str, Any],
        authoritative_state: dict[str, Any],
    ) -> ParameterisedPowerOffCase:
        if command != {"power": False}:
            raise DirectPowerSafeStop(
                "request is not an exact parameterised power-off command"
            )
        if authoritative_state.get("power") is not True:
            raise DirectPowerSafeStop(
                "parameterised power-off requires an authoritative On state"
            )
        missing = [
            field
            for field in QUALIFIED_FIELDS
            if field not in authoritative_state
        ]
        if missing:
            raise DirectPowerSafeStop(
                "authoritative direct state is incomplete: " + ", ".join(missing)
            )
        disabled_mismatches = [
            field
            for field, expected in COMMON_DISABLED.items()
            if authoritative_state.get(field) != expected
        ]
        if disabled_mismatches:
            raise DirectPowerSafeStop(
                "authoritative direct state has unqualified feature flags: "
                + ", ".join(disabled_mismatches)
            )

        mode = str(authoritative_state["mode"]).strip().lower()
        temperature = float(authoritative_state["temperature"])
        fan = str(authoritative_state["fan"]).strip().lower()
        swing = str(authoritative_state["swing"]).strip().lower()
        try:
            frame = build_parameterised_power_off_command(
                mode,
                temperature,
                fan,
                swing,
            )
            validate_parameterised_power_off_command(
                frame,
                mode,
                temperature,
                fan,
                swing,
            )
        except (TypeError, ValueError, YorkProtocolError) as error:
            raise DirectPowerSafeStop(str(error)) from error
        if len(frame) != 31 or york_xor(frame):
            raise DirectPowerSafeStop(
                "parameterised power-off frame failed canonical validation"
            )

        before = dict(authoritative_state)
        after = dict(authoritative_state)
        after["power"] = False
        return ParameterisedPowerOffCase(
            name=f"parameterised-off-{mode}-{fan}-{swing}",
            requested={"power": False},
            command=frame,
            before=before,
            after=after,
        )

    @classmethod
    def _build_parameterised_running_mode_case(
        cls,
        command: dict[str, Any],
        authoritative_state: dict[str, Any],
    ) -> ParameterisedRunningModeCase:
        if set(command) != {"power", "mode"} or command.get("power") is not True:
            raise DirectPowerSafeStop(
                "request is not an exact parameterised running-mode command"
            )
        if authoritative_state.get("power") is not True:
            raise DirectPowerSafeStop(
                "parameterised running-mode control requires an authoritative On state"
            )
        missing = [
            field
            for field in QUALIFIED_FIELDS
            if field not in authoritative_state
        ]
        if missing:
            raise DirectPowerSafeStop(
                "authoritative direct state is incomplete: " + ", ".join(missing)
            )
        disabled_mismatches = [
            field
            for field, expected in COMMON_DISABLED.items()
            if authoritative_state.get(field) != expected
        ]
        if disabled_mismatches:
            raise DirectPowerSafeStop(
                "authoritative direct state has unqualified feature flags: "
                + ", ".join(disabled_mismatches)
            )

        mode = str(command["mode"]).strip().lower()
        current_mode = str(authoritative_state["mode"]).strip().lower()
        if current_mode not in {"heat", "cool"} or mode not in {"heat", "cool"}:
            raise DirectPowerSafeStop(
                "parameterised running-mode control supports only Heat and Cool"
            )
        if mode == current_mode:
            raise DirectPowerSafeStop(
                "parameterised running-mode request does not change mode"
            )
        temperature = float(authoritative_state["temperature"])
        fan = str(authoritative_state["fan"]).strip().lower()
        swing = str(authoritative_state["swing"]).strip().lower()
        try:
            current_frame = build_parameterised_running_mode_command(
                current_mode,
                temperature,
                fan,
                swing,
            )
            validate_parameterised_running_mode_command(
                current_frame,
                current_mode,
                temperature,
                fan,
                swing,
            )
            frame = build_parameterised_running_mode_command(
                mode,
                temperature,
                fan,
                swing,
            )
            validate_parameterised_running_mode_command(
                frame,
                mode,
                temperature,
                fan,
                swing,
            )
        except (TypeError, ValueError, YorkProtocolError) as error:
            raise DirectPowerSafeStop(str(error)) from error
        if len(frame) != 31 or york_xor(frame):
            raise DirectPowerSafeStop(
                "parameterised running-mode frame failed canonical validation"
            )

        before = dict(authoritative_state)
        after = dict(authoritative_state)
        after["mode"] = mode
        return ParameterisedRunningModeCase(
            name=f"parameterised-mode-{current_mode}-to-{mode}-{fan}-{swing}",
            requested={"power": True, "mode": mode},
            command=frame,
            before=before,
            after=after,
        )

    @staticmethod
    def _select_official_sdk_mode_case(
        command: dict[str, Any],
        authoritative_state: dict[str, Any],
    ) -> OfficialSdkModeCase:
        if set(command) != {"power", "mode"} or command.get("power") is not True:
            raise DirectPowerSafeStop(
                "request is not an exact official-SDK mode command"
            )
        try:
            transition: OfficialSdkModeTransition = (
                select_official_sdk_mode_transition(
                    str(command["mode"]),
                    authoritative_state,
                )
            )
            validate_official_sdk_mode_command(transition.frame)
        except YorkProtocolError as error:
            raise DirectPowerSafeStop(str(error)) from error
        if len(transition.frame) != 31 or york_xor(transition.frame):
            raise DirectPowerSafeStop(
                "official-SDK mode frame failed byte-exact validation"
            )
        return OfficialSdkModeCase(
            name=transition.key,
            requested={"power": True, "mode": transition.requested_mode},
            command=transition.frame,
            before=dict(transition.source),
            after=dict(transition.target),
            source_fields=transition.source_fields,
            target_fields=transition.target_fields,
            dynamic_target_temperature=transition.dynamic_target_temperature,
        )

    def command(
        self,
        command: dict[str, Any],
        authoritative_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform one guarded captured power write with no retry."""

        try:
            case: (
                DirectPowerCase
                | ParameterisedPowerOnCase
                | ParameterisedPowerOffCase
                | ParameterisedRunningModeCase
                | OfficialSdkModeCase
            ) = self._select_case_for_state(command, authoritative_state)
        except DirectPowerSafeStop as exact_case_error:
            try:
                if command == {"power": False}:
                    case = self._build_parameterised_power_off_case(
                        command,
                        authoritative_state,
                    )
                elif (
                    set(command) == {"power", "mode"}
                    and command.get("power") is True
                    and authoritative_state.get("power") is True
                ):
                    try:
                        case = self._select_official_sdk_mode_case(
                            command,
                            authoritative_state,
                        )
                    except DirectPowerSafeStop:
                        case = self._build_parameterised_running_mode_case(
                            command,
                            authoritative_state,
                        )
                else:
                    case = self._build_parameterised_power_on_case(
                        command,
                        authoritative_state,
                    )
            except DirectPowerSafeStop:
                raise exact_case_error

        preflight_mismatches = (
            self._official_mode_mismatches(
                case,
                authoritative_state,
                target=False,
            )
            if isinstance(case, OfficialSdkModeCase)
            else self._mismatches(case.before, authoritative_state)
        )
        if preflight_mismatches:
            raise DirectPowerSafeStop(
                "authoritative direct state is outside the qualified power shape: "
                + ", ".join(preflight_mismatches)
            )

        before_state: dict[str, Any] = {}

        def approve_precondition(frame: bytes) -> None:
            nonlocal before_state
            before_state = self.decoder.decode_state(frame).to_dict()
            mismatches = (
                self._official_mode_mismatches(
                    case,
                    before_state,
                    target=False,
                )
                if isinstance(case, OfficialSdkModeCase)
                else self._mismatches(case.before, before_state)
            )
            if mismatches:
                raise DirectPowerSafeStop(
                    "direct pre-read differs from authoritative direct state: "
                    + ", ".join(mismatches)
                )

        client = self.client_factory(
            self.config.direct_host,
            self.config.direct_port,
            self.config.direct_mac,
            self.config.direct_connect_timeout,
            case.command,
        )
        execute_kwargs: dict[str, Any] = {
            "post_write_delay_seconds": (
                self.config.direct_control_post_write_delay_seconds
            )
        }
        if isinstance(case, OfficialSdkModeCase):
            def verify_postcondition(frame: bytes) -> bool:
                observed = self.decoder.decode_state(frame).to_dict()
                if case.after.get("power") is True and observed.get("power") is False:
                    raise DirectPowerCriticalVerificationError(
                        "CRITICAL: unexpected Power Off during delayed "
                        f"verification of {case.name}"
                    )
                return not self._official_mode_mismatches(
                    case,
                    observed,
                    target=True,
                )

            execute_kwargs.update(
                {
                    "postcondition_verifier": verify_postcondition,
                    "verification_window_seconds": (
                        MODE_VERIFICATION_WINDOW_SECONDS
                    ),
                    "verification_poll_interval_seconds": (
                        MODE_VERIFICATION_POLL_SECONDS
                    ),
                }
            )
        try:
            result = client.execute(approve_precondition, **execute_kwargs)
        finally:
            self.last_udp_sends = client.last_send_count

        after_state = self.decoder.decode_state(result.after_frame).to_dict()
        mismatches = (
            self._official_mode_mismatches(case, after_state, target=True)
            if isinstance(case, OfficialSdkModeCase)
            else self._mismatches(case.after, after_state)
        )
        if mismatches:
            raise DirectPowerVerificationError(
                "direct post-read verification failed: "
                + ", ".join(mismatches)
            )

        response = dict(authoritative_state)
        response.update(after_state)
        if (
            isinstance(case, OfficialSdkModeCase)
            and "temperature" not in case.target_fields
            and not case.dynamic_target_temperature
        ):
            response.pop("temperature", None)
        compared_field_count = (
            len(case.target_fields) + int(case.dynamic_target_temperature)
            if isinstance(case, OfficialSdkModeCase)
            else len(QUALIFIED_FIELDS)
        )
        response["_transaction"] = {
            "success": True,
            "source": "york_direct_power",
            "case": case.name,
            "requested": dict(case.requested),
            "before": before_state,
            "after": after_state,
            "verification": {
                "success": True,
                "matched_fields": compared_field_count,
                "compared_fields": compared_field_count,
            },
            "udp_sends": result.send_count,
            "verification_reads": result.verification_read_count,
            "automatic_retries": 0,
            "fallback_used": False,
        }
        LOG.info(
            "Direct power command %s passed (%s/%s); %s UDP sends; zero retries",
            case.name,
            compared_field_count,
            compared_field_count,
            result.send_count,
        )
        return response
