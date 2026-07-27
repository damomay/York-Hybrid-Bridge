"""Generate a self-contained York Protocol Lab dashboard from imported evidence."""
from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

FEATURE_ALIASES = {
    "power": ("power",),
    "mode": ("mode", "cool", "heat", "dehumid", "dry", "fan mode", "feel"),
    "temperature": ("temp", "temperature"),
    "fan": ("fan low", "fan med", "fan high", "fanlow", "fanhigh"),
    "swing_lr": ("swing left right", "swing lr", "left right"),
    "swing_ud": ("swing up down", "swing updown", "up down", "updown"),
    "turbo": ("turbo",),
    "eco": ("eco",),
    "health": ("health",),
    "sleep": ("sleep",),
    "display": ("display",),
    "timer": ("timer",),
}


def _load_json_files(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return records
    for item in sorted(path.rglob("*.json")):
        try:
            value = json.loads(item.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def _feature_for_mark(mark: str) -> str:
    lowered = mark.lower().strip()
    for feature, aliases in FEATURE_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            return feature
    return "other"


def build_lab_model(protocol_root: Path) -> dict:
    observed = _load_json_files(protocol_root / "packet_library" / "observed")
    verified = _load_json_files(protocol_root / "packet_library" / "verified")
    import_reports = _load_json_files(protocol_root / "reports")
    timelines = _load_json_files(protocol_root / "timelines")

    marks: list[str] = []
    total_occurrences = 0
    direction_counts: Counter[str] = Counter()
    length_counts: Counter[int] = Counter()
    status_counts: Counter[str] = Counter()
    for record in observed + verified:
        verification = record.get("verification", {})
        status_counts[str(verification.get("status", "unknown"))] += 1
        direction_counts[str(record.get("direction", "unknown"))] += 1
        length_counts[int(record.get("frame_length", 0) or 0)] += 1
        observations = record.get("observations", {})
        total_occurrences += int(observations.get("occurrence_count", 0) or 0)
        marks.extend(str(mark) for mark in observations.get("marks", []) if mark)

    feature_marks: dict[str, list[str]] = defaultdict(list)
    for mark in sorted(set(marks)):
        feature_marks[_feature_for_mark(mark)].append(mark)

    source_files: set[str] = set()
    quarantined = 0
    for report in import_reports:
        source_files.update(Path(item).name for item in report.get("source_files", []))
        quarantined += int(report.get("quarantined_candidate_count", 0) or 0)

    recent_events: list[dict] = []
    for timeline in timelines:
        if isinstance(timeline, list):
            recent_events.extend(item for item in timeline if isinstance(item, dict))
    recent_events = recent_events[-30:]

    feature_status = {}
    for feature in FEATURE_ALIASES:
        evidence = feature_marks.get(feature, [])
        feature_status[feature] = {
            "status": "observed" if evidence else "not_observed",
            "evidence": evidence,
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_capture_count": len(source_files),
        "source_files": sorted(source_files),
        "unique_observed_packets": len(observed),
        "verified_packets": len(verified),
        "total_occurrences": total_occurrences,
        "quarantined_candidates": quarantined,
        "directions": dict(direction_counts),
        "frame_lengths": {str(key): value for key, value in sorted(length_counts.items())},
        "verification_status": dict(status_counts),
        "feature_status": feature_status,
        "marks": sorted(set(marks)),
        "recent_events": recent_events,
    }


def _card(label: str, value: object) -> str:
    return f'<div class="card"><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></div>'


def render_dashboard(model: dict) -> str:
    feature_rows = []
    pretty = {
        "power": "Power", "mode": "Operating modes", "temperature": "Temperature",
        "fan": "Fan speeds", "swing_lr": "Swing left/right", "swing_ud": "Swing up/down",
        "turbo": "Turbo", "eco": "Eco", "health": "Health", "sleep": "Sleep",
        "display": "Display", "timer": "Timer",
    }
    for key, details in model["feature_status"].items():
        observed = details["status"] == "observed"
        evidence = ", ".join(details["evidence"]) or "No marked capture imported"
        feature_rows.append(
            f'<tr><td>{html.escape(pretty[key])}</td><td class="status {"ok" if observed else "pending"}">'
            f'{"Observed" if observed else "Pending"}</td><td>{html.escape(evidence)}</td></tr>'
        )

    source_items = "".join(f"<li>{html.escape(item)}</li>" for item in model["source_files"]) or "<li>No captures imported</li>"
    mark_items = "".join(f"<li>{html.escape(item)}</li>" for item in model["marks"]) or "<li>No MARK annotations imported</li>"
    direction_rows = "".join(
        f"<tr><td>{html.escape(key)}</td><td>{value}</td></tr>" for key, value in sorted(model["directions"].items())
    ) or "<tr><td>unknown</td><td>0</td></tr>"

    cards = "".join([
        _card("Imported captures", model["source_capture_count"]),
        _card("Unique packets", model["unique_observed_packets"]),
        _card("Packet occurrences", model["total_occurrences"]),
        _card("Verified packets", model["verified_packets"]),
        _card("Quarantined", model["quarantined_candidates"]),
    ])

    data_json = html.escape(json.dumps(model, indent=2))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>York Protocol Lab</title>
<style>
:root{{--bg:#0c1218;--panel:#151e27;--panel2:#1c2833;--text:#e8eef4;--muted:#9eb0bf;--accent:#73b7e6;--ok:#70d6a2;--warn:#f0c674;--border:#2c3d4b}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif}}
header{{padding:30px max(24px,5vw);background:linear-gradient(120deg,#172633,#10202b);border-bottom:1px solid var(--border)}}
h1{{margin:0 0 5px;font-size:30px}} header p{{margin:0;color:var(--muted)}} main{{padding:28px max(24px,5vw);max-width:1500px;margin:auto}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:24px}} .card{{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px}}
.card span{{display:block;color:var(--muted);font-size:13px}} .card strong{{display:block;font-size:28px;margin-top:4px}}
.grid{{display:grid;grid-template-columns:2fr 1fr;gap:20px}} section{{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:20px}}
h2{{font-size:19px;margin:0 0 14px}} table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--border);vertical-align:top}} th{{color:var(--muted)}}
.status{{font-weight:700}} .ok{{color:var(--ok)}} .pending{{color:var(--warn)}} ul{{padding-left:20px;margin:8px 0;max-height:310px;overflow:auto}} code,pre{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}
details{{margin-top:20px}} pre{{white-space:pre-wrap;max-height:500px;overflow:auto;background:#091016;padding:15px;border-radius:8px;color:#cfe1ee}}
footer{{color:var(--muted);padding:10px 0 30px}} @media(max-width:850px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>York Protocol Lab</h1><p>Evidence dashboard for Climate Bridge · Generated {html.escape(model['generated_at'])}</p></header>
<main><div class="cards">{cards}</div><div class="grid"><div>
<section><h2>Protocol feature coverage</h2><table><thead><tr><th>Feature</th><th>Status</th><th>Imported evidence</th></tr></thead><tbody>{''.join(feature_rows)}</tbody></table></section>
<section><h2>Imported MARK annotations</h2><ul>{mark_items}</ul></section>
</div><div>
<section><h2>Capture sources</h2><ul>{source_items}</ul></section>
<section><h2>Direction classification</h2><table><tbody>{direction_rows}</tbody></table></section>
<section><h2>Safety state</h2><p>Imported records remain <strong>observed and non-executable</strong>. Native transmission requires a separately reviewed record marked verified.</p></section>
</div></div>
<details><summary>Raw dashboard data</summary><pre>{data_json}</pre></details>
<footer>Climate Bridge Protocol Lab</footer></main></body></html>"""


def generate_dashboard(protocol_root: Path, output_dir: Path | None = None) -> dict:
    output_dir = output_dir or protocol_root / "dashboard"
    output_dir.mkdir(parents=True, exist_ok=True)
    model = build_lab_model(protocol_root)
    model_path = output_dir / "protocol-lab.json"
    html_path = output_dir / "index.html"
    model_path.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_dashboard(model), encoding="utf-8")
    return {"dashboard": str(html_path), "data": str(model_path), "model": model}
