# 20260929T052805Z-chroma-hybrid-flashrank-gated

Created: 2026-09-29T05:28:05Z · 0 live calls, 30 cache hits, $0.0000

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
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 1468 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 1341 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 1460 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 1397 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 1424 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 1436 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 1343 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 1397 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 2218 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 1914 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 2174 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 2200 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 1493 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 2290 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 1658 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 2932 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 1607 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 2246 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 1473 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 1796 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 1447 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 1417 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 1400 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 1424 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1426 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1895 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1492 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1451 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1715 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2382 |
