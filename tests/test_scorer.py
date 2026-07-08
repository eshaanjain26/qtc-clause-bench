from qtc_clause_bench import CLAUSE_TYPES
from qtc_clause_bench.scorer import aggregate, score_contract


def _blank_clause(present=False, **fields):
    base = {"present": present, "quote_span": ""}
    base.update(fields)
    return base


def _blank_result(contract_id="x"):
    return {
        "contract_id": contract_id,
        "pricing_tier": _blank_clause(tiers=[]),
        "discount_threshold": _blank_clause(discount_percent=None, trigger_type="none"),
        "renewal_term": _blank_clause(renewal_type="none"),
        "msa_sow_linkage": _blank_clause(reference_type="none"),
    }


def test_true_negative_all_clause_types():
    predicted = _blank_result()
    actual = _blank_result()
    result = score_contract(predicted, actual)
    for clause_type in CLAUSE_TYPES:
        assert result[clause_type]["confusion"] == "TN"
        assert result[clause_type]["field_match"] is None


def test_true_positive_with_matching_fields():
    predicted = _blank_result()
    actual = _blank_result()
    predicted["discount_threshold"] = _blank_clause(
        present=True, discount_percent=10, trigger_type="volume", trigger_value=100, trigger_unit="units"
    )
    actual["discount_threshold"] = _blank_clause(
        present=True, discount_percent=10, trigger_type="volume", trigger_value=100, trigger_unit="units"
    )
    result = score_contract(predicted, actual)
    assert result["discount_threshold"]["confusion"] == "TP"
    assert result["discount_threshold"]["field_match"] is True


def test_true_positive_with_wrong_fields():
    predicted = _blank_result()
    actual = _blank_result()
    predicted["discount_threshold"] = _blank_clause(present=True, discount_percent=5, trigger_type="volume")
    actual["discount_threshold"] = _blank_clause(present=True, discount_percent=10, trigger_type="volume")
    result = score_contract(predicted, actual)
    assert result["discount_threshold"]["confusion"] == "TP"
    assert result["discount_threshold"]["field_match"] is False


def test_false_positive_and_false_negative():
    predicted = _blank_result()
    actual = _blank_result()
    predicted["renewal_term"] = _blank_clause(present=True, renewal_type="auto")
    # actual stays present=False -> false positive
    result = score_contract(predicted, actual)
    assert result["renewal_term"]["confusion"] == "FP"

    predicted2 = _blank_result()
    actual2 = _blank_result()
    actual2["msa_sow_linkage"] = _blank_clause(present=True, reference_type="date")
    # predicted2 stays present=False -> false negative
    result2 = score_contract(predicted2, actual2)
    assert result2["msa_sow_linkage"]["confusion"] == "FN"


def test_pricing_tier_field_match_requires_same_tier_count():
    predicted = _blank_result()
    actual = _blank_result()
    predicted["pricing_tier"] = _blank_clause(
        present=True, tiers=[{"threshold_low": 1, "threshold_high": 10, "unit_price": 5, "unit": "seat", "currency": "USD"}]
    )
    actual["pricing_tier"] = _blank_clause(
        present=True,
        tiers=[
            {"threshold_low": 1, "threshold_high": 10, "unit_price": 5, "unit": "seat", "currency": "USD"},
            {"threshold_low": 11, "threshold_high": None, "unit_price": 4, "unit": "seat", "currency": "USD"},
        ],
    )
    result = score_contract(predicted, actual)
    assert result["pricing_tier"]["confusion"] == "TP"
    assert result["pricing_tier"]["field_match"] is False


def test_aggregate_precision_recall_f1():
    # 2 contracts: one TP, one FP for discount_threshold
    r1 = score_contract(
        {**_blank_result("a"), "discount_threshold": _blank_clause(present=True, discount_percent=10, trigger_type="volume")},
        {**_blank_result("a"), "discount_threshold": _blank_clause(present=True, discount_percent=10, trigger_type="volume")},
    )
    r2 = score_contract(
        {**_blank_result("b"), "discount_threshold": _blank_clause(present=True, discount_percent=10, trigger_type="volume")},
        _blank_result("b"),
    )
    report = aggregate([r1, r2])
    dt = report["discount_threshold"]
    assert dt["counts"]["TP"] == 1
    assert dt["counts"]["FP"] == 1
    assert dt["precision"] == 0.5
    assert dt["recall"] == 1.0


def test_aggregate_handles_zero_positives_gracefully():
    r1 = score_contract(_blank_result("a"), _blank_result("a"))
    report = aggregate([r1])
    for clause_type in CLAUSE_TYPES:
        # all TN, so precision/recall are undefined (no positives at all)
        assert report[clause_type]["precision"] is None
        assert report[clause_type]["recall"] is None
        assert report[clause_type]["presence_accuracy"] == 1.0
