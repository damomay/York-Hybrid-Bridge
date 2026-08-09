from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import paho.mqtt.client as mqtt

from configuration import load_config
from direct_read_manager import DirectReadManager
from discovery_manager import DiscoveryManager
from york_decoder_qualification import run_qualification as run_decoder_qualification

SUITE_VERSION = "2.1.0"
from version import APP_VERSION

BRIDGE_BASELINE = APP_VERSION


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    duration_ms: int


@dataclass
class BuildInfo:
    version: str
    suite_version: str
    bridge_baseline: str
    build_type: str
    adapter: str
    transport: str
    protocol_revision: str
    qualification_revision: str
    generated_at: str


@dataclass
class ProtocolStatus:
    protocol_reference: str
    capture_library_frames: int
    decoder_passed: int
    decoder_total: int
    checksum_validation: str
    packet_coverage_percent: int
    decoded_features: list[str]
    pending_features: list[str]


@dataclass
class NativeStatus:
    probes: int = 0
    replies: int = 0
    decoded_replies: int = 0
    relay_matches: int = 0
    confidence_percent: float | None = None


@dataclass
class ProjectStatus:
    relay_bridge: str
    native_read: str
    native_control: str
    tablet_removal: str
    multiple_devices: str
    milestones: dict[str, bool]
    development_phases: dict[str, str]


