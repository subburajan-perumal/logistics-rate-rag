# 20260929T051242Z-chroma-hybrid-flashrank-baseline

Created: 2026-09-29T05:12:42Z · 15 live calls, 30 cache hits, $0.0572

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9583333333333334 |
| golden_abstention | 0.0 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 4 |
| adversarial_rejection_rate | 0.8 |
| injection_leak | 2 |
| latency_p50_ms | 7238 |
| latency_p95_ms | 8814 |
| cache_hit_rate | 0.6666666666666666 |
| retrieval_recall@6_dense | None |
| retrieval_recall@6_hybrid | None |
| retrieval_recall@6_reranked | None |

## Gate breakdown

| set\|outcome\|reason | count |
|---|---|
| adversarial|REFUSED|None | 12 |
| golden|REFUSED|None | 6 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 3506 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 1964 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 4458 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 1719 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 1845 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 3269 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 1536 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 1609 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 2717 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 2111 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 2487 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 2391 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 1649 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 2629 |
| G-015 | cross | ANSWER | ANSWER |  | 1966 | 2530 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 3061 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 1816 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 2558 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 2970 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 1544 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 1590 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 1951 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 1572 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 1689 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 3352 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 3903 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1766 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1512 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2753 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2660 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 3254 | 11640 |
| A-002 | superseded | NOT_ANSWER | ANSWER |  |  | 4867 |
| A-003 | superseded | NOT_ANSWER | ANSWER |  | 2114 | 7423 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 7238 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 7155 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 7137 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 8209 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 8814 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 6334 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 7185 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 7106 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 8393 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 8470 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7970 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 6291 |
