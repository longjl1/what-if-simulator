# What If Simulator

`What If Simulator` is a standalone multi-agent project for simulating the likely consequences of everyday choices.

It uses:

- `LangGraph` for step-by-step orchestration
- `LangChain` agent wrappers around each simulation role
- rule-first semantic effects with optional LLM refinement
- DeepSeek as the default model provider through an OpenAI-compatible endpoint

## Agents

- `ProductivityAgent`
- `EnergyAgent`
- `EmotionAgent`
- `SocialAgent`
- `RiskAgent`
- `FutureSelfAgent`
- `PlannerAgent`

Each agent follows the same pattern:

1. Build a rule-based semantic judgment
2. Optionally call an LLM through LangChain to refine the judgment
3. Merge the result conservatively
4. Map semantic strength into bounded deltas

## Semantic Effects

Agents do not output raw numbers directly.

They produce bounded semantic levels such as:

```json
{
  "energy": "strong_negative",
  "stress": "moderate_positive",
  "productivity": "mild_positive"
}
```

The system then resolves them into:

- normalized semantic strengths in `[-1, 1]`
- per-metric deltas through metric caps

## Scenario Controls

The scenario tagger also emits control fields:

- `time_pattern`
- `duration_hint`
- `primary_domain`
- `risk_level`

These fields are for simulation control, horizon shaping, and output style, not direct scoring.

## Run

```bash
uv sync
uv run what-if-simulator simulate "如果我今晚熬夜到3点做项目会怎样？"
```

Built-in demo:

```bash
uv run what-if-simulator demo
```

## DeepSeek Configuration

The project defaults to DeepSeek when LLM refinement is enabled.

Set:

```dotenv
DEEPSEEK_API_KEY=your_key_here
WHAT_IF_ENABLE_LLM_AGENTS=true
WHAT_IF_MODEL_PROVIDER=deepseek
WHAT_IF_MODEL_NAME=deepseek-chat
WHAT_IF_MODEL_BASE_URL=https://api.deepseek.com/v1
WHAT_IF_MODEL_TEMPERATURE=0.2
```

If `DEEPSEEK_API_KEY` is missing, agents automatically fall back to rule-only mode.

## Project Structure

```text
what-if-simulator/
  src/
    agents/
      agent.py
      shared.py
      productivity/agent.py
      energy/agent.py
      emotion/agent.py
      social/agent.py
      risk/agent.py
      evaluator/agent.py
      planner/agent.py
      sum/agent.py
    simulation/
      cli.py
      config.py
      effects.py
      graph.py
      heuristics.py
      llm.py
      models.py
      scenario_tagger.py
  tests/
```

## Next Steps

- Add a true `llm_semantic_effects` merge policy per agent
- Add branch comparison mode (`A/B/C`)
- Add a small web UI
- Store user baseline traits and long-term simulation history
