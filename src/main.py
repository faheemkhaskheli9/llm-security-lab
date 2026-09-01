"""CLI for the prompt-injection test scenario library (defensive research use).

    python -m src.main list
    python -m src.main list --category jailbreak
    python -m src.main show ignore-previous-instructions
    python -m src.main stats
    python -m src.main validate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.scenarios import ScenarioError, load_scenarios

DEFAULT_PATH = Path("scenarios")


def _load(args: argparse.Namespace):
    return load_scenarios(args.path)


def _cmd_list(args: argparse.Namespace) -> int:
    lib = _load(args)
    rows = lib.filter(category=args.category, severity=args.severity, technique=args.technique)
    for s in rows:
        print(f"{s.id:40s} {s.category.value:20s} {s.severity.value:7s} {s.title}")
    print(f"\n{len(rows)} scenario(s)")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    lib = _load(args)
    s = lib.get(args.scenario_id)
    if s is None:
        print(f"error: no scenario with id {args.scenario_id!r}", file=sys.stderr)
        return 1
    print(json.dumps(s.model_dump(mode="json"), indent=2))
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    lib = _load(args)
    print(json.dumps({"total": len(lib), **lib.stats()}, indent=2))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    lib = _load(args)
    print(f"ok: {len(lib)} scenario(s) valid, ids unique")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-security-lab", description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH, help="Scenario file or directory.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List scenarios (optionally filtered).")
    p_list.add_argument("--category")
    p_list.add_argument("--severity")
    p_list.add_argument("--technique")
    p_list.set_defaults(func=_cmd_list)

    p_show = sub.add_parser("show", help="Print one scenario as JSON.")
    p_show.add_argument("scenario_id")
    p_show.set_defaults(func=_cmd_show)

    sub.add_parser("stats", help="Counts by category and severity.").set_defaults(func=_cmd_stats)
    sub.add_parser("validate", help="Validate the library and exit.").set_defaults(func=_cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ScenarioError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
