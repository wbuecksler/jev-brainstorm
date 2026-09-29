"""Command line: `jev-shadow lint <spec_dir>` and `jev-shadow run <spec_dir>`.

A spec directory holds spec.json and fixtures.jsonl (see specs/support-triage-example/).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from jev_shadow.evaluate import DryRunEvaluator, Evaluator, JevEvaluator
from jev_shadow.run import render_report, run, write_log
from jev_shadow.spec import LintResult, SpecError, lint_spec, load_fixtures, load_spec


def _load(spec_dir: Path):
    spec = load_spec(spec_dir / "spec.json")
    fixtures = load_fixtures(spec_dir / "fixtures.jsonl")
    return spec, fixtures


def _print_lint(spec_dir: Path, result: LintResult) -> None:
    for message in result.errors:
        print(f"error   {spec_dir}: {message}", file=sys.stderr)
    for message in result.warnings:
        print(f"warning {spec_dir}: {message}", file=sys.stderr)
    status = "ok" if result.ok else "FAILED"
    print(f"lint {status}: {spec_dir} ({len(result.errors)} errors, {len(result.warnings)} warnings)")


def cmd_lint(args: argparse.Namespace) -> int:
    failed = False
    for spec_dir in args.spec_dirs:
        try:
            spec, fixtures = _load(spec_dir)
        except SpecError as error:
            print(f"error   {error}", file=sys.stderr)
            failed = True
            continue
        result = lint_spec(spec, fixtures)
        _print_lint(spec_dir, result)
        failed |= not result.ok
    return 1 if failed else 0


def cmd_run(args: argparse.Namespace) -> int:
    spec_dir: Path = args.spec_dir
    try:
        spec, fixtures = _load(spec_dir)
    except SpecError as error:
        print(f"error   {error}", file=sys.stderr)
        return 1
    result = lint_spec(spec, fixtures)
    _print_lint(spec_dir, result)
    if not result.ok:
        return 1

    has_key = bool(os.environ.get("TYPESAFE_API_KEY", "").strip())
    if args.dry_run or not has_key:
        if not args.dry_run:
            print("TYPESAFE_API_KEY is not set: running a DRY RUN with placeholder answers (no model called).", file=sys.stderr)
        evaluator: Evaluator = DryRunEvaluator()
    else:
        evaluator = JevEvaluator(model=args.model or spec.get("model"))

    try:
        rows = run(spec, fixtures, evaluator)
    finally:
        evaluator.close()

    out_dir: Path = args.out / spec["name"]
    write_log(rows, spec, evaluator.live, out_dir / "shadow.jsonl")
    report = render_report(rows, spec, evaluator.live)
    (out_dir / "report.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {out_dir / 'shadow.jsonl'} and {out_dir / 'report.md'}", file=sys.stderr)
    if evaluator.live and rows and all(row.error for row in rows):
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jev-shadow", description="Shadow-mode harness for Jev opportunity specs. Never acts.")
    sub = parser.add_subparsers(dest="command", required=True)

    lint = sub.add_parser("lint", help="check specs against the anti-patterns (no network)")
    lint.add_argument("spec_dirs", nargs="+", type=Path)
    lint.set_defaults(func=cmd_lint)

    run_parser = sub.add_parser("run", help="ask Jev about each fixture and write a shadow log and report")
    run_parser.add_argument("spec_dir", type=Path)
    run_parser.add_argument("--out", type=Path, default=Path("out"))
    run_parser.add_argument("--model", help="override the spec's model (default: spec.model, then jev-latest)")
    run_parser.add_argument("--dry-run", action="store_true", help="use placeholder answers even if a key is set")
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
