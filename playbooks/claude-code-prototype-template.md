# Claude Code — Jev prototype prompt (template)

After a [discovery interview](discovery-interview.md), fill every `{{PLACEHOLDER}}` from what the leader said and from the [application map](../docs/application-map.md). Emit the completed prompt as **one** fenced markdown block they can paste into Claude Code.

Rules while you fill:

- Business facts come only from the interview. If a field is unknown, write `not stated` — do not guess a volume, a dollar figure, or a latency.
- Vendor-stated Jev facts below stay attributed. Do not add new benchmarks.
- Thresholds are **starting hypotheses** for shadow mode. Say that in the prompt.
- Do not put API keys, customer records, or production dumps in the prompt or in the repo.

The block below is the skeleton. Inner code fences are intentional; keep them inside the outer fence when you paste.

````markdown
# Claude Code task: Stand up a TypeSafe Jev prototype

## Goal
{{GOAL_ONE_SENTENCE}}

Build a **shadow-mode-first** working prototype: Jev evaluates typed questions on real-shaped state; code logs Act, Review, or Escalate; **no irreversible side effects** until thresholds are calibrated on this team's labeled traffic.

## Business context (from the discovery interview — do not invent)
- **Company / product:** {{COMPANY_PRODUCT}}
- **Leader / function:** {{LEADER_FUNCTION}}
- **Workflow in scope:** {{WORKFLOW_NAME_AND_DESCRIPTION}}
- **Unstructured inflow:** {{INFLOW_SOURCES}}
- **Volume (as stated):** {{VOLUME_AS_STATED}}
- **Current tools / process:** {{CURRENT_TOOLS}}
- **Pain:** {{PAIN}}
- **Consequence if wrong:** {{CONSEQUENCE_REVERSIBILITY}}
- **Labeled data / outcomes available:** {{LABELED_DATA}}
- **Policy owners:** {{POLICY_OWNERS}}
- **Map pattern / app card:** {{PATTERN_AND_MAP_CARD}}

## What Jev is (facts — obey these)
- TypeSafe **Jev** is a System One **decision** model. Primitives: **Choice** (at most 255 closed options, vendor-stated), **Score** (2–10 ordered levels), **Noul** (atomic yes/no plus a calibrated probability). **No text generation.**
- Vendor-stated economics: about $0.042 per million input tokens, output free; about 70–500 ms; about a 32k state window (OpenRouter/Vercel listings). These are not measurements of this prototype.
- Operating model: `state (text/JSON) + typed questions → Jev → answers + probabilities [+ confidence] → your code thresholds, routes, logs, and (later) acts`.
- Fit tests (all must hold): answer set known in advance; decision repeats at volume; code can act on confidence or probability.
- Docs to prefer: https://docs.typesafe.ai/llms.txt · primitives · confidence · patterns · how-to-build-with-system-one · relevant cookbooks for {{COOKBOOK_HINTS}}.

## Exact question schemas (implement these; do not invent open-ended prompts)
State shape (TypeScript-ish or JSON):

```ts
{{STATE_TYPE_OR_JSON_SCHEMA}}
```

Questions (one evaluate call; speculative fan-out is fine):

{{QUESTION_SCHEMAS_CHOICE_SCORE_NOUL}}

Escape hatches: include `other`, `unclear`, or `none` on Choices where a forced pick would be wrong. Keep each Noul atomic (one fact). Keep Score rubrics ordered and named.

