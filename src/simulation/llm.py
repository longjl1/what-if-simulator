from __future__ import annotations

from functools import lru_cache

from .config import ModelConfig, get_model_config


@lru_cache(maxsize=1)
def get_chat_model():
    config = get_model_config()
    if not config.enable_llm_agents or not config.api_key:
        return None

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=config.model,
        api_key=config.api_key,
        base_url=config.base_url,
        temperature=config.temperature,
        timeout=config.timeout_seconds,
        max_retries=1,
    )


def llm_is_enabled() -> bool:
    config = get_model_config()
    return config.enable_llm_agents and bool(config.api_key)
