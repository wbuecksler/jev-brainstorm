# Claude Code — Jev prototype prompt (template)

After a [discovery interview](discovery-interview.md), fill every `{{PLACEHOLDER}}` from the [opportunity spec](../spec/opportunity-spec.schema.json) and what the leader said. Emit the completed prompt as **one** fenced markdown block for **their engineer** to paste into Claude Code.

The leader has already seen the spec run on synthetic fixtures (in chat or in the [sandbox](../sandbox/README.md)). This prompt covers the next step: **run the same spec on the team's own labeled history, in shadow mode, and produce a comparison the policy owner can act on.**

Rules while you fill:

- Business facts come only from the interview. If a field is unknown, write `not stated`. Don't guess a volume, a dollar figure, or a latency.
- Paste the spec JSON verbatim. It is the single source of truth for the questions and the bands.
- Thresholds are **starting hypotheses**, and the prompt says so.
- No API keys, customer records, or production dumps in the prompt.

Inner code fences are intentional. Keep them inside the outer fence.

````markdown
# Claude Code task: shadow-test a TypeSafe Jev decision on our labeled history

## Goal
{{GOAL_ONE_SENTENCE}}

Deliver a **shadow-mode** comparison: for each historical item, what Jev would have recommended (Act / Review / Escalate) against what our people actually decided. **No production writes, no messages, no automatic actions.**

## Business context (from discovery — do not invent)
- **Company / product:** {{COMPANY_PRODUCT}}
- **Workflow:** {{WORKFLOW}}
- **Where the input text lives:** {{INFLOW_SOURCE_SYSTEM}}
- **Where the human decision is recorded:** {{LABEL_SOURCE}}
- **Volume (as stated):** {{VOLUME_AS_STATED}}
- **Consequence if wrong:** {{CONSEQUENCE}}
- **Policy owner:** {{POLICY_OWNER}}
- **Irreversible actions in this workflow:** {{HIGH_STAKES_ACTIONS}}

## Jev facts (obey these)
- TypeSafe Jev is a **decision** model: Choice (closed options), Score (ordered 2–10 level rubric → expected score + confidence), Noul (probability that one statement is true). **It generates no text.**
- Vendor-stated: about $0.042 per million input tokens (output free), about 70–500 ms, about a 32k state window. These are not measurements of this project.
- Verified SDK (Python, `typesafe-sdk` 0.7.2). Read `https://docs.typesafe.ai/llms.txt` if you can reach it; otherwise trust this snippet over memory:

```python
# pip install "typesafe-sdk>=0.7.2,<0.8"   — the SDK reads TYPESAFE_API_KEY from the environment
from typesafe_sdk import TypeSafeClient
with TypeSafeClient() as client:                     # model defaults to "jev-latest"
    r = client.system_one(state=state_dict_or_text, questions=spec["questions"])  # dict questions pass through as-is
    r.choices[name].choice, r.choices[name].confidence, r.choices[name].probabilities
    r.scores[name].score, r.scores[name].confidence, r.scores[name].probabilities  # int keys
    r.nouls[name].noul                                # probability of yes
    r.model, r.usage.input_tokens
```
HTTP equivalent: `POST https://api.typesafe.ai/v1/systemone` with `Authorization: Bearer $TYPESAFE_API_KEY` and body `{"state", "model", "questions"}`.

## The spec (single source of truth — do not change questions or bands without telling me)
```json
{{OPPORTUNITY_SPEC_JSON}}
```

## Start from the existing harness
Copy `sandbox/` and `specs/` from https://github.com/wbuecksler/jev-brainstorm (or the team's private copy of it). It already does: spec lint → Jev call → bands → `out/<name>/shadow.jsonl` + `report.md`, with offline tests. **Reuse it; don't rewrite it.** Your work is the data adapter and the comparison.

