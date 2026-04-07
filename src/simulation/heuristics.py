from __future__ import annotations

from .models import METRIC_KEYS, ScenarioProfile


DEFAULT_WORLD = {
    "energy": 72,
    "mood": 64,
    "stress": 42,
    "health": 68,
    "productivity": 58,
    "project_progress": 35,
    "career_readiness": 55,
    "social_connection": 60,
}


def clamp_metric(value: int) -> int:
    return max(0, min(100, value))


def apply_deltas(world: dict[str, int], deltas: dict[str, int]) -> dict[str, int]:
    updated = dict(world)
    for key, delta in deltas.items():
        updated[key] = clamp_metric(updated.get(key, 50) + delta)
    return updated


def summarize_outcome(profile: ScenarioProfile, world: dict[str, int]) -> tuple[str, str]:
    upside = world["project_progress"] + world["productivity"] + world["mood"]
    downside = world["stress"] + (100 - world["energy"]) + (100 - world["health"])
    balance = upside - downside

    if balance >= 55:
        verdict = "This looks net positive and sustainable."
    elif balance >= 10:
        verdict = "This can work, but only if you keep the decision bounded."
    elif balance >= -20:
        verdict = "Short-term gains exist, but the tradeoff is shaky."
    else:
        verdict = "The long-term cost is likely worse than it feels in the moment."

    recommendation = "Keep the choice, but with guardrails."
    if "sleep_debt" in profile.tags:
        recommendation = "Cap the session, sleep earlier, and continue with a fresh block tomorrow."
    elif "interview_neglect" in profile.tags:
        recommendation = "Protect a daily interview-prep floor so project work does not cannibalize opportunity."
    elif "fitness" in profile.tags:
        recommendation = "Stay consistent rather than intense. The streak matters more than one hard day."

    return verdict, recommendation


def metric_snapshot(world: dict[str, int]) -> dict[str, int]:
    return {key: int(world[key]) for key in METRIC_KEYS if key in world}
