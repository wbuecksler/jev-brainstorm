"""Turn Jev answers into Act | Review | Escalate.

Rules are declarative so the policy owner can read and change them without touching code:
escalate if any escalate_if condition holds; otherwise review if any review_if condition holds;
otherwise act. When the spec sets high_stakes, Act becomes Review: the harness never recommends
acting alone on an irreversible or consequential step. Shadow mode only ever logs the band.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BandDecision:
    band: str
    reasons: list[str] = field(default_factory=list)


def decide(spec: dict[str, Any], state: Any, answers: dict[str, dict[str, Any]]) -> BandDecision:
    bands = spec.get("bands") or {}
    for key, band in (("escalate_if", "escalate"), ("review_if", "review")):
        reasons = [_describe(c) for c in bands.get(key, []) if _holds(c, state, answers)]
        if reasons:
            return BandDecision(band, reasons)
    if spec.get("high_stakes"):
        return BandDecision("review", ["high_stakes: Act is never automatic on this workflow"])
    return BandDecision("act", ["no escalate or review condition held"])


def _holds(condition: dict[str, Any], state: Any, answers: dict[str, dict[str, Any]]) -> bool:
    if "state_missing" in condition:
        return not (isinstance(state, dict) and state.get(condition["state_missing"]))
    answer = answers.get(condition["question"])
    if answer is None:
        return False
    for op, value in condition.items():
        if op == "choice_in":
            return answer["choice"] in value
        if op == "choice_not_in":
            return answer["choice"] not in value
        if op == "confidence_lt":
            return answer["confidence"] < value
        if op == "confidence_gte":
            return answer["confidence"] >= value
        if op == "score_gte":
            return answer["score"] >= value
        if op == "score_lte":
            return answer["score"] <= value
        if op == "noul_gte":
            return answer["noul"] >= value
        if op == "noul_lt":
            return answer["noul"] < value
    return False


def _describe(condition: dict[str, Any]) -> str:
    if condition.get("why"):
        return str(condition["why"])
    if "state_missing" in condition:
        return f"state is missing {condition['state_missing']}"
    op, value = next((k, v) for k, v in condition.items() if k not in ("question", "why"))
    return f"{condition['question']} {op} {value}"
