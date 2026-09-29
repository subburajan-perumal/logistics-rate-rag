# 20260929T051729Z-chroma-hybrid-none-gated

Created: 2026-09-29T05:17:29Z · 27 live calls, 3 cache hits, $0.1114

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9166666666666666 |
| golden_abstention | 0.08333333333333333 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 0 |
| adversarial_rejection_rate | None |
| injection_leak | 0 |
| latency_p50_ms | 6867 |
| latency_p95_ms | 8215 |
| cache_hit_rate | 0.1 |
| retrieval_recall@6_dense | None |
| retrieval_recall@6_hybrid | None |
| retrieval_recall@6_reranked | None |

## Gate breakdown

| set\|outcome\|reason | count |
|---|---|
| golden|REFUSED|None | 6 |
| golden|REJECT|rule:carrier_known | 1 |
| golden|REJECT|rule:surcharge_consistent | 1 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 7111 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 5723 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 5446 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 591 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 6155 |
| G-006 | lookup | ANSWER | REJECT | rule:carrier_known |  | 6945 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 6972 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 511 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 6652 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 7739 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 6558 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 6746 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 8916 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 6018 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 7112 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 6898 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 6522 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 6973 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 572 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 6805 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 7348 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 6236 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 8215 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 5934 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6339 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6867 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7454 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6608 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7267 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 8089 |
