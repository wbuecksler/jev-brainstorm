---
name: jev-discovery
description: Interview a leader for TypeSafe Jev fit and produce a shadow-mode Claude Code prototype prompt. Use when the user asks where Jev applies, wants a discovery interview, Choice/Score/Noul routing or guardrails, or a paste-ready Jev prototype prompt. Jev is a decision API, not a chatbot.
---

# Jev discovery

Jev (TypeSafe System One) returns Choice, Score, or Noul probabilities. It does not generate text. Do not invent metrics. Attribute vendor and builder figures to their source.

## Read before recommending

1. `docs/application-map.md` (taxonomy, cards, fit matrix, attributed figures)
2. `docs/anti-patterns.md`
3. `docs/discovery-probes.md`
4. `playbooks/discovery-interview.md`
5. `playbooks/claude-code-prototype-template.md` when writing the prompt

## Flow

- Ask one question at a time. Paraphrase the 15 probes. Do not dump a form.
- After about 8–12 substantive answers, or when they say to skip, rank 1–3 apps with axes V/D/R/L (qualitative only). Cite a map card id.
- If the pain is writing prose, say so: generative model drafts, Jev verifies, or Jev is the wrong tool.
- Deliver one fenced prompt filled from the template. Business facts only from the interview; unknown fields stay `not stated`.
- Shadow mode first. Bands are hypotheses to calibrate on their labels. No hardcoded API keys. No real customer records in fixtures.

## Do not

- Claim savings, latency, or accuracy for their business.
- Copy cookbook thresholds into their Act rule.
- Send email or take external actions.
- Treat a schema-valid Choice as proof the decision is correct.
