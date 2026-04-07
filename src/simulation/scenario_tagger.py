from __future__ import annotations

from .models import ScenarioProfile


def build_scenario_profile(user_input: str) -> ScenarioProfile:
    text = user_input.strip()
    tags: list[str] = []
    action = "general_decision"
    horizon_steps = 4
    horizon_labels = ["T+0h", "T+1d", "T+3d", "T+1w"]
    intensity = "medium"
    time_pattern = "one_off"
    duration_hint = "medium"
    primary_domain = "general"
    risk_level = "medium"

    if any(keyword in text for keyword in ("熬夜", "通宵", "不睡", "到3点", "overnight", "stay up")):
        tags.extend(["sleep_debt", "project_focus"])
        action = "sleep_sacrifice_for_progress"
        intensity = "high"
        primary_domain = "health"
        risk_level = "high"
        duration_hint = "short"
    if any(keyword in text for keyword in ("健身", "跑步", "运动", "work out", "gym", "run")):
        tags.extend(["fitness", "routine_building"])
        action = "exercise_streak"
        primary_domain = "health"
        risk_level = "low"
    if any(keyword in text for keyword in ("面试", "interview")) and any(
        keyword in text for keyword in ("不准备", "只做项目", "skip", "ignore")
    ):
        tags.extend(["interview_neglect", "project_focus"])
        action = "trade_interview_prep_for_building"
        intensity = "high"
        primary_domain = "career"
        risk_level = "high"
    if any(keyword in text for keyword in ("上课", "class")) and any(
        keyword in text for keyword in ("不去", "skip", "不参加")
    ):
        tags.extend(["skip_class", "project_focus"])
        action = "skip_class_for_building"
        primary_domain = "study"
        risk_level = "medium"
    if any(keyword in text for keyword in ("外卖", "takeout", "junk food")):
        tags.extend(["diet_decline"])
        action = "convenience_eating"
        primary_domain = "health"
        risk_level = "medium"
    if any(keyword in text for keyword in ("发消息", "message", "聚会", "室友", "摊牌", "recruiter")):
        tags.extend(["social_decision"])
        action = "social_decision"
        primary_domain = "social"
    if any(keyword in text for keyword in ("每天", "连续", "一周", "7天", "week")):
        tags.append("habit")
        time_pattern = "daily"
        duration_hint = "long"
        horizon_steps = 5
        horizon_labels = ["T+0h", "T+1d", "T+3d", "T+1w", "T+2w"]
    elif any(keyword in text for keyword in ("一直", "反复", "持续", "repeated")):
        time_pattern = "repeated"
        duration_hint = "long"

    return ScenarioProfile(
        user_input=text,
        action=action,
        tags=sorted(set(tags)),
        horizon_steps=horizon_steps,
        horizon_labels=horizon_labels[:horizon_steps],
        intensity=intensity,
        time_pattern=time_pattern,
        duration_hint=duration_hint,
        primary_domain=primary_domain,
        risk_level=risk_level,
    )
