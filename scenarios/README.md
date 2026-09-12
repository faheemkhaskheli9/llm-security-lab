# Scenario library

**Defensive research use only.** These YAML files are structured test cases for
evaluating whether an LLM application's guardrails resist well-known, publicly
documented prompt-injection and jailbreak patterns. They contain no
operational exploit against any specific system.

- `prompt_injection.yaml` — direct/indirect instruction-injection and
  system-prompt-leak scenarios.
- `jailbreak.yaml` — role-play and instruction-override "jailbreak" scenarios
  (persona swaps, fake unlock modes, fictional framing, multi-turn
  escalation), kept in a separate file so jailbreak robustness can be
  evaluated independently of injection robustness.

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
