# TypeSafe Jev — research and toolkit

**Jev is a decision API (Choice, Score, Noul), not a chatbot.**

Find where a fast, cheap decision model fits your business, then watch it make that decision on your own examples. It all happens in the AI tool you already use. You don't need to know GitHub.

## Start here

Pick the AI tool you use. You'll be interviewed one question at a time, in that same window, for about five minutes. At the end you get a recommendation, a one-page brief you can forward, and a prompt your engineer can pick up.

### Claude Code or Cursor (can also run Jev live for you)

1. **Claude Code:** open it in any folder. In the desktop app, choose a folder; in a terminal, type `claude`.
   **Cursor:** *File → Open Folder*, pick any empty folder, then open the chat (Cmd/Ctrl + L) in **Agent** mode.
2. Paste this and press Enter:

```text
Set up Jev Discovery for me: clone https://github.com/wbuecksler/jev-brainstorm into a folder called jev-brainstorm (or pull the latest if it's already there), then read jev-brainstorm/bot/system-prompt.md and become Jev Discovery exactly as it describes. Do every technical step yourself and interview me one question at a time.
```

That's it. The AI handles the setup. When it's time to see Jev run, it asks you to paste your TypeSafe API key into a file it creates (`.env`), **not into the chat**. It then runs your examples and shows you the results in the same window.

If you already have this folder open, just type **`/discover`** in Claude Code, or **"start discovery"** in Cursor.

### ChatGPT, Grok, Claude.ai, or Gemini (interview and plan; no live run)

Paste this into a new chat:

```text
Open https://raw.githubusercontent.com/wbuecksler/jev-brainstorm/main/dist/jev-discovery-chat.md, follow the instructions inside it, and start.
```

If it says it can't open links, [download the file](https://github.com/wbuecksler/jev-brainstorm/raw/main/dist/jev-discovery-chat.md), attach it to a new chat, and send **"Start."**

Chat apps can't call Jev themselves. At the end, the AI gives you everything you need, plus a one-line way to see it run in Claude Code or Cursor.

### What each option gets you

| | Interview + recommendation | Brief + engineer prompt | Watch Jev run on your examples |
|---|---|---|---|
| Claude Code / Cursor | ✓ | ✓ | ✓ (with your API key in `.env`) |
| ChatGPT / Grok / Claude.ai / Gemini | ✓ | ✓ | Hand off to Claude Code or Cursor |

**Safe by design:** nothing is sent, changed, or approved in your systems. Jev's answers are logged as recommendations only. Don't paste API keys or customer personal data into any chat.

---

The rest of this page is for people maintaining or extending the toolkit. It's a public knowledge base and field toolkit for [TypeSafe Jev](https://docs.typesafe.ai/introduction.md), a System One decision model. It is not an official TypeSafe product and not a place to store customer data or API keys.

## The flow

```
Discovery interview (bot or person, 5–7 questions, two tracks)
  → Opportunity spec (JSON: questions, bands, business context)  ← linted against the anti-patterns
  → Live shadow run on examples     (in chat, or GitHub Actions in their private sandbox repo)
  → Opportunity Brief (leader)  +  Claude Code prompt (engineer: run it on labeled history)
```

1. **Interview.** Use the bot: [bot/system-prompt.md](bot/system-prompt.md), loaded by [CLAUDE.md](CLAUDE.md) / [AGENTS.md](AGENTS.md) / `/discover` in coding agents, and bundled for chat apps in [dist/jev-discovery-chat.md](dist/jev-discovery-chat.md). Or run it yourself with [playbooks/discovery-interview.md](playbooks/discovery-interview.md) and the [15 probes](docs/discovery-probes.md). The knowledge base behind it is the [application map](docs/application-map.md) and the [anti-patterns](docs/anti-patterns.md).
2. **Spec.** The interview produces an [opportunity spec](spec/opportunity-spec.schema.json) plus synthetic fixtures. [specs/support-triage-example](specs/support-triage-example/) shows the shape.
3. **Watch it run.** [sandbox/](sandbox/README.md) is a shadow-mode harness on the official Python SDK. In Claude Code or Cursor, the agent installs and runs it for you, and the key goes in `.env`. For a team setup, put `TYPESAFE_API_KEY` in a repository secret, commit a spec, and *Actions → Jev shadow run* posts the Act / Review / Escalate report. Without a key, it runs a labeled dry run.
4. **Hand off.** An [Opportunity Brief](playbooks/opportunity-brief-template.md) for the leader's approvers, and a [Claude Code prompt](playbooks/claude-code-prototype-template.md) that has an engineer run the same spec on the team's labeled history.

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
| **Score** | An expected level on an ordered rubric, plus confidence | 2–10 levels |
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

