from __future__ import annotations

from agents.shared import BaseSemanticAgent, SemanticAgentOutput
from simulation.models import AgentReport, ScenarioProfile


class SocialAgent(BaseSemanticAgent):
    name = "SocialAgent"
    description = "Judge social availability, trust, communication momentum, and downstream relationship effects."
    supported_metrics = ("social_connection", "mood")

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        effects: dict[str, str] = {}
        summary = "Social impact looks limited."

        if profile.primary_domain == "social":
            effects = {
                "social_connection": "moderate_positive" if step == 0 else "mild_positive",
                "mood": "mild_positive",
            }
            summary = "The choice likely reduces ambiguity and improves social momentum."
        elif profile.risk_level == "high" and world.get("energy", 100) < 55:
            effects = {"social_connection": "mild_negative"}
            summary = "Low bandwidth and a costly choice often reduce social availability."

        return SemanticAgentOutput(summary=summary, semantic_effects=effects)


SOCIAL_AGENT = SocialAgent()


def social_agent(profile: ScenarioProfile, world: dict[str, int], step: int) -> AgentReport:
    return SOCIAL_AGENT(profile, world, step)
