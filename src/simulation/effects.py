from __future__ import annotations

from .models import METRIC_KEYS, SemanticLevel


SEMANTIC_LEVELS: dict[SemanticLevel, float] = {
    "strong_negative": -0.9,
    "moderate_negative": -0.6,
    "mild_negative": -0.3,
    "neutral": 0.0,
    "mild_positive": 0.3,
    "moderate_positive": 0.6,
    "strong_positive": 0.9,
}

METRIC_CAPS: dict[str, int] = {
    "energy": 10,
    "mood": 8,
    "stress": 10,
    "health": 6,
    "productivity": 8,
    "project_progress": 6,
    "career_readiness": 5,
    "social_connection": 6,
}


def clamp_effect(effect: float) -> float:
    return max(-1.0, min(1.0, effect))


def resolve_semantic_effects(semantic_effects: dict[str, SemanticLevel]) -> dict[str, float]:
    return {metric: clamp_effect(SEMANTIC_LEVELS[level]) for metric, level in semantic_effects.items()}


def effect_to_delta(metric: str, effect: float, risk_level: str = "medium") -> int:
    capped = clamp_effect(effect)
    cap = METRIC_CAPS[metric]
    if risk_level == "low" and metric in {"stress", "health", "energy"}:
        cap = max(2, cap - 1)
    elif risk_level == "high" and metric in {"stress", "health", "energy", "career_readiness"}:
        cap += 1
    return round(capped * cap)


def semantic_effects_to_deltas(
    semantic_effects: dict[str, SemanticLevel],
    risk_level: str = "medium",
) -> tuple[dict[str, float], dict[str, int]]:
    resolved = resolve_semantic_effects(semantic_effects)
    deltas = {metric: effect_to_delta(metric, effect, risk_level) for metric, effect in resolved.items()}
    return resolved, deltas
