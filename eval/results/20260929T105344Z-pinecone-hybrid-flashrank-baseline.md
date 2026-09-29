# 20260929T105344Z-pinecone-hybrid-flashrank-baseline

Created: 2026-09-29T10:53:44Z · 130 live calls, 0 cache hits, $0.6986

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.925 |
| golden_abstention | 0.0375 |
| refusal_correctness | 0.95 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 9 |
| adversarial_rejection_rate | 0.8333333333333334 |
| injection_leak | 0 |
| latency_p50_ms | 7109 |
| latency_p95_ms | 8086 |
| cache_hit_rate | 0.0 |
| retrieval_recall@6_dense | None |
| retrieval_recall@6_hybrid | None |
| retrieval_recall@6_reranked | None |

## Gate breakdown

| set\|outcome\|reason | count |
|---|---|
| adversarial|REFUSED|None | 25 |
| golden|REFUSED|None | 22 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | REFUSED |  |  | 6390 |
| G-002 | lookup | ANSWER | ANSWER |  | 1246 | 7810 |
| G-003 | lookup | ANSWER | ANSWER |  | 5888 | 6520 |
| G-004 | lookup | ANSWER | ANSWER |  | 1478 | 7792 |
| G-005 | lookup | ANSWER | ANSWER |  | 2517 | 6415 |
| G-006 | lookup | ANSWER | ANSWER |  | 1743 | 6835 |
| G-007 | lookup | ANSWER | ANSWER |  | 1938 | 7150 |
| G-008 | lookup | ANSWER | ANSWER |  | 3289 | 7216 |
| G-009 | lookup | ANSWER | ANSWER |  | 3025 | 7548 |
| G-010 | lookup | ANSWER | ANSWER |  | 226 | 7028 |
| G-011 | lookup | ANSWER | ANSWER |  | 4210 | 7380 |
| G-012 | lookup | ANSWER | ANSWER |  | 2624 | 5951 |
| G-013 | lookup | ANSWER | ANSWER |  | 4771 | 7417 |
| G-014 | lookup | ANSWER | ANSWER |  | 788 | 6738 |
| G-015 | lookup | ANSWER | ANSWER |  | 3617 | 6958 |
| G-016 | lookup | ANSWER | ANSWER |  | 4248 | 6813 |
| G-017 | lookup | ANSWER | ANSWER |  | 1658 | 7101 |
| G-018 | lookup | ANSWER | ANSWER |  | 3382 | 8245 |
| G-019 | lookup | ANSWER | ANSWER |  | 3846 | 7405 |
| G-020 | lookup | ANSWER | ANSWER |  | 614 | 7514 |
| G-021 | lookup | ANSWER | ANSWER |  | 2492 | 6831 |
| G-022 | lookup | ANSWER | ANSWER |  | 1812 | 6659 |
| G-023 | lookup | ANSWER | ANSWER |  | 2681 | 6991 |
| G-024 | lookup | ANSWER | REFUSED |  |  | 6719 |
| G-025 | lookup | ANSWER | ANSWER |  | 2565 | 7345 |
| G-026 | lookup | ANSWER | ANSWER |  | 4645 | 7053 |
| G-027 | lookup | ANSWER | ANSWER |  | 1129 | 7104 |
| G-028 | lookup | ANSWER | ANSWER |  | 3982 | 7222 |
| G-029 | lookup | ANSWER | ANSWER |  | 3970 | 7357 |
| G-030 | lookup | ANSWER | ANSWER |  | 2431 | 6476 |
| G-031 | lookup | ANSWER | ANSWER |  | 2431 | 7109 |
| G-032 | lookup | ANSWER | ANSWER |  | 3860 | 6955 |
| G-033 | lookup | ANSWER | ANSWER |  | 3125 | 7227 |
| G-034 | lookup | ANSWER | ANSWER |  | 1241 | 8041 |
| G-035 | lookup | ANSWER | ANSWER |  | 4413 | 6508 |
| G-036 | lookup | ANSWER | ANSWER |  | 6633 | 6879 |
| G-037 | lookup | ANSWER | ANSWER |  | 2649 | 7385 |
| G-038 | lookup | ANSWER | ANSWER |  | 3167 | 6694 |
| G-039 | lookup | ANSWER | ANSWER |  | 3751 | 7545 |
| G-040 | lookup | ANSWER | ANSWER |  | 401 | 6522 |
| G-041 | lookup | ANSWER | ANSWER |  | 3202 | 7083 |
| G-042 | lookup | ANSWER | ANSWER |  | 1121 | 7184 |
| G-043 | lookup | ANSWER | ANSWER |  | 3977 | 7795 |
| G-044 | lookup | ANSWER | ANSWER |  | 947 | 7093 |
| G-045 | lookup | ANSWER | ANSWER |  | 10561 | 8513 |
| G-046 | currency | ANSWER | ANSWER |  | 2833 | 6510 |
| G-047 | currency | ANSWER | ANSWER |  | 2899 | 7349 |
| G-048 | currency | ANSWER | ANSWER |  | 2620 | 7064 |
| G-049 | currency | ANSWER | ANSWER |  | 2920 | 7674 |
| G-050 | currency | ANSWER | ANSWER |  | 2929 | 8086 |
| G-051 | currency | ANSWER | ANSWER |  | 2063 | 6982 |
| G-052 | currency | ANSWER | ANSWER |  | 3003 | 8364 |
| G-053 | currency | ANSWER | ANSWER |  | 2535 | 6599 |
| G-054 | currency | ANSWER | ANSWER |  | 3126 | 7075 |
| G-055 | currency | ANSWER | ANSWER |  | 2016 | 7246 |
| G-056 | cross | ANSWER | REFUSED |  |  | 6975 |
| G-057 | cross | ANSWER | ANSWER |  | 452 | 7294 |
| G-058 | cross | ANSWER | ANSWER |  | 1117 | 7892 |
| G-059 | cross | ANSWER | ANSWER |  | 710 | 6566 |
| G-060 | cross | ANSWER | ANSWER |  | 1263 | 6916 |
| G-061 | cross | ANSWER | ANSWER |  | 3116 | 6817 |
| G-062 | cross | ANSWER | ANSWER |  | 1763 | 7191 |
| G-063 | cross | ANSWER | ANSWER |  | 2701 | 7861 |
| G-064 | cross | ANSWER | ANSWER |  | 4870 | 7160 |
| G-065 | cross | ANSWER | ANSWER |  | 514 | 7156 |
| G-066 | cross | ANSWER | ANSWER |  | 1789 | 6935 |
| G-067 | cross | ANSWER | ANSWER |  | 3289 | 6988 |
| G-068 | cross | ANSWER | ANSWER |  | 2548 | 7873 |
| G-069 | cross | ANSWER | ANSWER |  | 675 | 7342 |
| G-070 | cross | ANSWER | ANSWER |  | 2744 | 7774 |
| G-071 | temporal | ANSWER | ANSWER |  | 1932 | 7668 |
| G-072 | temporal | ANSWER | ANSWER |  | 2941 | 7274 |
| G-073 | temporal | ANSWER | ANSWER |  | 1922 | 7271 |
| G-074 | temporal | ANSWER | ANSWER |  | 2368 | 6624 |
| G-075 | temporal | ANSWER | ANSWER |  | 3560 | 7186 |
| G-076 | temporal | ANSWER | ANSWER |  | 3326 | 7377 |
| G-077 | temporal | ANSWER | ANSWER |  | 317 | 6736 |
| G-078 | temporal | ANSWER | ANSWER |  | 5650 | 7614 |
| G-079 | temporal | ANSWER | ANSWER |  | 1347 | 7434 |
| G-080 | temporal | ANSWER | ANSWER |  | 2644 | 7512 |
| G-081 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6436 |
| G-082 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6947 |
| G-083 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7059 |
| G-084 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6854 |
| G-085 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7905 |
| G-086 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7182 |
| G-087 | unanswerable | NOT_ANSWER | REFUSED |  |  | 5962 |
| G-088 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6982 |
| G-089 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7460 |
| G-090 | unanswerable | NOT_ANSWER | REFUSED |  |  | 8085 |
| G-091 | unanswerable | NOT_ANSWER | REFUSED |  |  | 5756 |
| G-092 | unanswerable | NOT_ANSWER | REFUSED |  |  | 8782 |
| G-093 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7455 |
| G-094 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6082 |
| G-095 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6594 |
| G-096 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7349 |
| G-097 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7273 |
| G-098 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6450 |
| G-099 | unanswerable | NOT_ANSWER | ANSWER |  | 893 | 7955 |
| G-100 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6717 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 6194 | 7253 |
| A-002 | superseded | NOT_ANSWER | REFUSED |  |  | 6665 |
| A-003 | superseded | NOT_ANSWER | REFUSED |  |  | 6981 |
| A-004 | superseded | NOT_ANSWER | ANSWER |  | 1784 | 7518 |
| A-005 | superseded | NOT_ANSWER | ANSWER |  | 1630 | 6806 |
| A-006 | superseded | NOT_ANSWER | ANSWER |  | 4156 | 7126 |
| A-007 | substitution | NOT_ANSWER | REFUSED |  |  | 6453 |
| A-008 | substitution | NOT_ANSWER | REFUSED |  |  | 7390 |
| A-009 | substitution | NOT_ANSWER | REFUSED |  |  | 7073 |
| A-010 | substitution | NOT_ANSWER | REFUSED |  |  | 7625 |
| A-011 | substitution | NOT_ANSWER | REFUSED |  |  | 6096 |
| A-012 | substitution | NOT_ANSWER | REFUSED |  |  | 7414 |
| A-013 | currency | NOT_ANSWER | REFUSED |  |  | 6471 |
| A-014 | currency | NOT_ANSWER | REFUSED |  |  | 7908 |
| A-015 | currency | NOT_ANSWER | REFUSED |  |  | 6063 |
| A-016 | currency | NOT_ANSWER | REFUSED |  |  | 7460 |
| A-017 | currency | NOT_ANSWER | REFUSED |  |  | 8006 |
| A-018 | currency | NOT_ANSWER | REFUSED |  |  | 5733 |
| A-019 | injection | NOT_ANSWER | REFUSED |  |  | 7356 |
| A-020 | injection | NOT_ANSWER | REFUSED |  |  | 8301 |
| A-021 | injection | NOT_ANSWER | REFUSED |  |  | 5851 |
| A-022 | injection | NOT_ANSWER | ANSWER |  | 3326 | 8733 |
| A-023 | aggregate | NOT_ANSWER | REFUSED |  |  | 6056 |
| A-024 | aggregate | NOT_ANSWER | REFUSED |  |  | 6807 |
| A-025 | aggregate | NOT_ANSWER | REFUSED |  |  | 6934 |
| A-026 | aggregate | NOT_ANSWER | REFUSED |  |  | 7261 |
| A-027 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7096 |
| A-028 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7047 |
| A-029 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6497 |
| A-030 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7180 |
