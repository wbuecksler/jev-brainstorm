"""Ask Jev the spec's questions about one state.

Uses the official Python SDK (typesafe-sdk): TypeSafeClient.system_one(state, questions).
The key is read by the SDK from TYPESAFE_API_KEY; this module never reads, prints, or stores it.

DryRunEvaluator returns deterministic placeholder answers so the plumbing, bands, and report
can be exercised without a key. Its output is not Jev output and the report says so.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class Evaluation:
    answers: dict[str, dict[str, Any]]
    model: str
    input_tokens: int | None
    latency_ms: float


class Evaluator(Protocol):
    live: bool

    def evaluate(self, state: Any, questions: dict[str, Any]) -> Evaluation: ...

    def close(self) -> None: ...


def _answer_to_dict(answer: Any) -> dict[str, Any]:
    if answer.type == "choice":
        return {"type": "choice", "choice": answer.choice, "confidence": answer.confidence, "probabilities": dict(answer.probabilities)}
    if answer.type == "score":
        return {
            "type": "score",
            "score": answer.score,
            "confidence": answer.confidence,
            "probabilities": {int(k): v for k, v in answer.probabilities.items()},
        }
    return {"type": "noul", "noul": answer.noul}


class JevEvaluator:
    live = True

    def __init__(self, model: str | None = None, **client_options: Any) -> None:
        from typesafe_sdk import TypeSafeClient

        self._model = model
        self._client = TypeSafeClient(model=model, **client_options)

    def evaluate(self, state: Any, questions: dict[str, Any]) -> Evaluation:
        started = time.perf_counter()
        response = self._client.system_one(state=state, questions=questions)
        latency_ms = (time.perf_counter() - started) * 1000
        return Evaluation(
            answers={name: _answer_to_dict(answer) for name, answer in response.answers.items()},
            model=response.model,
            input_tokens=response.usage.input_tokens,
            latency_ms=latency_ms,
        )

    def close(self) -> None:
        self._client.close()


class DryRunEvaluator:
    """Deterministic placeholders keyed on the state and question. Not a model."""

    live = False

    def evaluate(self, state: Any, questions: dict[str, Any]) -> Evaluation:
        answers: dict[str, dict[str, Any]] = {}
        for name, question in questions.items():
            seed = int(hashlib.sha256(f"{state!r}|{name}".encode()).hexdigest(), 16)
            unit = (seed % 10_000) / 10_000
            if question["type"] == "choice":
                labels = list(question["criteria"])
                pick = labels[seed % len(labels)]
                rest = (1 - unit) / max(len(labels) - 1, 1)
                probabilities = {label: (unit if label == pick else rest) for label in labels}
                answers[name] = {"type": "choice", "choice": pick, "confidence": unit, "probabilities": probabilities}
            elif question["type"] == "score":
                levels = len(question["criteria"])
                answers[name] = {
                    "type": "score",
                    "score": round(unit * (levels - 1), 2),
                    "confidence": 1 - unit / 2,
                    "probabilities": {level: 1 / levels for level in range(levels)},
                }
            else:
                answers[name] = {"type": "noul", "noul": unit}
        return Evaluation(answers=answers, model="dry-run (no model called)", input_tokens=None, latency_ms=0.0)

    def close(self) -> None:
        pass
