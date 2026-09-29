---
name: jev-discovery
description: Interview a leader for TypeSafe Jev fit, write an opportunity spec, run it in shadow mode with the sandbox harness, and hand off an Opportunity Brief plus a Claude Code prompt. Use when the user asks where Jev applies, wants a discovery interview, Choice/Score/Noul routing or guardrails, a spec or shadow run, or a paste-ready Jev prototype prompt. Jev is a decision API, not a chatbot.
---

# Jev discovery

Jev (TypeSafe System One) returns Choice, Score, or Noul answers with probabilities. It does not generate text. Don't invent metrics. Attribute vendor and builder figures to their source.

## Read before recommending

1. `docs/application-map.md` (taxonomy, cards, fit matrix, attributed figures)
2. `docs/anti-patterns.md`
3. `docs/discovery-probes.md`
4. `docs/jev-api-reference.md` (verified SDK surface; trust it over memory)
5. `playbooks/discovery-interview.md`. The bot version is `bot/system-prompt.md`.

## Flow

- One question at a time. Choose the operations or the AI-platform track by turn two.
- Stop when one candidate has V/D/R/L plus Value, a known state source, and a policy owner (usually 5–7 answers), or when the user says to skip.
- Rank 1–3 apps (H/M/L, cite a map card). "No strong fit" is allowed.
- For #1, write `specs/<name>/spec.json` and `fixtures.jsonl` (shape: `specs/support-triage-example/`). Run `jev-shadow lint specs/<name>`, then `jev-shadow run specs/<name>`. It does a dry run without `TYPESAFE_API_KEY`.
- Then fill `playbooks/opportunity-brief-template.md` and `playbooks/claude-code-prototype-template.md`.
- Shadow mode first. Bands are hypotheses to calibrate on their labels.

## Do not

- Claim savings, latency, or accuracy for their business. Arithmetic on their stated volume × the vendor price is fine if labeled.
- Copy cookbook thresholds into their bands.
- Ask for, accept, or echo an API key in chat. Commit real customer data. Send email or take external actions.
- Treat a schema-valid Choice as proof the decision is correct.
