# TypeSafe Jev — application map

Knowledge base for discovery and prototyping. Jev is a **decision API** (Choice, Score, Noul), not a chatbot.

**Audience:** anyone running a discovery interview, plus coding agents that recommend a shadow-mode prototype.  
**Grounding rule:** claims below come from TypeSafe docs, cookbooks, the product introduction, or named partner and builder posts. This file does not add benchmarks. Fit scores are qualitative (H/M/L) on four axes, not fabricated KPIs.  
**Last reviewed:** 2026-09-29. Vendor facts drift; re-check against docs.typesafe.ai before quoting.  
**Verified API surface:** [jev-api-reference.md](jev-api-reference.md) (from the `typesafe-sdk` 0.7.2 source).  
**Model facts (vendor-stated):** System One decision model; Choice / Score / Noul; no text generation; ~$0.042/MTok input, output free; ~70–500 ms; RLCD-calibrated probabilities; Choice ≤255 options; Score 2–10 levels; ~32k state window (OpenRouter/Vercel listings).  
**Patterns to listen for:** tool pruning · decision/gen split · shadow routers · mass retag · irreversible gates. Definitions are in the [pattern cheat-sheet](#pattern-cheat-sheet).

Read this map with [anti-patterns](anti-patterns.md) and the [15 discovery probes](discovery-probes.md). Interview instructions: [playbooks/discovery-interview.md](../playbooks/discovery-interview.md).

## Contents

1. [Operating model](#0-operating-model)
2. [Taxonomy](#1-taxonomy-of-application-categories)
3. [Per-app detail cards](#2-per-app-detail-cards)
4. [Fit scoring matrix](#3-fit-scoring-matrix)
5. [Anti-patterns](#4-anti-patterns)
6. [Discovery probes](#5-discovery-probes)
7. [Canonical links](#6-canonical-links)
8. [Pattern cheat-sheet](#pattern-cheat-sheet)

---

## 0. Operating model

Every application in this map uses the same shape.

```
state (text/JSON) + typed questions
        → Jev (parallel evaluate)
        → Choice | Score | Noul + probs [+ confidence]
        → YOUR CODE: threshold · compose · route · act / review / block
```

**HITL default:** confidence / probability bands → Act | Review | Human/Escalate. Thresholds must be calibrated on the customer’s labeled traffic (docs + OpenRouter + Langfuse).

**Three Beam/OpenRouter fit tests (must all be true):** (1) answer set known in advance, (2) same decision repeated at volume, (3) code can act on confidence/probability.

---

## 1. Taxonomy of application categories

Each category lists 3–8 concrete apps grounded in docs, cookbooks, or published builds.

### A. AI harness / agent control plane
*(docs: Harness Engineering, MarkTechPost 20 agentic uses, Pulumi jev-router, Beam)*

1. **Model routing** — pick cheap vs frontier model per turn  
2. **Skill / tool selection** — pick ≤1 skill from a large catalog  
3. **Tool-call risk gating / irreversible gates** — block or confirm destructive tools  
4. **Read-only auto-approval** — auto-approve only high-prob safe actions  
5. **Loop stagnation / “done” verification** — CONTINUE|WARN|REPLAN|HALT; verify “done” claims  
6. **Context / tool-call pruning (compaction)** — drop stale tool results before LLM continues  
7. **Typed function calling** — map NL request → function name + closed-set args  
8. **Trace mining → reusable skills** — which agent runs are worth promoting to skills  

### B. Universal verification & guardrails
*(docs: Universal Verification, llm_guardrails cookbook, citation_check, RAG passages)*

1. **LLM I/O guardrails** — jailbreak, harm, medical, self-harm + severity → pass/review/block/support  
2. **Prompt-injection screening** (esp. RAG candidates)  
3. **Citation / claim support check** — supports | contradicts | says nothing  
4. **Extraction verification** — LLM extracts; Jev verifies field against source (decision/gen split)  
5. **Secret-leak / PII exposure guard**  
6. **Policy / brand / compliance claim check** on marketing or agent output  
7. **Eval-as-judge (Langfuse)** — typed scores on every observation vs sample LLM-judge  

### C. Search, retrieval, ranking
*(docs: Search and retrieval; cookbooks: rerank, classifying_rag_passages, semantic_find, skill_suggestion)*

1. **RAG passage relevance filter** before answering LLM  
2. **Legal / domain rerank** (CLERC cookbook pattern)  
3. **Semantic line/section find** inside long docs  
4. **Candidate shortlist re-check** (skill suggestion two-stage pattern)  
5. **Recommendation / listing quality rank**  
6. **Evidence retrieval for investigations** (which paragraphs matter)  

### D. Map-reduce over big data / mass labeling
*(docs: AI Map Reduce; Zac Gawn bookmark; MindStudio; Autoresearch cookbook)*

1. **Mass retag of historical tickets/emails/calls** when taxonomy changes  
2. **Corpus feature extraction** → classical ML (CatBoost etc.)  
3. **Agent-trace classification** at fleet scale  
4. **Survey / interview / field-note thematic labeling**  
5. **Paper / research screening** (inclusion/exclusion)  
6. **Real-time feed tagging** (X/comments/community posts — MindStudio pattern)  

### E. Customer support & success
*(docs: Customer support; intent-routing pattern; how-to-build triage example)*

1. **Ticket / chat intent + department routing**  
2. **Urgency / frustration / churn-risk scoring**  
3. **Refund / escalation request detection**  
4. **Outbound reply policy verify** before send  
5. **Call-transcript issue / commitment / follow-up tagging**  
6. **VIP / SLA / sensitive-credential phishing triage**  

### F. Sales, marketing, growth
*(docs: Lead generation, Advertising; Leonis YC screener; Zima lead scoring)*

1. **ICP / lead fit scoring + routing**  
2. **Inbound intent / purchase-signal detection**  
3. **Email/Slack corpus → upsell / complaint / missed-follow-up tags**  
4. **Ad creative brand-safety / compliance / LP alignment**  
5. **Landing-page / claim compliance check**  
6. **Content draft multi-dimension scoring** (many Scores on one draft)  

### G. Trust & safety / moderation
*(docs: Moderation and T&S; OpenRouter marketplace moderation tutorial)*

1. **UGC toxicity / harassment / spam moderation**  
2. **Marketplace listing policy + counterfeit / price-signal checks**  
3. **Review abuse / fake-review detection**  
4. **SDR / chatbot conversation policy enforcement**  
5. **Opt-out / sensitive-data exposure detection**  

### H. Risk, fraud, insurance, finance ops
*(docs: Insurance claims, Financial crime, Risk assessment; confidence-routing voice banking)*

1. **FNOL / claims complexity + missing-info triage**  
2. **Fraud / suspicious-narrative scoring** (alerts prioritization)  
3. **KYC / entity match across inconsistent records**  
4. **Transaction narrative risk flags**  
5. **Voice/chat banking intent with stake-based confidence gates**  
6. **Underwriting feature extraction from notes** (semantic signals → model)  

### I. Legal, compliance, contracts
*(docs: Legal and compliance; hierarchical_classification; citation_check)*

1. **Contract clause presence / missing-clause detection**  
2. **Marketing claim vs regulatory prohibition**  
3. **Filing / disclosure classification**  
4. **Hierarchical industry / patent / product taxonomy classification**  
5. **Knowledge-graph entity alignment** (entity_alignment cookbook)  

### J. E-commerce & marketplaces
*(docs: E-commerce marketplaces; OpenRouter moderation tutorial)*

1. **Listing category / attribute normalization**  
2. **Prohibited / counterfeit listing gate**  
3. **Title↔description contradiction checks**  
4. **Review / Q&A moderation**  
5. **Return-reason classification**  

### K. Recruiting & HR
*(docs: Recruiting)*

1. **Resume ↔ job criteria scoring**  
2. **Competency evidence scoring**  
3. **Candidate ↔ role matching / routing**  
4. **Interview-feedback theme tagging**  
5. **Duplicate-candidate detection** (Noul vs DB record pattern in how-to-build)  

### L. Healthcare admin (non-diagnostic)
*(docs use-case map + Leonis hybrid framing; jaggedness: keep clinical decisions human)*

1. **Prior-auth / referral packet completeness**  
2. **Denial-risk / queue priority scoring**  
3. **Document type classification** in RCM  
4. **PHI exposure / policy guard on chatbots**  
5. **Appointment / intake intent routing**  

### M. Scientific / research ops
*(docs: Scientific discovery)*

1. **Systematic-review inclusion screening**  
2. **Passage labeling to themes**  
3. **Claim↔citation support in manuscripts**  
4. **Missing-method detail flags**  
5. **Entity/relation extraction assist for research KGs**  

### N. Gaming / real-time / computer use
*(docs: Gaming, Real-time; Doom demo; Browser Use / mobile / desktop MarkTechPost)*

1. **In-game chat moderation**  
2. **Player-report triage / toxicity**  
3. **Churn / frustration scoring from support chats**  
4. **Browser/desktop/mobile next-action Choice**  
5. **Real-time game-state decisions** (structured state, not vision-first)  

### O. DevEx / semantic linting / CI
*(docs: Semantic code linting; jev-lint; date/value extraction cookbooks)*

1. **Semantic lint vs team conventions in CI / editor**  
2. **PR risk / irreversible-change gate**  
3. **Structure recovery / block classification** (autoformat cookbook)  
4. **Pre-parsed value selection** (regex candidates → Choice)  
5. **SDE cascade verify stage** (mini extract → Jev verify → reasoner)  

### P. Demand / ops forecasting enrichment
*(docs: Demand forecasting)*

1. **Purchase-intent / urgency features from inquiries**  
2. **Competitive-pressure / supply-concern themes from notes**  
3. **Support-ticket demand theme labeling**  
4. **Review → product-interest features**  

---

## 2. Per-app detail cards
Format: **Today → Jev insertion → Questions → HITL → Outcome**. Fit in §3.

**Apps listed in §1 without a card below** (C4–C6, D3–D6, E5–E6, F2, F5–F6, G3–G5, H4, H6, I2–I3, I5, J4–J5, K4–K5, L3–L5, M2–M5, N1–N3, N5, O2–O4, P2–P4) are **list only**. When you recommend one, build its card live from the closest carded sibling, say that you did, and do not attach figures to it.

When you recommend any app, also state **what Jev reads and where it lives** (the state source) — the engineer's first question.

### A1. Model routing
- **Today:** One default frontier model, or manual `/model`, or LLM-as-router (adds latency/cost).  
- **Jev:** Front every user message with Choice(difficulty/tier) + Nouls(sensitive / self-named-tier). Code picks handler (Pulumi jev-router; LangChain ModelRouterMiddleware).  
- **Asks:** Choice: mechanical|routine|complex|deep; Noul: production/credentials risk?; Noul: message claims a model already chosen?  
- **HITL:** Low confidence → escalate tier (never silently downgrade mid-session if cache matters). Shadow-route logs first.  
- **Outcome:** Lower $/session and latency without hand-switching; quality protected by asymmetric thresholds (cheap tiers need higher certainty).

### A2. Skill / tool selection
- **Today:** Stuff all tools into context or let LLM invent tool names.  
- **Jev:** Two-stage: score/rank candidates then Choice(+ Nouls “should suggest any?”) — skill_suggestion cookbook (182 Hermes skills).  
- **Asks:** Score/Choice over shortlist; Noul: is any skill warranted?  
- **HITL:** Low confidence or “none” → no skill / ask user.  
- **Outcome:** Fewer wrong tools; less context bloat; schema-bound tool names (Beam: cannot invent tool).

### A3. Irreversible tool gates
- **Today:** Coarse allowlists or always-ask; or AutoMode that mistakes context.  
- **Jev:** Before bash/write/edit/delete, Nouls: irreversible? off-task? authorized by user intent? (pi-warden pattern).  
- **Asks:** Noul: would this change production/credentials/billing?; Noul: does user intent authorize this exact command?  
- **HITL:** p below gate → require human; never auto on irreversible when uncertain. Code owns side effects.  
- **Outcome:** Separates “db:reset after reset request” from “db:reset after add column.”

### A4. Read-only auto-approval
- **Today:** Approve every tool or blanket YOLO.  
- **Jev:** Auto-approve only when Noul(safe & read-only) ≥ high bar (jev-auto-approve reported p≥0.95; 0/8 state-changing in its calibration — treat as example, not your threshold).  
- **Asks:** Noul: is action read-only and on-task?  
- **HITL:** Anything state-changing → always human or higher gate.  
- **Outcome:** Faster agent loops without silent mutation.

### A5. Loop stagnation / done verification
- **Today:** Agents claim done or spin; humans read traces.  
- **Jev:** Score trajectory progress; Choice CONTINUE|WARN|REPLAN|HALT; Noul: transcript evidences the claimed completion? (ProgressGate, jev-belay).  
- **Asks:** Score: progress vs stuck; Noul: evidence for “done”?  
- **HITL:** HALT/uncertain → human; never trust agent self-report alone for irreversible close.  
- **Outcome:** Fewer runaway loops; auditable stop conditions.

### A6. Context / tool pruning
- **Today:** Summarize with LLM (lossy, slow) or hit context limits.  
- **Jev:** Score each tool result for staleness/relevance; code drops low ones (fast-jev-compaction: ~1M→86K pattern in bookmarks).  
- **Asks:** Score/Noul per tool call: still needed for current goal?  
- **HITL:** Optional review of prune set in shadow; never prune secrets without policy.  
- **Outcome:** Lower LLM cost/latency; keep decision fidelity.

### A7. Typed function calling
- **Today:** LLM emits JSON tools; parse failures / invented args.  
- **Jev:** Choice over function names + closed-set arg Choices; confidence gate (function_calling cookbook).  
- **Asks:** Choice: which function?; Choice/Noul per arg constraint.  
- **HITL:** Low confidence → confirm with user.  
- **Outcome:** Guaranteed-valid call shapes into ordinary typed functions.

### A8. Trace mining for skills
- **Today:** Manual curation of “good runs.”  
- **Jev:** Score traces for reusability / success pattern (Beacon pattern).  
- **Asks:** Score: worth promoting to skill?; Choice: skill category.  
- **HITL:** Human approves promoted skills.  
- **Outcome:** Continuous skill library growth from fleet telemetry.

### B1. LLM I/O guardrails
- **Today:** System-prompt refusals + optional second LLM (jailbreakable, costly).  
- **Jev:** Battery of Nouls (jailbreak, harm, medical, self-harm) + Score severity; code routes pass/review/block/support (llm_guardrails cookbook).  
- **Asks:** As in cookbook batteries (input & output).  
- **HITL:** Review band + crisis → support path; thresholds named policies (strict/permissive).  
- **Outcome:** Product-owned safety line; cheap enough for every turn.

### B2. Prompt-injection screening
- **Today:** Embedding similarity can rank injections high.  
- **Jev:** Noul/Score “is this passage an injection / should be dropped?” (RAG cookbook: planted injection cosine 0.584 first vs Jev 0.99 drop — vendor cookbook numbers).  
- **Asks:** Noul: contains instruction override for the assistant?  
- **HITL:** Mid band → quarantine for review.  
- **Outcome:** Safer RAG without paying frontier per chunk.

### B3. Citation verification
- **Today:** LLM cites; humans spot-check; LLM-judge expensive.  
- **Jev:** Choice supports|contradicts|neither vs source section (citation_check).  
- **Asks:** Choice on claim↔passage.  
- **HITL:** contradicts / low confidence → block publish or human edit.  
- **Outcome:** Grounded answers; fewer hallucinated citations.

### B4. Extraction verification (decision/gen split)
- **Today:** LLM extracts fields; silent wrong values.  
- **Jev:** After extract, Noul: does source support this value?; or Choice among regex candidates (pre_parsed_value_extraction; Beam hybrid).  
- **Asks:** Noul verify; Choice pick span.  
- **HITL:** Uncertain → human key-entry.  
- **Outcome:** Unattended extraction only in high band.

### B5. Secret / PII guard
- **Today:** Regex scanners miss semantic leaks.  
- **Jev:** Noul on masked candidates (jev-secret-guard pattern).  
- **Asks:** Noul: is this a live secret / PII that must not leave?  
- **HITL:** Block on high p; review mid.  
- **Outcome:** Fewer exfil paths in agent logs/tool args.

### B6. Output policy / brand check
- **Today:** Manual brand review or LLM judge sample.  
- **Jev:** Nouls for prohibited claims, tone, competitor misuse; Score brand-fit.  
- **Asks:** Domain-specific Noul battery + Score.  
- **HITL:** Marketing/legal review on mid/high risk.  
- **Outcome:** Scalable pre-publish gate.

### B7. Eval-as-judge (every observation)
- **Today:** Sample LLM-as-judge; sparse coverage.  
- **Jev:** Langfuse decision-model evaluators — Choice/Score/Noul per criterion on all traces.  
- **Asks:** Topic, frustration, out-of-scope, conversation signals, etc.  
- **HITL:** Alert on bad bands; LLM-judge only on flagged sample.  
- **Outcome:** Continuous quality telemetry at decision-model economics.

### C1–C3. RAG filter / rerank / semantic find
- **Today:** Embeddings only; weak precision; full LLM rerank costly.  
- **Jev:** Per candidate Score/Noul relevance; optional Choice line-ids (rerank CLERC: top-1 5%→18%, top-10 38%→62% — cookbook; semantic_find 218 lines).  
- **Asks:** Score: relevance levels; Noul: doc contains answer?  
- **HITL:** Rare — usually automatic filter; audit samples.  
- **Outcome:** Better grounded answers; less context pollution.

### D1. Mass retag
- **Today:** Taxonomy freeze; re-label = prohibitive LLM or human cost.  
- **Jev:** Map-reduce Choice/Score/Noul across corpus (Zac Gawn: 20k items / ~7 min / ~$1.45 — builder report).  
- **Asks:** New tag schema as Choices + Nouls.  
- **HITL:** Spot-check strata; shadow label vs production.  
- **Outcome:** Living taxonomy; hypothesis loops on history.

### D2. Feature extraction → classical ML
- **Today:** Manual NLP features or embeddings only.  
- **Jev:** Autoresearch proposes questions; probabilities become features (autoresearch cookbook).  
- **Asks:** Many Nouls/Scores as features.  
- **HITL:** Scientist reviews feature defs; model owns prediction.  
- **Outcome:** Predictive lift from unstructured text without chatting.

### E1. Support triage & intent routing
- **Today:** Rules + keywords + occasional LLM; misroutes.  
- **Jev:** One call: Choice team/intent, Score frustration/complexity, Nouls refund/spam signals (intent-routing + how-to-build example).  
- **Asks:** As in TypeSafe triage example.  
- **HITL:** confidence < bar → human queue.  
- **Outcome:** Faster TTR; specialist LLM only when needed; deterministic paths for order status etc.

### E2–E3. Urgency / refund / churn
- **Today:** Manual priority; missed refund SLAs.  
- **Jev:** Score urgency/frustration; Noul refund_requested; Noul churn_threat.  
- **Asks:** Ordered rubrics + atomic Nouls.  
- **HITL:** High frustration + uncertain topic → senior queue.  
- **Outcome:** Better prioritization; fewer missed commitments.

### E4. Reply policy verify
- **Today:** Agents send; QA samples later.  
- **Jev:** Before send, Nouls: answers request? citations ok? contradicts policy?  
- **Asks:** Composite of Nouls weighted in code.  
- **HITL:** Fail → rewrite or human.  
- **Outcome:** Safer automation of replies.

### F1. Lead / ICP scoring
- **Today:** Rules + BANT forms; LLM scoring expensive at volume.  
- **Jev:** Score industry fit / maturity / intent; Choice route owner (Leonis: 659 YC cos, 8 criteria, ~7s, ~$0.03 — their report).  
- **Asks:** Multiple Scores + Nouls pain/buyer.  
- **HITL:** Mid band → SDR research; low → drop.  
- **Outcome:** Continuous reprioritization as signals arrive.

### F3. Inbox mass insight tagging
- **Today:** Search keywords; tribal knowledge.  
- **Jev:** Parallel tags (upsell, complaint, missed follow-up, …).  
- **Asks:** Battery of Nouls/Choices.  
- **HITL:** Sales ops validates new tag defs.  
- **Outcome:** Actionable CRM enrichment.

### F4. Ad brand safety
- **Today:** Vendor lists + manual.  
- **Jev:** Choice suitability; Nouls prohibited claims; Score creative quality / LP alignment (Advertising use cases).  
- **Asks:** Per asset battery.  
- **HITL:** Legal review on regulated claims.  
- **Outcome:** Faster creative iteration with compliance gate.

### G1–G2. Moderation / marketplace gates
- **Today:** Keyword filters; human mods; LLM mods costly.  
- **Jev:** Severity Score + policy Nouls; OpenRouter marketplace tutorial pattern (category, price_signal, contradicts_title).  
- **Asks:** Choice allow|warn|review|block via code on probs.  
- **HITL:** Review queue for mid severity.  
- **Outcome:** Nuanced, company-specific moderation at volume.

### H1. Insurance claims triage
- **Today:** Adjuster queue FIFO / crude rules.  
- **Jev:** Choice claim type; Score complexity; Nouls missing info / fraud indicators (Insurance claims map).  
- **Asks:** Atomic claim questions.  
- **HITL:** High risk / low confidence → human adjuster (Leonis hybrid: Jev sorts, LLM reads docs, human on consequential).  
- **Outcome:** Straight-through processing on simple band.

### H2–H3. Financial crime / KYC match
- **Today:** Rules engines + investigators; alert fatigue.  
- **Jev:** Score alert priority; Nouls suspicious traits; entity alignment Scores (Financial crime + entity_alignment).  
- **Asks:** Risk Nouls + match Score.  
- **HITL:** Always human for SAR-level actions; Jev prioritizes.  
- **Outcome:** Better investigator utilization (not autonomous prosecution).

### H5. Voice banking confidence gates
- **Today:** ASR → brittle NLU.  
- **Jev:** Choice intent; stake-based confidence (check_balance @0.6 vs approve_transfer @0.85 — docs example thresholds are illustrative).  
- **Asks:** Choice intents.  
- **HITL:** Below floor → agent; mid transfer → confirm.  
- **Outcome:** Safe automation gradient by consequence.

### I1. Contract missing-clause / compliance
- **Today:** Checklist lawyers; slow.  
- **Jev:** Noul per required clause; Choice risk tier.  
- **Asks:** One Noul per clause requirement.  
- **HITL:** Counsel on high-risk / uncertain.  
- **Outcome:** First-pass review acceleration.

### I4. Hierarchical classification
- **Today:** Flat classifiers struggle with deep taxonomies.  
- **Jev:** Beam search over Choice probs (hierarchical_classification cookbook — patents, retail, biomedical, source code).  
- **Asks:** Choice at each level; confidence may broaden to parent (classification_using_confidence SEC 75 groups).  
- **HITL:** Low confidence → broader bucket + human.  
- **Outcome:** Scalable taxonomy assignment.

### J1–J3. Listing normalize / policy / contradiction
- **Today:** Seller free text chaos.  
- **Jev:** Choice category; Nouls prohibited/counterfeit; Noul title↔desc contradict (OpenRouter tutorial).  
- **Asks:** Mixed battery one call.  
- **HITL:** Review queue for takedowns.  
- **Outcome:** Cleaner catalog; fewer policy incidents.

### K1–K3. Recruiting screen
- **Today:** Keyword ATS; inconsistent human screen.  
- **Jev:** Score competencies vs JD; Choice route; Noul meets must-have.  
- **Asks:** Explicit job-related criteria only.  
- **HITL:** Uncertain → recruiter; keep adverse-action / bias process in human policy (compliance).  
- **Outcome:** Consistent first pass; audit of criteria.

### L1–L2. Healthcare admin completeness / denial risk
- **Today:** Manual packet review.  
- **Jev:** Nouls missing elements; Score denial risk / priority.  
- **Asks:** Checklist Nouls.  
- **HITL:** Clinical decisions never auto; admin routing only.  
- **Outcome:** Fewer preventable denials; faster queues.

### M1. Systematic review screen
- **Today:** Dual human screen.  
- **Jev:** Nouls inclusion/exclusion criteria.  
- **Asks:** One Noul per criterion; compose in code.  
- **HITL:** Dual-screen disagreement band; humans resolve.  
- **Outcome:** Faster title/abstract screen with audit trail.

### N4. Browser / computer-use action Choice
- **Today:** VLM plans slowly; invents actions.  
- **Jev:** Choice operation + element from enumerated DOM/OCR candidates (Browser Use ~7.1s Flights; desktop ~$0.0002/step — MarkTechPost reports).  
- **Asks:** Choice next action; Choice target id.  
- **HITL:** Confirm purchases/logins.  
- **Outcome:** Real-time control loops economically viable.

### O1. Semantic lint
- **Today:** Syntax linters only; style in review.  
- **Jev:** Nouls for convention violations (jev-lint).  
- **Asks:** Per rule Noul.  
- **HITL:** CI warn vs block by severity.  
- **Outcome:** Earlier, consistent convention enforcement.

### O5. SDE cascade verify
- **Today:** Big reasoner on every extraction.  
- **Jev:** Mini extract → Jev verify → reasoner only on fails (sde_cascade cookbook).  
- **Asks:** Per-field Noul/Choice verify.  
- **HITL:** Failed verify → human or reasoner.  
- **Outcome:** Most quality at fraction of frontier cost.

### P1. Demand-signal features
- **Today:** Time-series only.  
- **Jev:** Extract intent/urgency/competitive themes from text → forecast model features.  
- **Asks:** Scores/Nouls as features.  
- **HITL:** Analyst validates feature defs.  
- **Outcome:** Richer forecasts from unstructured ops data.

---

## 3. Fit scoring matrix
Axes: **V** volume · **D** decision-shaped · **R** reversible / safe-to-automate-with-HITL · **L** labeled-data availability (historical outcomes or cheap to label).  
Scale: **H / M / L**. Overall ★ is a rough discovery priority (more H ranks higher). It is not a measured ROI.

| App | V | D | R | L | ★ |
|---|---|---|---|---|---|
| A1 Model routing | H | H | H | M | ★★★★★ |
| A3 Irreversible gates | H | H | M* | M | ★★★★★ |
| A6 Tool pruning | H | H | H | L† | ★★★★☆ |
| A2 Skill/tool select | H | H | H | M | ★★★★☆ |
| B1 I/O guardrails | H | H | M | M | ★★★★★ |
| B2 Injection screen | H | H | H | M | ★★★★☆ |
| B3 Citation check | M | H | H | M | ★★★★☆ |
| B4 Extract verify | H | H | H | M | ★★★★★ |
| B7 Eval-as-judge | H | H | H | M‡ | ★★★★☆ |
| C1–2 RAG filter/rerank | H | H | H | M | ★★★★★ |
| D1 Mass retag | H | H | H | M‡ | ★★★★★ |
| D2 Feature→ML | H | H | H | H | ★★★★☆ |
| E1 Support triage | H | H | H | H | ★★★★★ |
| E4 Reply verify | H | H | M | M | ★★★★☆ |
| F1 Lead scoring | H | H | H | H | ★★★★★ |
| G1–2 Moderation/listings | H | H | M | H | ★★★★★ |
| H1 Claims triage | H | H | M | H | ★★★★☆ |
| H2 Fraud prioritize | H | H | L** | H | ★★★☆☆ |
| H5 Voice banking | M | H | L** | M | ★★★☆☆ |
| I1 Contract clauses | M | H | M | M | ★★★★☆ |
| I4 Hierarchical class | H | H | H | H | ★★★★☆ |
| J marketplace gates | H | H | M | H | ★★★★★ |
| K Recruiting screen | M | H | M | H | ★★★☆☆ |
| L Healthcare admin | H | H | M | H | ★★★★☆ |
| M Research screen | M | H | H | H | ★★★☆☆ |
| N Computer-use actions | H | H | L** | L | ★★★☆☆ |
| O1 Semantic lint | M | H | H | M | ★★★☆☆ |
| O5 SDE cascade | H | H | H | M | ★★★★☆ |
| P Demand features | M | H | H | H | ★★★☆☆ |

\*R=M because mistakes are dangerous — still a strong fit when HITL gates are strict.  
†L=L but still ★★★★☆: pruning quality can be checked indirectly (task success with and without the pruned context) without a hand-labeled set.  
‡L=M, not H: a new taxonomy (D1) or a new eval rubric (B7) usually has **no** labels yet — that is why you are retagging or judging. Budget a stratified hand-labeled sample; that sample becomes the calibration set.  
\*\*R=L means do not fully automate consequential actions; use Jev to prioritize or confirm only.

### Figures cited in the cards

These numbers appear in the detail cards. They are **not** results from this repository, and they are **not** thresholds to copy.

| Figure | Card | How the source is labeled |
|---|---|---|
| ~$0.042/MTok input, output free; ~70–500 ms; Choice ≤255; Score 2–10; ~32k window; RLCD-calibrated probabilities | Header | Vendor-stated (32k window from OpenRouter/Vercel listings) |
| Auto-approve example p≥0.95; 0/8 state-changing in that calibration | A4 | jev-auto-approve report — example, not your threshold |
| Planted injection cosine 0.584 ranked first vs Jev 0.99 drop | B2 | Vendor cookbook numbers |
| CLERC rerank top-1 5%→18%, top-10 38%→62%; semantic_find on 218 lines | C1–C3 | Cookbook |
| Compaction ~1M→86K | A6 | Bookmark pattern (fast-jev-compaction) |
| 20k items / ~7 min / ~$1.45 | D1 | Zac Gawn builder report |
| 659 YC companies, 8 criteria, ~7s, ~$0.03 | F1 | Leonis report |
| Illustrative gates: check balance at 0.6 vs approve transfer at 0.85 | H5 | Docs example thresholds |
| Browser Use ~7.1s on Flights; desktop ~$0.0002/step | N4 | MarkTechPost reports |
| 182 Hermes skills in the two-stage suggestion pattern | A2 | skill_suggestion cookbook |

---

## 4. Anti-patterns

Where not to use Jev. The full list, with what to do instead, is [anti-patterns.md](anti-patterns.md). It is grounded in the jaggedness doc, the Beam rule of thumb, OpenRouter “when to skip,” Leonis, and Langfuse.

Short form, so this map still stands alone:

1. Prose as the primary output (replies, summaries, patches, plans) — use an LLM; Jev may verify.
2. Open-ended answers with no closed label set.
3. Exact arithmetic, counting, or date/time math — code owns that.
4. Multi-hop “System Two” reasoning.
5. Huge noisy state — filter first.
6. Forcing generation through chained Choices.
7. Treating a schema-valid answer as a correct one.
8. Carrying thresholds across primitives (Noul ≠ Choice yes-probability).
9. Autonomous high-consequence acts (wire transfer, clinical diagnosis, SAR filing, safety-critical control).
10. Overlapping Choices with no `other` / `unclear` escape hatch.
11. Images, audio, or video as the only state.
12. Score interpolation treated as a precise continuous meter.
13. Replacing deterministic rules, regex, or database lookups.
14. Treating a shadow-router result as authorization.

---

## 5. Discovery probes

Fifteen questions for a leader, paraphrased one at a time. Full prompts, what to listen for, and which fit axis each probe informs: [discovery-probes.md](discovery-probes.md).

1. Where do humans repeatedly pick from a short fixed menu?
2. What unstructured inflow drives those picks?
3. What happens when that judgment is wrong?
4. Do historical labels or outcomes already exist?
5. Where does an LLM only emit a label or JSON you then parse?
6. Where did a taxonomy freeze because re-labeling history was too expensive?
7. How much of agent/LLM cost is routing, tool choice, or guardrails versus writing?
8. Which tool calls are irreversible, and what is the approval UX?
9. Where do you sample QA because judging every item is too costly?
10. What confidence language do operators already use?
11. Which generative outputs must be grounded before send or publish?
12. Where do embedding or keyword filters fail?
13. If decisions were 50–200× cheaper, what would you run on every record overnight? (a hypothetical probe, not a measured speedup)
14. Who owns policy, and can they change code-side coefficients?
15. Can this start in shadow mode on one workflow?

---

## 6. Canonical links

### Official TypeSafe
- https://docs.typesafe.ai/llms.txt  
- https://docs.typesafe.ai/introduction.md  
- https://docs.typesafe.ai/concepts/use-case-map.md  
- https://docs.typesafe.ai/concepts/system-one.md  
- https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md  
- https://docs.typesafe.ai/primitives.md · choice.md · score.md · noul.md  
- https://docs.typesafe.ai/confidence.md  
- https://docs.typesafe.ai/patterns.md · fan-out.md · confidence-routing.md · composite-scoring.md · intent-routing.md  
- https://docs.typesafe.ai/cookbooks.md (+ guardrails, rerank, citation_check, classifying_rag_passages, skill_suggestion, function_calling, hierarchical_classification, entity_alignment, sde_cascade, autoresearch, consistency_*, semantic_find, …)  
- https://docs.typesafe.ai/model-jaggedness/jev-1.13.md  
- https://typesafe.ai/blog/introducing-system-one-models-and-jev  

### Access / partners
- https://openrouter.ai/blog/insights/what-is-jev/  
- https://openrouter.ai/blog/tutorials/how-to-use-jev/  
- https://vercel.com/kb/guide/typesafe-jev-and-ai-sdk  
- https://vercel.com/changelog/ai-gateway-now-supports-typesafe-clients-and-http-api-for-jev  
- https://langfuse.com/docs/evaluation/evaluation-methods/jev-as-a-judge  
- https://www.pulumi.com/blog/route-every-claude-code-message-to-the-right-model-with-jev/  

### Secondary analyses (use carefully; some numbers are builder/vendor reports)
- https://www.marktechpost.com/2026/09/27/20-agentic-use-cases-of-typesafe-ais-jev/  
- https://beam.ai/agentic-insights/jev-typesafe-ai-agents  
- https://www.leoniscap.com/research/jev-and-the-rise-of-decision-models  
- https://www.mindstudio.ai/blog/jev-use-cases-automation  

### Bookmark-pattern exemplars
- Tool pruning: github.com/tamaratran/fast-jev-compaction (cited in field bookmarks)  
- Shadow routers / irreversible retained by humans: Pulumi jev-router + Codila Grok Bot pattern  
- Mass retag: Zac Gawn corpus tagging reports  
- Decision/gen split: Beam extraction verify; TypeSafe SDE cascade  

---

## Pattern cheat-sheet

| Pattern | Meaning |
|---|---|
| **Decision/gen split** | LLM writes or extracts; Jev decides/verifies |
| **Shadow router** | Log Jev route vs production; no auto act until calibrated |
| **Irreversible gate** | Noul/Choice before mutating tools; human below bar |
| **Tool pruning** | Score tool results; drop before next LLM turn |
| **Mass retag** | Re-run new schema across history cheaply |
| **Speculative fan-out** | Many atomic questions one call; code uses subset |
| **Confidence-gated routing** | Answer = what; confidence = whether to act |
| **Composite scoring** | Weighted sum of Nouls/Scores in code |

Prefer official TypeSafe docs over secondary metrics. Any dollar, latency, or accuracy figure above is vendor-stated, cookbook-reported, or builder-reported, and is labeled as such in the card where it appears. Calibrate every threshold on the customer’s own labeled data. Do not copy another deployment’s probability cutoff.
