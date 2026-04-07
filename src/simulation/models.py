from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


METRIC_KEYS = (
    "energy",
    "mood",
    "stress",
    "health",
    "productivity",
    "project_progress",
    "career_readiness",
    "social_connection",
)

TimePattern = Literal["one_off", "daily", "repeated"]
DurationHint = Literal["short", "medium", "long"]
PrimaryDomain = Literal["career", "health", "social", "study", "general"]
RiskLevel = Literal["low", "medium", "high"]
SemanticLevel = Literal[
    "strong_negative",
    "moderate_negative",
    "mild_negative",
    "neutral",
    "mild_positive",
    "moderate_positive",
    "strong_positive",
]


class ScenarioProfile(BaseModel):
    user_input: str
    action: str
    tags: list[str] = Field(default_factory=list)
    horizon_steps: int = 4
    horizon_labels: list[str] = Field(default_factory=list)
    intensity: str = "medium"
    time_pattern: TimePattern = "one_off"
    duration_hint: DurationHint = "medium"
    primary_domain: PrimaryDomain = "general"
    risk_level: RiskLevel = "medium"


class SemanticTrace(BaseModel):
    summary: str = ""
    semantic_effects: dict[str, SemanticLevel] = Field(default_factory=dict)


class AgentReport(BaseModel):
    agent: str
    step: int
    horizon_label: str
    summary: str
    semantic_effects: dict[str, SemanticLevel] = Field(default_factory=dict)
    resolved_effects: dict[str, float] = Field(default_factory=dict)
    deltas: dict[str, int] = Field(default_factory=dict)
    llm_output: SemanticTrace | None = None
    fallback_output: SemanticTrace | None = None
    merged_output: SemanticTrace | None = None
    llm_error: str | None = None
    llm_used: bool = False
    fallback_used: bool = False
    rationale: str | None = None


class TimelineBeat(BaseModel):
    step: int
    label: str
    reports: list[AgentReport] = Field(default_factory=list)
    world: dict[str, int] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    scenario: ScenarioProfile
    initial_world: dict[str, int]
    final_world: dict[str, int]
    timeline: list[TimelineBeat]
    final_summary: str
    recommendation: str
    raw_state: dict[str, Any] = Field(default_factory=dict)
