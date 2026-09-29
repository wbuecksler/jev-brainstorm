# Worked handoff (fictional)

This walks one fictional interview through every artifact. **Harborline is invented.** Every number is either something the leader said in the example, or it's marked `not stated`. None of them are Jev benchmarks.

## 1. Interview scraps

The leader runs a B2B support desk with "a few hundred tickets a day", Zendesk queues, and a generative-model macro tool that drafts replies. The pain is misroutes to billing: the leader called them "the top complaint from the billing team". A wrong route wastes a specialist's time and is reversible. Closed tickets already record the queue that handled them. Support ops owns the policy. They agreed to shadow mode. They didn't state a cost split, an irreversible action, or an SDK preference.

Track: **operations**. Fit: V H · D H · R H · L H · Value M → card **E1 support triage · confidence-gated routing**.

## 2. Spec and fixtures

Those scraps became [specs/support-triage-example/spec.json](../specs/support-triage-example/spec.json) and eight synthetic [fixtures](../specs/support-triage-example/fixtures.jsonl). What to notice:

- `volume_as_stated` is a quote, not a number.
- The macro tool is acknowledged as the writer. Jev only routes ([anti-pattern 1](../docs/anti-patterns.md)).
- `queue` has an `other` escape hatch, so an unknown topic isn't forced into billing.
- Each Noul asks about one fact. `urgency` is a named four-level rubric.
- `escalate_if` covers a missing message, a possible injection, urgent tickets, and "no queue fits". The `review_if` thresholds are labeled as hypotheses.
- `prompt_injection` exists because ticket text is untrusted input.

Check it:

```bash
pip install -e "sandbox[test]"
jev-shadow lint specs/support-triage-example
jev-shadow run specs/support-triage-example     # dry run without TYPESAFE_API_KEY; live with it
```

## 3. Live run

In GitHub, commit the spec to a private copy of this repo that has the `TYPESAFE_API_KEY` secret. *Actions → Jev shadow run* posts the report table (answers, band, hypothesized band, human label) to the run summary. Eight fixtures are a smoke test. The report says so.

## 4. Brief and engineer prompt

- **Brief:** fill [opportunity-brief-template.md](../playbooks/opportunity-brief-template.md). For Harborline, the cost line reads `Not estimated: item size not stated`, because "a few hundred a day" gives a volume but no ticket length.
- **Engineer prompt:** fill [claude-code-prototype-template.md](../playbooks/claude-code-prototype-template.md). `INFLOW_SOURCE_SYSTEM` = Zendesk, `LABEL_SOURCE` = the queue on closed tickets, `SAMPLE_SIZE` = 300, `HIGH_STAKES_ACTIONS` = `none stated`. Paste the spec in verbatim.

## Fill rules

| Do | Don't |
|---|---|
| Quote volume the way they said it ("a few hundred tickets a day") | Invent "12,400 tickets/week" or a savings figure |
| Write `not stated` when you lack a fact | Smooth the gap with a plausible number |
| Cite a cookbook figure only with its source, and never as their threshold | Copy `0.95` from the auto-approve anecdote into their bands |
| Use synthetic fixtures shaped like their workflow | Paste real tickets, resumes, claims, or secrets into a public repo |
| Keep Act / Review / Escalate as hypotheses | Claim the bands are calibrated |
| Put the key in a repository secret | Paste the key into chat, a prompt, or a file |

## After the engineer's Claude Code run

Check:

- It reuses `sandbox/` rather than rewriting it, and `pytest -q sandbox/tests` still passes.
- The adapter is read-only, and `history.jsonl` / `out/` are not committed.
- It calls Jev only with Choice, Score, and Noul. There are no generation calls.
- The comparison shows per-band agreement and a threshold sweep, and leaves the choice of threshold to the policy owner.

If Claude Code "improves" the design by generating the customer reply inside Jev, reject the change and point it at [docs/anti-patterns.md](../docs/anti-patterns.md).
