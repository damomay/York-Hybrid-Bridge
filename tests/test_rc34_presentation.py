import unittest
from diagnostics_manager import DiagnosticsManager, format_duration


class Rc34PresentationTests(unittest.TestCase):
    def manager(self):
        return DiagnosticsManager("test/diagnostic", "3.0.0-rc.3.4", lambda *_: True)

    def test_friendly_duration(self):
        self.assertEqual(format_duration(0), "0s")
        self.assertEqual(format_duration(3723), "1h 2m 3s")

    def test_healthy_summary_is_compact(self):
        manager = self.manager()
        manager.health_status = "excellent"
        manager.health_score = 100
        manager.mqtt_status = "connected"
        manager.bridge_status = "ready"
        manager.last_poll_time_ms = 450
        manager.update_narrative()
        self.assertEqual(manager.bridge_summary, "Healthy • MQTT ✓ • Relay ✓ • 450 ms")
        self.assertIn("operating normally", manager.health_advisor.lower())

    def test_recovery_age_starts_never(self):
        manager = self.manager()
        manager.update_narrative()
        self.assertEqual(manager.last_recovery_age, "Never")


if __name__ == "__main__":
    unittest.main()
