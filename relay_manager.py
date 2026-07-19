from __future__ import annotations

from typing import Any

import requests

from configuration import Config


class RelayManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = requests.Session()

    def get_state(self) -> dict[str, Any]:
        response = self.session.get(
            f"{self.config.relay_url}/state",
            timeout=self.config.relay_timeout,
        )
        response.raise_for_status()
        return response.json()

    def command(self, **changes: Any) -> dict[str, Any]:
        response = self.session.post(
            f"{self.config.relay_url}/command",
            json=changes,
            timeout=self.config.relay_timeout,
        )
        response.raise_for_status()
        return response.json()
