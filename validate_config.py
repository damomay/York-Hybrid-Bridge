from pathlib import Path
import sys

from configuration import ConfigError, load_config


def validate(path: Path) -> str:
    """Validate the same configuration model used by the running bridge."""
    config = load_config(path)

    missing: list[str] = []
    if config.transport_type in {"york", "york_direct"}:
        if not config.direct_enabled:
            missing.append("direct_device.enabled")
        if not config.direct_host:
            missing.append("direct_device.host")
        if not config.direct_mac:
            missing.append("direct_device.mac")
        if not config.direct_state_request_hex:
            missing.append("direct_device.state_request_hex")

    if not config.device_name:
        missing.append("device.name")
    if not config.unique_id:
        missing.append("device.unique_id")
    if missing:
        raise ConfigError("Missing required settings: " + ", ".join(missing))

    return config.transport_type


def main(path: Path = Path("/config/config.yml")) -> int:
    try:
        transport_type = validate(path)
    except ConfigError as exc:
        print(f"Invalid configuration: {exc}", file=sys.stderr)
        return 2

    print(f"Configuration looks valid (transport: {transport_type}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
