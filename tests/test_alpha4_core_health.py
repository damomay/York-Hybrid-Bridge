import unittest
from pathlib import Path

from transport.relay_transport import RelayTransport
from version import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]


class Alpha4CoreHealthTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(APP_VERSION, "1.0.0-alpha.20")

    def test_relay_has_friendly_display_name(self):
        self.assertEqual(RelayTransport.display_name, "Relay (Legacy)")

    def test_bridge_banner_uses_display_name(self):
        source = (ROOT / "bridge.py").read_text(encoding="utf-8")
        self.assertIn("self.transport.display_name", source)

    def test_healthcheck_combines_local_liveness_with_relay_validation(self):
        source = (ROOT / "healthcheck.py").read_text(encoding="utf-8")
        self.assertIn("/proc/1/cmdline", source)
        self.assertIn("climate_bridge.heartbeat", source)
        self.assertIn("def _check_relay", source)
        self.assertIn('f"{base_url}/health"', source)

    def test_docker_copies_healthcheck(self):
        source = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("healthcheck.py", source)


if __name__ == "__main__":
    unittest.main()
