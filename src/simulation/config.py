from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str
    base_url: str
    api_key: str
    temperature: float
    timeout_seconds: float
    enable_llm_agents: bool


def get_model_config() -> ModelConfig:
    provider = os.getenv("WHAT_IF_MODEL_PROVIDER", "deepseek").strip() or "deepseek"
    model = os.getenv("WHAT_IF_MODEL_NAME", "deepseek-chat").strip() or "deepseek-chat"
    base_url = os.getenv("WHAT_IF_MODEL_BASE_URL", "https://api.deepseek.com").strip() or "https://api.deepseek.com"
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    temperature = float(os.getenv("WHAT_IF_MODEL_TEMPERATURE", "0.2"))
    timeout_seconds = float(os.getenv("WHAT_IF_MODEL_TIMEOUT_SECONDS", "20"))
    enable_llm_agents = _parse_bool(os.getenv("WHAT_IF_ENABLE_LLM_AGENTS"), bool(api_key))
    return ModelConfig(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
        enable_llm_agents=enable_llm_agents,
    )
