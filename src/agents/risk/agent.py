from __future__ import annotations

from agents.shared import BaseSemanticAgent, SemanticAgentOutput
from simulation.models import AgentReport, ScenarioProfile


class RiskAgent(BaseSemanticAgent):
    name = "RiskAgent"
    description = "Look for delayed downside, fragility, hidden tradeoffs, and consequences the user may discount."
    supported_metrics = ("career_readiness", "stress", "health", "energy")

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        effects: dict[str, str] = {}
        summary = "Risk looks manageable."

        if profile.risk_level == "high":
            effects["stress"] = "moderate_positive"
            summary = "This decision carries delayed downside that will likely surface after the short-term benefit."
        if profile.primary_domain == "career":
            effects["career_readiness"] = "mild_negative" if profile.risk_level == "high" else "neutral"
        if profile.primary_domain == "health":
            effects["health"] = "mild_negative" if profile.risk_level == "high" else "neutral"
        if world.get("energy", 100) < 40:
            effects["energy"] = "mild_negative"

        return SemanticAgentOutput(summary=summary, semantic_effects=effects)


RISK_AGENT = RiskAgent()


def risk_agent(profile: ScenarioProfile, world: dict[str, int], step: int) -> AgentReport:
    return RISK_AGENT(profile, world, step)
