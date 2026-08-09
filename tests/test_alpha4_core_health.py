import unittest
from pathlib import Path

from transport.native_command_boundary import NativeCommandBoundaryTransport
from version import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]


class CoreHealthTests(unittest.TestCase):
    def test_stable_release_version(self):
        self.assertEqual(APP_VERSION, "1.0.0")

    def test_native_transport_has_operator_friendly_name(self):
        self.assertTrue(NativeCommandBoundaryTransport.display_name)

    def test_bridge_banner_uses_transport_display_name(self):
        source = (ROOT / "bridge.py").read_text(encoding="utf-8")
        self.assertIn("self.transport.display_name", source)

    def test_healthcheck_uses_local_liveness(self):
        source = (ROOT / "healthcheck.py").read_text(encoding="utf-8")
        self.assertIn("/proc/1/cmdline", source)
        self.assertIn("climate_bridge.heartbeat", source)
        self.assertNotIn("_check_relay", source)

    def test_docker_copies_healthcheck(self):
        source = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("healthcheck.py", source)


if __name__ == "__main__":
    unittest.main()
