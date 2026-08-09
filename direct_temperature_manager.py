from __future__ import annotations

import logging
from typing import Any, Callable

from adapters.york.broadlink import (
    BroadlinkYorkCapturedTemperatureWriteClient,
    BroadlinkYorkCoolFanAutoTemperatureWriteClient,
    BroadlinkYorkLowVerticalTemperatureWriteClient,
    BroadlinkYorkTemperatureWriteClient,
)
from adapters.york.captured_temperature_command import (
    build_captured_heat_high_vertical_temperature_command,
)
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.cool_fan_auto_temperature_qualification import (
    COOL_20_5_FAN_AUTO_SOURCE,
    COOL_20_5_FAN_AUTO_TARGET,
    COOL_20_FAN_AUTO_SOURCE,
    COOL_20_FAN_AUTO_TARGET,
    COOL_21_FAN_AUTO_TARGET,
    COOL_22_FAN_AUTO_SOURCE,
    COOL_22_FAN_AUTO_TARGET,
    COOL_22_5_FAN_AUTO_SOURCE,
    COOL_23_FAN_AUTO_SOURCE,
    COOL_24_FAN_AUTO_SOURCE,
    COOL_24_5_FAN_AUTO_SOURCE,
    build_general_cool_fan_auto_temperature_command,
    build_general_cool_qualified_fan_temperature_command,
    build_grouped_cool_fan_auto_temperature_command,
    build_cool_20_5_to_20_fan_auto_command,
    build_cool_20_to_20_5_fan_auto_command,
    build_cool_20_to_22_fan_auto_command,
    build_cool_22_to_20_fan_auto_command,
    build_cool_23_to_21_fan_auto_command,
)
from adapters.york.low_vertical_temperature_command import (
    build_captured_heat_low_vertical_temperature_command,
)
from configuration import Config

LOG = logging.getLogger("climate_bridge.direct_temperature")

QUALIFIED_FIELDS = (
    "power",
    "mode",
    "temperature",
    "fan",
    "swing",
    "turbo",
    "eco",
    "health",
    "display",
)


class DirectTemperatureSafeStop(RuntimeError):
    """Stop a direct write before transmission when its safety gate fails."""


class DirectTemperatureVerificationError(RuntimeError):
    """The one-shot write completed but its post-read did not match."""


class DirectTemperatureCriticalVerificationError(
    DirectTemperatureVerificationError
):
    """A delayed read observed an unexpected Power Off transition."""


TEMPERATURE_VERIFICATION_WINDOW_SECONDS = 30.0
TEMPERATURE_VERIFICATION_POLL_SECONDS = 5.0


