"""Prompt building tests. No live API calls."""

from qtc_clause_bench import engine


def test_build_extraction_prompt_fills_all_slots():
    prompt = engine.build_extraction_prompt("Sample contract text about pricing.")
    assert "{clause_descriptions}" not in prompt
    assert "{contract_text}" not in prompt
    assert "{output_schema}" not in prompt
    assert "Sample contract text about pricing." in prompt


def test_clause_descriptions_block_mentions_all_four_types():
    block = engine.build_clause_descriptions_block()
    for clause_type in ["pricing_tier", "discount_threshold", "renewal_term", "msa_sow_linkage"]:
        assert clause_type in block