The SDK surface this repo relies on (`typesafe-sdk` 0.7.2: `TypeSafeClient.system_one`, response fields, `POST /v1/systemone`) is written down in [docs/jev-api-reference.md](docs/jev-api-reference.md), verified from the SDK source.

Partner access paths (OpenRouter, Vercel, Langfuse, Pulumi) and secondary write-ups are listed in the [application map](docs/application-map.md#6-canonical-links).

## Ground rules

- **Shadow first.** The prototype logs a recommended band. It does not send, delete, charge, file, diagnose, or mutate production.
- **Calibrate on your data.** Starting bands in a prompt are hypotheses. Do not carry a threshold from one primitive, cookbook, or customer to another.
- **Never put secrets in this repo, or in a chat.** No API keys, customer records, transcripts, or `.env` files. The key lives in the environment or a GitHub Actions secret. Real examples belong in a **private** copy of this repo. `.gitignore` ignores `.env`, `out/`, and `history.jsonl`.
- **Do not invent benchmarks.** If you cite price, speed, or accuracy, name the source and keep the number in that source’s scope.

## Layout

| Path | Role |
|---|---|
| [bot/system-prompt.md](bot/system-prompt.md) | The Jev Discovery bot (adapts to coding agents, chat apps, or a custom host with the `jev_shadow_run` tool) |
| [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md), [.claude/commands/discover.md](.claude/commands/discover.md) | Make Claude Code / Cursor / other agents start the interview when the folder is opened |
| [dist/jev-discovery-chat.md](dist/jev-discovery-chat.md) | One-file bundle for chat apps. Generated by [scripts/build_chat_bundle.py](scripts/build_chat_bundle.py); a test fails if it's stale |
| [.env.example](.env.example) | Where a person pastes their key; the harness reads `.env` |
| [docs/application-map.md](docs/application-map.md) | Categories, app cards, qualitative fit matrix, attributed figures, sources |
| [docs/anti-patterns.md](docs/anti-patterns.md) | Where not to use Jev |
| [docs/discovery-probes.md](docs/discovery-probes.md) | Fifteen interview probes, two tracks, and when to stop |
| [docs/jev-api-reference.md](docs/jev-api-reference.md) | Verified SDK and HTTP surface |
| [playbooks/discovery-interview.md](playbooks/discovery-interview.md) | How to run the interview and what to deliver |
| [playbooks/opportunity-brief-template.md](playbooks/opportunity-brief-template.md) | One-page brief for the leader's approvers |
| [playbooks/claude-code-prototype-template.md](playbooks/claude-code-prototype-template.md) | Engineer prompt: run the spec on labeled history |
| [spec/opportunity-spec.schema.json](spec/opportunity-spec.schema.json) | JSON Schema for the interview's structured output |
| [specs/](specs/) | One directory per spec (`spec.json` + `fixtures.jsonl`); the workflow runs each one |
| [sandbox/](sandbox/README.md) | `jev-shadow`: lint, run, and report. Shadow only. Offline tests. |
| [.github/workflows/jev-shadow.yml](.github/workflows/jev-shadow.yml) | Tests, lint, and a shadow run on every spec change; report in the run summary |
| [examples/README.md](examples/README.md) | A worked handoff with a fictional company |
| [.cursor/skills/jev-discovery/SKILL.md](.cursor/skills/jev-discovery/SKILL.md) | Short skill for coding agents |

## License

No license file is included yet. Ask the repository owner before reuse beyond reading and private experimentation.
