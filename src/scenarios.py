"""Structured model + loader for the prompt-injection test scenario library.

Defensive-research use only: every scenario is a *test case* for evaluating a
target application's guardrails in Phase 2. Attack strings are canonical,
publicly documented patterns, kept generic and non-operational.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Iterable

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class ScenarioError(ValueError):
    """Raised when a scenario file cannot be read or validated."""


class Category(str, Enum):
    PROMPT_INJECTION = "prompt-injection"
    JAILBREAK = "jailbreak"
    SYSTEM_PROMPT_LEAK = "system-prompt-leak"
    INDIRECT_INJECTION = "indirect-injection"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(..., pattern=r"^[a-z0-9][a-z0-9\-]{2,63}$")
    category: Category
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=3)
    technique: list[str] = Field(default_factory=list)
    severity: Severity = Severity.MEDIUM
    # The adversarial user/content input handed to the target app under test.
    attack_input: str = Field(..., min_length=1)
    # What a correctly defended system should do instead of complying.
    expected_safe_behavior: str = Field(..., min_length=3)
    # Substrings whose presence in a response suggests the attack succeeded;
    # consumed by the Phase 2 evaluation harness.
    success_signals: list[str] = Field(default_factory=list)
    # Where this pattern is documented (public research / advisories).
    references: list[str] = Field(default_factory=list)

    @field_validator("technique", "success_signals", "references")
    @classmethod
    def _no_blank_items(cls, v: list[str]) -> list[str]:
        if any(not str(item).strip() for item in v):
            raise ValueError("list items must be non-empty")
        return v


class ScenarioLibrary:
    def __init__(self, scenarios: Iterable[Scenario]) -> None:
        self._scenarios: list[Scenario] = list(scenarios)
        seen: dict[str, int] = {}
        for i, s in enumerate(self._scenarios):
            if s.id in seen:
                raise ScenarioError(f"duplicate scenario id: {s.id!r}")
            seen[s.id] = i

    def __len__(self) -> int:
        return len(self._scenarios)

    def __iter__(self):
        return iter(self._scenarios)

    def get(self, scenario_id: str) -> Scenario | None:
        return next((s for s in self._scenarios if s.id == scenario_id), None)

    def filter(
        self,
        *,
        category: str | Category | None = None,
        severity: str | Severity | None = None,
        technique: str | None = None,
    ) -> list[Scenario]:
        out = self._scenarios
        if category is not None:
            cat = Category(category)
            out = [s for s in out if s.category == cat]
        if severity is not None:
            sev = Severity(severity)
            out = [s for s in out if s.severity == sev]
        if technique is not None:
            out = [s for s in out if technique in s.technique]
        return list(out)

    def stats(self) -> dict[str, dict[str, int]]:
        by_cat: dict[str, int] = {}
        by_sev: dict[str, int] = {}
        for s in self._scenarios:
            by_cat[s.category.value] = by_cat.get(s.category.value, 0) + 1
            by_sev[s.severity.value] = by_sev.get(s.severity.value, 0) + 1
        return {"by_category": by_cat, "by_severity": by_sev}


def _iter_yaml_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(p for p in path.glob("*.y*ml"))
    if path.is_file():
        return [path]
    raise ScenarioError(f"scenario path not found: {path}")


def load_scenarios(path: str | Path) -> ScenarioLibrary:
    """Load scenarios from a YAML file or a directory of YAML files.

    Each file is a mapping with a ``scenarios:`` list (or a bare list).
    """
    root = Path(path)
    files = _iter_yaml_files(root)
    if not files:
        raise ScenarioError(f"no YAML scenario files under {root}")

    collected: list[Scenario] = []
    for f in files:
        try:
            raw = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ScenarioError(f"invalid YAML in {f}: {exc}") from exc
        if raw is None:
            continue
        items = raw.get("scenarios", raw) if isinstance(raw, dict) else raw
        if not isinstance(items, list):
            raise ScenarioError(f"{f}: expected a list of scenarios")
        for entry in items:
            try:
                collected.append(Scenario.model_validate(entry))
            except ValidationError as exc:
                raise ScenarioError(f"{f}: invalid scenario:\n{exc}") from exc

    return ScenarioLibrary(collected)
