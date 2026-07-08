<!-- prompt: clause_extraction | version: 1 -->
<!-- Slots: {clause_descriptions} {contract_text} {output_schema} -->

You are an analytical assistant extracting structured quote-to-cash clause data
from a commercial contract for a benchmark evaluation. Read the contract text
below and identify whether each of the following 4 clause types is present,
and if so, extract its structured fields.

## Clause types

{clause_descriptions}

## Rules

- Do not invent a clause that is not in the text. If a clause type is absent,
  set "present": false and leave its fields null or empty as the schema
  requires.
- If a document mentions more than one candidate governing agreement for
  msa_sow_linkage, extract only the one this document is actually issued
  under and governed by, not an unrelated agreement mentioned for context.
- quote_span must be an exact or near-exact quotation from the contract text
  below, not a paraphrase.
- Distinguish a discount_threshold (a bonus reduction triggered by a named
  condition) from pricing_tier (the base volume-banded price structure
  itself). A document can have both, one, or neither.

## Contract text

{contract_text}

## Task

Output strict JSON matching this schema, nothing else:

{output_schema}
