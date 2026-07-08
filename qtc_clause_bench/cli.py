"""Command-line entry point.

    python -m qtc_clause_bench.cli extract --file my_contract.txt
    python -m qtc_clause_bench.cli extract --contract c001_msa_northwind
    python -m qtc_clause_bench.cli benchmark
    python -m qtc_clause_bench.cli benchmark --output results/latest_run.md
"""

from __future__ import annotations

import argparse
import json
import sys

from qtc_clause_bench import dataset, engine, scorer


def cmd_extract(args: argparse.Namespace) -> int:
    if args.contract:
        text = dataset.load_contract_text(args.contract)
        contract_id = args.contract
    else:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
        contract_id = args.file

    try:
        result = engine.extract(contract_id, text, model=args.model)
    except engine.SchemaError as e:
        print(f"SCHEMA VALIDATION FAILED: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    examples = dataset.load_dataset()
    per_contract_results = []
    errors = []

    for example in examples:
        try:
            predicted = engine.extract(example.contract_id, example.text, model=args.model)
        except engine.SchemaError as e:
            errors.append(str(e))
            continue
        per_contract_results.append(scorer.score_contract(predicted, example.annotation))

    if errors:
        print(f"{len(errors)} contract(s) failed schema validation and were excluded:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)

    if not per_contract_results:
        print("No contracts scored, nothing to report.", file=sys.stderr)
        return 1

    report = scorer.aggregate(per_contract_results)
    markdown = scorer.format_report_markdown(report, dataset_size=len(per_contract_results))
    print(markdown)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown + "\n")
        print(f"\nWritten to {args.output}", file=sys.stderr)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qtc-clause-bench")
    parser.add_argument("--model", default=engine.DEFAULT_MODEL)
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract", help="extract clauses from one contract")
    group = p_extract.add_mutually_exclusive_group(required=True)
    group.add_argument("--contract", help="contract_id from the bundled dataset (data/contracts/)")
    group.add_argument("--file", help="path to an arbitrary contract text file")
    p_extract.set_defaults(func=cmd_extract)

    p_bench = sub.add_parser("benchmark", help="run extraction + scoring over the full dataset")
    p_bench.add_argument("--output", help="optional path to write the markdown report")
    p_bench.set_defaults(func=cmd_benchmark)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
