
import json
from datetime import datetime, timezone
from pathlib import Path

def _em(s): return {"critical":"🔴","high":"🟠","medium":"🟡","low":"🟢"}.get(s,"⚪")

def generate_markdown(metrics, results, model, scenario_file, defend):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# LLM Red Team Evaluation Report\n\n",
        f"**Generated:** {ts}  \n**Model:** `{model}`  \n**Scenarios:** `{scenario_file}`  \n**Defense stack:** {'enabled' if defend else 'disabled'}\n\n---\n",
        "## Summary\n\n| Metric | Value |\n|---|---|\n",
        f"| Total scenarios | {metrics.total} |\n",
        f"| Attack success rate | **{metrics.attack_success_rate:.1%}** |\n",
        f"| Severity-weighted risk | {metrics.severity_weighted_risk:.1f}/100 |\n",
        f"| Mean latency | {metrics.mean_latency_ms:.0f} ms |\n\n",
    ]
    if metrics.defense_lift is not None:
        lines.append(f"| Defense lift | {metrics.defense_lift:.1%} |\n")
    lines += ["\n## By Category\n\n| Category | Total | ASR |\n|---|---|---|\n"]
    for cat, d in sorted(metrics.per_category.items()):
        lines.append(f"| {cat} | {d['total']} | {d['asr']:.1%} |\n")
    lines += ["\n## By Severity\n\n| Severity | Total | Succeeded |\n|---|---|---|\n"]
    for sev in ["critical","high","medium","low"]:
        if sev in metrics.per_severity:
            d = metrics.per_severity[sev]
            lines.append(f"| {_em(sev)} {sev} | {d['total']} | {d['succeeded']} |\n")
    lines.append("\n## Individual Results\n\n")
    for r in results:
        status = "✘ ATTACK SUCCESS" if r.attack_succeeded else "✔ DEFENDED"
        lines.append(f"### {_em(r.severity)} `{r.scenario_id}` — {r.scenario_name}\n")
        lines.append(f"**Category:** {r.category} | **Severity:** {r.severity} | **Status:** {status}\n\n")
        lines.append(f"**Reasoning:** {r.judge_reasoning}\n\n")
        preview = (r.output[:250].replace(chr(10)," ") if r.output else "(no output)")
        lines.append(f"**Output preview:** `{preview}...`\n\n---\n\n")
    return "".join(lines)

def save_report(metrics, results, model, scenario_file, defend, output_dir="reports"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    payload = {
        "metadata": {"model":model,"scenario_file":scenario_file,"defend":defend,"timestamp":ts},
        "metrics": {"total":metrics.total,"attack_success_rate":metrics.attack_success_rate,
                    "severity_weighted_risk":metrics.severity_weighted_risk,
                    "defense_lift":metrics.defense_lift,"mean_latency_ms":metrics.mean_latency_ms,
                    "per_category":metrics.per_category,"per_severity":metrics.per_severity},
        "results": [{"id":r.scenario_id,"name":r.scenario_name,"category":r.category,
                     "severity":r.severity,"attack_succeeded":r.attack_succeeded,
                     "judge_reasoning":r.judge_reasoning,
                     "output_preview":r.output[:400] if r.output else "","error":r.error} for r in results],
    }
    jp = output_dir / f"run_{ts}.json"
    mp = output_dir / f"run_{ts}.md"
    jp.write_text(json.dumps(payload, indent=2))
    mp.write_text(generate_markdown(metrics, results, model, scenario_file, defend), encoding="utf-8")
    return str(jp), str(mp)
