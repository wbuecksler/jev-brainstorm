# Discovery probes

Fifteen questions for a business leader. They are the spine of the [discovery interview](../playbooks/discovery-interview.md). Ask **one** at a time, in the leader’s language. Do not hand them this page as a form.

Each probe maps to the fit axes in the [application map](application-map.md): **V** volume, **D** decision-shaped (closed answer set), **R** reversible or safe to automate with a human in the loop, **L** labeled data or outcomes you can calibrate on.

Record what they actually said. Do not convert a vague answer into a metric.

**Tracks.** Most leaders are on the **operations** track: lead with probes 1–4, 6, 9, 10, and 13–15. Add probes 5, 7, 8, 11, and 12 (the **AI-platform** track) only when they say they run LLMs or agents in production. Those probes assume vocabulary a COO won't have.

**Value.** Alongside V/D/R/L, listen for **why the workflow matters**, in their words: hours lost, SLA misses, risk exposure, a complaint that keeps coming back. Recommendations rank by Value first among workflows that pass the fit tests. Record it as they said it. Never convert it to dollars.

Probe 13’s “50–200× cheaper” is a **hypothetical prompt** to surface backlog, not a claim that Jev is that multiple for their stack.

## 1. Fixed menus at volume

**Ask:** Where do people repeatedly pick from a short fixed menu — queue, severity, yes/no, tier — hundreds of times a day or more?

**Listen for:** V and D. Named menus, who picks, how often in their words.

**Thin answer:** Ask what the options on the menu actually are. If they cannot list them, it may not be decision-shaped yet.

## 2. Unstructured inflow

**Ask:** What unstructured inflow drives those picks — email, chat, voice, PDFs, tickets, listings, traces?

**Listen for:** The state Jev would see. Text or JSON you already store, not a wish for new instrumentation.

**Thin answer:** Ask for one real example from this week, with the fields a reviewer looks at.

## 3. Consequence if wrong

**Ask:** When that judgment is wrong, is it a reversible annoyance, or money, safety, or legal harm?

**Listen for:** R. This decides shadow-only versus a strict escalate band. High harm does not disqualify Jev; it disqualifies unattended Act.

**Thin answer:** Ask what the operator does in the next ten minutes after a bad call.

## 4. Historical labels or outcomes

**Ask:** Do you already have labels or outcomes — closed tickets with the team that handled them, approved or denied claims, converted leads?

**Listen for:** L. A calibration set you can join to the same state the model will see.

**Thin answer:** Ask whether a person could label a small set of past items without a new taxonomy project.

## 5. LLM-as-a-parser

**Ask:** Which steps today use a generative model only to emit a label or JSON that you then parse?

**Listen for:** A decision/gen split that already exists by accident. Those steps are often the first Jev candidates.

**Thin answer:** Ask what breaks when the JSON is invalid or the label is outside the enum.

## 6. Frozen taxonomy

**Ask:** Where did you freeze a taxonomy because re-labeling history was too expensive?

**Listen for:** Mass-retag fit (map card D1). The new label set must be closed and written down.

**Thin answer:** Ask what the new tags would be, and who is blocked from asking questions of the old corpus.

## 7. Cost that is not writing

**Ask:** Of what you spend on agents or generative models, how much feels like routing, tool choice, or guardrails, versus actually writing?

**Listen for:** Harness and guardrail cards (A and B). Accept qualitative answers (“most of the agent loop is picking tools”). Do not invent a percentage if they do not give one.

**Thin answer:** Ask them to walk one recent session: what was decided, and what was written.

## 8. Irreversible tool calls

**Ask:** Which tool calls are irreversible, and what does approval look like today?

**Listen for:** Irreversible gates (A3). Current UX: always-ask, allowlist, or unattended.

**Thin answer:** Ask for one command or action that should never run on a hunch.

## 9. Sampled QA

**Ask:** Where do you sample quality checks because judging every item is too costly?

**Listen for:** Eval-as-judge, moderation, citation, and reply-verify cards. The rubric they already use in the sample.

**Thin answer:** Ask what “bad” means on the scorecard the reviewer fills in.

## 10. Confidence language they already use

**Ask:** What threshold language do operators already use — “if unsure, escalate,” VIP queues, stake-based confirms?

**Listen for:** Starting bands you can mirror in code. Their words, not a borrowed probability.

**Thin answer:** Ask who is allowed to act alone, and who must get a second look.

## 11. Grounding before send or publish

**Ask:** Which generative outputs must match a policy or a source document before they go out?

**Listen for:** Decision/gen split and citation or policy Nouls (B3, B6, E4). The document that is the source of truth.

**Thin answer:** Ask what a reviewer compares the draft against.

## 12. Filters that fail

**Ask:** Where do embedding or keyword filters fail — injections, nuanced policy, frustration, lookalike listings?

**Listen for:** A closed question the filter cannot express. Examples of false positives and false negatives, in their words.

**Thin answer:** Ask for one item the filter got wrong last month.

## 13. Overnight backlog

**Ask:** If each decision were 50–200× cheaper, what would you run on every record overnight?

**Listen for:** Latent volume (V) and a closed schema they have wanted and not funded. This multiple is a prompt, not a measured Jev speedup.

**Thin answer:** Ask which corpus they stopped reprocessing, and what question they would ask of each row.

## 14. Policy owner

**Ask:** Who owns the policy — thresholds and rubrics — product, risk, or legal? Can that owner change coefficients in code, or only in a document?

**Listen for:** Whether Act/Review/Escalate can live in code they control. A prototype that nobody can retune will stall after shadow mode.

**Thin answer:** Ask who would sign off before any auto-act flag flips.

## 15. Shadow start

**Ask:** Can we log Jev beside the human on one workflow — no automatic action — long enough to compare?

**Listen for:** Permission to start in shadow mode. A willing workflow beats a perfect one that cannot be logged.

**Thin answer:** If they want auto-act immediately, restate consequence (probe 3) and keep the prototype in shadow anyway.

## Coverage check

Before ranking applications, you want a picture of:

- Business model and the workflow in scope
- Volume, in their words
- A closed answer set
- What a wrong call costs
- Labels or outcomes you can calibrate on
- Current tools (rules, generative model, humans)
- Irreversible actions, if any
- Who owns the rubric
- Why it matters (Value), in their words
- Where the input text lives, so an engineer can export it

**Stop when one candidate has V, D, R, L, and Value, plus a known state source and policy owner.** That's usually 5–7 answers, because one good answer often covers several axes. Fewer is fine when they explicitly skip ahead: mark the missing axes instead of filling them in.
