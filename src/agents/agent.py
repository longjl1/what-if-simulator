from __future__ import annotations

from agents.evaluator.agent import future_self_agent
from agents.planner.agent import planner_agent
from agents.productivity.agent import productivity_agent
from agents.emotion.agent import emotion_agent
from agents.energy.agent import energy_agent
from agents.risk.agent import risk_agent
from agents.shared import AgentSpec
from agents.social.agent import social_agent
from agents.sum.agent import summarize_simulation


AGENTS = [
    AgentSpec(name="productivity", runner=productivity_agent),
    AgentSpec(name="energy", runner=energy_agent),
    AgentSpec(name="emotion", runner=emotion_agent),
    AgentSpec(name="social", runner=social_agent),
    AgentSpec(name="risk", runner=risk_agent),
    AgentSpec(name="future_self", runner=future_self_agent),
]

__all__ = ["AGENTS", "planner_agent", "summarize_simulation"]