## Build
1. **`adapters/{{ADAPTER_NAME}}.py` — read-only export.** Pull {{SAMPLE_SIZE}} recent items from {{INFLOW_SOURCE_SYSTEM}} with the human decision from {{LABEL_SOURCE}}. Write `specs/{{SPEC_NAME}}/history.jsonl` in the fixture shape `{"id", "state", "human": {"<question>": <label>, "band": <optional>}}`.
   - The state holds only the fields in the spec's `state.description`. Trim long text. No account numbers, emails, or phone numbers unless a question needs them.
   - Map the system's labels onto the spec's labels in one explicit table in code. Unmappable → leave the label out; never guess.
   - Read-only credentials. `history.jsonl` and `out/` are git-ignored.
2. **Run** `jev-shadow run` against the history (point it at a spec dir whose `fixtures.jsonl` is `history.jsonl`).
3. **`scripts/compare.py` — the comparison the policy owner reads.** Using `out/<name>/shadow.jsonl`, produce:
   - For each Choice question, a confusion table (Jev vs human).
   - Band counts, plus agreement with the human decision *within each band*. The key question: "when Jev would have said Act, how often was it right?"
   - The 10 most confident disagreements, with their ids, so someone can read them.
   - A threshold sweep for the one confidence rule that gates Act: at each candidate threshold, the share of items that would Act and the agreement among them. Present it as options for the policy owner. **Do not pick one.**

## Rules
- Mode is shadow. No code path writes to {{INFLOW_SOURCE_SYSTEM}} or anything else.
- `TYPESAFE_API_KEY` comes from the environment only. Fail fast if it's missing. Never print it.
- Never add a generation call. If a question needs text written, stop and tell me.
- Arithmetic, dates, and counting stay in code.
- If {{HIGH_STAKES_ACTIONS}} is not `none stated`, the Act band must stay a recommendation even after this project.
- Don't reuse thresholds from cookbooks or other deployments.

## Done when
- [ ] `pytest -q sandbox/tests` passes, and the adapter has a test that uses a small hand-written sample (no real data in the repo).
- [ ] `history.jsonl` exists locally with {{SAMPLE_SIZE}} items (or the reason why fewer).
- [ ] `out/<name>/report.md` and the `compare.py` output exist, and `compare.py`'s output reads like a one-page summary for {{POLICY_OWNER}}.
- [ ] A README section says how to re-run, and states that the bands are hypotheses until {{POLICY_OWNER}} signs off.

## Out of scope
{{OUT_OF_SCOPE}}
````

## Placeholder cheat-sheet

| Placeholder | Fill from |
|---|---|
| `{{GOAL_ONE_SENTENCE}}` | The spec's `summary` |
| `{{COMPANY_PRODUCT}}` … `{{POLICY_OWNER}}` | Spec `business.*`. Unknown → `not stated` |
| `{{INFLOW_SOURCE_SYSTEM}}` | Where the text lives (Zendesk, Gmail, S3 PDFs, …), as they said it |
| `{{LABEL_SOURCE}}` | The field that records the human outcome (closed ticket's queue, claim decision, …). If none, write `none yet: label {{SAMPLE_SIZE}} items by hand first` |
| `{{HIGH_STAKES_ACTIONS}}` | Spec `business.irreversible_actions`, or `none stated` |
| `{{OPPORTUNITY_SPEC_JSON}}` | The full spec, verbatim |
| `{{SPEC_NAME}}`, `{{ADAPTER_NAME}}` | Spec `name`; the source system in snake_case |
| `{{SAMPLE_SIZE}}` | Default `300`, or whatever the leader agreed to |
| `{{OUT_OF_SCOPE}}` | Spec `out_of_scope`, plus "turning on Act" and "final thresholds" |

For the fields and anti-patterns the spec must satisfy, see [spec/opportunity-spec.schema.json](../spec/opportunity-spec.schema.json) and `jev-shadow lint`. For a worked example, see [examples/README.md](../examples/README.md).