## HITL thresholds (shadow first)
- Mode default: **`shadow`** — always compute the Jev decision and the recommended band; **log only**; never auto-mutate production, send, delete, or charge.
- Starting bands (illustrative — **calibrate on this team's labeled set**; do not treat as universal):
  - **Act:** {{ACT_BAND_RULE}}
  - **Review:** {{REVIEW_BAND_RULE}}
  - **Escalate / human:** {{ESCALATE_BAND_RULE}}
- Consequence rule: if the action is irreversible or high-stakes ({{HIGH_STAKES_ACTIONS}}), **never Act on uncertainty** — force Review or Escalate.
- Do **not** carry thresholds across primitives (a Noul probability is not a Choice yes-probability; complements need not sum to 1).
- After shadow agreement looks acceptable on a labeled sample, a single feature flag may enable Act for the safest band only. Do not flip that flag in this prototype.

## TypeSafe SDK setup
1. Require env `TYPESAFE_API_KEY` (never hardcode; fail fast with a clear error if missing). Do not commit `.env`.
2. Install the current TypeSafe / Jev client per https://docs.typesafe.ai (or the OpenRouter / Vercel AI Gateway path if the project already uses it — prefer {{SDK_PATH_PREFERENCE}}).
3. One module owns `evaluate(state, questions)` and returns typed results, probabilities, and confidence.
4. One module owns `band(results) → 'act' | 'review' | 'escalate'` using the rules above.
5. One module owns `shadowLog(...)` (JSONL or a structured logger): timestamp, state id, questions, answers, probabilities, band, and an optional human label.
6. No network side effects in v0 except the Jev API and reading fixture files.

## Files to create

```
{{PROJECT_ROOT}}/
  README.md                 # how to run the shadow demo and set TYPESAFE_API_KEY
  package.json or pyproject # dependencies only
  .env.example              # TYPESAFE_API_KEY=
  .gitignore                # ignore .env
  src/
    jev/client.ts|py        # SDK wrapper
    jev/questions.ts|py     # schemas above (single source of truth)
    jev/bands.ts|py         # Act | Review | Escalate
    jev/shadow.ts|py        # JSONL logger
    pipeline.ts|py          # state → evaluate → band → log
  fixtures/
    {{FIXTURE_FILE_NAMES}}  # sample states from the test plan
  scripts/
    run-shadow.ts|py        # CLI: run fixtures and print a table
  tests/
    bands.test.ts|py
    questions.snapshot.*    # schema sanity
```

Language: {{LANGUAGE_PREFERENCE}} (default TypeScript unless the interview said otherwise). Keep modules small and typed.

## Success criteria
- [ ] `TYPESAFE_API_KEY` is required. The demo runs on fixtures with no production writes.
- [ ] Every question is Choice, Score, or Noul — zero generation calls.
- [ ] The shadow log has one row per fixture, with probabilities and a band.
- [ ] At least one fixture lands in each of Act, Review, and Escalate under the starting bands (or the README explains why not, and the rubrics change).
- [ ] Irreversible paths cannot Act while `MODE=shadow`, or when confidence is below the gate.
- [ ] The README says to calibrate on {{LABELED_DATA_SHORT}}, then raise the Act bar only with evidence.
- [ ] The README does not invent business metrics. It describes the mechanism.

## Anti-patterns (refuse these in the implementation)
- Do not use Jev to write replies, summaries, code, or plans. A generative model may draft elsewhere; Jev decides or verifies only.
- Do not put arithmetic, counting, date/time math, or numeric precision into Jev. Code or regex owns that.
- Do not force generation through chained Choices.
- Do not treat a schema-valid answer as a correct one. Calibrate, and keep a Review band.
- Do not auto-Act on high-consequence tools ({{HIGH_STAKES_ACTIONS}}).
- Do not use overlapping, non-exclusive Choice sets without an escape hatch.
- Do not pass huge noisy state. Truncate or filter to what the questions need (vendor-stated window is about 32k).
- Do not use images or audio as the only state (text or JSON only).

## Test plan — sample states
Run `scripts/run-shadow` on these fixtures. Expected bands are **hypotheses** for the starting thresholds, not acceptance targets copied from another deployment.

| ID | Scenario | State gist | Expected band (hypothesis) |
|----|----------|------------|----------------------------|
| {{T1_ID}} | {{T1_SCENARIO}} | {{T1_GIST}} | {{T1_BAND}} |
| {{T2_ID}} | {{T2_SCENARIO}} | {{T2_GIST}} | {{T2_BAND}} |
| {{T3_ID}} | {{T3_SCENARIO}} | {{T3_GIST}} | {{T3_BAND}} |
| {{T4_ID}} | {{T4_SCENARIO}} | {{T4_GIST}} | {{T4_BAND}} |
| {{T5_ID}} | {{T5_SCENARIO}} | {{T5_GIST}} | {{T5_BAND}} |
| {{T6_ID}} | {{T6_SCENARIO}} | {{T6_GIST}} | {{T6_BAND}} |
| {{T7_ID}} | {{T7_SCENARIO}} | {{T7_GIST}} | {{T7_BAND}} |
| {{T8_ID}} | {{T8_SCENARIO}} | {{T8_GIST}} | {{T8_BAND}} |

Include at least: a clear happy-path Act; an ambiguous Review; an adversarial, injection, or policy-fail Escalate; a missing-fields Escalate; an irreversible-tool attempt that must not Act in shadow.

Use synthetic fixtures. Do not paste real customer records, secrets, or production identifiers.

## Implementation order
1. Scaffold the layout, `.env.example`, `.gitignore`, and README.
2. Implement question schemas and the client wrapper.
3. Implement bands and the shadow logger.
4. Add fixtures from the table. Run the shadow CLI. Paste one sample JSONL line into the README (redacted).
5. Stop. Do not wire production side effects. Document the feature-flag path for a later Act enablement.

## Out of scope for this prototype
{{OUT_OF_SCOPE}}
````

## Placeholder cheat-sheet

| Placeholder | Fill from |
|---|---|
| `{{GOAL_ONE_SENTENCE}}` | The #1 recommendation, as an outcome |
| `{{COMPANY_PRODUCT}}` through `{{POLICY_OWNERS}}` | The interview only. Unknown → `not stated` |
| `{{VOLUME_AS_STATED}}` | Their words, or `not stated`. Never a number you estimated |
| `{{PATTERN_AND_MAP_CARD}}` | Pattern name plus card id from the map (example: `E1 support triage · confidence-gated routing`) |
| `{{COOKBOOK_HINTS}}` | Closest cookbooks named in the map’s link list |
| `{{STATE_TYPE_OR_JSON_SCHEMA}}` | The smallest state this workflow needs |
| `{{QUESTION_SCHEMAS_CHOICE_SCORE_NOUL}}` | Concrete Choice, Score, and Noul questions |
| `{{ACT_BAND_RULE}}` and the other bands | Starting rules. Insist on calibration |
| `{{HIGH_STAKES_ACTIONS}}` | From the irreversibility probe. `none stated` if they named none |
| `{{SDK_PATH_PREFERENCE}}` | TypeSafe direct, OpenRouter, or Vercel — whichever they already use; otherwise TypeSafe direct |
| `{{PROJECT_ROOT}}`, `{{LANGUAGE_PREFERENCE}}` | Sensible defaults (`jev-shadow-prototype`, TypeScript) |
| `{{FIXTURE_FILE_NAMES}}` | One file per test-plan row |
| `{{T1_*}}` … `{{T8_*}}` | Synthetic fixtures grounded in their domain |
| `{{LABELED_DATA_SHORT}}` | The calibration set they said they have, or “a labeled sample you still need to pull” |
| `{{OUT_OF_SCOPE}}` | Generation, production wiring, and “final” thresholds |

Worked fill, with a fictional company marked as an example: [examples/README.md](../examples/README.md).
