# User guide

## 1. Extract clauses from a single contract

Against a bundled sample:

```bash
python -m qtc_clause_bench.cli extract --contract c001_msa_northwind
```

Against your own file:

```bash
python -m qtc_clause_bench.cli extract --file my_contract.txt
```

### Reading the output

```json
{
  "contract_id": "c001_msa_northwind",
  "pricing_tier": {"present": false, "tiers": [], "quote_span": ""},
  "discount_threshold": {
    "present": true,
    "discount_percent": 15,
    "trigger_type": "multi_year_commitment",
    "trigger_value": 36,
    "trigger_unit": "months",
    "quote_span": "..."
  },
  "renewal_term": {
    "present": true,
    "renewal_type": "auto",
    "initial_term_months": 12,
    "renewal_term_months": 12,
    "notice_period_days": 45,
    "price_escalation_percent": 3,
    "quote_span": "..."
  },
  "msa_sow_linkage": {"present": false, "reference_type": "none", "referenced_document": null, "order_of_precedence_note": null, "quote_span": ""}
}
```

Every one of the 4 clause types is always present as a key, `present: false` means the pipeline concluded that clause type doesn't appear in the document, which is itself a real, scoreable answer, not a missing field.

`quote_span` is meant to be an exact or near-exact quotation from the source contract. If it doesn't read like it came from the document verbatim, that's worth flagging, it's the one field this pipeline doesn't currently double-check against the source text (see [known gaps](ARCHITECTURE.md#known-gaps)).

## 2. Run the full benchmark

```bash
python -m qtc_clause_bench.cli benchmark
```

This runs extraction on all 12 bundled contracts and scores every result against the hand-authored ground truth in `data/annotations/`, then prints a markdown table:

```
Benchmark run over 12 contracts.

| Clause type | Precision | Recall | F1 | Presence accuracy | Field accuracy (n) |
|---|---|---|---|---|---|
| `pricing_tier` | 0.80 | 1.00 | 0.89 | 0.92 | 0.75 (4) |
| ...
```

Save the report to a file:

```bash
python -m qtc_clause_bench.cli benchmark --output results/$(date +%Y%m%d)_claude-sonnet-4-5.md
```

### Reading the metrics

The scorer answers two separate questions per clause type, deliberately not blended into one number:

**Did the pipeline correctly say the clause is present or absent?** This is a standard presence-classification problem, "present" is the positive class, "absent" is the negative class, across all 12 contracts.

| Metric | Meaning |
|---|---|
| Precision | Of the times the pipeline said "present," how often was it actually present. Low precision means it's hallucinating clauses that aren't there. |
| Recall | Of the times a clause was actually present, how often did the pipeline catch it. Low recall means it's missing real clauses. |
| F1 | Harmonic mean of precision and recall, one number when you need a single ranking. |
| Presence accuracy | (true positives + true negatives) / total contracts. Can look artificially high on a clause type that's rare in the dataset, that's why precision and recall are reported separately, not folded away. |

**When it said "present" and it actually is, did it extract the right fields?** This is `field_accuracy`, computed only over true positives (the `(n)` after the number is how many true positives that clause type had, a field accuracy of 1.00 on `n=1` means much less than 1.00 on `n=8`). A clause type can have perfect presence detection and still score low field accuracy if the pipeline finds the clause but gets the discount percentage or notice period wrong.

Field-match is exact-match, not fuzzy: for `pricing_tier` every tier's threshold, price, unit, and currency must match, including tier count; for `renewal_term` every populated field (`renewal_type`, `initial_term_months`, `renewal_term_months`, `notice_period_days`, `price_escalation_percent`) must match; for `discount_threshold`, `discount_percent`, `trigger_type`, `trigger_value`, `trigger_unit`; for `msa_sow_linkage`, `reference_type`. See `qtc_clause_bench/scorer.py` for the exact comparison logic per clause type.

## 3. Extending the dataset

Add a new contract/annotation pair under `data/contracts/<id>.txt` and `data/annotations/<id>.json`. Run `pytest tests/test_dataset.py -v` to confirm it's paired correctly and validates against the schema before running the benchmark. See [CONTRIBUTING.md](../CONTRIBUTING.md) for what makes a good addition (edge cases and distractors are more valuable than more easy examples).

## Troubleshooting

**A contract is excluded from the benchmark report with "SCHEMA VALIDATION FAILED"**
The CLI prints which contract and why to stderr, then continues scoring the rest. This is intentional, one bad model response shouldn't block the whole report, but check the excluded contract count against your total, a run with several exclusions isn't a real benchmark result.

**Field accuracy looks worse than it should**
Check whether the ground truth and the model disagree on units, currency, or null-vs-zero. The scorer does exact comparison on purpose (see [Architecture](ARCHITECTURE.md) for why), a near-miss is still a miss, which is the honest way to report this, not a reason to loosen the comparison after the fact.

## Next steps

- [Architecture](ARCHITECTURE.md): how the pipeline and scorer are built, and where to extend them.
