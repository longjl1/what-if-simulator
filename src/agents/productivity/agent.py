from __future__ import annotations

from agents.shared import BaseSemanticAgent, SemanticAgentOutput
from simulation.models import AgentReport, ScenarioProfile


class ProductivityAgent(BaseSemanticAgent):
    name = "ProductivityAgent"
    description = (
        "Judge execution quality, project throughput, learning output, and whether the choice helps or harms durable progress."
    )
    supported_metrics = ("productivity", "project_progress", "career_readiness")

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        effects: dict[str, str] = {}
        summary = "Productivity impact looks modest."

        if profile.primary_domain in {"career", "study"}:
            effects["productivity"] = "mild_positive"
            summary = "The decision likely creates some immediate output."
        if profile.risk_level == "high" and step > 0:
            effects["productivity"] = "mild_negative"
            summary = "The short-term push may stop compounding once the costs land."
        if profile.primary_domain == "career" and profile.time_pattern in {"daily", "repeated"}:
            effects["project_progress"] = "moderate_positive"
        if profile.primary_domain == "career" and profile.risk_level == "high":
            effects["career_readiness"] = "moderate_negative"

        return SemanticAgentOutput(summary=summary, semantic_effects=effects)


PRODUCTIVITY_AGENT = ProductivityAgent()


def productivity_agent(profile: ScenarioProfile, world: dict[str, int], step: int) -> AgentReport:
    return PRODUCTIVITY_AGENT(profile, world, step)
