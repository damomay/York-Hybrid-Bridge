import unittest
from pathlib import Path

from configuration import load_config
from transport import RelayTransport, YorkDirectTransport, create_transport


BASE = """
mqtt:
  host: 192.0.2.10
device:
  name: Test AC
  unique_id: test_ac
"""


class TransportFoundationTests(unittest.TestCase):
    def load(self, body: str):
        path = self._testMethodName
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as folder:
            config_path = Path(folder) / f"{path}.yml"
            config_path.write_text(body + BASE, encoding="utf-8")
            return load_config(config_path)

    def test_relay_transport_is_default(self):
        cfg = self.load("relay:\n  base_url: http://192.0.2.20:8765\n")
        self.assertIsInstance(create_transport(cfg), RelayTransport)
        self.assertEqual(cfg.relay_url, cfg.transport_url)

    def test_new_transport_configuration(self):
        cfg = self.load(
            "transport:\n  type: relay\n  base_url: http://192.0.2.20:8765\n"
        )
        self.assertIsInstance(create_transport(cfg), RelayTransport)

    def test_york_direct_scaffold_is_selectable(self):
        cfg = self.load(
            """transport:
  type: york_direct
direct_device:
  enabled: true
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
"""
        )
        transport = create_transport(cfg)
        self.assertIsInstance(transport, YorkDirectTransport)
        with self.assertRaises(NotImplementedError):
            transport.get_state()


if __name__ == "__main__":
    unittest.main()
