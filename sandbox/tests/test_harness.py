import json
from pathlib import Path

import httpx2
import jsonschema
import pytest

from jev_shadow.bands import decide
from jev_shadow.cli import main
from jev_shadow.evaluate import DryRunEvaluator, JevEvaluator
from jev_shadow.run import agrees, render_report, run
from jev_shadow.spec import lint_spec, load_fixtures, load_spec

REPO = Path(__file__).resolve().parents[2]
SPECS = sorted(p.parent for p in (REPO / "specs").glob("*/spec.json"))
SCHEMA = json.loads((REPO / "spec" / "opportunity-spec.schema.json").read_text())
EXAMPLE = REPO / "specs" / "support-triage-example"


@pytest.mark.parametrize("spec_dir", SPECS, ids=lambda p: p.name)
def test_committed_specs_match_schema_and_lint_clean(spec_dir):
    spec = load_spec(spec_dir / "spec.json")
    jsonschema.validate(spec, SCHEMA)
    result = lint_spec(spec, load_fixtures(spec_dir / "fixtures.jsonl"))
    assert result.errors == []


def _spec(**overrides):
    spec = load_spec(EXAMPLE / "spec.json")
    spec.update(overrides)
    return spec


def test_lint_rejects_generation_and_bad_bounds():
    spec = _spec()
    spec["questions"]["reply"] = {"type": "noul", "instructions": "Write a reply to the customer"}
    spec["questions"]["tiny"] = {"type": "score", "instructions": "Rate it", "criteria": ["only one"]}
    errors = lint_spec(spec).errors
    assert any("generated text" in e for e in errors)
    assert any("2-10 levels" in e for e in errors)


def test_lint_rejects_open_answer_set_and_unguarded_high_consequence():
    spec = _spec()
    spec["fit"] = {**spec["fit"], "D": "L", "R": "L"}
    errors = lint_spec(spec).errors
    assert any("anti-pattern 2" in e for e in errors)
    assert any("high_stakes" in e for e in errors)


def test_lint_warns_on_missing_escape_hatch_and_compound_noul():
    spec = _spec()
    spec["questions"]["queue"]["criteria"].pop("other")
    spec["bands"]["escalate_if"] = [c for c in spec["bands"]["escalate_if"] if c.get("question") != "queue"]
    spec["questions"]["billing_intent"]["instructions"] = "The customer mentions a refund or a discount."
    warnings = lint_spec(spec).warnings
    assert any("escape hatch" in w for w in warnings)
    assert any("exactly one fact" in w for w in warnings)


def test_lint_checks_condition_operators_against_question_type():
    spec = _spec()
    spec["bands"]["review_if"].append({"question": "billing_intent", "choice_in": ["billing"]})
    spec["bands"]["review_if"].append({"question": "queue", "choice_in": ["refunds"]})
    errors = lint_spec(spec).errors
    assert any("does not apply to a noul" in e for e in errors)
    assert any("labels from queue" in e for e in errors)


ANSWERS_CONFIDENT = {
    "queue": {"type": "choice", "choice": "billing", "confidence": 0.95, "probabilities": {}},
    "urgency": {"type": "score", "score": 0.4, "confidence": 0.9, "probabilities": {}},
    "billing_intent": {"type": "noul", "noul": 0.97},
    "account_access": {"type": "noul", "noul": 0.02},
    "prompt_injection": {"type": "noul", "noul": 0.01},
}


def test_bands_act_review_escalate_and_high_stakes():
    spec = _spec()
    state = {"first_message": "charged twice"}
    assert decide(spec, state, ANSWERS_CONFIDENT).band == "act"

    unsure = {**ANSWERS_CONFIDENT, "queue": {**ANSWERS_CONFIDENT["queue"], "confidence": 0.6}}
    assert decide(spec, state, unsure).band == "review"

    injected = {**ANSWERS_CONFIDENT, "prompt_injection": {"type": "noul", "noul": 0.9}}
    decision = decide(spec, state, injected)
    assert decision.band == "escalate" and "injection" in decision.reasons[0]

    assert decide(spec, {"first_message": ""}, ANSWERS_CONFIDENT).band == "escalate"
    assert decide(_spec(high_stakes=True), state, ANSWERS_CONFIDENT).band == "review"


def test_agreement_readout_per_primitive():
    assert agrees({"type": "choice", "choice": "billing"}, "billing")
    assert agrees({"type": "score", "score": 2.4}, 2)
    assert agrees({"type": "noul", "noul": 0.7}, True)
    assert not agrees({"type": "noul", "noul": 0.2}, True)


def test_dry_run_report_is_labeled_and_never_acts():
    spec = load_spec(EXAMPLE / "spec.json")
    rows = run(spec, load_fixtures(EXAMPLE / "fixtures.jsonl"), DryRunEvaluator())
    report = render_report(rows, spec, live=False)
    assert "DRY RUN" in report
    assert "Nothing was sent, changed, or acted on" in report
    assert len(rows) == 8


