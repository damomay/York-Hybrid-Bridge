"""Evidence-based request-candidate scoring.

The scorer is deliberately conservative: known state responses are excluded from
request candidacy. No record is verified or made executable.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from typing import Any

from .loader import YorkAnalysisData


def _normalise_hex(value: str) -> str:
    return " ".join(str(value or "").upper().split())


@dataclass(frozen=True)
class RequestCandidate:
    record_id: str
    frame_hex: str
    score: int
    confidence: str
    suggested_direction: str
    suggested_purpose: str
    reasons: list[str]
    disqualifiers: list[str]
    evidence: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def rank_request_candidates(data: YorkAnalysisData) -> tuple[list[RequestCandidate], list[dict[str, Any]]]:
    fixture_hex = {_normalise_hex(item.get("frame_hex", "")) for item in data.fixtures}
    timeline_counts: Counter[str] = Counter()
    marks_by_frame: dict[str, set[str]] = defaultdict(set)
    for event in data.timeline_events:
        if event.get("event") != "frame":
            continue
        record_id = str(event.get("frame_id", ""))
        if not record_id:
            continue
        timeline_counts[record_id] += 1
        mark = str(event.get("mark", "")).strip()
        if mark:
            marks_by_frame[record_id].add(mark)

    candidates: list[RequestCandidate] = []
    excluded: list[dict[str, Any]] = []

    for raw in data.records:
        record_id = str(raw.get("id", "")).strip() or "unknown"
        frame_hex = _normalise_hex(raw.get("frame_hex", ""))
        direction = str(raw.get("direction", "unknown")).strip().lower()
        kind = str(raw.get("kind", raw.get("purpose", "unknown"))).strip().lower()
        classifier = data.classifier_results.get(record_id, {})
        suggested_kind = str(classifier.get("suggested_kind", "")).lower()
        suggested_direction = str(classifier.get("suggested_direction", "")).lower()
        parts = frame_hex.split()

        disqualifiers: list[str] = []
        reasons: list[str] = []
        score = 0

        known_response = (
            kind == "state_response"
            or direction in {"device_to_controller", "response"}
            or suggested_kind == "state_response"
            or suggested_direction == "device_to_controller"
            or frame_hex in fixture_hex
            or (len(parts) == 21 and parts[:4] == ["BB", "01", "00", "03"])
        )
        if known_response:
            disqualifiers.append("Evidence identifies this frame as a device-to-controller state response.")

        if direction in {"controller_to_device", "request"}:
            score += 45
            reasons.append("Record direction is controller-to-device.")
        elif direction == "unknown":
            score += 5
            reasons.append("Direction is unresolved; further capture evidence would be required.")

        if kind in {"state_request", "command", "request"}:
            score += 35
            reasons.append(f"Record purpose/kind is labelled {kind}.")
        elif kind == "unknown":
            score += 5
            reasons.append("Purpose is unresolved.")

        occurrence_count = timeline_counts.get(record_id, 0)
        marks = sorted(marks_by_frame.get(record_id, set()))
        if occurrence_count:
            score += min(10, occurrence_count)
            reasons.append(f"Observed {occurrence_count} time(s) in the imported timeline.")
        if marks:
            score += min(10, len(marks) * 2)
            reasons.append(f"Associated with {len(marks)} operator mark(s).")

        if frame_hex in fixture_hex:
            disqualifiers.append("Exact qualified decoder-fixture match confirms response semantics.")

        if disqualifiers:
            excluded.append({
                "record_id": record_id,
                "frame_hex": frame_hex,
                "reasons": reasons,
                "disqualifiers": disqualifiers,
                "timeline_occurrences": occurrence_count,
                "marks": marks,
            })
            continue

        score = min(score, 100)
        confidence = "high" if score >= 80 else "medium" if score >= 60 else "low"
        candidates.append(RequestCandidate(
            record_id=record_id,
            frame_hex=frame_hex,
            score=score,
            confidence=confidence,
            suggested_direction="controller_to_device" if score >= 60 else "unknown",
            suggested_purpose="state_request" if score >= 80 else "unknown",
            reasons=reasons or ["No positive request evidence was found."],
            disqualifiers=disqualifiers,
            evidence={
                "timeline_occurrences": occurrence_count,
                "marks": marks,
                "source_path": raw.get("_source_path", ""),
            },
        ))

    candidates.sort(key=lambda item: (-item.score, item.record_id))
    return candidates, excluded
