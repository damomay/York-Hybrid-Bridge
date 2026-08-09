"""Fail-fast release/package verification for Climate Bridge."""
from __future__ import annotations

import re
from pathlib import Path

from version import APP_VERSION

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "Dockerfile", "docker-compose.yml", "bridge.py", "configuration.py",
    "container_qualification.py",
    "transport/__init__.py", "transport/factory.py",
    "transport/native_command_boundary.py",
    "adapters/__init__.py", "adapters/york/__init__.py",
    "adapters/york/broadlink.py",
    "direct_read_manager.py",
    "test_sprint_290_direct_read_integration.py",
    "test_sprint_293_target_temperature.py",
    "SPRINT_2_9_3_TARGET_TEMPERATURE.md",
    "york_one_shot_write_qualification.py",
    "test_sprint_300_one_shot_direct_write.py",
    "SPRINT_3_0_0_ONE_SHOT_DIRECT_WRITE.md",
    "protocols/york/qualification/alpha25_one_shot_write.json",
    "york_heat_one_shot_write_qualification.py",
    "test_sprint_301_heat_one_shot_direct_write.py",
    "SPRINT_3_0_1_HEAT_ONE_SHOT_DIRECT_WRITE.md",
    "protocols/york/qualification/alpha26_heat_one_shot_write.json",
    "adapters/york/temperature_command.py",
    "york_dynamic_temperature_qualification.py",
    "test_sprint_302_dynamic_temperature_command.py",
    "SPRINT_3_0_2_DYNAMIC_TEMPERATURE_COMMAND.md",
    "protocols/york/qualification/alpha27_dynamic_temperature_command.json",
    "york_uncaptured_temperature_qualification.py",
    "test_sprint_303_uncaptured_temperature_command.py",
    "SPRINT_3_0_3_UNCAPTURED_HEAT_COOL_TEMPERATURE.md",
    "direct_temperature_manager.py",
    "direct_power_manager.py",
    "test_sprint_315_guarded_direct_power.py",
    "SPRINT_3_1_5_GUARDED_DIRECT_POWER_CONTROL.md",
    "test_sprint_317_guarded_power_off_heat.py",
    "SPRINT_3_1_7_GUARDED_POWER_OFF_HEAT_CONTROL.md",
    "york_mode_one_shot_qualification.py",
    "test_sprint_318_running_mode_qualification.py",
    "SPRINT_3_1_8_RUNNING_MODE_CHANGE_QUALIFICATION.md",
    "protocols/york/qualification/alpha37_running_mode_changes.json",
    "test_sprint_319_guarded_running_mode_control.py",
    "SPRINT_3_1_9_GUARDED_RUNNING_MODE_CONTROL.md",
    "adapters/york/captured_temperature_command.py",
    "york_temperature_one_shot_qualification.py",
    "test_sprint_3110_temperature_encoding_qualification.py",
    "SPRINT_3_1_10_TEMPERATURE_ENCODING_QUALIFICATION.md",
    "protocols/york/qualification/alpha39_heat_temperature_encoding.json",
    "test_sprint_3111_temperature_boundary_qualification.py",
    "SPRINT_3_1_11_TEMPERATURE_BOUNDARY_QUALIFICATION.md",
    "protocols/york/qualification/alpha40_heat_temperature_boundaries.json",
    "test_sprint_3112_guarded_temperature_control.py",
    "SPRINT_3_1_12_GUARDED_TEMPERATURE_CONTROL.md",
    "adapters/york/low_vertical_temperature_command.py",
    "york_low_vertical_temperature_qualification.py",
    "test_sprint_3113_low_vertical_temperature_qualification.py",
    "SPRINT_3_1_13_LOW_VERTICAL_TEMPERATURE_QUALIFICATION.md",
    "protocols/york/qualification/alpha42_heat_low_vertical_temperature.json",
    "test_sprint_3114_guarded_low_vertical_temperature_control.py",
    "SPRINT_3_1_14_GUARDED_LOW_VERTICAL_TEMPERATURE_CONTROL.md",
    "york_low_vertical_temperature_range_qualification.py",
    "test_sprint_3115_parameterised_low_vertical_temperature.py",
    "SPRINT_3_1_15_PARAMETERISED_LOW_VERTICAL_TEMPERATURE.md",
    "protocols/york/qualification/alpha44_heat_low_vertical_temperature_range.json",
    "test_sprint_3116_parameterised_low_vertical_control.py",
    "SPRINT_3_1_16_PARAMETERISED_LOW_VERTICAL_CONTROL.md",
    "test_sprint_3117_half_degree_temperature_control.py",
    "SPRINT_3_1_17_HALF_DEGREE_TEMPERATURE_CONTROL.md",
    "adapters/york/fan_command.py",
    "direct_fan_manager.py",
    "test_sprint_3118_guarded_native_fan_control.py",
    "SPRINT_3_1_18_GUARDED_NATIVE_FAN_CONTROL.md",
    "adapters/york/swing_command.py",
    "direct_swing_manager.py",
    "test_sprint_3119_guarded_native_swing_control.py",
    "SPRINT_3_1_19_GUARDED_NATIVE_SWING_CONTROL.md",
    "SPRINT_3_1_20_HORIZONTAL_SWING_QUALIFICATION.md",
    "protocols/york/qualification/alpha49_horizontal_swing.json",
    "york_horizontal_axis_qualification.py",
    "test_sprint_3121_independent_horizontal_axis_qualification.py",
    "SPRINT_3_1_21_INDEPENDENT_HORIZONTAL_AXIS_QUALIFICATION.md",
    "protocols/york/qualification/alpha50_horizontal_axis.json",
    "york_dry_horizontal_axis_qualification.py",
    "test_sprint_3122_dry_horizontal_axis_qualification.py",
    "SPRINT_3_1_22_DRY_HORIZONTAL_AXIS_QUALIFICATION.md",
    "protocols/york/qualification/alpha51_dry_horizontal_axis.json",
    "test_sprint_3123_native_dry_horizontal_axis_control.py",
    "SPRINT_3_1_23_NATIVE_DRY_HORIZONTAL_AXIS_CONTROL.md",
    "york_heat_horizontal_axis_qualification.py",
    "test_sprint_3124_heat_horizontal_axis_qualification.py",
    "SPRINT_3_1_24_HEAT_HORIZONTAL_AXIS_QUALIFICATION.md",
    "protocols/york/qualification/alpha53_heat_horizontal_axis.json",
    "test_sprint_3125_native_heat_horizontal_axis_control.py",
    "SPRINT_3_1_25_NATIVE_HEAT_HORIZONTAL_AXIS_CONTROL.md",
    "test_sprint_3126_direct_state_authority.py",
    "SPRINT_3_1_26_DIRECT_STATE_AUTHORITY.md",
    "test_sprint_3127_tablet_free_restart_recovery.py",
    "SPRINT_3_1_27_TABLET_FREE_RESTART_RECOVERY.md",
    "test_sprint_3128_poll_failure_counter_correction.py",
    "SPRINT_3_1_28_POLL_FAILURE_COUNTER_CORRECTION.md",
    "test_sprint_3129_relay_free_command_boundary.py",
    "SPRINT_3_1_29_RELAY_FREE_COMMAND_BOUNDARY.md",
    "test_sprint_3130_legacy_relay_runtime_removal.py",
    "SPRINT_3_1_30_LEGACY_RELAY_RUNTIME_REMOVAL.md",
    "adapters/york/power_on_command.py",
    "test_sprint_3131_parameterised_power_on_control.py",
    "SPRINT_3_1_31_PARAMETERISED_POWER_ON_CONTROL.md",
    "adapters/york/power_off_command.py",
    "test_sprint_3132_parameterised_power_off_control.py",
    "SPRINT_3_1_32_PARAMETERISED_POWER_OFF_CONTROL.md",
    "adapters/york/cool_fan_off_qualification.py",
    "test_sprint_3135_grouped_fan_qualification_matrix.py",
    "SPRINT_3_1_35_GROUPED_FAN_QUALIFICATION_MATRIX.md",
    "adapters/york/swing_matrix_qualification.py",
    "test_sprint_3136_grouped_swing_qualification_matrix.py",
    "SPRINT_3_1_36_GROUPED_SWING_QUALIFICATION_MATRIX.md",
    "test_sprint_3137_post_swing_fan_compatibility.py",
    "SPRINT_3_1_37_POST_SWING_FAN_COMPATIBILITY.md",
    "test_sprint_3139_auto_feel_22c_mode_matrix_correction.py",
    "SPRINT_3_1_38_GROUPED_REMAINING_MODES_MATRIX.md",
    "SPRINT_3_1_39_AUTO_FEEL_22C_MODE_MATRIX_CORRECTION.md",
    "test_sprint_3140_auto_feel_dynamic_ambient_mode_matrix.py",
    "SPRINT_3_1_40_AUTO_FEEL_DYNAMIC_AMBIENT_MODE_MATRIX.md",
    "test_sprint_3141_real_client_mode_transport_integration.py",
    "SPRINT_3_1_41_REAL_CLIENT_MODE_TRANSPORT_INTEGRATION.md",
    "test_sprint_3142_dry_dynamic_status_mode_matrix.py",
    "SPRINT_3_1_42_DRY_DYNAMIC_STATUS_MODE_MATRIX_CORRECTION.md",
    "test_sprint_3143_fan_only_containment_delayed_verification.py",
    "SPRINT_3_1_43_FAN_ONLY_CONTAINMENT_DELAYED_VERIFICATION.md",
    "test_sprint_3144_official_sdk_fan_only_qualification.py",
    "SPRINT_3_1_44_OFFICIAL_SDK_FAN_ONLY_QUALIFICATION.md",
    "test_sprint_3145_fan_only_temperature_semantics.py",
    "SPRINT_3_1_45_FAN_ONLY_TEMPERATURE_SEMANTICS.md",
    "test_sprint_3146_dry_and_fan_only_temperature_semantics.py",
    "SPRINT_3_1_46_DRY_AND_FAN_ONLY_TEMPERATURE_SEMANTICS.md",
    "test_sprint_3147_mqtt_non_applicable_setpoint_reset.py",
    "SPRINT_3_1_47_MQTT_NON_APPLICABLE_SETPOINT_RESET.md",
    "test_sprint_3148_official_sdk_fan_only_to_heat_qualification.py",
    "SPRINT_3_1_48_OFFICIAL_SDK_FAN_ONLY_TO_HEAT_QUALIFICATION.md",
    "test_sprint_3149_official_sdk_heat_23_to_auto_feel_qualification.py",
    "SPRINT_3_1_49_OFFICIAL_SDK_HEAT_23_TO_AUTO_FEEL_QUALIFICATION.md",
    "test_sprint_3150_official_sdk_auto_feel_21_to_cool_qualification.py",
    "SPRINT_3_1_50_OFFICIAL_SDK_AUTO_FEEL_21_TO_COOL_QUALIFICATION.md",
    "test_sprint_3151_official_sdk_cool_21_to_dry_qualification.py",
    "SPRINT_3_1_51_OFFICIAL_SDK_COOL_21_TO_DRY_QUALIFICATION.md",
    "adapters/york/official_sdk_mode_transitions.py",
    "test_sprint_3152_qualified_mode_loop_consolidation.py",
    "SPRINT_3_1_52_QUALIFIED_MODE_LOOP_CONSOLIDATION.md",
    "protocols/york/qualification/alpha81_qualified_mode_loop_consolidation.json",
    "test_sprint_3153_auto_feel_program_and_indoor_temperature_correction.py",
    "SPRINT_3_1_53_AUTO_FEEL_PROGRAM_AND_INDOOR_TEMPERATURE_CORRECTION.md",
    "protocols/york/qualification/alpha82_auto_feel_program_and_indoor_temperature.json",
    "adapters/york/cool_fan_auto_temperature_qualification.py",
    "test_sprint_3154_official_sdk_cool_23_to_21_fan_auto.py",
    "SPRINT_3_1_54_OFFICIAL_SDK_COOL_23_TO_21_FAN_AUTO_QUALIFICATION.md",
    "protocols/york/qualification/alpha83_cool_23_to_21_fan_auto.json",
    "test_sprint_3155_auto_feel_20_program_qualification.py",
    "SPRINT_3_1_55_AUTO_FEEL_20_PROGRAM_QUALIFICATION.md",
    "protocols/york/qualification/alpha84_auto_feel_20_program.json",
    "test_sprint_3156_official_sdk_auto_feel_20_to_cool_qualification.py",
    "SPRINT_3_1_56_OFFICIAL_SDK_AUTO_FEEL_20_TO_COOL_QUALIFICATION.md",
    "protocols/york/qualification/alpha85_official_sdk_auto_20_to_cool.json",
    "test_sprint_3157_official_sdk_cool_20_to_20_5_fan_auto.py",
    "SPRINT_3_1_57_OFFICIAL_SDK_COOL_20_TO_20_5_FAN_AUTO_QUALIFICATION.md",
    "protocols/york/qualification/alpha86_official_sdk_cool_20_to_20_5_fan_auto.json",
    "test_sprint_3158_official_sdk_cool_20_5_to_20_fan_auto.py",
    "SPRINT_3_1_58_OFFICIAL_SDK_COOL_20_5_TO_20_FAN_AUTO_QUALIFICATION.md",
    "protocols/york/qualification/alpha87_official_sdk_cool_20_5_to_20_fan_auto.json",
    "test_sprint_3159_official_sdk_cool_20_to_22_fan_auto.py",
    "SPRINT_3_1_59_OFFICIAL_SDK_COOL_20_TO_22_FAN_AUTO_QUALIFICATION.md",
    "protocols/york/qualification/alpha88_official_sdk_cool_20_to_22_fan_auto.json",
    "test_sprint_3160_official_sdk_cool_22_to_20_fan_auto.py",
    "SPRINT_3_1_60_OFFICIAL_SDK_COOL_22_TO_20_FAN_AUTO_QUALIFICATION.md",
    "protocols/york/qualification/alpha89_official_sdk_cool_22_to_20_fan_auto.json",
    "test_sprint_3161_grouped_cool_fan_auto_temperature_matrix.py",
    "SPRINT_3_1_61_GROUPED_OFFICIAL_SDK_COOL_FAN_AUTO_TEMPERATURE_MATRIX.md",
    "protocols/york/qualification/alpha90_grouped_cool_fan_auto_temperature_matrix.json",
    "test_sprint_3162_general_cool_fan_auto_temperature_encoder.py",
    "SPRINT_3_1_62_GENERAL_COOL_FAN_AUTO_TEMPERATURE_ENCODER.md",
    "protocols/york/qualification/alpha91_general_cool_fan_auto_temperature_encoder.json",
    "test_sprint_3163_general_cool_qualified_fan_temperature_encoder.py",
    "SPRINT_3_1_63_GENERAL_COOL_QUALIFIED_FAN_TEMPERATURE_ENCODER.md",
    "protocols/york/qualification/alpha92_general_cool_qualified_fan_temperature_encoder.json",
    "test_sprint_310_guarded_direct_temperature.py",
    "SPRINT_3_1_0_GUARDED_DIRECT_TEMPERATURE_CONTROL.md",
    "york_power_one_shot_qualification.py",
    "test_sprint_313_power_on_heat_qualification.py",
    "SPRINT_3_1_2_CORRECTED_POWER_OFF_QUALIFICATION.md",
    "protocols/york/qualification/alpha31_corrected_power_off.json",
    "SPRINT_3_1_3_POWER_ON_HEAT_QUALIFICATION.md",
    "protocols/york/qualification/alpha32_power_on_heat.json",
    "SPRINT_3_1_4_POWER_ON_COOL_QUALIFICATION.md",
    "protocols/york/qualification/alpha33_power_on_cool.json",
    "york_capture_probe.py",
    "transport/tx_logger.py",
    "york_replay_engine.py",
    "york_request_hunter.py",
    "protocols/york/analysis/__init__.py",
    "protocols/york/analysis/loader.py",
    "protocols/york/analysis/scoring.py",
    "test_sprint_282_phase2_request_hunter.py",
    "test_sprint_282_tx_instrumentation.py",
    "york_capture_importer.py",
    "york_protocol_lab.py",
    "protocols/york/lab_dashboard.py",
    "protocols/york/dashboard/index.html",
    "protocols/york/qualification-reports/README.md",
    "qualification-reports/README.md",
    "protocols/york/capture_importer.py",
    "test_sprint_251_capture_importer.py",
    "protocols/york/README.md",
    "protocols/york/packet_library/template.json",
    "protocols/york/packet_library.py",
    "test_sprint_25_packet_library.py",
    "protocols/york/documentation/observations.md",
    "protocols/york/qualification/decoder_fixtures.json",
    "york_decoder_qualification.py",
    "test_sprint_26_decoder_qualification.py",
]


