# qtc-clause-bench

An open benchmark and extraction pipeline for quote-to-cash commercial contract clauses: pricing tiers, discount thresholds, renewal terms, and MSA-to-SOW linkage. Synthetic contracts, hand-authored ground truth, a reference extraction pipeline, and a scorer that reports precision, recall, and field-level accuracy the way you'd report it internally, not a single vanity number.

## Disclaimer

The synthetic dataset in this repo does not contain any real client, employer, or customer contract data. Every company name, contract, and clause is fabricated for benchmarking purposes. This tool is not legal advice and is not a substitute for review by qualified contracts or legal counsel.

## Why this exists

Every open clause-extraction tool we could find, OpenContracts, contract-analyzer, legal_summarizer, ContractEval, targets litigation, NDAs, or generic legal document review. None target the commercial quote-to-cash documents (MSAs, SOWs, Order Forms) that actually drive revenue recognition and CPQ operations: tiered pricing, volume and commitment discounts, renewal and escalation terms, and how a Statement of Work legally hangs off a Master Service Agreement. This repo is that missing benchmark.

## The 4 clause types

| Key | What it captures |
|---|---|
| `pricing_tier` | Volume-banded unit pricing (per-seat, per-call, per-unit price steps). A single flat price is not a tier. |
| `discount_threshold` | A discount or credit triggered by a named condition: annual contract value, volume commitment, multi-year term, or a one-time condition like prepayment. |
| `renewal_term` | Auto-renewal, manual renewal, or no renewal, plus initial term, renewal term, notice period, and any price escalation. |
| `msa_sow_linkage` | How a subordinate document (SOW, Order Form) names and incorporates its governing master agreement, and the order-of-precedence language between them. |

## Quickstart

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# Extract clauses from one bundled sample contract
python -m qtc_clause_bench.cli extract --contract c001_msa_northwind

# Extract clauses from your own contract file
python -m qtc_clause_bench.cli extract --file my_contract.txt

# Run the full benchmark: extract + score against ground truth for all 12 contracts
python -m qtc_clause_bench.cli benchmark
```

## Results

No results are published in this repo yet. The dataset and scorer are built and tested (49 passing tests covering dataset integrity and scoring logic), but running the extraction pipeline itself requires a live Anthropic API call, which this build environment doesn't have credentials for. Run `qtc-clause-bench benchmark` yourself and see [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit your numbers to `results/`. We'd rather ship an honest "run it yourself" than an invented accuracy figure.

## Documentation

- [Installation guide](docs/INSTALLATION.md)
- [User guide](docs/USER_GUIDE.md): building the dataset, running extraction, reading the scoring report.
- [Architecture](docs/ARCHITECTURE.md): pipeline design, scoring methodology, dataset construction, known limitations.

## Repository layout

```
docs/                Installation guide, user guide, architecture doc
data/contracts/      12 synthetic MSA/SOW/Order Form contracts (no real data)
data/annotations/    Hand-authored ground truth per contract, matching the schema
prompts/             The extraction prompt template
schema/              JSON Schema for the extraction result
qtc_clause_bench/     The engine: dataset loader, prompt builder, Claude call, scorer, CLI
tests/               49 tests: dataset integrity, prompt building, scoring logic (no live API calls)
results/             Where benchmark run reports live, empty until someone runs it
```

## License

MIT. See `LICENSE`.
