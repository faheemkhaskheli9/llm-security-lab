"""Tests for the scenario library model and loader."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from src.scenarios import Category, ScenarioError, ScenarioLibrary, load_scenarios

SCENARIOS_DIR = Path(__file__).resolve().parents[1] / "scenarios"

MINIMAL = """
scenarios:
  - id: sample-case
    category: prompt-injection
    title: Sample case
    description: A sample scenario.
    attack_input: "ignore instructions"
    expected_safe_behavior: "keeps its policy"
"""


def _write(tmp_path: Path, text: str, name: str = "s.yaml") -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_shipped_library_loads_and_is_consistent():
    lib = load_scenarios(SCENARIOS_DIR)
    assert len(lib) >= 7
    ids = [s.id for s in lib]
    assert len(ids) == len(set(ids))
    for s in lib:
        assert s.expected_safe_behavior  # acceptance: documents defended behavior
        assert s.references              # acceptance: documents source/inspiration


def test_filter_and_stats():
    lib = load_scenarios(SCENARIOS_DIR)
    jb = lib.filter(category="jailbreak")
    assert all(s.category is Category.JAILBREAK for s in jb)
    stats = lib.stats()
    assert sum(stats["by_category"].values()) == len(lib)
    assert lib.filter(technique="indirect-injection")


def test_missing_path_is_error(tmp_path):
    with pytest.raises(ScenarioError, match="not found"):
        load_scenarios(tmp_path / "nope")


def test_empty_dir_is_error(tmp_path):
    with pytest.raises(ScenarioError, match="no YAML"):
        load_scenarios(tmp_path)


def test_duplicate_ids_rejected(tmp_path):
    _write(
        tmp_path,
        """
        scenarios:
          - {id: dup, category: jailbreak, title: One, description: first entry,
             attack_input: a, expected_safe_behavior: keeps its policy}
          - {id: dup, category: jailbreak, title: Two, description: second entry,
             attack_input: b, expected_safe_behavior: keeps its policy}
        """,
    )
    with pytest.raises(ScenarioError, match="duplicate scenario id"):
        load_scenarios(tmp_path)


def test_unknown_field_rejected(tmp_path):
    _write(
        tmp_path,
        """
        scenarios:
          - id: x-case
            category: jailbreak
            title: Case
            description: desc
            attack_input: a
            expected_safe_behavior: keeps policy
            oops: true
        """,
    )
    with pytest.raises(ScenarioError):
        load_scenarios(tmp_path)


def test_bad_id_pattern_rejected(tmp_path):
    _write(tmp_path, MINIMAL.replace("sample-case", "Bad_ID"))
    with pytest.raises(ScenarioError):
        load_scenarios(tmp_path)


def test_bad_category_rejected(tmp_path):
    _write(tmp_path, MINIMAL.replace("prompt-injection", "not-a-category"))
    with pytest.raises(ScenarioError):
        load_scenarios(tmp_path)


def test_library_get_and_len_from_minimal(tmp_path):
    lib = load_scenarios(_write(tmp_path, MINIMAL))
    assert isinstance(lib, ScenarioLibrary)
    assert len(lib) == 1
    assert lib.get("sample-case").title == "Sample case"
    assert lib.get("absent") is None
