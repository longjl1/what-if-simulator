from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph

from agents.agent import AGENTS, planner_agent, summarize_simulation
from .heuristics import DEFAULT_WORLD, apply_deltas, metric_snapshot
from .models import AgentReport, ScenarioProfile, SimulationResult, TimelineBeat
from .scenario_tagger import build_scenario_profile


class GraphState(TypedDict, total=False):
    user_input: str
    scenario: ScenarioProfile
    world: dict[str, int]
    initial_world: dict[str, int]
    current_step: int
    reports: dict[str, AgentReport]
    timeline: Annotated[list[TimelineBeat], operator.add]
    final_summary: str
    recommendation: str


def _parse_input(state: GraphState) -> GraphState:
    scenario = build_scenario_profile(state["user_input"])
    initial_world = dict(DEFAULT_WORLD)
    return {
        "scenario": scenario,
        "world": dict(initial_world),
        "initial_world": initial_world,
        "current_step": 0,
        "reports": {},
        "timeline": [],
    }


def _run_agent(agent_name: str, agent_fn):
    def _node(state: GraphState) -> GraphState:
        report = agent_fn(state["scenario"], state["world"], state["current_step"])
        reports = dict(state.get("reports", {}))
        reports[agent_name] = report
        return {"reports": reports}

    return _node


def _planner_node(state: GraphState) -> GraphState:
    planner_report = planner_agent(
        state["scenario"],
        state["world"],
        state["current_step"],
        state["reports"],
    )
    reports = dict(state["reports"])
    reports["planner"] = planner_report
    return {"reports": reports}


def _advance_step(state: GraphState) -> GraphState:
    world = dict(state["world"])
    step = state["current_step"]
    reports = list(state["reports"].values())

    for report in reports:
        world = apply_deltas(world, report.deltas)

    beat = TimelineBeat(
        step=step,
        label=state["scenario"].horizon_labels[step],
        reports=reports,
        world=metric_snapshot(world),
    )

    return {
        "world": world,
        "timeline": [beat],
        "current_step": step + 1,
        "reports": {},
    }


def _should_continue(state: GraphState) -> str:
    return "continue" if state["current_step"] < state["scenario"].horizon_steps else "summarize"


def _summarize(state: GraphState) -> GraphState:
    final_summary, recommendation = summarize_simulation(state["scenario"], state["world"])
    return {"final_summary": final_summary, "recommendation": recommendation}


def build_simulation_graph():
    graph = StateGraph(GraphState)
    graph.add_node("parse_input", _parse_input)

    prev = "parse_input"
    for agent_spec in AGENTS:
        node_name = f"{agent_spec.name}_agent"
        graph.add_node(node_name, _run_agent(agent_spec.name, agent_spec.runner))
        graph.add_edge(prev, node_name)
        prev = node_name

    graph.add_node("planner_agent", _planner_node)
    graph.add_node("advance_step", _advance_step)
    graph.add_node("summarize", _summarize)

    graph.add_edge(prev, "planner_agent")
    graph.add_edge("planner_agent", "advance_step")
    graph.add_conditional_edges(
        "advance_step",
        _should_continue,
        {"continue": "productivity_agent", "summarize": "summarize"},
    )
    graph.add_edge("summarize", END)
    graph.set_entry_point("parse_input")

    return graph.compile()


def run_simulation(user_input: str) -> SimulationResult:
    graph = build_simulation_graph()
    state = graph.invoke({"user_input": user_input})
    return SimulationResult(
        scenario=state["scenario"],
        initial_world=state["initial_world"],
        final_world=state["world"],
        timeline=state["timeline"],
        final_summary=state["final_summary"],
        recommendation=state["recommendation"],
        raw_state=state,
    )