def main() -> int:
    def reconciled_path(item: str) -> Path:
        # Sprint evidence is intentionally grouped under docs/history in the
        # reconciled repository instead of flattening hundreds of files at root.
        if item.startswith("SPRINT_") and item.endswith(".md"):
            return ROOT / "docs" / "history" / item
        return ROOT / item

    generated = {"protocols/york/dashboard/index.html"}
    missing = [
        item for item in REQUIRED
        if item not in generated and not reconciled_path(item).exists()
    ]
    if missing:
        raise SystemExit("Missing release files: " + ", ".join(missing))

    removed_runtime = [
        "relay_manager.py",
        "transport/relay_transport.py",
        "transport/relay_extraction_logger.py",
        "york_relay_extraction_report.py",
        "adapters/york/remaining_mode_matrix.py",
        "adapters/york/fan_only_qualification.py",
        "adapters/york/fan_only_heat_qualification.py",
        "adapters/york/heat_auto_qualification.py",
        "adapters/york/auto_cool_qualification.py",
        "adapters/york/cool_dry_qualification.py",
    ]
    present_removed = [item for item in removed_runtime if (ROOT / item).exists()]
    if present_removed:
        raise SystemExit(
            "Obsolete runtime files must be absent: "
            + ", ".join(present_removed)
        )

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    match = re.search(r'org\.opencontainers\.image\.version="([^"]+)"', dockerfile)
    if not match or match.group(1) != APP_VERSION:
        raise SystemExit("Dockerfile version does not match version.py")

    version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version_file != APP_VERSION:
        raise SystemExit("VERSION does not match version.py")

    copy_sources = []
    for line in dockerfile.splitlines():
        stripped = line.strip()
        if not stripped.startswith("COPY "):
            continue
        parts = stripped.split()
        for source in parts[1:-1]:
            if source.startswith("--"):
                continue
            copy_sources.append(source)
    missing_copy_sources = [source for source in copy_sources if not (ROOT / source).exists()]
    if missing_copy_sources:
        raise SystemExit("Dockerfile COPY sources missing: " + ", ".join(missing_copy_sources))


    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    if "source: ./qualification-reports" not in compose:
        raise SystemExit("docker-compose.yml must mount ./qualification-reports")
    if not (ROOT / "qualification-reports").is_dir():
        raise SystemExit("Missing root qualification-reports directory")

    print(f"Release verification passed for Climate Bridge {APP_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
