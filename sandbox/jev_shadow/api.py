"""One-call entry point for a bot host's `jev_shadow_run` tool (see bot/system-prompt.md)."""

from __future__ import annotations

from typing import Any

from jev_shadow.evaluate import Evaluator, JevEvaluator
from jev_shadow.run import render_report, run
from jev_shadow.spec import SpecError, lint_spec, parse_fixture

MAX_FIXTURES = 25


def shadow_run(spec: dict[str, Any], fixtures: list[dict[str, Any]], evaluator: Evaluator | None = None) -> str:
    """Lint, run, and return the Markdown report. Raises SpecError with the lint output on failure.

    The host's environment supplies TYPESAFE_API_KEY; it never passes through the conversation.
    """
    if len(fixtures) > MAX_FIXTURES:
        raise SpecError(f"at most {MAX_FIXTURES} fixtures per in-chat run; use the sandbox repo for more")
    parsed = [parse_fixture(raw, f"fixtures[{index}]") for index, raw in enumerate(fixtures)]
    result = lint_spec(spec, parsed)
    if not result.ok:
        raise SpecError("spec failed lint:\n" + "\n".join(f"- {message}" for message in result.errors))
    evaluator = evaluator or JevEvaluator(model=spec.get("model"))
    try:
        rows = run(spec, parsed, evaluator)
    finally:
        evaluator.close()
    report = render_report(rows, spec, evaluator.live)
    if result.warnings:
        report += "\n## Lint warnings\n\n" + "\n".join(f"- {message}" for message in result.warnings) + "\n"
    return report
