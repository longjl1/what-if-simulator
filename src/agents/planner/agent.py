from __future__ import annotations

from agents.shared import BaseSemanticAgent, SemanticAgentOutput
from simulation.models import AgentReport, ScenarioProfile


class PlannerAgent(BaseSemanticAgent):
    name = "PlannerAgent"
    description = "Convert the current trajectory into a practical next-step recommendation."
    supported_metrics: tuple[str, ...] = ()

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        suggestions = []
        if world.get("energy", 100) < 45:
            suggestions.append("protect sleep")
        if world.get("career_readiness", 100) < 45:
            suggestions.append("recover interview prep")
        if world.get("stress", 0) > 65:
            suggestions.append("reduce load tomorrow")
        if not suggestions:
            suggestions.append("keep the plan small and repeatable")

        return SemanticAgentOutput(
            summary=f"Suggested adjustment: {', '.join(suggestions)}.",
            semantic_effects={},
        )


PLANNER_AGENT = PlannerAgent()


def planner_agent(
    profile: ScenarioProfile,
    world: dict[str, int],
    step: int,
    reports: dict[str, AgentReport] | None = None,
) -> AgentReport:
    return PLANNER_AGENT(profile, world, step)
