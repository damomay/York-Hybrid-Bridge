import unittest
from health_manager import HealthManager


class HealthManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = HealthManager()

    def test_healthy_system_is_excellent(self):
        result = self.manager.evaluate(
            mqtt_connected=True,
            consecutive_poll_failures=0,
            relay_offline_after_failures=3,
            average_command_time_ms=1800,
            bridge_status="ready",
        )
        self.assertEqual(result.score, 100)
        self.assertEqual(result.status, "excellent")

    def test_mqtt_disconnect_is_critical(self):
        result = self.manager.evaluate(
            mqtt_connected=False,
            consecutive_poll_failures=0,
            relay_offline_after_failures=3,
            average_command_time_ms=0,
            bridge_status="recovering",
        )
        self.assertEqual(result.status, "critical")
        self.assertIn("MQTT", result.reason)

    def test_single_poll_failure_is_temporary_warning(self):
        result = self.manager.evaluate(
            mqtt_connected=True,
            consecutive_poll_failures=1,
            relay_offline_after_failures=3,
            average_command_time_ms=0,
            bridge_status="recovering",
        )
        self.assertEqual(result.score, 85)
        self.assertEqual(result.status, "good")
