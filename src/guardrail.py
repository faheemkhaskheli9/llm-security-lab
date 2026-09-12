"""Configurable guardrail (input/output filtering) layer (issue #4).

Sits in front of a target LLM call so the Phase 1 scenario library can be
run both with and without this defensive layer to measure its effect
(Phase 2 evaluation harness, issue #5).

Rule-based and fully offline -- no paid API call, matching this repo's
CPU-only/no-budget constraint. The README's Tech Stack lists LangChain as a
possible guardrail backend for a future, LLM-backed classifier guardrail;
that is a documented extension point, not required for the pattern-matching
defense this issue's acceptance criteria ask for (block/flag known injection
phrasing, toggle on/off, unit-testable blocked vs. passed-through cases).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class GuardrailAction(str, Enum):
    BLOCK = "block"
    FLAG = "flag"


@dataclass(frozen=True)
class GuardrailRule:
    name: str
    pattern: re.Pattern
    action: GuardrailAction = GuardrailAction.BLOCK

    @classmethod
    def keyword(
        cls,
        name: str,
        phrases: Iterable[str],
        *,
        action: GuardrailAction = GuardrailAction.BLOCK,
    ) -> "GuardrailRule":
        alternation = "|".join(re.escape(p) for p in phrases)
        return cls(name=name, pattern=re.compile(alternation, re.IGNORECASE), action=action)


# Canonical, publicly documented injection/jailbreak phrasing -- generic
# patterns, not an operational exploit against any specific system (same
# defensive framing as src/scenarios.py).
DEFAULT_RULES: tuple[GuardrailRule, ...] = (
    GuardrailRule.keyword(
        "ignore-instructions",
        [
            "ignore previous instructions",
            "ignore all previous instructions",
            "ignore the above",
            "disregard the above",
            "disregard previous instructions",
        ],
    ),
    GuardrailRule.keyword(
        "reveal-system-prompt",
        [
            "reveal your system prompt",
            "print your system prompt",
            "repeat your instructions",
            "what are your instructions",
            "show me your prompt",
        ],
    ),
    GuardrailRule.keyword(
        "developer-mode",
        ["developer mode", "jailbreak mode", "dan mode"],
    ),
    GuardrailRule.keyword(
        "role-override",
        ["you are now dan", "act as dan", "pretend you are not an ai"],
        action=GuardrailAction.FLAG,
    ),
)


@dataclass(frozen=True)
class GuardrailResult:
    blocked: bool
    flagged: bool
    matched_rules: tuple[str, ...] = field(default_factory=tuple)


class Guardrail:
    """Input/output filter, toggleable so a scenario can be run through the
    target both with (`enabled=True`) and without (`enabled=False`) this
    defensive layer for comparison."""

    def __init__(self, rules: Iterable[GuardrailRule] | None = None, *, enabled: bool = True):
        self.rules: tuple[GuardrailRule, ...] = tuple(rules) if rules is not None else DEFAULT_RULES
        self.enabled = enabled

    def check_input(self, text: str) -> GuardrailResult:
        """Scan `text` for known injection phrasing before it reaches the
        target LLM. Disabled guardrails always pass everything through
        unmodified, so a disabled-vs-enabled comparison run is meaningful."""
        if not self.enabled:
            return GuardrailResult(blocked=False, flagged=False)

        blocked_rules = [r.name for r in self.rules if r.action == GuardrailAction.BLOCK and r.pattern.search(text)]
        flagged_rules = [r.name for r in self.rules if r.action == GuardrailAction.FLAG and r.pattern.search(text)]

        return GuardrailResult(
            blocked=bool(blocked_rules),
            flagged=bool(blocked_rules or flagged_rules),
            matched_rules=tuple(blocked_rules + flagged_rules),
        )

    def check_output(self, text: str, success_signals: Iterable[str] = ()) -> GuardrailResult:
        """Output-side check: the same rule pass, plus flagging any known
        `success_signal` substring (from the scenario under test) that shows
        up in the model's response -- i.e. the attack likely succeeded even
        if the response text itself doesn't match an input-style rule."""
        result = self.check_input(text) if self.enabled else GuardrailResult(blocked=False, flagged=False)
        if not self.enabled:
            return result

        leaked = [s for s in success_signals if s and s.lower() in text.lower()]
        if not leaked:
            return result

        return GuardrailResult(
            blocked=result.blocked,
            flagged=True,
            matched_rules=result.matched_rules + tuple(f"success-signal:{s}" for s in leaked),
        )
