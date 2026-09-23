# 20260923T070638Z-chroma-dense-none-baseline

Created: 2026-09-23T07:06:38Z · 45 live calls, 0 cache hits

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9583333333333334 |
| golden_abstention | 0.0 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 4 |
| adversarial_rejection_rate | 0.0 |
| injection_leak | 2 |
| latency_p50_ms | 7063 |
| latency_p95_ms | 9033 |
| cache_hit_rate | 0.0 |
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
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 10992 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 9033 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 5490 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 7063 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 6290 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 7442 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 6681 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 6811 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 7093 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 7226 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 7336 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 6803 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 8858 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 6999 |
| G-015 | cross | ANSWER | ANSWER |  | 1966 | 7670 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 8056 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 6286 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 8514 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 5422 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 7222 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 7787 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 7186 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 6316 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 6106 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 10061 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 4038 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7822 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7785 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 5046 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7251 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 2838 | 7959 |
| A-002 | superseded | NOT_ANSWER | ANSWER |  | 1882 | 6642 |
| A-003 | superseded | NOT_ANSWER | ANSWER |  | 2114 | 7450 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 6146 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 6367 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 7638 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 7271 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 6770 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 8265 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 6034 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 6646 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 6826 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 8441 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6821 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 5400 |
