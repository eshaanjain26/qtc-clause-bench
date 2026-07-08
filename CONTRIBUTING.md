# Contributing

## Adding a contract to the benchmark

Every contract needs a matching pair:

1. `data/contracts/<id>.txt`, the contract text. Use a fictional company name and no real client data, ever.
2. `data/annotations/<id>.json`, hand-authored ground truth matching `schema/extraction_result.schema.json`.

Good additions are the ones that break something: a phrasing pattern the current dataset doesn't cover, a true negative (a clause type genuinely absent), or a distractor (two candidate answers in one document, only one of which is correct). Run `pytest tests/` before opening a pull request, the dataset-integrity tests check every contract has a matching annotation and every annotation validates against the schema.

Explain the edge case you're adding in an `annotation_note` field (see `schema/extraction_result.schema.json`, it's an optional ground-truth-only field, never produced by the pipeline and never scored) so reviewers understand what the example is testing.

## Reporting benchmark results

If you run `qtc-clause-bench benchmark` against a model and want to contribute the results, open a pull request adding your numbers to `results/`, name the file after the model and date, and note the model version and any prompt changes you made. Unmodified prompts and unmodified dataset only, otherwise the numbers aren't comparable to anyone else's run.

## Rubric-adjacent scope

This benchmark only covers 4 clause types by design: pricing_tier, discount_threshold, renewal_term, msa_sow_linkage. Proposals to add a 5th clause type (payment_terms and termination_for_convenience are the obvious next candidates) are welcome, but should come with at least 3 contracts covering it, not just a schema change.

## Code changes

Keep `qtc_clause_bench/engine.py`'s `_call_model` as the only function that imports the `anthropic` package. Anything that needs to swap model providers should only need to touch that one function.
