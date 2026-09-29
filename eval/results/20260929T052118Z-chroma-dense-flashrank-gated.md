# 20260929T052118Z-chroma-dense-flashrank-gated

Created: 2026-09-29T05:21:18Z · 25 live calls, 5 cache hits, $0.1067

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9583333333333334 |
| golden_abstention | 0.041666666666666664 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 0 |
| adversarial_rejection_rate | None |
| injection_leak | 0 |
| latency_p50_ms | 6892 |
| latency_p95_ms | 7962 |
| cache_hit_rate | 0.16666666666666666 |
| retrieval_recall@6_dense | None |
| retrieval_recall@6_hybrid | None |
| retrieval_recall@6_reranked | None |

## Gate breakdown

| set\|outcome\|reason | count |
|---|---|
| golden|REFUSED|None | 6 |
| golden|REJECT|rule:surcharge_consistent | 1 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 1559 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 4734 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 6945 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 7021 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 1416 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 5290 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 7038 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 1497 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 6336 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 1515 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 4582 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 7063 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 6827 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 7143 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 6657 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 7291 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 6892 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 8000 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 1390 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 4769 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 7037 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 7183 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 6554 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 7317 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6449 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7962 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 5964 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6857 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7240 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6946 |
