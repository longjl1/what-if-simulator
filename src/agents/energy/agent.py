from __future__ import annotations

from agents.shared import BaseSemanticAgent, SemanticAgentOutput
from simulation.models import AgentReport, ScenarioProfile


class EnergyAgent(BaseSemanticAgent):
    name = "EnergyAgent"
    description = (
        "Focus on stamina, sleep recovery, physical resilience, and whether the user's choice drains or restores capacity."
    )
    supported_metrics = ("energy", "health", "stress", "mood")

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        effects: dict[str, str] = {}
        summary = "Energy impact looks limited."

        if profile.primary_domain == "health" and profile.risk_level == "high":
            effects = {
                "energy": "strong_negative" if step <= 1 else "moderate_negative",
                "health": "moderate_negative" if step == 0 else "mild_negative",
                "stress": "mild_positive",
            }
            summary = "This choice likely trades away recovery and makes the next stretch harder to sustain."
        elif profile.primary_domain == "health" and profile.time_pattern == "daily":
            effects = {
                "energy": "mild_positive" if step == 0 else "moderate_positive",
                "health": "moderate_positive",
                "stress": "mild_negative",
            }
            summary = "The choice likely improves baseline energy if repeated consistently."
        elif world.get("energy", 100) < 45:
            effects = {"energy": "mild_negative", "stress": "mild_positive"}
            summary = "With your current state already low, this step likely increases fatigue."

        return SemanticAgentOutput(summary=summary, semantic_effects=effects)


ENERGY_AGENT = EnergyAgent()


def energy_agent(profile: ScenarioProfile, world: dict[str, int], step: int) -> AgentReport:
    return ENERGY_AGENT(profile, world, step)