class DirectTemperatureManager:
    """Guarded normal-control path for qualified York temperature writes."""

    def __init__(
        self,
        config: Config,
        *,
        client_factory: Callable[..., BroadlinkYorkTemperatureWriteClient] = (
            BroadlinkYorkTemperatureWriteClient
        ),
        captured_client_factory: Callable[
            ..., BroadlinkYorkCapturedTemperatureWriteClient
        ] = BroadlinkYorkCapturedTemperatureWriteClient,
        low_vertical_client_factory: Callable[
            ..., BroadlinkYorkLowVerticalTemperatureWriteClient
        ] = BroadlinkYorkLowVerticalTemperatureWriteClient,
        cool_fan_auto_client_factory: Callable[
            ..., BroadlinkYorkCoolFanAutoTemperatureWriteClient
        ] = BroadlinkYorkCoolFanAutoTemperatureWriteClient,
    ) -> None:
        self.config = config
        self.client_factory = client_factory
        self.captured_client_factory = captured_client_factory
        self.low_vertical_client_factory = low_vertical_client_factory
        self.cool_fan_auto_client_factory = cool_fan_auto_client_factory
        self.decoder = YorkPacketDecoder()
        self.last_udp_sends = 0

    @staticmethod
    def _legacy_required_shape(mode: str, temperature: float) -> dict[str, Any]:
        return {
            "power": True,
            "mode": mode,
            "temperature": float(temperature),
            "fan": "low",
            "swing": "off",
            "turbo": False,
            "eco": False,
            "health": False,
            "display": True,
        }

    @staticmethod
    def _captured_required_shape(temperature: float) -> dict[str, Any]:
        return {
            "power": True,
            "mode": "heat",
            "temperature": float(temperature),
            "fan": "high",
            "swing": "vertical",
            "turbo": False,
            "eco": False,
            "health": False,
            "display": True,
        }

    @staticmethod
    def _low_vertical_required_shape(temperature: float) -> dict[str, Any]:
        return {
            "power": True,
            "mode": "heat",
            "temperature": float(temperature),
            "fan": "low",
            "swing": "vertical",
            "turbo": False,
            "eco": False,
            "health": False,
            "display": True,
        }

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

    def command(
        self,
        target_temperature: float,
        relay_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform one guarded direct temperature write with no retry."""

        mode = str(relay_state.get("mode", "")).strip().lower()
        if mode not in {"heat", "cool"}:
            raise DirectTemperatureSafeStop(
                "direct temperature control requires Heat or Cool mode"
            )
        if relay_state.get("temperature") is None:
            raise DirectTemperatureSafeStop(
                "relay state has no current target temperature"
            )

        legacy_expected = self._legacy_required_shape(
            mode,
            float(relay_state["temperature"]),
        )
        captured_expected = self._captured_required_shape(
            float(relay_state["temperature"])
        )
        legacy_mismatches = self._mismatches(legacy_expected, relay_state)
        captured_mismatches = self._mismatches(captured_expected, relay_state)
        low_vertical_expected = self._low_vertical_required_shape(
            float(relay_state["temperature"])
        )
        low_vertical_mismatches = self._mismatches(
            low_vertical_expected,
            relay_state,
        )

        cool_fan_auto_mismatches = self._mismatches(
            COOL_23_FAN_AUTO_SOURCE,
            relay_state,
        )
        current_fan = str(relay_state.get("fan", "")).strip().lower()
        general_cool_qualified_fan_expected = {
            **COOL_20_FAN_AUTO_SOURCE,
            "temperature": float(relay_state["temperature"]),
            "fan": current_fan,
        }
        general_cool_qualified_fan_mismatches = self._mismatches(
            general_cool_qualified_fan_expected,
            relay_state,
        )
        if current_fan not in {"auto", "low", "high"}:
            general_cool_qualified_fan_mismatches = sorted(
                set(general_cool_qualified_fan_mismatches).union({"fan"})
            )
        cool_20_fan_auto_mismatches = self._mismatches(
            COOL_20_FAN_AUTO_SOURCE,
            relay_state,
        )
        cool_20_5_fan_auto_mismatches = self._mismatches(
            COOL_20_5_FAN_AUTO_SOURCE,
            relay_state,
        )
        cool_22_fan_auto_mismatches = self._mismatches(
            COOL_22_FAN_AUTO_SOURCE,
            relay_state,
        )
        grouped_source_states = {
            22.5: COOL_22_5_FAN_AUTO_SOURCE,
            24.0: COOL_24_FAN_AUTO_SOURCE,
            24.5: COOL_24_5_FAN_AUTO_SOURCE,
        }
        grouped_source_temperature = next(
            (
                temperature
                for temperature, expected in grouped_source_states.items()
                if not self._mismatches(expected, relay_state)
            ),
            None,
        )

        if not general_cool_qualified_fan_mismatches:
            command = build_general_cool_qualified_fan_temperature_command(
                relay_state,
                target_temperature,
            )
            edge = (
                float(relay_state["temperature"]),
                float(target_temperature),
            )
            path = {
                (23.0, 21.0): "official_sdk_cool_23_to_21_fan_auto",
                (20.0, 20.5): "official_sdk_cool_20_to_20_5_fan_auto",
                (20.5, 20.0): "official_sdk_cool_20_5_to_20_fan_auto",
                (20.0, 22.0): "official_sdk_cool_20_to_22_fan_auto",
                (22.0, 20.0): "official_sdk_cool_22_to_20_fan_auto",
                (20.0, 22.5): "official_sdk_cool_20_to_22_5_fan_auto_matrix",
                (22.5, 24.0): "official_sdk_cool_22_5_to_24_fan_auto_matrix",
                (24.0, 24.5): "official_sdk_cool_24_to_24_5_fan_auto_matrix",
                (24.5, 20.5): "official_sdk_cool_24_5_to_20_5_fan_auto_matrix",
                (20.5, 22.0): "official_sdk_cool_20_5_to_22_fan_auto_matrix",
            }.get(edge, "general_cool_fan_auto_temperature_encoder") if current_fan == "auto" else (
                f"general_cool_temperature_encoder_fan_{current_fan}"
            )
            before_expected = general_cool_qualified_fan_expected
            client = self.cool_fan_auto_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                command,
            )
        elif not cool_fan_auto_mismatches:
            command = build_cool_23_to_21_fan_auto_command(
                relay_state,
                target_temperature,
            )
            path = "official_sdk_cool_23_to_21_fan_auto"
            before_expected = dict(COOL_23_FAN_AUTO_SOURCE)
            client = self.cool_fan_auto_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                command,
            )
        elif not cool_20_fan_auto_mismatches:
            if (
                not isinstance(target_temperature, bool)
                and float(target_temperature) == 22.0
            ):
                command = build_cool_20_to_22_fan_auto_command(
                    relay_state,
                    target_temperature,
                )
                path = "official_sdk_cool_20_to_22_fan_auto"
            elif (
                not isinstance(target_temperature, bool)
                and float(target_temperature) == 22.5
            ):
                command = build_grouped_cool_fan_auto_temperature_command(
                    relay_state,
                    target_temperature,
                )
                path = "official_sdk_cool_20_to_22_5_fan_auto_matrix"
            else:
                command = build_cool_20_to_20_5_fan_auto_command(
                    relay_state,
                    target_temperature,
                )
                path = "official_sdk_cool_20_to_20_5_fan_auto"
            before_expected = dict(COOL_20_FAN_AUTO_SOURCE)
            client = self.cool_fan_auto_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                command,
            )
        elif not cool_20_5_fan_auto_mismatches:
            if (
                not isinstance(target_temperature, bool)
                and float(target_temperature) == 22.0
            ):
                command = build_grouped_cool_fan_auto_temperature_command(
                    relay_state,
                    target_temperature,
                )
                path = "official_sdk_cool_20_5_to_22_fan_auto_matrix"
            else:
                command = build_cool_20_5_to_20_fan_auto_command(
                    relay_state,
                    target_temperature,
                )
                path = "official_sdk_cool_20_5_to_20_fan_auto"
            before_expected = dict(COOL_20_5_FAN_AUTO_SOURCE)
            client = self.cool_fan_auto_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                command,
            )
        elif not cool_22_fan_auto_mismatches:
            command = build_cool_22_to_20_fan_auto_command(
                relay_state,
                target_temperature,
            )
            path = "official_sdk_cool_22_to_20_fan_auto"
            before_expected = dict(COOL_22_FAN_AUTO_SOURCE)
            client = self.cool_fan_auto_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                command,
            )
        elif grouped_source_temperature is not None:
            command = build_grouped_cool_fan_auto_temperature_command(
                relay_state,
                target_temperature,
            )
            path = {
                (22.5, 24.0): "official_sdk_cool_22_5_to_24_fan_auto_matrix",
                (24.0, 24.5): "official_sdk_cool_24_to_24_5_fan_auto_matrix",
                (24.5, 20.5): "official_sdk_cool_24_5_to_20_5_fan_auto_matrix",
            }.get(
                (grouped_source_temperature, float(target_temperature)),
                "official_sdk_cool_fan_auto_matrix",
            )
            before_expected = dict(
                grouped_source_states[grouped_source_temperature]
            )
            client = self.cool_fan_auto_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                command,
            )
        elif not low_vertical_mismatches:
            # Alpha.46 extends the qualified parameterised 16–31 °C generator
            # to 0.5 °C increments for normal guarded Low/Vertical control.
            # Validate the target before creating a client or opening a socket.
            build_captured_heat_low_vertical_temperature_command(
                target_temperature
            )
            path = "parameterised_heat_low_vertical"
            before_expected = low_vertical_expected
            client = self.low_vertical_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                float(target_temperature),
            )
        elif not captured_mismatches:
            # Validate the complete 0.5 °C captured-generator boundary before
            # creating a client or opening a socket.
            build_captured_heat_high_vertical_temperature_command(
                target_temperature
            )
            path = "captured_heat_high_vertical"
            before_expected = captured_expected
            client = self.captured_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                float(target_temperature),
            )
        elif not legacy_mismatches:
            path = "legacy_low_swing_off"
            before_expected = legacy_expected
            client = self.client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                mode,
                float(target_temperature),
            )
        else:
            mismatch_fields = sorted(
                set(legacy_mismatches)
                .intersection(captured_mismatches)
                .intersection(low_vertical_mismatches)
                .intersection(cool_fan_auto_mismatches)
                .intersection(cool_20_fan_auto_mismatches)
                .intersection(cool_20_5_fan_auto_mismatches)
                .intersection(cool_22_fan_auto_mismatches)
                .intersection(general_cool_qualified_fan_mismatches)
            )
            if not mismatch_fields:
                mismatch_fields = sorted(
                    set(legacy_mismatches)
                    .union(captured_mismatches)
                    .union(low_vertical_mismatches)
                    .union(cool_fan_auto_mismatches)
                    .union(cool_20_fan_auto_mismatches)
                    .union(cool_20_5_fan_auto_mismatches)
                    .union(cool_22_fan_auto_mismatches)
                    .union(general_cool_qualified_fan_mismatches)
                )
            raise DirectTemperatureSafeStop(
                "relay state is outside every qualified temperature shape: "
                + ", ".join(mismatch_fields)
            )

        after_expected = {
            **before_expected,
            "temperature": float(target_temperature),
        }
        before_state: dict[str, Any] = {}

        def approve_precondition(frame: bytes) -> None:
            nonlocal before_state
            before_state = self.decoder.decode_state(frame).to_dict()
            mismatches = self._mismatches(before_expected, before_state)
            if mismatches:
                raise DirectTemperatureSafeStop(
                    "direct pre-read differs from relay state: "
                    + ", ".join(mismatches)
                )

        execute_kwargs: dict[str, Any] = {
            "post_write_delay_seconds": (
                self.config.direct_control_post_write_delay_seconds
            )
        }
        if (
            path.startswith("official_sdk_cool_")
            or path == "general_cool_fan_auto_temperature_encoder"
            or path.startswith("general_cool_temperature_encoder_fan_")
        ):
            edge_label = (
                "Cool 23 to 21 Fan Auto"
                if path == "official_sdk_cool_23_to_21_fan_auto"
                else (
                    "Cool 20 to 20.5 Fan Auto"
                    if path == "official_sdk_cool_20_to_20_5_fan_auto"
                    else (
                        "Cool 20.5 to 20 Fan Auto"
                        if path == "official_sdk_cool_20_5_to_20_fan_auto"
                        else (
                            "Cool 20 to 22 Fan Auto"
                            if path == "official_sdk_cool_20_to_22_fan_auto"
                            else (
                                f"Cool {before_expected['temperature']:g} to "
                                f"{float(target_temperature):g} Fan "
                                f"{before_expected['fan'].title()}"
                            )
                        )
                    )
                )
            )

            def verify_postcondition(frame: bytes) -> bool:
                observed = self.decoder.decode_state(frame).to_dict()
                if observed.get("power") is False:
                    raise DirectTemperatureCriticalVerificationError(
                        "CRITICAL: unexpected Power Off during delayed "
                        f"verification of {edge_label}"
                    )
                return not self._mismatches(after_expected, observed)

            execute_kwargs.update(
                {
                    "postcondition_verifier": verify_postcondition,
                    "verification_window_seconds": (
                        TEMPERATURE_VERIFICATION_WINDOW_SECONDS
                    ),
                    "verification_poll_interval_seconds": (
                        TEMPERATURE_VERIFICATION_POLL_SECONDS
                    ),
                }
            )
        try:
            result = client.execute(approve_precondition, **execute_kwargs)
        finally:
            self.last_udp_sends = client.last_send_count

        after_state = self.decoder.decode_state(result.after_frame).to_dict()
        mismatches = self._mismatches(after_expected, after_state)
        if mismatches:
            raise DirectTemperatureVerificationError(
                "direct post-read verification failed: "
                + ", ".join(mismatches)
            )

        # Preserve relay-only observations such as indoor temperature until the
        # next regular poll, while direct evidence replaces every decoded field.
        response = dict(relay_state)
        response.update(after_state)
        response["_transaction"] = {
            "success": True,
            "source": (
                "york_direct_temperature_low_vertical"
                if path == "parameterised_heat_low_vertical"
                else (
                    "york_direct_temperature_official_sdk_fan_auto"
                    if (
                        path.startswith("official_sdk_cool_")
                        or path == "general_cool_fan_auto_temperature_encoder"
                    )
                    else (
                        "york_direct_temperature_general_cool_qualified_fan"
                        if path.startswith("general_cool_temperature_encoder_fan_")
                        else (
                            "york_direct_temperature_captured"
                            if path == "captured_heat_high_vertical"
                            else "york_direct_temperature"
                        )
                    )
                )
            ),
            "requested": {"temperature": float(target_temperature)},
            "qualified_path": path,
            "before": before_state,
            "after": after_state,
            "verification": {
                "success": True,
                "matched_fields": len(QUALIFIED_FIELDS),
                "compared_fields": len(QUALIFIED_FIELDS),
            },
            "udp_sends": result.send_count,
            "verification_reads": result.verification_read_count,
            "automatic_retries": 0,
            "fallback_used": False,
        }
        LOG.info(
            "Direct temperature command passed (%s/%s, %s); %s -> %s °C; "
            "%s UDP sends; zero retries",
            len(QUALIFIED_FIELDS),
            len(QUALIFIED_FIELDS),
            path,
            before_expected["temperature"],
            target_temperature,
            result.send_count,
        )
        return response
