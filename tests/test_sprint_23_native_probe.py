import unittest

from adapters.york.encoder import YorkPacketEncoder
from adapters.york.errors import YorkFrameError, YorkProtocolNotReady
from release_verifier import main as verify_release
from version import APP_VERSION


class Sprint23Tests(unittest.TestCase):
    def test_release_version(self):
        self.assertEqual(APP_VERSION, "1.0.0")

    def test_captured_request_hex_is_parsed(self):
        self.assertEqual(
            YorkPacketEncoder.parse_captured_hex("BB 01:02-03"),
            bytes.fromhex("BB010203"),
        )

    def test_empty_request_is_refused(self):
        with self.assertRaises(YorkProtocolNotReady):
            YorkPacketEncoder.parse_captured_hex("")

    def test_non_bb_request_is_refused(self):
        with self.assertRaises(YorkFrameError):
            YorkPacketEncoder.parse_captured_hex("AA 01 02 03")

    def test_release_package_verifies(self):
        self.assertEqual(verify_release(), 0)


if __name__ == "__main__":
    unittest.main()
