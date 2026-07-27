import unittest
from pathlib import Path

from version import APP_NAME, APP_VERSION, PROTOCOL_NAME, TRANSPORT_NAME


ROOT = Path(__file__).resolve().parents[1]


class ReleaseHardeningTests(unittest.TestCase):
    def test_release_metadata(self) -> None:
        self.assertEqual(APP_NAME, "Climate Bridge")
        self.assertEqual(APP_VERSION, "1.0.0-alpha.20")
        self.assertEqual(PROTOCOL_NAME, "TFIAC 20014")
        self.assertEqual(TRANSPORT_NAME, "selectable")

    def test_bridge_uses_central_version(self) -> None:
        source = (ROOT / "bridge.py").read_text(encoding="utf-8")
        self.assertIn(
            "from version import ADAPTER_NAME, APP_NAME, APP_VERSION",
            source,
        )
        self.assertNotIn("APP_VERSION =", source)


if __name__ == "__main__":
    unittest.main()
