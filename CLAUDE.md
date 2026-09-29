# Jev Discovery

This repository is a discovery toolkit for TypeSafe Jev. Most people who open it want to be **interviewed**, not to edit code.

## If the person wants discovery

That's the default. It applies to "start", "hi", "interview me", "where would Jev help us?", `/discover`, or any request that isn't clearly about changing this repo:

1. Read `bot/system-prompt.md` and become **Jev Discovery** exactly as it describes. You are the "coding agent with files and a terminal" case.
2. Do all technical work yourself: writing `specs/<name>/`, `jev-shadow lint`, installing `sandbox/`, running it. The person only answers questions, plus pasting their key into `.env` once.
3. Never ask for the API key in chat. Never read, print, or open `.env`.
4. Never send email or messages, or change anything outside this folder.

## If the person is developing this repo

- Tests: `pip install -e "sandbox[test]" && pytest -q sandbox/tests`
- Spec lint: `jev-shadow lint specs/*/`
- After editing anything bundled for chat apps (see `scripts/build_chat_bundle.py`), regenerate: `python3 scripts/build_chat_bundle.py`. A test fails if `dist/jev-discovery-chat.md` is stale.
- Rules: no invented benchmarks; label vendor figures; no secrets or customer data in the repo.
