# 20260929T052622Z-chroma-hybrid-flashrank-gated

Created: 2026-09-29T05:26:22Z · 0 live calls, 30 cache hits, $0.0000

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
| latency_p50_ms | None |
| latency_p95_ms | None |
| cache_hit_rate | 1.0 |
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
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 1431 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 1526 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 1394 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 1519 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 1654 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 1685 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 1487 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 1540 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 2483 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 1933 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 2131 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 2334 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 1547 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 2325 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 4041 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 2837 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 1749 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 2358 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 1345 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 1456 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 1743 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 2520 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 2154 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 1508 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1700 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2133 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1438 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1424 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1881 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2562 |
