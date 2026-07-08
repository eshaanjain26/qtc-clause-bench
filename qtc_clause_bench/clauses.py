"""Human-readable descriptions of the 4 clause types this benchmark covers.

Used in prompt building and in documentation. Keeping the descriptions here,
not duplicated in the prompt template, keeps the taxonomy definition in one
place.
"""

from __future__ import annotations

CLAUSE_DESCRIPTIONS: dict[str, str] = {
    "pricing_tier": (
        "A structure where unit price depends on a volume band (e.g. per-seat, "
        "per-call, or per-unit pricing that steps down as quantity increases). "
        "A single flat price with no bands is NOT a pricing_tier."
    ),
    "discount_threshold": (
        "A discount, credit, or price reduction triggered by a specific, named "
        "condition: exceeding an annual contract value, committing to a volume "
        "or multi-year term, or a one-time condition like prepayment. Distinct "
        "from pricing_tier: a discount_threshold is a bonus reduction layered on "
        "top of otherwise-applicable pricing, not the base tier structure itself."
    ),
    "renewal_term": (
        "How the agreement's term behaves at expiration: automatic renewal, "
        "renewal requiring a new signed instrument, or no renewal at all. "
        "Captures initial term length, renewal term length, notice period, and "
        "any price escalation tied to renewal. An evergreen or perpetual term "
        "with a termination-for-convenience notice period is a distinct pattern "
        "from a fixed-term auto-renewal and should be recorded as such."
    ),
    "msa_sow_linkage": (
        "Language in a subordinate document (an SOW, Order Form, or similar) "
        "that names and incorporates a governing master agreement, including "
        "how that master agreement is identified (by date, by title and date, "
        "or by exhibit number) and any stated order of precedence between the "
        "two documents. Does not apply to the master agreement itself referring "
        "to future SOWs in the abstract."
    ),
}
