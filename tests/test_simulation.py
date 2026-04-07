from simulation.effects import METRIC_CAPS, SEMANTIC_LEVELS, effect_to_delta, semantic_effects_to_deltas
from simulation.config import get_model_config
from simulation.graph import run_simulation
from simulation.scenario_tagger import build_scenario_profile


def test_semantic_effects_are_mapped_into_deltas():
    resolved, deltas = semantic_effects_to_deltas(
        {
            "energy": "strong_negative",
            "stress": "moderate_positive",
            "productivity": "mild_positive",
        }
    )
    assert resolved["energy"] == SEMANTIC_LEVELS["strong_negative"]
    assert deltas["energy"] == round(SEMANTIC_LEVELS["strong_negative"] * METRIC_CAPS["energy"])
    assert deltas["stress"] == round(SEMANTIC_LEVELS["moderate_positive"] * METRIC_CAPS["stress"])


def test_effect_to_delta_clamps_values():
    assert effect_to_delta("energy", -5.0) == -METRIC_CAPS["energy"]
    assert effect_to_delta("health", 5.0) == METRIC_CAPS["health"]


def test_sleep_debt_scenario_reduces_energy():
    result = run_simulation("如果我今晚熬夜到3点做项目会怎样？")
    assert result.final_world["energy"] < result.initial_world["energy"]
    energy_report = next(report for report in result.timeline[0].reports if report.agent == "EnergyAgent")
    assert energy_report.semantic_effects
    assert energy_report.fallback_output is not None
    assert energy_report.merged_output is not None
    assert isinstance(energy_report.llm_used, bool)
    assert isinstance(energy_report.fallback_used, bool)


def test_fitness_scenario_improves_health():
    result = run_simulation("如果我连续一周每天健身会怎样？")
    assert result.final_world["health"] > result.initial_world["health"]


def test_scenario_tagger_extracts_control_fields():
    profile = build_scenario_profile("如果我今晚熬夜到3点做项目会怎样？")
    assert "sleep_debt" in profile.tags
    assert profile.action == "sleep_sacrifice_for_progress"
    assert profile.primary_domain == "health"
    assert profile.risk_level == "high"


def test_default_model_config_targets_deepseek():
    config = get_model_config()
    assert config.provider == "deepseek"
    assert config.model == "deepseek-chat"
    assert "api.deepseek.com" in config.base_url