def test_live_path_uses_real_sdk_wire_format(monkeypatch):
    """Drive the real typesafe-sdk client through a mock transport: checks the request we send and the response we parse."""
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key-not-real")
    seen = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        body = json.loads(request.content)
        seen["body"] = body
        answers = {}
        for name, q in body["questions"].items():
            if q["type"] == "choice":
                answers[name] = {"type": "choice", "choice": "billing", "confidence": 0.93, "probabilities": {k: 0.0 for k in q["criteria"]} | {"billing": 0.93}}
            elif q["type"] == "score":
                answers[name] = {"type": "score", "score": 0.2, "confidence": 0.9, "legend": {str(i): c for i, c in enumerate(q["criteria"])}, "probabilities": {str(i): 0.25 for i in range(len(q["criteria"]))}}
            else:
                answers[name] = {"type": "noul", "noul": 0.03 if name == "prompt_injection" else 0.96}
        return httpx2.Response(200, json={"model": "jev-test", "answers": answers, "usage": {"input_tokens": 321, "output_tokens": 9}})

    spec = load_spec(EXAMPLE / "spec.json")
    evaluator = JevEvaluator(model="jev-latest", transport=httpx2.MockTransport(handler))
    evaluation = evaluator.evaluate({"subject": "x", "first_message": "charged twice"}, spec["questions"])
    evaluator.close()

    assert seen["url"] == "https://api.typesafe.ai/v1/systemone"
    assert seen["auth"] == "Bearer test-key-not-real"
    assert seen["body"]["model"] == "jev-latest"
    assert set(seen["body"]["questions"]) == set(spec["questions"])
    assert evaluation.model == "jev-test" and evaluation.input_tokens == 321
    assert evaluation.answers["urgency"]["probabilities"][0] == 0.25
    assert decide(spec, {"first_message": "charged twice"}, evaluation.answers).band == "act"


def test_cli_run_without_key_falls_back_to_dry_run(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)  # keep a developer's real .env out of this test
    assert main(["run", str(EXAMPLE), "--out", str(tmp_path)]) == 0
    log = (tmp_path / "support-triage-example" / "shadow.jsonl").read_text().splitlines()
    assert len(log) == 8
    assert all(json.loads(line)["acted"] is False for line in log)
    assert "DRY RUN" in capsys.readouterr().out


def test_host_entry_point_lints_caps_and_reports():
    from jev_shadow.api import shadow_run
    from jev_shadow.spec import SpecError

    spec = load_spec(EXAMPLE / "spec.json")
    raw = [json.loads(line) for line in (EXAMPLE / "fixtures.jsonl").read_text().splitlines() if line.strip()]
    report = shadow_run(spec, raw, evaluator=DryRunEvaluator())
    assert "| T8 |" in report

    with pytest.raises(SpecError, match="at most 25"):
        shadow_run(spec, raw * 4, evaluator=DryRunEvaluator())

    bad = _spec()
    bad["questions"]["reply"] = {"type": "noul", "instructions": "Draft a reply"}
    with pytest.raises(SpecError, match="generated text"):
        shadow_run(bad, raw, evaluator=DryRunEvaluator())


def test_dotenv_fills_only_unset_typesafe_keys(tmp_path, monkeypatch):
    from jev_shadow.cli import load_dotenv

    (tmp_path / ".env").write_text('# comment\nTYPESAFE_API_KEY="from-file"\nOTHER_SECRET=nope\nTYPESAFE_DEFAULT_MODEL=\n')
    nested = tmp_path / "specs" / "x"
    nested.mkdir(parents=True)
    monkeypatch.setenv("TYPESAFE_API_KEY", "")  # empty counts as unset; monkeypatch restores the original afterwards
    monkeypatch.delenv("OTHER_SECRET", raising=False)
    load_dotenv(nested)
    import os

    assert os.environ["TYPESAFE_API_KEY"] == "from-file"
    assert "OTHER_SECRET" not in os.environ

    monkeypatch.setenv("TYPESAFE_API_KEY", "from-env")
    load_dotenv(nested)
    assert os.environ["TYPESAFE_API_KEY"] == "from-env"


def test_chat_bundle_is_current():
    import importlib.util

    spec = importlib.util.spec_from_file_location("build_chat_bundle", REPO / "scripts" / "build_chat_bundle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    committed = (REPO / "dist" / "jev-discovery-chat.md").read_text(encoding="utf-8")
    assert committed == module.build(), "dist/jev-discovery-chat.md is stale: run python3 scripts/build_chat_bundle.py"
    assert "Optional host tool" not in committed  # chat apps have no tools
