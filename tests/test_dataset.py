"""Dataset integrity: every contract has a matching, schema-valid annotation."""

import json
from pathlib import Path

import jsonschema
import pytest

from qtc_clause_bench import CLAUSE_TYPES, dataset

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "extraction_result.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_at_least_ten_contracts():
    assert len(dataset.list_contract_ids()) >= 10


def test_every_contract_has_matching_annotation():
    # list_contract_ids() itself raises if contracts and annotations don't pair up 1:1
    ids = dataset.list_contract_ids()
    assert len(ids) > 0


@pytest.mark.parametrize("contract_id", dataset.list_contract_ids())
def test_annotation_validates_against_schema(contract_id):
    annotation = dataset.load_annotation(contract_id)
    jsonschema.validate(annotation, SCHEMA)


@pytest.mark.parametrize("contract_id", dataset.list_contract_ids())
def test_annotation_contract_id_matches_filename(contract_id):
    annotation = dataset.load_annotation(contract_id)
    assert annotation["contract_id"] == contract_id


@pytest.mark.parametrize("contract_id", dataset.list_contract_ids())
def test_annotation_has_all_clause_types(contract_id):
    annotation = dataset.load_annotation(contract_id)
    for clause_type in CLAUSE_TYPES:
        assert clause_type in annotation


def test_dataset_has_at_least_one_true_negative_per_clause_type():
    """Every clause type should have at least one contract where it's genuinely absent,
    otherwise the benchmark can't catch a pipeline that hallucinates that clause type."""
    examples = dataset.load_dataset()
    for clause_type in CLAUSE_TYPES:
        absent_count = sum(1 for ex in examples if not ex.annotation[clause_type]["present"])
        assert absent_count >= 1, f"no true-negative example for {clause_type}"


def test_dataset_has_at_least_one_positive_per_clause_type():
    examples = dataset.load_dataset()
    for clause_type in CLAUSE_TYPES:
        present_count = sum(1 for ex in examples if ex.annotation[clause_type]["present"])
        assert present_count >= 1, f"no positive example for {clause_type}"
