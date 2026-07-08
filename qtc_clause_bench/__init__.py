"""qtc-clause-bench: an open benchmark and extraction pipeline for quote-to-cash
commercial contract clauses.

Informational tooling for benchmarking clause extraction. Not a substitute for
legal or contracts review. See README.md.
"""

__version__ = "0.1.0"

CLAUSE_TYPES = [
    "pricing_tier",
    "discount_threshold",
    "renewal_term",
    "msa_sow_linkage",
]
