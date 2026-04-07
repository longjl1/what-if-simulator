from __future__ import annotations

from simulation.heuristics import summarize_outcome
from simulation.models import ScenarioProfile


def summarize_simulation(profile: ScenarioProfile, world: dict[str, int]) -> tuple[str, str]:
    return summarize_outcome(profile, world)
