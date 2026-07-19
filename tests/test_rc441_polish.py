import json
import unittest
from pathlib import Path
from configuration import load_config
from discovery_manager import DiscoveryManager


class Rc441PolishTests(unittest.TestCase):
    def test_last_state_timestamp_migrates_to_disabled_diagnostic(self):
        cfg = load_config(Path("config.example.yml"))
        published = []
        manager = DiscoveryManager(cfg, "3.0.0-rc.4.4.1", lambda t, p, r=True: published.append((t, p, r)) or True)
        manager.publish_all(force=True)

        old_topic = f"{cfg.discovery_prefix}/sensor/{cfg.unique_id}_last_state_update/config"
        self.assertIn((old_topic, "", True), published)

        new_topic = f"{cfg.discovery_prefix}/sensor/{cfg.unique_id}_last_state_change_timestamp/config"
        payload_text = next(p for t, p, _ in published if t == new_topic and p)
        payload = json.loads(payload_text)
        self.assertFalse(payload["enabled_by_default"])
        self.assertEqual(payload["entity_category"], "diagnostic")
        self.assertEqual(payload["device_class"], "timestamp")

    def test_meaningful_activity_entities_remain_enabled(self):
        cfg = load_config(Path("config.example.yml"))
        published = []
        manager = DiscoveryManager(cfg, "3.0.0-rc.4.4.1", lambda t, p, r=True: published.append((t, p, r)) or True)
        manager.publish_all(force=True)
        topic = f"{cfg.discovery_prefix}/sensor/{cfg.unique_id}_activity_last_event/config"
        payload = json.loads(next(p for t, p, _ in published if t == topic))
        self.assertNotEqual(payload.get("enabled_by_default"), False)


if __name__ == "__main__":
    unittest.main()
