from __future__ import annotations

from agents.shared import BaseSemanticAgent, SemanticAgentOutput
from simulation.models import AgentReport, ScenarioProfile


class EmotionAgent(BaseSemanticAgent):
    name = "EmotionAgent"
    description = "Judge mood, regret, motivation, anxiety, and emotional sustainability."
    supported_metrics = ("mood", "stress")

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        effects: dict[str, str] = {}
        summary = "Emotional impact looks moderate."

        if profile.risk_level == "high":
            effects = {
                "mood": "mild_positive" if step == 0 else "moderate_negative",
                "stress": "mild_positive",
            }
            summary = "The choice may feel good at first, then create emotional drag."
        elif profile.primary_domain == "health" and profile.time_pattern == "daily":
            effects = {"mood": "mild_positive", "stress": "mild_negative"}
            summary = "This pattern likely improves emotional steadiness over time."
        elif world.get("stress", 0) > 70:
            effects = {"mood": "mild_negative", "stress": "mild_positive"}
            summary = "Given the current pressure, this step likely adds emotional friction."

        return SemanticAgentOutput(summary=summary, semantic_effects=effects)


EMOTION_AGENT = EmotionAgent()


def emotion_agent(profile: ScenarioProfile, world: dict[str, int], step: int) -> AgentReport:
    return EMOTION_AGENT(profile, world, step)
