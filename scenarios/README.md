# Scenario library

**Defensive research use only.** These YAML files are structured test cases for
evaluating whether an LLM application's guardrails resist well-known, publicly
documented prompt-injection and jailbreak patterns. They contain no
operational exploit against any specific system.

Each scenario carries:

| Field | Meaning |
|-------|---------|
| `id` | stable slug (unique across the library) |
| `category` | `prompt-injection` / `jailbreak` / `system-prompt-leak` / `indirect-injection` |
| `attack_input` | the untrusted input handed to the target app under test |
| `expected_safe_behavior` | what a correctly defended system should do |
| `success_signals` | substrings that suggest the attack worked (used by the Phase 2 harness) |
| `references` | public research / advisories the pattern is drawn from |

Load and inspect them:

```bash
python -m src.main list
python -m src.main show ignore-previous-instructions
python -m src.main stats
```
