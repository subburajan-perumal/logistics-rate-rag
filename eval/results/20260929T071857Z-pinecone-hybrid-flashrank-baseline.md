# 20260929T071857Z-pinecone-hybrid-flashrank-baseline

Created: 2026-09-29T07:18:57Z · 45 live calls, 0 cache hits, $0.1843

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
| latency_p50_ms | 7048 |
| latency_p95_ms | 8034 |
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
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 5731 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 6839 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 7521 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 7148 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 6629 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 6930 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 7135 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 7226 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 6896 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 7697 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 6853 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 7048 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 6754 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 7165 |
| G-015 | cross | ANSWER | ANSWER |  | 1966 | 6929 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 7994 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 6900 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 8034 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 8568 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 7608 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 6745 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 7318 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 7218 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 6955 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6763 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6747 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7211 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6867 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7255 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6656 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 3254 | 7966 |
| A-002 | superseded | NOT_ANSWER | ANSWER |  |  | 7059 |
| A-003 | superseded | NOT_ANSWER | ANSWER |  | 2114 | 7338 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 9317 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 6946 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 7154 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 6949 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 7143 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 6955 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 7126 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 6872 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 7890 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6194 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6949 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 7087 |
