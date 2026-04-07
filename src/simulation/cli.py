from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .graph import run_simulation

app = typer.Typer(help="Daily life what-if simulator powered by LangGraph.")
console = Console()


def _render_result(result) -> None:
    console.print(Panel.fit(result.final_summary, title="Outcome"))
    console.print(f"[bold]Input:[/bold] {result.scenario.user_input}")
    console.print(f"[bold]Recommendation:[/bold] {result.recommendation}")
    console.print(
        f"[bold]Control:[/bold] domain={result.scenario.primary_domain}, "
        f"time_pattern={result.scenario.time_pattern}, duration={result.scenario.duration_hint}, "
        f"risk={result.scenario.risk_level}"
    )
    console.print()

    for beat in result.timeline:
        console.print(f"[bold cyan]{beat.label}[/bold cyan]")
        for report in beat.reports:
            debug = f"llm_used={report.llm_used}, fallback_used={report.fallback_used}"
            if report.llm_error:
                debug += f", llm_error={report.llm_error}"
            if report.semantic_effects:
                console.print(f"- [{report.agent}] {report.summary} | effects={report.semantic_effects} | {debug}")
            else:
                console.print(f"- [{report.agent}] {report.summary} | {debug}")
        console.print()

    table = Table(title="World State")
    table.add_column("Metric")
    table.add_column("Initial", justify="right")
    table.add_column("Final", justify="right")
    for key, initial in result.initial_world.items():
        table.add_row(key, str(initial), str(result.final_world[key]))
    console.print(table)


@app.command()
def simulate(
    prompt: str = typer.Argument(..., help="A what-if question, for example: 如果我今晚熬夜做项目会怎样？"),
    json_output: bool = typer.Option(False, "--json", help="Return raw JSON output."),
) -> None:
    result = run_simulation(prompt)
    if json_output:
        console.print_json(json.dumps(result.model_dump(), ensure_ascii=False))
        return
    _render_result(result)


@app.command()
def demo() -> None:
    _render_result(run_simulation("如果我今晚熬夜到3点做项目会怎样？"))


if __name__ == "__main__":
    app()
