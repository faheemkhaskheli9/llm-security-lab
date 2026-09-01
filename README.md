# Prompt Injection / LLM Security Experiments

> Experimental / Smaller Projects portfolio project — independent open-source implementation.
> This is an original, from-scratch build. It is not affiliated with, and does not
> contain any code, prompts, data, or business logic from, any employer or client.

![status](https://img.shields.io/badge/status-in%20progress-yellow)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## 1. Problem

As LLM apps proliferate, understanding and defending against prompt injection and jailbreaks is a practical security skill worth demonstrating responsibly.

> **Defensive-research purpose.** This repository is a testing tool for
> evaluating whether an LLM application's guardrails withstand well-known,
> publicly documented attack patterns. The scenario library in `scenarios/`
> contains no operational exploit against any specific system; every entry
> documents the expected *defended* behavior. Do not use it to attack systems
> you do not own or have permission to test.

## 2. Architecture

```text
Attack Scenario Library -> Target LLM App -> Guardrail Layer -> Pass/Fail Evaluation -> Defensive Report
```

## 3. Technology Stack

- Python
- OpenAI API
- LangChain (guardrails)
- Pytest

## 4. Feature List

- Prompt injection test scenarios
- Jailbreak robustness evaluation
- System-prompt leakage testing
- Indirect prompt injection scenarios
- Guardrail evaluation framework

## 5. Implementation Plan

1. Phase 1: Build a library of known injection/jailbreak scenarios (defensive framing only)
2. Phase 2: Guardrail implementation and evaluation harness
3. Phase 3: Reporting on robustness across scenarios

## 6. Repository Structure

```text
llm-security-lab/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── .env.example
├── docker/
├── docs/
│   ├── architecture.md
│   └── evaluation.md
├── src/
├── tests/
├── configs/
├── scripts/
├── notebooks/
├── examples/
├── assets/
└── .github/
    └── workflows/
```

## 7. Setup

```bash
git clone <this-repo-url>
cd llm-security-lab
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # or: pip install -e .
cp .env.example .env              # fill in API keys / config
```

## 8. Dataset

Document which public dataset(s) or synthetic data generators are used here.
No proprietary, employer-owned, or client-identifiable data is used in this project.

## 9. Training / Execution

Document the commands used to run training, ingestion, or the main pipeline, e.g.:

```bash
# Phase 1: browse the defensive prompt-injection scenario library
python -m src.main list
python -m src.main list --category jailbreak
python -m src.main show ignore-previous-instructions
python -m src.main stats
python -m src.main validate
```

## 10. Evaluation

Document evaluation metrics and how to reproduce them here (see `docs/evaluation.md`).

## 11. Results

_To be filled in as the implementation progresses — screenshots, metrics tables, and
sample outputs go here._

## 12. API

_If this project exposes an API, document the main endpoints here (or link to
auto-generated OpenAPI docs, e.g. `/docs` for FastAPI)._

## 13. Docker

```bash
docker build -t llm-security-lab .
docker run -p 8000:8000 llm-security-lab
```

## 14. Tests

```bash
pytest tests/
```

## 15. Limitations

- This is a from-scratch, independent recreation built for portfolio purposes.
- Performance numbers, once added, are based on public datasets and are not
  representative of any production system's real-world results.

## 16. Future Work

- Expand evaluation coverage and add CI-based regression checks.
- Add more configuration presets and deployment targets.
- Track open items as GitHub Issues.

## 17. Disclosure

This repository is an **independent open-source recreation inspired by the kind of
production systems I have worked on professionally**. It contains no employer or
client source code, prompts, datasets, credentials, architecture diagrams, or
business logic. All code, data, and documentation here are original or built on
publicly available datasets and open-source tools.

---
_Last updated: 2026-08-18_
