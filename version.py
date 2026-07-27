"""Canonical Climate Bridge product and version information."""

from pathlib import Path


APP_NAME = "Climate Bridge"
APP_VERSION = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
PROTOCOL_NAME = "TFIAC 20014"
ADAPTER_NAME = "York TFIAC"

# Compatibility alias retained for existing callers.
__version__ = APP_VERSION
