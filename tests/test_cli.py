"""Tests for the Phase 1 CLI."""
from __future__ import annotations

import json
from pathlib import Path

from src.main import main

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_list_shipped(capsys, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    rc = main(["list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ignore-previous-instructions" in out
    assert "scenario(s)" in out


def test_list_filtered_by_category(capsys, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    rc = main(["list", "--category", "jailbreak"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "roleplay-persona-swap" in out
    assert "ignore-previous-instructions" not in out


def test_show_json(capsys, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    rc = main(["show", "system-prompt-exfiltration"])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["category"] == "system-prompt-leak"


def test_show_unknown_id(capsys, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    rc = main(["show", "nope"])
    assert rc == 1
    assert "no scenario" in capsys.readouterr().err


def test_stats_and_validate(capsys, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    assert main(["stats"]) == 0
    assert "total" in capsys.readouterr().out
    assert main(["validate"]) == 0
    assert "valid" in capsys.readouterr().out


def test_bad_path_returns_1(capsys, tmp_path):
    rc = main(["--path", str(tmp_path / "missing"), "list"])
    assert rc == 1
    assert "error:" in capsys.readouterr().err
