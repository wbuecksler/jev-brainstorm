# Filling the Claude Code prompt

This folder shows how to turn a finished discovery interview into a prompt you paste into [Claude Code](https://docs.anthropic.com). It is not a sample integration and it does not call the Jev API.

The company below is **fictional**. Numbers in the example are things that leader said in the example, or they are marked `not stated`. They are not Jev benchmarks.

## Steps

1. Finish the interview in [playbooks/discovery-interview.md](../playbooks/discovery-interview.md), or stop early only if the leader asks to skip. Keep your notes.
2. Copy the fenced skeleton from [playbooks/claude-code-prototype-template.md](../playbooks/claude-code-prototype-template.md).
3. Replace each `{{PLACEHOLDER}}` using the cheat-sheet at the bottom of that file.
4. Read the filled prompt once and delete anything the leader did not say: guessed volumes, guessed savings, borrowed probability cutoffs presented as theirs.
5. Paste the filled prompt into Claude Code as the task.
6. In that prototype’s environment, set `TYPESAFE_API_KEY`. Put it in a local `.env` that `.gitignore` already excludes. Do not paste the key into chat, into the prompt, or into this repository.
7. Run shadow mode on synthetic fixtures. Compare the log to labels later. Do not enable Act in the first prototype.

## Fill rules

| Do | Don’t |
|---|---|
| Quote volume the way they said it (“a few hundred tickets a day”) | Invent “12,400 tickets/week” or a savings figure |
| Write `not stated` when you lack a fact | Smooth the gap with a plausible number |
| Cite a cookbook figure only with its source, and never as their threshold | Copy `0.95` from the auto-approve anecdote into their Act band |
| Use synthetic fixtures shaped like their workflow | Paste real tickets, resumes, claims, or secrets |
| Keep Act / Review / Escalate as hypotheses | Claim the bands are calibrated |

## Worked fragment (fictional)

**Interview scraps used below.** Harborline is invented. The leader said they run a support desk, “a few hundred tickets a day,” Zendesk plus a generative-model macro tool, pain is misroutes to billing, wrong routes waste a specialist’s time (reversible), closed tickets already store the queue that handled them, and policy sits with support ops. They agreed to shadow mode. They did not state a cost split, an irreversible action, or an SDK preference.

Those scraps are enough to fill a prompt. The fragment is the middle of that prompt, not the whole template.

````markdown
## Goal
Shadow-log a queue and urgency decision for incoming Harborline support tickets so support ops can compare Jev with the queue a human actually chose.

## Business context (from the discovery interview — do not invent)
- **Company / product:** Harborline (fictional example) — B2B support desk
- **Leader / function:** Support operations lead
- **Workflow in scope:** First-pass queue routing for new tickets
- **Unstructured inflow:** Zendesk ticket subject + first customer message
- **Volume (as stated):** "a few hundred tickets a day"
- **Current tools / process:** Zendesk queues; a generative-model macro tool drafts replies separately
- **Pain:** Tickets land in billing when they are product questions
- **Consequence if wrong:** Specialist time wasted; reversible reassignment. No refunds or account changes in this workflow.
- **Labeled data / outcomes available:** Closed tickets store the queue that handled them
- **Policy owners:** Support operations
- **Map pattern / app card:** E1 support triage · confidence-gated routing

## Exact question schemas (implement these; do not invent open-ended prompts)
State shape:

```ts
type TicketState = {
  id: string;
  subject: string;
  firstMessage: string;
};
```

Questions (one evaluate call):
- Choice `queue`: billing | product | account | other
- Score `urgency`: low | normal | high | urgent  (ordered)
- Noul `billing_intent`: the customer is asking about an invoice, charge, or payment method
- Noul `account_access`: the customer cannot sign in or is locked out

## HITL thresholds (shadow first)
- Mode default: `shadow` — log only.
- Starting bands (hypotheses — calibrate on closed tickets; not universal):
  - **Act:** queue Choice confidence is high AND the matching intent Noul agrees AND urgency is low or normal
  - **Review:** queue and intent disagree, or confidence is middling, or urgency is high
  - **Escalate / human:** Choice is `other`, required text is missing, or urgency is urgent
- High-stakes actions: none in this workflow (routing only). Still no Act while MODE=shadow.
- A reply draft, if any, stays in the existing macro tool. Jev does not write it.
````

The rest of the template (SDK setup, file tree, success criteria, anti-patterns, eight synthetic fixtures, out of scope) still has to be filled. Fixture text should be invented tickets (“I was charged twice”), not exports from a helpdesk.

### How the fragment stays honest

- Volume stays a quote.
- The generative model is acknowledged as the writer; Jev only routes (anti-pattern 1).
- Bands describe agreement between primitives. They do not reuse a published probability from another project.
- `other` is an escape hatch so an unknown topic is not forced into billing.

## After Claude Code finishes

Check the prototype against the template’s success criteria:

- It refuses to start without `TYPESAFE_API_KEY`.
- It calls Jev only with Choice, Score, and Noul.
- `scripts/run-shadow` writes one log row per fixture.
- Nothing sends, deletes, refunds, or edits production.
- The prototype README tells the team to calibrate on their labeled tickets before any Act flag.

If Claude Code “improves” the design by generating the customer reply inside Jev, reject that change. Point it at [docs/anti-patterns.md](../docs/anti-patterns.md).

## What not to commit back here

This research repo stays free of keys, `.env` files, customer fixtures, and shadow logs from a real deployment. Keep the prototype in its own project.
