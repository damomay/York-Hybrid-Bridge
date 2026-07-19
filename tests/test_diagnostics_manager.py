import unittest
from diagnostics_manager import DiagnosticsManager


class StabilityTests(unittest.TestCase):
    def manager(self, size=100):
        return DiagnosticsManager("test/diagnostic", "test", lambda *_: True, stability_window_size=size)

    def test_stability_starts_at_100(self):
        manager = self.manager()
        self.assertEqual(manager.stability_score, 100.0)
        self.assertEqual(manager.stability_status, "excellent")

    def test_failure_reduces_stability(self):
        manager = self.manager(size=10)
        manager.record_stability_event(True)
        manager.record_stability_event(False)
        self.assertEqual(manager.stability_score, 50.0)
        self.assertEqual(manager.stability_status, "poor")

    def test_old_failure_ages_out_of_rolling_window(self):
        manager = self.manager(size=10)
        manager.record_stability_event(False)
        for _ in range(10):
            manager.record_stability_event(True)
        self.assertEqual(manager.stability_score, 100.0)
        self.assertEqual(manager.stability_status, "excellent")
