import unittest

from diagnostics_manager import DiagnosticsManager


class Rc35PolishTests(unittest.TestCase):
    def manager(self):
        return DiagnosticsManager(
            diagnostic_base="test/diagnostic",
            app_version="3.0.0-rc.3.5",
            publish_fn=lambda topic, value, retain=True: True,
        )

    def test_event_classification(self):
        manager = self.manager()
        manager.record_event("recovery", "Relay restored")
        self.assertEqual(manager.event_level, "RECOVERY")
        self.assertEqual(manager.event_message, "Relay restored")
        self.assertEqual(manager.last_event, "RECOVERY • Relay restored")

    def test_advisor_mentions_recovery(self):
        manager = self.manager()
        manager.bridge_status = "ready"
        manager.mqtt_status = "connected"
        manager.health_status = "excellent"
        manager.recovery_count = 1
        manager.last_recovery = "never"
        manager.update_narrative()
        self.assertIn("Last recovery", manager.health_advisor)

    def test_information_fields(self):
        manager = self.manager()
        self.assertEqual(manager.protocol_name, "TFIAC 20014")
        self.assertEqual(manager.discovery_status, "connected")


if __name__ == "__main__":
    unittest.main()
