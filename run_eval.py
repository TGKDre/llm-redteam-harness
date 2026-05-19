
#!/usr/bin/env python3
"""
LLM Red Team Evaluation Harness

Usage:
  python run_eval.py --scenarios scenarios/prompt_injection.yaml --model gpt-4o
  python run_eval.py --scenarios scenarios/ --model gpt-4o --defend
  python run_eval.py --scenarios scenarios/ --model claude-3-5-sonnet-20241022 --provider anthropic
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from utils.logger import console, log_pass, log_fail, log_warn
from utils.config import load_config
from scenarios.loader import load_scenario_file, load_all_scenarios
from runners.base import RunResult
from judges.keyword_judge import judge as kj
from defenses.input_sanitizer import sanitize
from defenses.output_classifier import classify_output
from reports.scoring import compute_metrics
from reports.report_generator import save_report

def get_runner(cfg):
    if cfg.provider == "anthropic":
        from runners.anthropic_runner import AnthropicRunner
        return AnthropicRunner(model=cfg.model, api_key=cfg.anthropic_api_key,
                               temperature=cfg.temperature, max_tokens=cfg.max_tokens)
    from runners.openai_runner import OpenAIRunner
    return OpenAIRunner(model=cfg.model, api_key=cfg.openai_api_key,
                        temperature=cfg.temperature, max_tokens=cfg.max_tokens)

def run_one(scenario, runner, cfg, category):
    messages = scenario.conversation.copy() if scenario.conversation else                [{"role":"user","content":scenario.user_message}]
    system_prompt = scenario.system_prompt
    defense_triggered = False
    if cfg.defend and messages:
        san, triggered, _ = sanitize(messages[-1]["content"])
        if triggered:
            defense_triggered = True
            messages[-1] = {"role":"user","content":san}
    try:
        output, tokens, latency = runner.run(system_prompt, messages)
    except Exception as e:
        return RunResult(scenario_id=scenario.id, scenario_name=scenario.name,
                         category=category, severity=scenario.severity, tags=scenario.tags,
                         model=runner.model, prompt_tokens=0, output="", latency_ms=0.0,
                         error=str(e), defended=cfg.defend)
    if cfg.defend:
        v = classify_output(output)
        if v.blocked:
            defense_triggered = True
            output = f"[OUTPUT BLOCKED: {v.reason}]"
    jv = kj(output, scenario.success_indicators, scenario.failure_indicators)
    return RunResult(scenario_id=scenario.id, scenario_name=scenario.name,
                     category=category, severity=scenario.severity, tags=scenario.tags,
                     model=runner.model, prompt_tokens=tokens, output=output,
                     latency_ms=latency, defended=cfg.defend,
                     defense_triggered=defense_triggered,
                     attack_succeeded=jv.attack_succeeded, judge_reasoning=jv.reasoning)

def print_table(results):
    t = Table(title="Evaluation Results", show_header=True, header_style="bold")
    t.add_column("ID", style="dim", width=8)
    t.add_column("Scenario", max_width=42)
    t.add_column("Severity", justify="center", width=10)
    t.add_column("Result", justify="center", width=18)
    t.add_column("Latency", justify="right", width=10)
    colors = {"critical":"red","high":"orange1","medium":"yellow","low":"green"}
    for r in results:
        res = (Text("⚠ ERROR","yellow") if r.error else
               Text("✘ ATTACK SUCCESS","bold red") if r.attack_succeeded else
               Text("✔ DEFENDED","green"))
        t.add_row(r.scenario_id, r.scenario_name[:42],
                  Text(r.severity.upper(), style=colors.get(r.severity,"white")),
                  res, f"{r.latency_ms:.0f} ms")
    console.print(t)

def main():
    p = argparse.ArgumentParser(description="LLM Red Team Evaluation Harness")
    p.add_argument("--scenarios", required=True, help="Path to YAML file or directory")
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--provider", default="openai", choices=["openai","anthropic"])
    p.add_argument("--defend", action="store_true", help="Enable defense stack")
    p.add_argument("--report", default="reports", help="Output directory for reports")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=1024)
    args = p.parse_args()

    cfg = load_config(model=args.model, provider=args.provider, defend=args.defend,
                      report_dir=args.report, temperature=args.temperature,
                      max_tokens=args.max_tokens)

    sp = Path(args.scenarios)
    if sp.is_dir():
        scenarios, sf_name, category = load_all_scenarios(sp), str(sp), "mixed"
    else:
        sf = load_scenario_file(sp)
        scenarios, sf_name, category = sf.scenarios, sf.name, sf.category

    if not scenarios:
        console.print("[red]No scenarios loaded.[/red]"); sys.exit(1)

    console.print(Panel(
        f"[bold]LLM Red Team Harness[/bold]\n"
        f"Model: [cyan]{cfg.model}[/cyan] ({cfg.provider})\n"
        f"Scenarios: [cyan]{len(scenarios)}[/cyan] loaded\n"
        f"Defense stack: {'[green]enabled[/green]' if cfg.defend else '[dim]disabled[/dim]'}",
        title="Config"))

    runner = get_runner(cfg)
    results = []
    with Progress(SpinnerColumn(), TextColumn("{task.description}"),
                  BarColumn(), TextColumn("{task.percentage:>3.0f}%"),
                  TimeElapsedColumn(), console=console) as prog:
        task = prog.add_task("Running...", total=len(scenarios))
        for s in scenarios:
            prog.update(task, description=f"[dim]{s.id}[/dim] {s.name[:40]}")
            r = run_one(s, runner, cfg, category)
            results.append(r)
            if r.error: log_warn(f"{s.id}: {r.error}")
            elif r.attack_succeeded: log_fail(f"{s.id}: attack succeeded [{s.severity}]")
            else: log_pass(f"{s.id}: defended [{s.severity}]")
            prog.advance(task)

    print_table(results)
    metrics = compute_metrics(results)
    jp, mp = save_report(metrics, results, cfg.model, sf_name, cfg.defend, cfg.report_dir)
    console.print(Panel(
        f"[bold]Batch complete[/bold]\n"
        f"Attack Success Rate: [red]{metrics.attack_success_rate:.1%}[/red]\n"
        f"Severity-Weighted Risk: [yellow]{metrics.severity_weighted_risk:.1f}/100[/yellow]\n"
        f"Mean Latency: {metrics.mean_latency_ms:.0f} ms\n\n"
        f"JSON: {jp}\nMarkdown: {mp}",
        title="Results"))

if __name__ == "__main__":
    main()
