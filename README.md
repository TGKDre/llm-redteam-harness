# LLM Red Team Evaluation Harness

![Language](https://img.shields.io/badge/language-Python-3776AB?style=flat&logo=python&logoColor=white)
![Focus](https://img.shields.io/badge/focus-Adversarial%20LLM%20Evaluation-red?style=flat)
![Providers](https://img.shields.io/badge/providers-OpenAI%20%7C%20Anthropic-blueviolet?style=flat)

A structured, reproducible adversarial evaluation framework for LLM systems. Runs configurable attack scenario libraries against multiple model providers and defense stacks, producing scored reports with per-category breakdowns, defense lift metrics, and severity-weighted risk scores.

Part of the [llm-redteam-portfolio](https://github.com/TGKDre/llm-redteam-portfolio) research series.

---

## Quickstart

```bash
git clone https://github.com/TGKDre/llm-redteam-harness.git
cd llm-redteam-harness
pip install -r requirements.txt

export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Baseline evaluation (no defenses)
python run_eval.py --scenarios scenarios/prompt_injection.yaml --model gpt-4o

# With defense stack enabled
python run_eval.py --scenarios scenarios/prompt_injection.yaml --model gpt-4o --defend

# Run all scenarios against Claude
python run_eval.py --scenarios scenarios/ --model claude-3-5-sonnet-20241022 --provider anthropic --defend
```

---

## Repository Structure

```
llm-redteam-harness/
├── scenarios/          YAML attack scenario library (prompt injection, exfiltration, role confusion)
├── runners/            Model adapters for OpenAI and Anthropic APIs
├── judges/             Output classifier for success/failure detection
├── defenses/           Input sanitizer and output classifier defense stack
├── reports/            Scoring engine with Markdown and JSON output
└── run_eval.py         CLI entrypoint
```

---

## Metrics Produced

| Metric | Description |
|---|---|
| Attack Success Rate (ASR) | Percentage of prompts that produced restricted output |
| Defense Lift | ASR reduction after enabling the defense stack |
| Severity-Weighted Risk Score | Composite score weighted by critical / high / medium / low |
| Per-category ASR | Broken down by attack family (injection, exfiltration, role confusion, etc.) |
| Mean Latency | Average model response time across the evaluation batch |

---

## How It Works

The harness loads attack scenarios from YAML files, routes them through a model adapter (OpenAI or Anthropic), and passes the response to a judge that classifies each output as a success or failure based on threat-class-specific detection logic. When `--defend` is enabled, the defense stack intercepts inputs and outputs before they reach the judge. Results are written to `reports/` as both JSON and Markdown with a timestamp per run.

---

## Related Projects

- [agent-security-sandbox](https://github.com/TGKDre/agent-security-sandbox) — Multi-phase adversarial evaluation of tool-using LLM agents
- [autonomous-injection-agent](https://github.com/TGKDre/autonomous-injection-agent) — Autonomous red-team agent for prompt injection discovery
- [llm-redteam-portfolio](https://github.com/TGKDre/llm-redteam-portfolio) — Full research portfolio index

---

## Author

**Andre Uzoukwu** — IAM & Cybersecurity Engineer / AI Security Researcher

- GitHub: [@TGKDre](https://github.com/TGKDre)
- LinkedIn: [linkedin.com/in/andre-uzoukwu-tgkdre](https://www.linkedin.com/in/andre-uzoukwu-tgkdre/)
- Email: andre.obiuzo@gmail.com
