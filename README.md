# LLM Red Team Evaluation Harness

Structured, reproducible adversarial evaluation framework for LLM systems.
Portfolio project targeting the Anthropic AI Security Fellows track.

## Quickstart

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...

# Baseline (no defenses)
python run_eval.py --scenarios scenarios/prompt_injection.yaml --model gpt-4o

# With defense stack enabled
python run_eval.py --scenarios scenarios/prompt_injection.yaml --model gpt-4o --defend

# Run all scenarios against Claude
python run_eval.py --scenarios scenarios/ --model claude-3-5-sonnet-20241022 --provider anthropic --defend
```

## Structure

```
scenarios/          YAML attack scenario library
runners/            Model adapters (OpenAI + Anthropic)
judges/             Output success/failure classifier
defenses/           Input sanitizer + output classifier
reports/            Scoring engine + Markdown/JSON reporter
run_eval.py         CLI entrypoint
```

## Metrics Produced

| Metric | Description |
|---|---|
| Attack Success Rate (ASR) | % of prompts that produced restricted output |
| Defense Lift | ASR reduction after enabling defense stack |
| Severity-Weighted Risk Score | Composite score weighted by critical/high/medium/low |
| Per-category ASR | Broken down by attack family |
| Mean latency | Average model response time across the batch |
