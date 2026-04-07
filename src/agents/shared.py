from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from simulation.effects import semantic_effects_to_deltas
from simulation.llm import get_chat_model
from simulation.models import (
    AgentReport,
    METRIC_KEYS,
    ScenarioProfile,
    SemanticLevel,
    SemanticTrace,
)


AgentRunner = Callable[[ScenarioProfile, dict[str, int], int], AgentReport]


@dataclass(frozen=True)
class AgentSpec:
    name: str
    runner: AgentRunner


class SemanticAgentOutput(BaseModel):
    summary: str = Field(default="")
    semantic_effects: dict[str, SemanticLevel] = Field(default_factory=dict)


class BaseSemanticAgent:
    name = "BaseAgent"
    description = "General semantic impact agent."
    supported_metrics: tuple[str, ...] = METRIC_KEYS

    def build_report(
        self,
        profile: ScenarioProfile,
        step: int,
        summary: str,
        semantic_effects: dict[str, SemanticLevel] | None = None,
        rationale: str | None = None,
        llm_output: SemanticAgentOutput | None = None,
        fallback_output: SemanticAgentOutput | None = None,
        merged_output: SemanticAgentOutput | None = None,
        llm_error: str | None = None,
        llm_used: bool = False,
        fallback_used: bool = False,
    ) -> AgentReport:
        effects = self._sanitize_effects(semantic_effects or {})
        resolved_effects, deltas = semantic_effects_to_deltas(effects, profile.risk_level)
        return AgentReport(
            agent=self.name,
            step=step,
            horizon_label=profile.horizon_labels[step],
            summary=summary,
            semantic_effects=effects,
            resolved_effects=resolved_effects,
            deltas=deltas,
            llm_output=self._to_trace(llm_output),
            fallback_output=self._to_trace(fallback_output),
            merged_output=self._to_trace(merged_output),
            llm_error=llm_error,
            llm_used=llm_used,
            fallback_used=fallback_used,
            rationale=rationale,
        )

    def fallback_judgment(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> SemanticAgentOutput:
        raise NotImplementedError

    def llm_semantic_effects(
        self,
        profile: ScenarioProfile,
        world: dict[str, int],
        step: int,
    ) -> tuple[SemanticAgentOutput | None, str | None]:
        llm = get_chat_model()
        if llm is None:
            return None, None

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are {agent_name}, a specialized agent in a daily-life what-if simulator. "
                    "{agent_description} "
                    "Return only a valid JSON object with exactly two top-level keys: "
                    "\"summary\" and \"semantic_effects\". "
                    "The summary must be concise. "
                    "The semantic_effects value must be an object using only these supported metrics: {supported_metrics}. "
                    "Use only these semantic levels: strong_negative, moderate_negative, mild_negative, neutral, "
                    "mild_positive, moderate_positive, strong_positive. "
                    "Do not invent new metrics. Infer impacts from the scenario itself rather than from parser tags. "
                    "Stay conservative and realistic. "
                    "Write the summary in the same language as the user's input. "
                    "If the input is mostly Chinese, respond in Chinese. "
                    "If the input is mostly English, respond in English. "
                    "Do not restate or paraphrase the user's original action. "
                    "Do not repeat the full scenario. "
                    "Only describe the consequence from this agent's perspective. "
                    "Focus on the current step's new impact, not the whole story. "
                    "Keep the summary to one sentence. "
                    "Do not wrap the JSON in markdown fences.",
                ),
                (
                    "human",
                    "Scenario input: {user_input}\n"
                    "Control fields: action={action}, time_pattern={time_pattern}, duration_hint={duration_hint}, "
                    "primary_domain={primary_domain}, risk_level={risk_level}\n"
                    "Current step: {step_label}\n"
                    "Current world state: {world}\n"
                    "Supported metrics for this agent: {supported_metrics}\n"
                    "Assess the likely semantic impact for this step.",
                ),
            ]
        )
        try:
            message = (prompt | llm).invoke(
                {
                    "agent_name": self.name,
                    "agent_description": self.description,
                    "supported_metrics": ", ".join(self.supported_metrics),
                    "user_input": profile.user_input,
                    "action": profile.action,
                    "time_pattern": profile.time_pattern,
                    "duration_hint": profile.duration_hint,
                    "primary_domain": profile.primary_domain,
                    "risk_level": profile.risk_level,
                    "step_label": profile.horizon_labels[step],
                    "world": world,
                }
            )
        except Exception as exc:
            return None, str(exc)

        raw_text = self._extract_text(message)
        try:
            payload = self._parse_json_payload(raw_text)
        except ValueError as exc:
            return None, str(exc)

        try:
            output = SemanticAgentOutput.model_validate(payload)
        except Exception as exc:
            return None, f"Invalid LLM JSON schema: {exc}"

        sanitized = self._sanitize_effects(output.semantic_effects)
        if not output.summary and not sanitized:
            return None, "LLM returned neither summary nor supported semantic effects."
        return SemanticAgentOutput(summary=output.summary, semantic_effects=sanitized), None

    def merge_semantic_effects(
        self,
        llm_output: SemanticAgentOutput | None,
        fallback_output: SemanticAgentOutput,
    ) -> SemanticAgentOutput:
        if llm_output is None:
            return fallback_output

        merged_effects = dict(self._sanitize_effects(llm_output.semantic_effects))
        for metric, level in self._sanitize_effects(fallback_output.semantic_effects).items():
            merged_effects.setdefault(metric, level)
        summary = llm_output.summary.strip() or fallback_output.summary
        return SemanticAgentOutput(summary=summary, semantic_effects=merged_effects)

    def __call__(self, profile: ScenarioProfile, world: dict[str, int], step: int) -> AgentReport:
        llm_output, llm_error = self.llm_semantic_effects(profile, world, step)
        fallback_output = self.fallback_judgment(profile, world, step)
        merged_output = self.merge_semantic_effects(llm_output, fallback_output)
        llm_used = llm_output is not None
        fallback_used = (not llm_used) or bool(
            set(self._sanitize_effects(fallback_output.semantic_effects)) - set(self._sanitize_effects(merged_output.semantic_effects))
        ) or merged_output.summary == fallback_output.summary
        rationale = (
            "Summary and semantic effects are LLM-first; fallback only fills missing coverage when LLM is absent or incomplete."
        )
        return self.build_report(
            profile=profile,
            step=step,
            summary=merged_output.summary,
            semantic_effects=merged_output.semantic_effects,
            rationale=rationale,
            llm_output=llm_output,
            fallback_output=fallback_output,
            merged_output=merged_output,
            llm_error=llm_error,
            llm_used=llm_used,
            fallback_used=fallback_used,
        )

    def _sanitize_effects(self, semantic_effects: dict[str, SemanticLevel]) -> dict[str, SemanticLevel]:
        return {
            metric: level
            for metric, level in semantic_effects.items()
            if metric in self.supported_metrics
        }

    def _to_trace(self, output: SemanticAgentOutput | None) -> SemanticTrace | None:
        if output is None:
            return None
        return SemanticTrace(summary=output.summary, semantic_effects=output.semantic_effects)

    def _extract_text(self, message) -> str:
        content = getattr(message, "content", "")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)
            return "\n".join(parts).strip()
        return str(content).strip()

    def _parse_json_payload(self, raw_text: str) -> dict:
        text = raw_text.strip()
        if not text:
            raise ValueError("LLM returned empty content.")
        fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if fenced:
            text = fenced.group(1).strip()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise ValueError(f"LLM did not return valid JSON: {raw_text}")
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise ValueError(f"LLM returned unparsable JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError("LLM JSON payload must be an object.")
        return payload
