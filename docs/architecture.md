# Architecture Notes: Prompt Injection / LLM Security Experiments

## Pipeline

```text
Attack Scenario Library -> Target LLM App -> Guardrail Layer -> Pass/Fail Evaluation -> Defensive Report
```

## Components

- Prompt injection test scenarios
- Jailbreak robustness evaluation
- System-prompt leakage testing
- Indirect prompt injection scenarios
- Guardrail evaluation framework

## Design Notes

- Keep provider/model choices swappable behind interfaces (see `multi-llm-router`
  and similar projects in this portfolio for the general pattern).
- Prefer configuration-driven pipelines (YAML/JSON in `configs/`) over hardcoded
  parameters so experiments are reproducible.
