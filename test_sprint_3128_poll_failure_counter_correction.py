from __future__ import annotations

import logging

from test_sprint_3127_tablet_free_restart_recovery import make_bridge


def test_long_outage_never_displays_a_counter_above_threshold(caplog):
    climate, _reader, _relay = make_bridge()

    with caplog.at_level(logging.WARNING, logger="climate_bridge"):
        for _ in range(19):
            climate._handle_poll_failure(TimeoutError("York module unavailable"))

    poll_lines = [
        record.getMessage()
        for record in caplog.records
        if "Transport poll failed" in record.getMessage()
    ]
    assert poll_lines[0].startswith("Transport poll failed (1/3)")
    assert poll_lines[1].startswith("Transport poll failed (2/3)")
    assert all("/3)" in line for line in poll_lines)
    assert all(f"({count}/3)" not in " ".join(poll_lines) for count in range(4, 20))
    assert climate.consecutive_poll_failures == 19


def test_retry_diagnostics_are_capped_during_a_long_outage():
    climate, _reader, _relay = make_bridge()

    for _ in range(19):
        climate._handle_poll_failure(TimeoutError("York module unavailable"))

    transport_values = [
        call.args[1]
        for call in climate.mqtt.publish.call_args_list
        if call.args and call.args[0].endswith("/transport_status")
    ]
    state_source_values = [
        call.args[1]
        for call in climate.mqtt.publish.call_args_list
        if call.args and call.args[0].endswith("/state_source_status")
    ]
    assert "retrying (1)" in transport_values
    assert "retrying (2)" in transport_values
    assert "retrying (3)" in transport_values
    allowed = {"retrying (1)", "retrying (2)", "retrying (3)", "unavailable"}
    assert set(transport_values) <= allowed
    assert set(state_source_values) <= allowed


def test_successful_direct_read_resets_the_next_displayed_failure(caplog):
    climate, _reader, _relay = make_bridge()

    for _ in range(8):
        climate._handle_poll_failure(TimeoutError("first outage"))
    climate.poll_once()

    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="climate_bridge"):
        climate._handle_poll_failure(TimeoutError("second outage"))

    assert climate.consecutive_poll_failures == 1
    assert "Transport poll failed (1/3): second outage" in caplog.text


def test_counter_correction_does_not_change_unavailable_threshold():
    climate, _reader, _relay = make_bridge()

    climate._handle_poll_failure(TimeoutError("one"))
    climate._handle_poll_failure(TimeoutError("two"))
    assert climate.authoritative_state_confirmed is False
    assert climate.recovery.failure_count == 0

    climate._handle_poll_failure(TimeoutError("three"))
    assert climate.recovery.failure_count == 1
    climate.mqtt.publish.assert_any_call(
        f"{climate.config.base_topic}/availability", "offline", retain=True
    )
