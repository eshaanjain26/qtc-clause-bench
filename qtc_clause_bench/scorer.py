"""Scoring: presence classification (precision/recall/F1 per clause type) plus
field-level accuracy on the subset where both prediction and ground truth
agree the clause is present.

Two separate questions, deliberately not blended into one number:

1. Did the pipeline correctly say a clause type is present or absent?
   (presence confusion matrix, per clause type, across the dataset)
2. When it said "present" and it actually is, did it extract the right
   structured fields? (field_match, only meaningful on true positives)
"""

from __future__ import annotations

from qtc_clause_bench import CLAUSE_TYPES


def _fields_match_pricing_tier(pred: dict, actual: dict) -> bool:
    p_tiers = pred.get("tiers", [])
    a_tiers = actual.get("tiers", [])
    if len(p_tiers) != len(a_tiers):
        return False
    for pt, at in zip(p_tiers, a_tiers):
        if pt.get("threshold_low") != at.get("threshold_low"):
            return False
        if pt.get("threshold_high") != at.get("threshold_high"):
            return False
        if pt.get("unit_price") != at.get("unit_price"):
            return False
        if pt.get("unit") != at.get("unit"):
            return False
        if pt.get("currency", "USD") != at.get("currency", "USD"):
            return False
    return True


def _fields_match_discount_threshold(pred: dict, actual: dict) -> bool:
    keys = ["discount_percent", "trigger_type", "trigger_value", "trigger_unit"]
    return all(pred.get(k) == actual.get(k) for k in keys)


def _fields_match_renewal_term(pred: dict, actual: dict) -> bool:
    keys = ["renewal_type", "initial_term_months", "renewal_term_months", "notice_period_days", "price_escalation_percent"]
    return all(pred.get(k) == actual.get(k) for k in keys)


def _fields_match_msa_sow_linkage(pred: dict, actual: dict) -> bool:
    return pred.get("reference_type") == actual.get("reference_type")


FIELD_MATCHERS = {
    "pricing_tier": _fields_match_pricing_tier,
    "discount_threshold": _fields_match_discount_threshold,
    "renewal_term": _fields_match_renewal_term,
    "msa_sow_linkage": _fields_match_msa_sow_linkage,
}


def score_contract(predicted: dict, actual: dict) -> dict:
    """Compare one predicted extraction against its ground truth. Returns a
    dict keyed by clause type: {"confusion": "TP"|"FP"|"FN"|"TN", "field_match": bool|None}.
    """
    result = {}
    for clause_type in CLAUSE_TYPES:
        pred_clause = predicted.get(clause_type, {}) or {}
        actual_clause = actual.get(clause_type, {}) or {}
        pred_present = bool(pred_clause.get("present"))
        actual_present = bool(actual_clause.get("present"))

        if pred_present and actual_present:
            confusion = "TP"
        elif pred_present and not actual_present:
            confusion = "FP"
        elif not pred_present and actual_present:
            confusion = "FN"
        else:
            confusion = "TN"

        field_match = None
        if confusion == "TP":
            field_match = FIELD_MATCHERS[clause_type](pred_clause, actual_clause)

        result[clause_type] = {"confusion": confusion, "field_match": field_match}
    return result


def aggregate(per_contract_results: list[dict]) -> dict:
    """Roll up score_contract() results across the dataset into per-clause-type
    precision/recall/F1 and field-match accuracy.
    """
    report = {}
    for clause_type in CLAUSE_TYPES:
        counts = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
        field_matches = 0
        field_checked = 0
        for contract_result in per_contract_results:
            entry = contract_result[clause_type]
            counts[entry["confusion"]] += 1
            if entry["field_match"] is not None:
                field_checked += 1
                if entry["field_match"]:
                    field_matches += 1

        tp, fp, fn, tn = counts["TP"], counts["FP"], counts["FN"], counts["TN"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else None
        recall = tp / (tp + fn) if (tp + fn) > 0 else None
        f1 = (2 * precision * recall / (precision + recall)) if (precision and recall) else None
        accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) > 0 else None
        field_accuracy = field_matches / field_checked if field_checked > 0 else None

        report[clause_type] = {
            "counts": counts,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "presence_accuracy": accuracy,
            "field_accuracy": field_accuracy,
            "field_checked_n": field_checked,
        }
    return report


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def format_report_markdown(report: dict, dataset_size: int) -> str:
    lines = [
        f"Benchmark run over {dataset_size} contracts.",
        "",
        "| Clause type | Precision | Recall | F1 | Presence accuracy | Field accuracy (n) |",
        "|---|---|---|---|---|---|",
    ]
    for clause_type in CLAUSE_TYPES:
        r = report[clause_type]
        field_acc = _fmt(r["field_accuracy"])
        n = r["field_checked_n"]
        lines.append(
            f"| `{clause_type}` | {_fmt(r['precision'])} | {_fmt(r['recall'])} | "
            f"{_fmt(r['f1'])} | {_fmt(r['presence_accuracy'])} | {field_acc} ({n}) |"
        )
    return "\n".join(lines)
