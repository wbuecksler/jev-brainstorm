# Sandbox: see Jev run on your workflow

`jev-shadow` takes an [opportunity spec](../spec/opportunity-spec.schema.json) and a handful of fixtures. It asks Jev the spec's questions about each fixture, turns the answers into **Act / Review / Escalate**, and writes a report plus a JSONL log. It is **shadow only**: it calls the Jev API and writes files, and it never sends, changes, or approves anything.

It's built on the official Python SDK, `typesafe-sdk` 0.7.2. The API surface it relies on is documented in [docs/jev-api-reference.md](../docs/jev-api-reference.md), and its tests exercise the real SDK through a mock transport.

## In GitHub (no local setup)

1. Create a **private** repository from this one. Use *Use this template*, or copy it. Keep it private if you'll ever add real examples.
2. *Settings → Secrets and variables → Actions → New repository secret*: name it `TYPESAFE_API_KEY` and paste your key there. The key goes in the secret, never in a chat, a prompt, or a file.
3. Add your spec as `specs/<name>/spec.json` and `specs/<name>/fixtures.jsonl`. The discovery bot produces both. [specs/support-triage-example](../specs/support-triage-example/) shows the shape.
4. Commit. *Actions → Jev shadow run* starts on its own. You can also run it by hand from *Run workflow*. The report appears in the run's summary page, and the logs are attached as an artifact.

With no secret, the workflow runs a **dry run**: placeholder answers, clearly labeled, so you can check the plumbing first.

## Locally

```bash
pip install -e "sandbox[test]"
jev-shadow lint specs/*/                       # anti-pattern checks, no network
cp .env.example .env                           # then paste your key into .env (git-ignored); or export TYPESAFE_API_KEY
jev-shadow run specs/support-triage-example    # writes out/<name>/report.md and shadow.jsonl
pytest -q sandbox/tests                        # offline
```

`jev-shadow run` reads `TYPESAFE_*` values from the nearest `.env` (the current folder or a parent) when they aren't already set in the environment. It never prints them. `--dry-run` forces placeholder answers even when a key is set. `--model` overrides the spec's model.

## What the linter enforces

| Rule | Source |
|---|---|
| Choice has 2–255 options; Score has 2–10 levels | Vendor-stated bounds |
| No question asks Jev to write, summarize, or draft (error) | Anti-pattern 1 |
| `fit.D = L` is rejected: the answer set isn't closed | Anti-pattern 2 |
| Arithmetic or counting wording (warning) | Anti-pattern 3 |
| State near the ~32k window (warning; chars/4 estimate) | Anti-pattern 5 |
| Choice with no `other` / `unclear` / `none` (warning) | Anti-pattern 10 |
| Noul with "and"/"or" (warning: one fact per Noul) | Noul primitive |
| `fit.R = L` requires `high_stakes: true`, which turns Act into Review | Anti-pattern 9 |
| Band conditions use operators that fit the question type | — |

## Reading the report

- **Band vs Expected:** the fixture's `expected_band` is the hypothesis written during discovery. A mismatch means the fixture, the question wording, or the starting threshold needs another look. Don't read it as a score.
- **Agreement with human label:** only meaningful on real, labeled history. For a Noul, agreement is read at 0.5. That's a readout, not a recommended threshold.
- **Cost line:** input tokens reported by the API × the vendor-stated price.
- **Latency line:** measured from the runner, network included.

Eight synthetic fixtures are a smoke test. The real next step is a few hundred labeled historical items, in a private repo. The [Claude Code prompt](../playbooks/claude-code-prototype-template.md) asks an engineer to build exactly that export.

## Using it from a bot

`jev_shadow.api.shadow_run(spec, fixtures)` lints, runs, and returns the Markdown report. It backs the optional `jev_shadow_run` tool in [bot/system-prompt.md](../bot/system-prompt.md). The host keeps the key in its own environment.
