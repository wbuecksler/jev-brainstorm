# TypeSafe Jev — research and toolkit

**Jev is a decision API (Choice, Score, Noul), not a chatbot.**

This repository is a public knowledge base and field toolkit for [TypeSafe Jev](https://docs.typesafe.ai/introduction.md), a System One decision model. Use it to find workflows where a typed decision — not generated prose — can route, score, verify, or gate work, then stand up a shadow-mode prototype.

It is not an official TypeSafe product, not an SDK, and not a place to store customer data or API keys.

## How to use

1. **Read the application map.** Start with [docs/application-map.md](docs/application-map.md). It catalogs where Jev fits, with qualitative fit scores and links to official sources. Read [anti-patterns](docs/anti-patterns.md) before you recommend anything.
2. **Run a discovery interview with a leader.** Follow [playbooks/discovery-interview.md](playbooks/discovery-interview.md) and the [15 probes](docs/discovery-probes.md). One question at a time. The outcome is one to three ranked applications.
3. **Fill the Claude Code template for a shadow-mode prototype.** Copy [playbooks/claude-code-prototype-template.md](playbooks/claude-code-prototype-template.md), fill it only from the interview, and paste it into Claude Code. [examples/README.md](examples/README.md) walks through that handoff, including a fictional filled fragment.

Coding agents in this repo can follow [.cursor/skills/jev-discovery/SKILL.md](.cursor/skills/jev-discovery/SKILL.md).

## What Jev is

Jev answers typed questions about state you already have. Your code decides what to do with the probabilities.

```
state (text/JSON) + typed questions
        → Jev
        → Choice | Score | Noul + probabilities [+ confidence]
        → your code: threshold · compose · route · act / review / block
```

| Primitive | What it returns | Bound (vendor-stated) |
|---|---|---|
| **Choice** | One option from a closed set, with probabilities | ≤255 options |
| **Score** | One level on an ordered rubric | 2–10 levels |
| **Noul** | An atomic yes/no with a calibrated probability | One fact per question |

Jev does not generate text. Replies, summaries, code, and plans stay with a generative model or a person. Jev decides, classifies, scores, or verifies.

**Vendor-stated economics and shape** (TypeSafe; the 32k window is from OpenRouter / Vercel listings). These are not measurements from this repo:

- About **$0.042 per million input tokens**; output free
- About **70–500 ms**
- About a **32k** state window
- Probabilities described as **RLCD-calibrated**

Any other dollar, latency, or accuracy figure in the [application map](docs/application-map.md) is labeled as vendor-stated, cookbook-reported, or builder-reported. It is not a promise for your traffic, and it is not a threshold to copy. A table of those figures sits in the map next to the fit matrix.

Three fit tests should all be true (Beam / OpenRouter framing used in the source notes):

1. The answer set is known in advance.
2. The same decision repeats at volume.
3. Code can act on confidence or probability.

Default human-in-the-loop shape: probability bands become **Act | Review | Escalate**. Start in **shadow mode** (log Jev beside the human or the current system; do not auto-act). Calibrate thresholds on **your** labeled data.

## Canonical TypeSafe docs

Prefer these over secondary posts:

- [llms.txt index](https://docs.typesafe.ai/llms.txt)
- [Introduction](https://docs.typesafe.ai/introduction.md)
- [Use-case map](https://docs.typesafe.ai/concepts/use-case-map.md)
- [System One](https://docs.typesafe.ai/concepts/system-one.md)
- [How to build with System One](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)
- [Primitives](https://docs.typesafe.ai/primitives.md) — [Choice](https://docs.typesafe.ai/choice.md), [Score](https://docs.typesafe.ai/score.md), [Noul](https://docs.typesafe.ai/noul.md)
- [Confidence](https://docs.typesafe.ai/confidence.md)
- [Patterns](https://docs.typesafe.ai/patterns.md)
- [Introducing System One models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [Model jaggedness (Jev 1.13)](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)

Partner access paths (OpenRouter, Vercel, Langfuse, Pulumi) and secondary write-ups are listed in the [application map](docs/application-map.md#6-canonical-links).

## Ground rules

- **Shadow first.** The prototype logs a recommended band. It does not send, delete, charge, file, diagnose, or mutate production.
- **Calibrate on your data.** Starting bands in a prompt are hypotheses. Do not carry a threshold from one primitive, cookbook, or customer to another.
- **Never put secrets in this repo.** No API keys, customer records, transcripts, or `.env` files. A prototype reads `TYPESAFE_API_KEY` from the environment. `.gitignore` ignores `.env`.
- **Do not invent benchmarks.** If you cite price, speed, or accuracy, name the source and keep the number in that source’s scope.

## Layout

| Path | Role |
|---|---|
| [docs/application-map.md](docs/application-map.md) | Categories, app cards, qualitative fit matrix, attributed figures, sources |
| [docs/anti-patterns.md](docs/anti-patterns.md) | Where not to use Jev |
| [docs/discovery-probes.md](docs/discovery-probes.md) | Fifteen interview probes and what to listen for |
| [playbooks/discovery-interview.md](playbooks/discovery-interview.md) | How to run the interview and what to deliver |
| [playbooks/claude-code-prototype-template.md](playbooks/claude-code-prototype-template.md) | Prompt skeleton for a shadow prototype |
| [examples/README.md](examples/README.md) | How to fill the template and paste it into Claude Code |
| [.cursor/skills/jev-discovery/SKILL.md](.cursor/skills/jev-discovery/SKILL.md) | Short skill for coding agents |

## License

No license file is included yet. Ask the repository owner before reuse beyond reading and private experimentation.
