from __future__ import annotations

import logging
from typing import Any, Callable

from adapters.york.broadlink import (
    BroadlinkYorkCoolFanOffQualificationClient,
    BroadlinkYorkFanOffQualificationClient,
    BroadlinkYorkFanWriteClient,
)
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.fan_command import (
    QUALIFIED_FAN_MODES,
    build_qualified_heat_vertical_fan_command,
)
from configuration import Config

LOG = logging.getLogger("climate_bridge.direct_fan")

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


class DirectFanSafeStop(RuntimeError):
    """Stop a native fan write before transmission when a guard fails."""


class DirectFanVerificationError(RuntimeError):
    """The one-shot fan write completed but its post-read did not match."""


class DirectFanManager:
    """Guarded normal-control path for qualified Low/High fan changes."""

    def __init__(
        self,
        config: Config,
        *,
        client_factory: Callable[..., BroadlinkYorkFanWriteClient] = (
            BroadlinkYorkFanWriteClient
        ),
        off_client_factory: Callable[..., BroadlinkYorkFanOffQualificationClient] = (
            BroadlinkYorkFanOffQualificationClient
        ),
        cool_off_client_factory: Callable[
            ..., BroadlinkYorkCoolFanOffQualificationClient
        ] = BroadlinkYorkCoolFanOffQualificationClient,
    ) -> None:
        self.config = config
        self.client_factory = client_factory
        self.off_client_factory = off_client_factory
        self.cool_off_client_factory = cool_off_client_factory
        self.decoder = YorkPacketDecoder()
        self.last_udp_sends = 0

    @staticmethod
    def _required_shape(
        temperature: float,
        fan: str,
    ) -> dict[str, Any]:
        return {
            "power": True,
            "mode": "heat",
            "temperature": float(temperature),
            "fan": fan,
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
        target_fan: str,
        relay_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform one guarded Low/High fan write with no retry."""

        fan = str(target_fan).strip().lower()
        if fan not in QUALIFIED_FAN_MODES:
            raise DirectFanSafeStop(
                "native fan control supports only Low and High"
            )
        current_fan = str(relay_state.get("fan", "")).strip().lower()
        if current_fan not in QUALIFIED_FAN_MODES:
            raise DirectFanSafeStop(
                "native fan control requires a current Low or High state"
            )
        if fan == current_fan:
            raise DirectFanSafeStop(
                "native fan control requires a Low to High or High to Low change"
            )
        if relay_state.get("temperature") is None:
            raise DirectFanSafeStop(
                "relay state has no current target temperature"
            )

        temperature = float(relay_state["temperature"])
        current_mode = str(relay_state.get("mode", "")).strip().lower()
        current_swing = str(relay_state.get("swing", "")).strip().lower()
        fan_off_qualification = (
            current_mode in ("heat", "cool")
            and temperature == 22.5
            and current_swing == "off"
        )
        # Alpha.65 field evidence showed that the final matrix edge can leave
        # the authoritative packet decoded as Horizontal even after the
        # physical louvers have stopped and Home Assistant displays Off. Keep
        # that compatibility case isolated to the exact failed Step 5 source
        # and normalise it with the already fingerprint-locked High/Off frame.
        post_swing_qualification = (
            current_mode == "heat"
            and temperature == 22.5
            and current_fan == "low"
            and fan == "high"
            and current_swing == "horizontal"
        )
        before_expected = self._required_shape(temperature, current_fan)
        if fan_off_qualification:
            before_expected["mode"] = current_mode
            before_expected["swing"] = "off"
        elif post_swing_qualification:
            before_expected["swing"] = "horizontal"
        mismatches = self._mismatches(before_expected, relay_state)
        if mismatches:
            raise DirectFanSafeStop(
                "relay state is outside the qualified fan shape: "
                + ", ".join(mismatches)
            )

        # Validate fan, setpoint range and 0.5 °C increment before client
        # creation or socket use.
        if post_swing_qualification:
            client = self.off_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                fan,
            )
            qualified_path = (
                "alpha66_heat_22_5_low_horizontal_to_high_off_qualification"
            )
        elif fan_off_qualification and current_mode == "heat":
            client = self.off_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                fan,
            )
            qualified_path = "alpha63_heat_22_5_off_low_high_qualification"
        elif fan_off_qualification and current_mode == "cool":
            client = self.cool_off_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                fan,
            )
            qualified_path = "alpha64_cool_22_5_off_low_high_qualification"
        else:
            build_qualified_heat_vertical_fan_command(fan, temperature)
            client = self.client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                fan,
                temperature,
            )
            qualified_path = "parameterised_heat_vertical_low_high"
        after_expected = {**before_expected, "fan": fan}
        if post_swing_qualification:
            after_expected["swing"] = "off"
        before_state: dict[str, Any] = {}

        def approve_precondition(frame: bytes) -> None:
            nonlocal before_state
            before_state = self.decoder.decode_state(frame).to_dict()
            live_mismatches = self._mismatches(
                before_expected,
                before_state,
            )
            if live_mismatches:
                raise DirectFanSafeStop(
                    "direct pre-read differs from relay state: "
                    + ", ".join(live_mismatches)
                )

        try:
            result = client.execute(
                approve_precondition,
                post_write_delay_seconds=(
                    self.config.direct_control_post_write_delay_seconds
                ),
            )
        finally:
            self.last_udp_sends = client.last_send_count

        after_state = self.decoder.decode_state(result.after_frame).to_dict()
        mismatches = self._mismatches(after_expected, after_state)
        if mismatches:
            raise DirectFanVerificationError(
                "direct post-read verification failed: "
                + ", ".join(mismatches)
            )

        response = dict(relay_state)
        response.update(after_state)
        response["_transaction"] = {
            "success": True,
            "source": "york_direct_fan",
            "requested": {"fan": fan},
            "qualified_path": qualified_path,
            "before": before_state,
            "after": after_state,
            "verification": {
                "success": True,
                "matched_fields": len(QUALIFIED_FIELDS),
                "compared_fields": len(QUALIFIED_FIELDS),
            },
            "udp_sends": result.send_count,
            "automatic_retries": 0,
            "fallback_used": False,
        }
        LOG.info(
            "Direct fan command passed (%s/%s, %s); %s -> %s; %.1f °C and "
            "Swing %s preserved; %s UDP sends; zero retries",
            len(QUALIFIED_FIELDS),
            len(QUALIFIED_FIELDS),
            qualified_path,
            current_fan,
            fan,
            temperature,
            str(after_state["swing"]).title(),
            result.send_count,
        )
        return response
