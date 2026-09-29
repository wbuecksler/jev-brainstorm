"""Load and lint an opportunity spec.

The linter enforces the rules in docs/anti-patterns.md that can be checked mechanically.
Errors block a run. Warnings print but do not block. Nothing here calls the network.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CHOICE_MAX_OPTIONS = 255  # vendor-stated
SCORE_MIN_LEVELS = 2
SCORE_MAX_LEVELS = 10  # vendor-stated
STATE_WINDOW_TOKENS = 32_000  # vendor-stated (OpenRouter / Vercel listings)
CHARS_PER_TOKEN_ESTIMATE = 4  # rough heuristic for a size warning only, not a billing figure

ESCAPE_HATCHES = {"other", "unclear", "none", "unknown", "not_applicable", "n/a"}
FIT_LEVELS = {"H", "M", "L"}
BANDS = ("act", "review", "escalate")

CONDITION_OPS: dict[str, set[str]] = {
    "choice": {"choice_in", "choice_not_in", "confidence_lt", "confidence_gte"},
    "score": {"score_gte", "score_lte", "confidence_lt", "confidence_gte"},
    "noul": {"noul_gte", "noul_lt"},
}

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_GENERATION_RE = re.compile(r"^\s*(write|draft|compose|summari[sz]e|generate|rewrite|explain|describe|reply)\b", re.I)
_ARITHMETIC_RE = re.compile(
    r"\b(calculate|compute|sum of|add up|how many|count the|total of|average|days between|difference between .* dates?)\b", re.I
)
_COMPOUND_NOUL_RE = re.compile(r"\b(and|or)\b", re.I)


class SpecError(Exception):
    """The spec cannot be loaded or has blocking lint errors."""


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class Fixture:
    id: str
    state: Any
    scenario: str = ""
    expected_band: str | None = None
    human: dict[str, Any] = field(default_factory=dict)


def load_spec(path: Path) -> dict[str, Any]:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SpecError(f"cannot read spec {path}: {error}") from error
    if not isinstance(spec, dict):
        raise SpecError(f"spec {path} must be a JSON object")
    return spec


def load_fixtures(path: Path) -> list[Fixture]:
    fixtures: list[Fixture] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise SpecError(f"cannot read fixtures {path}: {error}") from error
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as error:
            raise SpecError(f"{path}:{number}: invalid JSON: {error}") from error
        fixtures.append(parse_fixture(raw, f"{path}:{number}"))
    if not fixtures:
        raise SpecError(f"{path}: no fixtures")
    return fixtures


def parse_fixture(raw: Any, where: str = "fixture") -> Fixture:
    if not isinstance(raw, dict) or "id" not in raw or "state" not in raw:
        raise SpecError(f"{where}: each fixture needs an 'id' and a 'state'")
    return Fixture(
        id=str(raw["id"]),
        state=raw["state"],
        scenario=str(raw.get("scenario", "")),
        expected_band=raw.get("expected_band"),
        human=raw.get("human") or {},
    )


def estimate_tokens(state: Any) -> int:
    text = state if isinstance(state, str) else json.dumps(state, ensure_ascii=False)
    return len(text) // CHARS_PER_TOKEN_ESTIMATE


def lint_spec(spec: dict[str, Any], fixtures: list[Fixture] | None = None) -> LintResult:
    result = LintResult()
    err, warn = result.errors.append, result.warnings.append

    if spec.get("spec_version") != "1":
        err('spec_version must be "1"')
    name = spec.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        err("name must be lowercase letters, digits, and dashes")

    fit = spec.get("fit")
    if not isinstance(fit, dict):
        err("fit is required (V, D, R, L, value as H/M/L, plus map_card and pattern)")
    else:
        for axis in ("V", "D", "R", "L", "value"):
            if fit.get(axis) not in FIT_LEVELS:
                err(f"fit.{axis} must be H, M, or L")
        if fit.get("D") == "L":
            err("fit.D is L: the answer set is not closed, so this is not a Jev question yet (anti-pattern 2)")
        if fit.get("R") == "L" and not spec.get("high_stakes"):
            err("fit.R is L but high_stakes is false: consequential workflows must set high_stakes so Act is never automatic")

    questions = spec.get("questions")
    if not isinstance(questions, dict) or not questions:
        err("questions must be a nonempty object")
        questions = {}

    for qname, question in questions.items():
        where = f"questions.{qname}"
        if not _NAME_RE.match(qname):
            err(f"{where}: name must be snake_case, starting with a letter")
        if not isinstance(question, dict):
            err(f"{where}: must be an object")
            continue
        qtype = question.get("type")
        instructions = question.get("instructions")
        text = instructions if isinstance(instructions, str) else ""
        if qtype not in CONDITION_OPS:
            err(f"{where}: type must be choice, score, or noul")
            continue
        if not text.strip():
            warn(f"{where}: no instructions; Jev will interpret the criteria by label alone")
        if _GENERATION_RE.search(text):
            err(f"{where}: instructions ask for generated text; Jev does not write (anti-pattern 1)")
        if _ARITHMETIC_RE.search(text):
            warn(f"{where}: instructions look like arithmetic or counting; keep exact math in code (anti-pattern 3)")

        criteria = question.get("criteria")
        if qtype == "choice":
            if not isinstance(criteria, dict):
                err(f"{where}: choice criteria must be an object of label -> description")
                continue
            if len(criteria) < 2:
                err(f"{where}: a choice needs at least 2 options")
            if len(criteria) > CHOICE_MAX_OPTIONS:
                err(f"{where}: {len(criteria)} options exceeds the vendor-stated {CHOICE_MAX_OPTIONS}; split hierarchically")
            if not ESCAPE_HATCHES & {label.lower() for label in criteria}:
                warn(f"{where}: no escape hatch (other / unclear / none); a forced pick can be confidently wrong (anti-pattern 10)")
        elif qtype == "score":
            if not isinstance(criteria, list):
                err(f"{where}: score criteria must be an ordered list, lowest level first")
                continue
            if not SCORE_MIN_LEVELS <= len(criteria) <= SCORE_MAX_LEVELS:
                err(f"{where}: score needs {SCORE_MIN_LEVELS}-{SCORE_MAX_LEVELS} levels, got {len(criteria)}")
        elif qtype == "noul":
            if criteria is not None and (not isinstance(criteria, dict) or set(criteria) - {"true", "false"}):
                err(f"{where}: noul criteria may only have 'true' and 'false'")
            if _COMPOUND_NOUL_RE.search(text):
                warn(f"{where}: instructions contain 'and'/'or'; a Noul should ask about exactly one fact")

    bands = spec.get("bands")
    if not isinstance(bands, dict):
        err("bands is required, with escalate_if and review_if condition lists")
        bands = {}
    for key in ("escalate_if", "review_if"):
        conditions = bands.get(key, [])
        if not isinstance(conditions, list):
            err(f"bands.{key} must be a list")
            continue
        if key == "escalate_if" and not conditions:
            warn("bands.escalate_if is empty; every workflow should have a path to a human")
        for index, condition in enumerate(conditions):
            _lint_condition(f"bands.{key}[{index}]", condition, questions, spec, result)

    if fixtures is not None:
        if len(fixtures) < 5:
            warn(f"only {len(fixtures)} fixtures; the test plan asks for 5-10")
        seen: set[str] = set()
        for fixture in fixtures:
            where = f"fixture {fixture.id}"
            if fixture.id in seen:
                err(f"{where}: duplicate id")
            seen.add(fixture.id)
            if fixture.expected_band is not None and fixture.expected_band not in BANDS:
                err(f"{where}: expected_band must be one of {', '.join(BANDS)}")
            if fixture.human.get("band") not in (None, *BANDS):
                err(f"{where}: human.band must be one of {', '.join(BANDS)}")
            tokens = estimate_tokens(fixture.state)
            if tokens > STATE_WINDOW_TOKENS * 0.8:
                warn(
                    f"{where}: state is roughly {tokens} tokens (chars/4 estimate), near the vendor-stated "
                    f"{STATE_WINDOW_TOKENS} window; filter it first (anti-pattern 5)"
                )
            for label in fixture.human:
                if label != "band" and label not in questions:
                    warn(f"{where}: human label '{label}' does not match a question; it will be ignored")
    return result


def _lint_condition(where: str, condition: Any, questions: dict[str, Any], spec: dict[str, Any], result: LintResult) -> None:
    if not isinstance(condition, dict):
        result.errors.append(f"{where}: must be an object")
        return
    if "state_missing" in condition:
        required = (spec.get("state") or {}).get("required", [])
        if condition["state_missing"] not in required:
            result.warnings.append(f"{where}: state_missing '{condition['state_missing']}' is not listed in state.required")
        return
    qname = condition.get("question")
    if qname not in questions:
        result.errors.append(f"{where}: unknown question '{qname}'")
        return
    qtype = questions[qname].get("type") if isinstance(questions[qname], dict) else None
    ops = [key for key in condition if key not in ("question", "why")]
    if len(ops) != 1:
        result.errors.append(f"{where}: exactly one operator per condition, got {ops or 'none'}")
        return
    op = ops[0]
    allowed = CONDITION_OPS.get(qtype or "", set())
    if op not in allowed:
        result.errors.append(f"{where}: '{op}' does not apply to a {qtype} question (allowed: {', '.join(sorted(allowed))})")
        return
    value = condition[op]
    if op in ("choice_in", "choice_not_in"):
        labels = set((questions[qname].get("criteria") or {}).keys())
        if not isinstance(value, list) or not value or not set(value) <= labels:
            result.errors.append(f"{where}: {op} must list labels from {qname}'s criteria")
    elif op in ("score_gte", "score_lte"):
        levels = len(questions[qname].get("criteria") or [])
        if not isinstance(value, (int, float)) or not 0 <= value <= max(levels - 1, 0):
            result.errors.append(f"{where}: {op} must be a level between 0 and {levels - 1}")
    elif not isinstance(value, (int, float)) or not 0 <= value <= 1:
        result.errors.append(f"{where}: {op} must be a probability between 0 and 1")
