from __future__ import annotations

import logging
from typing import Any, Callable

from adapters.york.broadlink import (
    BroadlinkYorkOneShotWriteClient,
    BroadlinkYorkSwingMatrixQualificationClient,
    BroadlinkYorkSwingWriteClient,
    YORK_QUALIFICATION_DRY_LOW_BOTH_21,
    YORK_QUALIFICATION_DRY_LOW_VERTICAL_21,
    YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5,
    YORK_QUALIFICATION_HEAT_LOW_OFF_21_5,
)
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.swing_command import (
    QUALIFIED_SWING_MODES,
    build_qualified_heat_low_swing_command,
)
from configuration import Config

LOG = logging.getLogger("climate_bridge.direct_swing")

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


class DirectSwingSafeStop(RuntimeError):
    """Stop a native swing write before transmission when a guard fails."""


class DirectSwingVerificationError(RuntimeError):
    """The one-shot swing write completed but its post-read did not match."""


class DirectSwingManager:
    """Guarded normal-control path for physically qualified swing changes."""

    def __init__(
        self,
        config: Config,
        *,
        client_factory: Callable[..., BroadlinkYorkSwingWriteClient] = (
            BroadlinkYorkSwingWriteClient
        ),
        axis_client_factory: Callable[..., BroadlinkYorkOneShotWriteClient] = (
            BroadlinkYorkOneShotWriteClient
        ),
        matrix_client_factory: Callable[
            ..., BroadlinkYorkSwingMatrixQualificationClient
        ] = BroadlinkYorkSwingMatrixQualificationClient,
    ) -> None:
        self.config = config
        self.client_factory = client_factory
        self.axis_client_factory = axis_client_factory
        self.matrix_client_factory = matrix_client_factory
        self.decoder = YorkPacketDecoder()
        self.last_udp_sends = 0

    @staticmethod
    def _required_shape(
        temperature: float,
        swing: str,
    ) -> dict[str, Any]:
        return {
            "power": True,
            "mode": "heat",
            "temperature": float(temperature),
            "fan": "low",
            "swing": swing,
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
        target_swing: str,
        relay_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform one guarded, physically qualified swing write with no retry."""

        swing = str(target_swing).strip().lower()
        current_swing = str(relay_state.get("swing", "")).strip().lower()
        if swing == current_swing:
            raise DirectSwingSafeStop("native swing control requires a state change")
        if relay_state.get("temperature") is None:
            raise DirectSwingSafeStop(
                "relay state has no current target temperature"
            )

        mode = str(relay_state.get("mode", "")).strip().lower()
        temperature = float(relay_state["temperature"])
        matrix_transitions = {
            ("off", "vertical"),
            ("vertical", "both"),
            ("both", "horizontal"),
            ("horizontal", "off"),
        }
        matrix_path = (
            mode == "heat"
            and temperature == 22.5
            and relay_state.get("fan") == "low"
            and (current_swing, swing) in matrix_transitions
        )
        dry_axis_path = (
            mode == "dry"
            and temperature == 21.0
            and (current_swing, swing)
            in {("vertical", "both"), ("both", "vertical")}
        )
        heat_axis_path = (
            mode == "heat"
            and temperature == 21.5
            and (current_swing, swing)
            in {("off", "horizontal"), ("horizontal", "off")}
        )

        if matrix_path:
            before_expected = self._required_shape(22.5, current_swing)
            qualified_path = "alpha65_heat_22_5_low_grouped_swing_matrix"
        elif dry_axis_path:
            before_expected = {
                **self._required_shape(21.0, current_swing),
                "mode": "dry",
            }
            command = (
                YORK_QUALIFICATION_DRY_LOW_BOTH_21
                if swing == "both"
                else YORK_QUALIFICATION_DRY_LOW_VERTICAL_21
            )
            qualified_path = "dry_21_low_independent_horizontal_axis"
        elif heat_axis_path:
            before_expected = self._required_shape(21.5, current_swing)
            command = (
                YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5
                if swing == "horizontal"
                else YORK_QUALIFICATION_HEAT_LOW_OFF_21_5
            )
            qualified_path = "heat_21_5_low_horizontal_only_axis"
        else:
            if swing not in QUALIFIED_SWING_MODES:
                raise DirectSwingSafeStop(
                    "native Horizontal control requires Heat / 21.5 °C / "
                    "Fan Low and an Off/Horizontal transition; Both control "
                    "requires Dry / 21 °C / Fan Low and a Vertical/Both "
                    "transition"
                )
            if current_swing not in QUALIFIED_SWING_MODES:
                raise DirectSwingSafeStop(
                    "native Off/Vertical control requires a current Off or "
                    "Vertical state"
                )
            before_expected = self._required_shape(temperature, current_swing)
            qualified_path = "parameterised_heat_low_off_vertical"

        mismatches = self._mismatches(before_expected, relay_state)
        if mismatches:
            raise DirectSwingSafeStop(
                "relay state is outside the qualified swing shape: "
                + ", ".join(mismatches)
            )

        if matrix_path:
            client = self.matrix_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                swing,
            )
        elif dry_axis_path or heat_axis_path:
            client = self.axis_client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                command,
            )
        else:
            # Validate swing, setpoint range and 0.5 °C increment before client
            # creation or socket use.
            build_qualified_heat_low_swing_command(swing, temperature)
            client = self.client_factory(
                self.config.direct_host,
                self.config.direct_port,
                self.config.direct_mac,
                self.config.direct_connect_timeout,
                swing,
                temperature,
            )
        after_expected = {**before_expected, "swing": swing}
        before_state: dict[str, Any] = {}

        def approve_precondition(frame: bytes) -> None:
            nonlocal before_state
            before_state = self.decoder.decode_state(frame).to_dict()
            live_mismatches = self._mismatches(
                before_expected,
                before_state,
            )
            if live_mismatches:
                raise DirectSwingSafeStop(
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
            raise DirectSwingVerificationError(
                "direct post-read verification failed: "
                + ", ".join(mismatches)
            )

        response = dict(relay_state)
        response.update(after_state)
        response["_transaction"] = {
            "success": True,
            "source": "york_direct_swing",
            "requested": {"swing": swing},
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
            "Direct swing command passed (%s/%s, %s); %s -> %s; "
            "%.1f °C and Fan Low preserved; "
            "%s UDP sends; zero retries",
            len(QUALIFIED_FIELDS),
            len(QUALIFIED_FIELDS),
            qualified_path,
            current_swing,
            swing,
            temperature,
            result.send_count,
        )
        return response
