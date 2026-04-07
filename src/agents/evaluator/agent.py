from __future__ import annotations

from agents.shared import BaseSemanticAgent, SemanticAgentOutput
from simulation.models import AgentReport, ScenarioProfile


class FutureSelfAgent(BaseSemanticAgent):
    name = "FutureSelfAgent"
    description = "Evaluate the trajectory from the perspective of the user's future self."
    supported_metrics: tuple[str, ...] = ()

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        summary = "Future you prefers consistency over spikes."
        if profile.risk_level == "high":
            summary = "Future you would likely prefer a smaller version of this choice with less downside."
        elif profile.time_pattern == "daily" and profile.primary_domain == "health":
            summary = "Future you likes this because it compounds without creating chaos elsewhere."
        elif profile.primary_domain == "career":
            summary = "Future you would want progress that does not quietly weaken readiness elsewhere."
        return SemanticAgentOutput(summary=summary, semantic_effects={})


FUTURE_SELF_AGENT = FutureSelfAgent()


def future_self_agent(profile: ScenarioProfile, world: dict[str, int], step: int) -> AgentReport:
    return FUTURE_SELF_AGENT(profile, world, step)
