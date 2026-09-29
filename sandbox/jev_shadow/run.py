"""Run a spec over its fixtures in shadow mode and write a log and a report."""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jev_shadow.bands import decide
from jev_shadow.evaluate import Evaluator
from jev_shadow.spec import BANDS, Fixture

VENDOR_PRICE_PER_MTOK = 0.042  # vendor-stated input price; output is stated as free


@dataclass
class Row:
    fixture: Fixture
    answers: dict[str, dict[str, Any]]
    band: str
    reasons: list[str]
    model: str
    input_tokens: int | None
    latency_ms: float
    error: str | None = None
    agreement: dict[str, bool] = field(default_factory=dict)


def agrees(answer: dict[str, Any], label: Any) -> bool:
    """Compare one Jev answer with a human label. The 0.5 cut for Noul is a readout, not a threshold."""
    if answer["type"] == "choice":
        return answer["choice"] == label
    if answer["type"] == "score":
        return round(answer["score"]) == label
    return (answer["noul"] >= 0.5) == bool(label)


def run(spec: dict[str, Any], fixtures: list[Fixture], evaluator: Evaluator) -> list[Row]:
    questions = spec["questions"]
    rows: list[Row] = []
    for fixture in fixtures:
        try:
            evaluation = evaluator.evaluate(fixture.state, questions)
        except Exception as error:  # noqa: BLE001 - one failed call must not stop the batch; the row escalates.
            rows.append(
                Row(fixture, {}, "escalate", [f"Jev call failed: {type(error).__name__}"], "n/a", None, 0.0, error=str(error)[:300])
            )
            continue
        decision = decide(spec, fixture.state, evaluation.answers)
        row = Row(fixture, evaluation.answers, decision.band, decision.reasons, evaluation.model, evaluation.input_tokens, evaluation.latency_ms)
        for label_name, label in fixture.human.items():
            if label_name == "band":
                row.agreement["band"] = decision.band == label
            elif label_name in evaluation.answers:
                row.agreement[label_name] = agrees(evaluation.answers[label_name], label)
        rows.append(row)
    return rows


def write_log(rows: list[Row], spec: dict[str, Any], live: bool, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            record = {
                "ts": now,
                "spec": spec["name"],
                "mode": "shadow",
                "live": live,
                "fixture_id": row.fixture.id,
                "state": row.fixture.state,
                "model": row.model,
                "answers": row.answers,
                "recommended_band": row.band,
                "reasons": row.reasons,
                "acted": False,
                "expected_band": row.fixture.expected_band,
                "human": row.fixture.human or None,
                "agreement": row.agreement or None,
                "input_tokens": row.input_tokens,
                "latency_ms": round(row.latency_ms, 1),
                "error": row.error,
            }
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _format_answer(answer: dict[str, Any]) -> str:
    if answer["type"] == "choice":
        return f"{answer['choice']} ({answer['confidence']:.2f})"
    if answer["type"] == "score":
        return f"{answer['score']:.1f} ({answer['confidence']:.2f})"
    return f"p={answer['noul']:.2f}"


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_report(rows: list[Row], spec: dict[str, Any], live: bool) -> str:
    qnames = list(spec["questions"])
    lines: list[str] = [f"# Jev shadow run: `{spec['name']}`", ""]
    if spec.get("fictional"):
        lines += ["> Fictional example spec. Fixtures are synthetic.", ""]
    if live:
        models = sorted({row.model for row in rows if row.model != "n/a"})
        lines += [f"**Mode:** shadow, live Jev calls · **model:** {', '.join(models) or 'n/a'} · **fixtures:** {len(rows)}", ""]
    else:
        lines += [
            "> **DRY RUN.** No API key was available, so no model was called. Answers below are deterministic",
            "> placeholders that exercise the bands and the report. They say nothing about Jev's accuracy.",
            "> Add a `TYPESAFE_API_KEY` secret and re-run to see real answers.",
            "",
        ]
    lines += ["Nothing was sent, changed, or acted on. Every band is a recommendation written to the log.", ""]

    header = ["ID", "Scenario", *qnames, "Band", "Expected", "Human", "Why"]
    lines += ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for row in rows:
        answers = [_format_answer(row.answers[q]) if q in row.answers else "—" for q in qnames]
        expected = row.fixture.expected_band or "—"
        if live and row.fixture.expected_band:
            expected += " ✓" if row.fixture.expected_band == row.band else " ✗"
        human = row.fixture.human.get("band", "—")
        if live and "band" in row.agreement:
            human += " ✓" if row.agreement["band"] else " ✗"
        cells = [row.fixture.id, row.fixture.scenario, *answers, f"**{row.band}**", expected, human, "; ".join(row.reasons)]
        lines.append("| " + " | ".join(_cell(str(c)) for c in cells) + " |")
    lines.append("")

    lines += ["## Summary", ""]
    counts = {band: sum(1 for row in rows if row.band == band) for band in BANDS}
    lines.append("- **Bands:** " + " · ".join(f"{band} {count}" for band, count in counts.items()))
    with_expected = [row for row in rows if row.fixture.expected_band]
    if not live:
        lines.append("- **Agreement:** not shown for a dry run; placeholder answers cannot agree or disagree with anyone.")
        with_expected = []
    if with_expected:
        hits = sum(1 for row in with_expected if row.fixture.expected_band == row.band)
        lines.append(f"- **Matched the hypothesized band:** {hits}/{len(with_expected)}")
    agreement_keys = sorted({key for row in rows for key in row.agreement}) if live else []
    for key in agreement_keys:
        scored = [row.agreement[key] for row in rows if key in row.agreement]
        lines.append(f"- **Agreement with human label `{key}`:** {sum(scored)}/{len(scored)}")
    errors = [row for row in rows if row.error]
    if errors:
        lines.append(f"- **Failed calls:** {len(errors)} (escalated). First error: `{_cell(errors[0].error or '')}`")
    if live:
        tokens = [row.input_tokens for row in rows if row.input_tokens is not None]
        latencies = [row.latency_ms for row in rows if not row.error]
        if tokens:
            total = sum(tokens)
            cost = total * VENDOR_PRICE_PER_MTOK / 1_000_000
            lines.append(
                f"- **Input tokens (reported by the API):** {total:,} · **cost at the vendor-stated "
                f"${VENDOR_PRICE_PER_MTOK}/MTok:** ${cost:.6f}"
            )
        if latencies:
            lines.append(
                f"- **Round-trip latency measured from this runner:** median {statistics.median(latencies):.0f} ms "
                f"(includes network; n={len(latencies)})"
            )
    lines += [
        "",
        "## Read this before drawing conclusions",
        "",
        "- A handful of fixtures is a smoke test, not a calibration. Bands in the spec are starting hypotheses.",
        "- Next step: run the same spec on a few hundred of your own labeled historical items (in a private repo),",
        "  compare with what people actually decided, then have the policy owner move the thresholds.",
        "- Keep the workflow in shadow until that comparison is acceptable to the policy owner. Act stays off.",
    ]
    return "\n".join(lines) + "\n"
