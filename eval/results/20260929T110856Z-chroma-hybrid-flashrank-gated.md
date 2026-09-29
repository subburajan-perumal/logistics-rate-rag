# 20260929T110856Z-chroma-hybrid-flashrank-gated

Created: 2026-09-29T11:08:56Z · 130 live calls, 0 cache hits, $0.6972

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.8375 |
| golden_abstention | 0.1625 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 1 |
| adversarial_rejection_rate | 0.9666666666666667 |
| injection_leak | 0 |
| latency_p50_ms | 6964 |
| latency_p95_ms | 8108 |
| cache_hit_rate | 0.0 |
| retrieval_recall@6_dense | None |
| retrieval_recall@6_hybrid | None |
| retrieval_recall@6_reranked | None |

## Gate breakdown

| set\|outcome\|reason | count |
|---|---|
| adversarial|NEEDS_REVIEW|low_confidence | 1 |
| adversarial|REFUSED|None | 26 |
| adversarial|REJECT|rule:not_expired | 2 |
| golden|NEEDS_REVIEW|low_confidence | 3 |
| golden|REFUSED|None | 22 |
| golden|REJECT|rule:carrier_named | 1 |
| golden|REJECT|rule:surcharge_consistent | 7 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | REFUSED |  |  | 5686 |
| G-002 | lookup | ANSWER | ANSWER |  | 1246 | 7672 |
| G-003 | lookup | ANSWER | ANSWER |  | 5888 | 6681 |
| G-004 | lookup | ANSWER | ANSWER |  | 1478 | 7748 |
| G-005 | lookup | ANSWER | ANSWER |  | 2517 | 6497 |
| G-006 | lookup | ANSWER | ANSWER |  | 1743 | 8665 |
| G-007 | lookup | ANSWER | ANSWER |  | 1938 | 5577 |
| G-008 | lookup | ANSWER | REJECT | rule:surcharge_consistent |  | 6859 |
| G-009 | lookup | ANSWER | ANSWER |  | 3025 | 7096 |
| G-010 | lookup | ANSWER | NEEDS_REVIEW | low_confidence |  | 7123 |
| G-011 | lookup | ANSWER | ANSWER |  | 4210 | 7068 |
| G-012 | lookup | ANSWER | ANSWER |  | 2624 | 6797 |
| G-013 | lookup | ANSWER | ANSWER |  | 4771 | 7088 |
| G-014 | lookup | ANSWER | ANSWER |  | 788 | 7056 |
| G-015 | lookup | ANSWER | ANSWER |  | 3617 | 7972 |
| G-016 | lookup | ANSWER | ANSWER |  | 4248 | 5820 |
| G-017 | lookup | ANSWER | ANSWER |  | 1658 | 7002 |
| G-018 | lookup | ANSWER | ANSWER |  | 3382 | 7230 |
| G-019 | lookup | ANSWER | ANSWER |  | 3846 | 6744 |
| G-020 | lookup | ANSWER | NEEDS_REVIEW | low_confidence |  | 6922 |
| G-021 | lookup | ANSWER | REJECT | rule:surcharge_consistent |  | 7274 |
| G-022 | lookup | ANSWER | ANSWER |  | 1812 | 6830 |
| G-023 | lookup | ANSWER | ANSWER |  | 2681 | 7367 |
| G-024 | lookup | ANSWER | REFUSED |  |  | 5969 |
| G-025 | lookup | ANSWER | ANSWER |  | 2565 | 8631 |
| G-026 | lookup | ANSWER | ANSWER |  | 4645 | 6756 |
| G-027 | lookup | ANSWER | NEEDS_REVIEW | low_confidence |  | 6312 |
| G-028 | lookup | ANSWER | ANSWER |  | 3982 | 6857 |
| G-029 | lookup | ANSWER | ANSWER |  | 3970 | 8222 |
| G-030 | lookup | ANSWER | ANSWER |  | 2431 | 6665 |
| G-031 | lookup | ANSWER | ANSWER |  | 2431 | 6474 |
| G-032 | lookup | ANSWER | ANSWER |  | 3860 | 7001 |
| G-033 | lookup | ANSWER | ANSWER |  | 3125 | 6836 |
| G-034 | lookup | ANSWER | ANSWER |  | 1241 | 7551 |
| G-035 | lookup | ANSWER | ANSWER |  | 4413 | 6412 |
| G-036 | lookup | ANSWER | ANSWER |  | 6633 | 7055 |
| G-037 | lookup | ANSWER | ANSWER |  | 2649 | 7275 |
| G-038 | lookup | ANSWER | ANSWER |  | 3167 | 6904 |
| G-039 | lookup | ANSWER | ANSWER |  | 3751 | 6770 |
| G-040 | lookup | ANSWER | ANSWER |  | 401 | 7069 |
| G-041 | lookup | ANSWER | ANSWER |  | 3202 | 6782 |
| G-042 | lookup | ANSWER | ANSWER |  | 1121 | 6964 |
| G-043 | lookup | ANSWER | ANSWER |  | 3977 | 8171 |
| G-044 | lookup | ANSWER | ANSWER |  | 947 | 5882 |
| G-045 | lookup | ANSWER | ANSWER |  | 10561 | 7196 |
| G-046 | currency | ANSWER | ANSWER |  | 2833 | 7694 |
| G-047 | currency | ANSWER | ANSWER |  | 2899 | 6729 |
| G-048 | currency | ANSWER | ANSWER |  | 2620 | 6430 |
| G-049 | currency | ANSWER | ANSWER |  | 2920 | 6750 |
| G-050 | currency | ANSWER | ANSWER |  | 2929 | 7973 |
| G-051 | currency | ANSWER | ANSWER |  | 2063 | 6057 |
| G-052 | currency | ANSWER | ANSWER |  | 3003 | 6931 |
| G-053 | currency | ANSWER | REJECT | rule:surcharge_consistent |  | 7667 |
| G-054 | currency | ANSWER | ANSWER |  | 3126 | 6819 |
| G-055 | currency | ANSWER | REJECT | rule:surcharge_consistent |  | 6956 |
| G-056 | cross | ANSWER | REFUSED |  |  | 7817 |
| G-057 | cross | ANSWER | ANSWER |  | 452 | 6401 |
| G-058 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 6268 |
| G-059 | cross | ANSWER | ANSWER |  | 710 | 7099 |
| G-060 | cross | ANSWER | ANSWER |  | 1263 | 7625 |
| G-061 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 6388 |
| G-062 | cross | ANSWER | ANSWER |  | 1763 | 7203 |
| G-063 | cross | ANSWER | ANSWER |  | 2701 | 7131 |
| G-064 | cross | ANSWER | ANSWER |  | 4870 | 7792 |
| G-065 | cross | ANSWER | ANSWER |  | 514 | 6071 |
| G-066 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 8108 |
| G-067 | cross | ANSWER | ANSWER |  | 3289 | 5740 |
| G-068 | cross | ANSWER | ANSWER |  | 2548 | 7081 |
| G-069 | cross | ANSWER | ANSWER |  | 675 | 6678 |
| G-070 | cross | ANSWER | ANSWER |  | 2744 | 7577 |
| G-071 | temporal | ANSWER | ANSWER |  | 1932 | 7292 |
| G-072 | temporal | ANSWER | ANSWER |  | 2941 | 6885 |
| G-073 | temporal | ANSWER | ANSWER |  | 1922 | 6716 |
| G-074 | temporal | ANSWER | ANSWER |  | 2368 | 6417 |
| G-075 | temporal | ANSWER | ANSWER |  | 3560 | 7438 |
| G-076 | temporal | ANSWER | ANSWER |  | 3326 | 8495 |
| G-077 | temporal | ANSWER | ANSWER |  | 317 | 6879 |
| G-078 | temporal | ANSWER | ANSWER |  | 5650 | 6003 |
| G-079 | temporal | ANSWER | ANSWER |  | 1347 | 6682 |
| G-080 | temporal | ANSWER | ANSWER |  | 2644 | 7592 |
| G-081 | unanswerable | NOT_ANSWER | REFUSED |  |  | 5809 |
| G-082 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7964 |
| G-083 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6101 |
| G-084 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7267 |
| G-085 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6929 |
| G-086 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6537 |
| G-087 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7715 |
| G-088 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7887 |
| G-089 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7038 |
| G-090 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6077 |
| G-091 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6486 |
| G-092 | unanswerable | NOT_ANSWER | REFUSED |  |  | 8105 |
| G-093 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6184 |
| G-094 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7000 |
| G-095 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6717 |
| G-096 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6852 |
| G-097 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7272 |
| G-098 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6952 |
| G-099 | unanswerable | NOT_ANSWER | REJECT | rule:carrier_named |  | 7484 |
| G-100 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6629 |
| A-001 | superseded | NOT_ANSWER | NEEDS_REVIEW | low_confidence |  | 7462 |
| A-002 | superseded | NOT_ANSWER | REFUSED |  |  | 6243 |
| A-003 | superseded | NOT_ANSWER | REFUSED |  |  | 7188 |
| A-004 | superseded | NOT_ANSWER | REJECT | rule:not_expired |  | 7517 |
| A-005 | superseded | NOT_ANSWER | ANSWER |  | 1630 | 7240 |
| A-006 | superseded | NOT_ANSWER | REJECT | rule:not_expired |  | 6786 |
| A-007 | substitution | NOT_ANSWER | REFUSED |  |  | 6705 |
| A-008 | substitution | NOT_ANSWER | REFUSED |  |  | 7170 |
| A-009 | substitution | NOT_ANSWER | REFUSED |  |  | 6763 |
| A-010 | substitution | NOT_ANSWER | REFUSED |  |  | 7228 |
| A-011 | substitution | NOT_ANSWER | REFUSED |  |  | 6613 |
| A-012 | substitution | NOT_ANSWER | REFUSED |  |  | 7323 |
| A-013 | currency | NOT_ANSWER | REFUSED |  |  | 6908 |
| A-014 | currency | NOT_ANSWER | REFUSED |  |  | 6538 |
| A-015 | currency | NOT_ANSWER | REFUSED |  |  | 7614 |
| A-016 | currency | NOT_ANSWER | REFUSED |  |  | 7734 |
| A-017 | currency | NOT_ANSWER | REFUSED |  |  | 6485 |
| A-018 | currency | NOT_ANSWER | REFUSED |  |  | 7544 |
| A-019 | injection | NOT_ANSWER | REFUSED |  |  | 6345 |
| A-020 | injection | NOT_ANSWER | REFUSED |  |  | 8550 |
| A-021 | injection | NOT_ANSWER | REFUSED |  |  | 6612 |
| A-022 | injection | NOT_ANSWER | REFUSED |  |  | 6968 |
| A-023 | aggregate | NOT_ANSWER | REFUSED |  |  | 7042 |
| A-024 | aggregate | NOT_ANSWER | REFUSED |  |  | 7179 |
| A-025 | aggregate | NOT_ANSWER | REFUSED |  |  | 7013 |
| A-026 | aggregate | NOT_ANSWER | REFUSED |  |  | 6589 |
| A-027 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7173 |
| A-028 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7116 |
| A-029 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6813 |
| A-030 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7310 |