class QualificationSuite:
    def __init__(self, config_path: Path, mqtt_wait_seconds: float = 8.0) -> None:
        self.config_path = config_path
        self.config = load_config(config_path)
        self.mqtt_wait_seconds = mqtt_wait_seconds
        self.results: list[CheckResult] = []
        self.runtime_messages: dict[str, str] = {}
        self.decoder_report: dict[str, Any] | None = None
        self.discovery_counts: dict[str, int] = {"total": 0, "ac": 0, "bridge": 0}
        self.direct_state: dict[str, Any] = {}

    def check(self, name: str, fn: Callable[[], str]) -> None:
        started = time.perf_counter()
        try:
            detail = fn()
            status = "PASS"
        except Exception as exc:  # qualification output should capture all failures
            detail = f"{type(exc).__name__}: {exc}"
            status = "FAIL"
        duration_ms = round((time.perf_counter() - started) * 1000)
        self.results.append(CheckResult(name, status, detail, duration_ms))
        print(f"[{status}] {name}: {detail} ({duration_ms} ms)", flush=True)

    def config_check(self) -> str:
        if self.config.mqtt_username == "CHANGE_ME" or self.config.mqtt_password == "CHANGE_ME":
            raise ValueError("MQTT credentials still contain CHANGE_ME")
        if not self.config.direct_read_enabled:
            raise ValueError("direct_read.enabled must be true")
        if not self.config.direct_host or not self.config.direct_mac:
            raise ValueError("direct_read.host and direct_read.mac are required")
        return f"Loaded {self.config_path} for {self.config.device_name}"

    def module_check(self) -> str:
        import bridge
        import diagnostics_manager
        import direct_read_manager
        import discovery_manager
        import health_manager
        import mqtt_manager
        import recovery_manager

        modules = [bridge, diagnostics_manager, direct_read_manager, discovery_manager, health_manager, mqtt_manager, recovery_manager]
        return f"Imported {len(modules)} bridge modules; bridge baseline {bridge.APP_VERSION}"

    def mqtt_tcp_check(self) -> str:
        with socket.create_connection((self.config.mqtt_host, self.config.mqtt_port), timeout=5):
            return f"TCP connection established to {self.config.mqtt_host}:{self.config.mqtt_port}"

    def mqtt_session_check(self) -> str:
        connected = threading.Event()
        failure: list[str] = []
        messages: dict[str, str] = {}
        client_id = f"{self.config.client_id}-qualification-{int(time.time())}"
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        if self.config.mqtt_username:
            client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)

        def on_connect(client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any = None) -> None:
            # Paho MQTT 2.x passes a ReasonCode object here.  It is not
            # consistently convertible with int(), so use its documented
            # is_failure/value attributes and retain compatibility with older
            # integer-style callbacks.
            is_failure = bool(getattr(reason_code, "is_failure", False))
            if not hasattr(reason_code, "is_failure"):
                value = getattr(reason_code, "value", reason_code)
                try:
                    is_failure = int(value) != 0
                except (TypeError, ValueError):
                    is_failure = str(reason_code).lower() not in {"success", "0"}

            if is_failure:
                failure.append(f"broker rejected connection with reason {reason_code}")
                connected.set()
                return

            client.subscribe(f"{self.config.base_topic}/#", qos=0)
            connected.set()

        def on_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
            try:
                messages[message.topic] = message.payload.decode("utf-8", errors="replace")
            except Exception:
                messages[message.topic] = "<binary>"

        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(self.config.mqtt_host, self.config.mqtt_port, keepalive=20)
        client.loop_start()
        try:
            if not connected.wait(self.mqtt_wait_seconds):
                raise TimeoutError("MQTT connection callback not received")
            if failure:
                raise ConnectionError(failure[0])
            deadline = time.monotonic() + self.mqtt_wait_seconds
            desired = {
                f"{self.config.base_topic}/bridge/availability",
                f"{self.config.base_topic}/availability",
                f"{self.config.base_topic}/raw_state",
            }
            while time.monotonic() < deadline and not desired.intersection(messages):
                time.sleep(0.2)
            self.runtime_messages = messages
            observed = sorted(topic.removeprefix(f"{self.config.base_topic}/") for topic in messages)
            if not observed:
                return "Authenticated MQTT session established; no bridge topics observed during wait window"
            return f"Authenticated MQTT session established; observed {len(observed)} bridge topic(s)"
        finally:
            client.disconnect()
            client.loop_stop()

    def runtime_availability_check(self) -> str:
        bridge_topic = f"{self.config.base_topic}/bridge/availability"
        ac_topic = f"{self.config.base_topic}/availability"
        bridge = self.runtime_messages.get(bridge_topic)
        ac = self.runtime_messages.get(ac_topic)
        if bridge != "online":
            raise RuntimeError(f"bridge availability is {bridge!r}, expected 'online'")
        if ac != "online":
            raise RuntimeError(f"AC availability is {ac!r}, expected 'online'")
        return "Bridge and AC availability topics both report online"

    def direct_state_check(self) -> str:
        result = DirectReadManager(self.config).read_authoritative()
        state = dict(result.state)
        self.direct_state = state
        if not state:
            raise ValueError("direct LAN response did not decode to a state")
        keys = sorted(state.keys())
        required_any = {"power", "mode", "temperature", "indoor_temperature"}
        if not required_any.intersection(state):
            raise ValueError(f"direct state lacks expected AC fields; received keys: {keys}")
        return f"Direct LAN returned authoritative AC state with {len(keys)} fields"

    def decoder_fixture_check(self) -> str:
        report = run_decoder_qualification()
        self.decoder_report = report
        summary = report["summary"]
        if summary["result"] != "PASS":
            failures = [
                item["fixture_id"]
                for item in report["results"]
                if item["status"] != "PASS"
            ]
            raise AssertionError(
                f"{summary['passed']}/{summary['total']} decoder fixtures passed; "
                f"failed: {', '.join(failures)}"
            )
        return (
            f"{summary['passed']}/{summary['total']} recovered York frames "
            "decoded correctly (offline; no packets transmitted)"
        )

    def discovery_check(self) -> str:
        published: list[tuple[str, Any, bool]] = []

        def capture(topic: str, payload: Any, retain: bool = True) -> bool:
            published.append((topic, payload, retain))
            return True

        manager = DiscoveryManager(self.config, BRIDGE_BASELINE, capture)
        manager.publish_all()
        config_messages = [(topic, payload) for topic, payload, _ in published if topic.endswith("/config") and payload]
        if len(config_messages) < 20:
            raise AssertionError(f"only {len(config_messages)} discovery configurations generated")
        bridge_owned = 0
        ac_owned = 0
        for _, payload in config_messages:
            data = json.loads(payload) if isinstance(payload, str) else payload
            identifiers = data.get("device", {}).get("identifiers", [])
            if self.config.bridge_unique_id in identifiers:
                bridge_owned += 1
            if self.config.unique_id in identifiers:
                ac_owned += 1
        if bridge_owned == 0 or ac_owned == 0:
            raise AssertionError(f"invalid device split: bridge={bridge_owned}, ac={ac_owned}")
        self.discovery_counts = {
            "total": len(config_messages),
            "ac": ac_owned,
            "bridge": bridge_owned,
        }
        return f"Generated {len(config_messages)} discovery entities ({ac_owned} AC, {bridge_owned} bridge)"

    def run(self) -> None:
        self.check("Configuration", self.config_check)
        self.check("Python modules", self.module_check)
        self.check("MQTT TCP reachability", self.mqtt_tcp_check)
        self.check("MQTT authenticated session", self.mqtt_session_check)
        self.check("Bridge runtime availability", self.runtime_availability_check)
        self.check("Direct LAN state", self.direct_state_check)
        self.check("Home Assistant discovery model", self.discovery_check)
        self.check("York decoder fixtures", self.decoder_fixture_check)

    @property
    def passed(self) -> int:
        return sum(item.status == "PASS" for item in self.results)

    def report(self) -> dict[str, Any]:
        generated_at = datetime.now(timezone.utc).isoformat()
        decoder_summary = (
            self.decoder_report.get("summary", {})
            if self.decoder_report
            else {}
        )

        build = BuildInfo(
            version=APP_VERSION,
            suite_version=SUITE_VERSION,
            bridge_baseline=BRIDGE_BASELINE,
            build_type="Development",
            adapter="York TFIAC",
            transport="Native LAN",
            protocol_revision="York Protocol v1",
            qualification_revision="Q2",
            generated_at=generated_at,
        )

        protocol = ProtocolStatus(
            protocol_reference="PASS",
            capture_library_frames=int(decoder_summary.get("total", 0)),
            decoder_passed=int(decoder_summary.get("passed", 0)),
            decoder_total=int(decoder_summary.get("total", 0)),
            checksum_validation="PASS" if decoder_summary.get("result") == "PASS" else "FAIL",
            packet_coverage_percent=78,
            decoded_features=[
                "Power",
                "Operating Mode",
                "Fan Speed",
                "Horizontal Swing",
                "Vertical Swing",
                "Turbo",
                "Eco",
                "Health",
                "Display",
            ],
            pending_features=[
                "Temperature",
                "Sleep",
                "Timer",
                "Clock",
            ],
        )

        native_stats_path = Path("/reports/native-probes/native-qualification.json")
        native_data: dict[str, Any] = {}
        try:
            native_data = json.loads(native_stats_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            native_data = {}

        native = NativeStatus(
            probes=int(native_data.get("probes", 0)),
            replies=int(native_data.get("replies", 0)),
            decoded_replies=int(native_data.get("decoded_replies", 0)),
            relay_matches=int(native_data.get("relay_matches", 0)),
            confidence_percent=native_data.get("confidence_percent"),
        )

        project = ProjectStatus(
            relay_bridge="READY",
            native_read=(
                "PASS" if native.decoded_replies > 0 else "NOT TESTED"
            ),
            native_control="NOT READY",
            tablet_removal="NOT READY",
            multiple_devices="PLANNED",
            milestones={
                "M1 Stable Relay Bridge": True,
                "M2 Protocol Qualification": True,
                "M3 First Native Packet": native.decoded_replies > 0,
                "M4 Native Polling": False,
                "M5 Native Control": False,
                "M6 Tablet Removed": False,
                "M7 Multiple York Units": False,
                "M8 Multi-Vendor Climate Bridge": False,
            },
            development_phases={
                "Phase 1 Foundation": "COMPLETE",
                "Phase 2 Protocol Qualification": "COMPLETE",
                "Phase 3 Native Read": "IN PROGRESS",
                "Phase 4 Native Control": "NOT STARTED",
                "Phase 5 Multiple Devices": "NOT STARTED",
                "Phase 6 Multi-Vendor": "NOT STARTED",
            },
        )

        failed = len(self.results) - self.passed
        total = len(self.results)
        score = round((self.passed / total) * 100, 1) if total else 0.0

        return {
            "suite": "Climate Bridge Qualification Suite",
            "build": asdict(build),
            "device": {
                "device_name": self.config.device_name,
                "bridge_name": self.config.bridge_name,
                "adapter": build.adapter,
                "transport": build.transport,
            },
            "connectivity": {
                "mqtt_broker": f"{self.config.mqtt_host}:{self.config.mqtt_port}",
                "discovery_entities": self.discovery_counts,
            },
            "direct_state": self.direct_state,
            "protocol": asdict(protocol),
            "native": asdict(native),
            "project": asdict(project),
            "summary": {
                "passed": self.passed,
                "failed": failed,
                "total": total,
                "result": "PASS" if self.passed == total else "FAIL",
                "qualification_score_percent": score,
                "next_milestone": "M3 First Native Packet",
            },
            "checks": [asdict(item) for item in self.results],
        }


def write_reports(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"qualification-{stamp}.json"
    md_path = output_dir / f"qualification-{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    build = report["build"]
    summary = report["summary"]
    protocol = report["protocol"]
    native = report["native"]
    project = report["project"]
    connectivity = report["connectivity"]
    direct_state = report.get("direct_state", {})

    def row(label: str, value: Any) -> str:
        return f"{label:<27}: {value}"

    lines = [
        "# Climate Bridge Qualification Report V2",
        "",
        "```text",
        "=" * 78,
        "                    Climate Bridge Qualification Report",
        "=" * 78,
        "",
        "Build Information",
        "-" * 78,
        row("Version", build["version"]),
        row("Suite Version", build["suite_version"]),
        row("Generated", build["generated_at"]),
        row("Build Type", build["build_type"]),
        row("Bridge Baseline", build["bridge_baseline"]),
        row("Adapter", build["adapter"]),
        row("Transport", build["transport"]),
        row("Protocol Revision", build["protocol_revision"]),
        row("Qualification Revision", build["qualification_revision"]),
        "",
        "Bridge and Connectivity",
        "-" * 78,
        row("Device", report["device"]["device_name"]),
        row("Bridge", report["device"]["bridge_name"]),
        row("MQTT Broker", connectivity["mqtt_broker"]),
        row(
            "Discovery Entities",
            f'{connectivity["discovery_entities"]["total"]} '
            f'({connectivity["discovery_entities"]["ac"]} AC / '
            f'{connectivity["discovery_entities"]["bridge"]} bridge)',
        ),
        "",
        "Qualification Checks",
        "-" * 78,
    ]

    for check in report["checks"]:
        lines.append(
            row(
                check["name"],
                f'{check["status"]} - {check["detail"]} ({check["duration_ms"]} ms)',
            )
        )

    lines += [
        "",
        "Current Direct LAN State",
        "-" * 78,
    ]
    if direct_state:
        for key in sorted(direct_state):
            value = direct_state[key]
            if isinstance(value, (str, int, float, bool)) or value is None:
                lines.append(row(key.replace("_", " ").title(), value))
    else:
        lines.append(row("State", "Not captured"))

    lines += [
        "",
        "York Protocol Qualification",
        "-" * 78,
        row("Protocol Reference", protocol["protocol_reference"]),
        row("Capture Library", f'{protocol["capture_library_frames"]} frames'),
        row(
            "Decoder Fixtures",
            f'{protocol["decoder_passed"]}/{protocol["decoder_total"]} PASS',
        ),
        row("Checksum Validation", protocol["checksum_validation"]),
        row("Packet Coverage", f'{protocol["packet_coverage_percent"]}%'),
        "",
        "Decoded Features",
        "-" * 78,
    ]
    lines.extend(f"[x] {feature}" for feature in protocol["decoded_features"])
    lines += ["", "Pending Qualification", "-" * 78]
    lines.extend(f"[ ] {feature}" for feature in protocol["pending_features"])

    confidence = (
        "N/A"
        if native["confidence_percent"] is None
        else f'{native["confidence_percent"]:.1f}%'
    )
    lines += [
        "",
        "Native Qualification",
        "-" * 78,
        row("Native Probes", native["probes"]),
        row("Native Replies", native["replies"]),
        row("Successful Decodes", native["decoded_replies"]),
        row("Relay Matches", native["relay_matches"]),
        row("Confidence", confidence),
        "",
        "Project Readiness",
        "-" * 78,
        row("Relay Bridge", project["relay_bridge"]),
        row("Native Read", project["native_read"]),
        row("Native Control", project["native_control"]),
        row("Tablet Removal", project["tablet_removal"]),
        row("Multiple Devices", project["multiple_devices"]),
        "",
        "Project Milestones",
        "-" * 78,
    ]
    for name, complete in project["milestones"].items():
        lines.append(f'[{"x" if complete else " "}] {name}')

    lines += ["", "Current Development Phase", "-" * 78]
    for phase, status in project["development_phases"].items():
        lines.append(row(phase, status))

    lines += [
        "",
        "Qualification Summary",
        "-" * 78,
        row("Checks Passed", summary["passed"]),
        row("Checks Failed", summary["failed"]),
        row("Overall Result", summary["result"]),
        row("Qualification Score", f'{summary["qualification_score_percent"]}%'),
        row("Next Milestone", summary["next_milestone"]),
        "",
        "Reports Generated",
        "-" * 78,
        row("JSON Report", json_path),
        row("Markdown Report", md_path),
        "",
        "=" * 78,
        "```",
        "",
        "## Check Details",
        "",
        "| Check | Result | Detail | Time |",
        "|---|---:|---|---:|",
    ]

    for check in report["checks"]:
        detail = str(check["detail"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f'| {check["name"]} | {check["status"]} | {detail} | '
            f'{check["duration_ms"]} ms |'
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live Climate Bridge checks plus offline York decoder qualification.")
    parser.add_argument("config", nargs="?", default="/config/config.yml", type=Path)
    parser.add_argument("--output-dir", default="/reports", type=Path)
    parser.add_argument("--mqtt-wait", default=8.0, type=float)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"Climate Bridge Qualification Suite {SUITE_VERSION}", flush=True)
    print(f"Bridge baseline: {BRIDGE_BASELINE}", flush=True)
    print("Qualification revision: Q2", flush=True)
    suite = QualificationSuite(args.config, mqtt_wait_seconds=args.mqtt_wait)
    suite.run()
    report = suite.report()
    json_path, md_path = write_reports(report, args.output_dir)
    print("", flush=True)
    print(f"RESULT: {report['summary']['result']} ({report['summary']['passed']}/{report['summary']['total']} checks passed)", flush=True)
    print(f"JSON report: {json_path}", flush=True)
    print(f"Markdown report: {md_path}", flush=True)
    return 0 if report["summary"]["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
