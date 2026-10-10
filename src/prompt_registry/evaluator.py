from typing import Dict, Any, List
from .storage import PromptStorage


class PromptEvaluator:
    """Promptlarning AI model natijalarini baholash va reytingini hisoblash."""

    def __init__(self, storage: PromptStorage):
        self.storage = storage

    def evaluate(self, prompt_id: int, score: float, output: str = "", latency_ms: float = 0.0, notes: str = ""):
        if not (0.0 <= score <= 5.0):
            raise ValueError("Baholash balli 0 dan 5 gacha bo'lishi kerak")
        self.storage.record_evaluation(prompt_id, score, output, latency_ms, notes)

    def get_metrics(self, prompt_id: int) -> Dict[str, Any]:
        evals = self.storage.get_evaluations(prompt_id)
        if not evals:
            return {"count": 0, "average_score": 0.0, "average_latency_ms": 0.0}

        avg_score = sum(e["score"] for e in evals) / len(evals)
        avg_latency = sum(e["latency_ms"] for e in evals) / len(evals)

        return {
            "count": len(evals),
            "average_score": round(avg_score, 2),
            "average_latency_ms": round(avg_latency, 2),
            "evaluations": evals,
        }
