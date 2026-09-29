# Jev API reference (verified)

What a prototype needs to call Jev, **read from the source of the official Python SDK, `typesafe-sdk` 0.7.2** (PyPI), including its generated OpenAPI models. Nothing here is a guess. It was verified on 2026-09-29. When you upgrade the SDK, re-check this page, and prefer [docs.typesafe.ai](https://docs.typesafe.ai/llms.txt) if the two disagree.

The runnable harness in [`sandbox/`](../sandbox/) uses exactly this surface, and its tests drive the real SDK through a mock transport.

## Install and authenticate

```bash
pip install "typesafe-sdk>=0.7.2,<0.8"
export TYPESAFE_API_KEY=...   # read by the SDK; never hardcode, never commit, never paste into chat
```

| Environment variable | Purpose | Default |
|---|---|---|
| `TYPESAFE_API_KEY` | API key (required) | — |
| `TYPESAFE_DEFAULT_MODEL` | Model name or alias | `jev-latest` |
| `TYPESAFE_BASE_URL` | API root | `https://api.typesafe.ai` |
| `TYPESAFE_LOG_LEVEL` | SDK log level (`debug`, `info`, …) | — |

The SDK redacts secret headers in its logs. It does **not** redact request or response bodies, so don't turn on debug logging over sensitive state.

A TypeScript package, `@typesafe-ai/sdk`, is also published on npm (0.6.0 at the time of writing). It has **not** been verified here. If you use it, check its README before trusting any method names.

## One call

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:  # reads TYPESAFE_API_KEY
    result = client.system_one(
        state={"subject": "Charged twice", "first_message": "Two charges on the March invoice."},
        questions={
            "queue": Choice(
                instructions="Which support queue should handle this ticket first?",
                criteria={"billing": "Charges, refunds, invoices", "product": "Features, bugs", "other": "None fit"},
            ),
            "urgency": Score(
                instructions="How urgent is this for the customer?",
                criteria=["Can wait", "Normal", "High", "Urgent"],  # ordered; position = score from 0
            ),
            "billing_intent": Noul(
                instructions="The customer is asking about a charge on their account.",
                criteria={"true": "Mentions a charge or refund", "false": "Not about money charged"},
            ),
        },
    )

result.choices["queue"].choice          # "billing"
result.choices["queue"].confidence      # 0..1
result.choices["queue"].probabilities   # {"billing": 0.9, "product": 0.07, "other": 0.03}
result.scores["urgency"].score          # expected score, probability-weighted; may fall between levels
result.scores["urgency"].confidence     # 0..1
result.scores["urgency"].probabilities  # {0: ..., 1: ..., 2: ..., 3: ...}  (int keys)
result.nouls["billing_intent"].noul     # probability of yes, 0..1
result.model                            # model that answered (may differ from the alias sent)
result.usage.input_tokens               # billable input tokens
```

Questions can also be plain dicts (`{"type": "choice", "instructions": ..., "criteria": {...}}`). That's the form the [opportunity spec](../spec/opportunity-spec.schema.json) stores, and the harness passes it through unchanged.

`AsyncTypeSafeClient` has the same surface with `await`. `client.models.list()` returns the models your account can use.

## HTTP

```
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFE_API_KEY
Content-Type: application/json

{"state": <text | object | array>, "model": "jev-latest", "questions": {"<name>": <question>, ...}}
```

The response is `{"model": str, "answers": {"<name>": <answer>}, "usage": {"input_tokens": int, "output_tokens": int}}`. Each answer carries `type` plus:

| type | fields |
|---|---|
| `choice` | `choice`, `confidence`, `probabilities` (by label; sums to about 1) |
| `score` | `score` (expected value), `confidence`, `legend`, `probabilities` (by level; sums to about 1) |
| `noul` | `noul` (probability of yes) |

`GET /v1/models` lists the available models.

## Behavior worth knowing

- **Retries.** By default the SDK retries up to 2 times with backoff. Use `RetryPolicy(max_retries=0)` to disable. The default timeout is 10 s per HTTP operation.
- **Errors.** `TypeSafeAuthenticationError`, `TypeSafeRateLimitError`, `TypeSafeBadRequestError`, `TypeSafeAPIConnectionError`, and others, all subclasses of `TypeSafeError`. In the harness, a failed call escalates that item. It never acts.
- **Client-side checks.** The SDK checks that at least one question exists and that no Score has empty criteria. It does **not** enforce the vendor-stated bounds (Choice ≤255 options, Score 2–10 levels) or the ~32k state window. `jev-shadow lint` does.
- **Choice vs Noul probabilities.** A Choice's `probabilities` sum to about 1 across labels. A Noul is a standalone probability. Don't reuse a cutoff from one for the other ([anti-pattern 8](anti-patterns.md)).
- **Score is an expected value.** `score` is a probability-weighted average, not a picked level. For a named level, use the argmax of `probabilities`. Don't treat it as a precise continuous meter ([anti-pattern 12](anti-patterns.md)).
