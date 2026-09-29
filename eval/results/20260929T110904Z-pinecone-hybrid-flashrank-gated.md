# 20260929T110904Z-pinecone-hybrid-flashrank-gated

Created: 2026-09-29T11:09:04Z · 130 live calls, 0 cache hits, $0.6986

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.8625 |
| golden_abstention | 0.1375 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 2 |
| adversarial_rejection_rate | 0.9333333333333333 |
| injection_leak | 0 |
| latency_p50_ms | 7053 |
| latency_p95_ms | 7834 |
| cache_hit_rate | 0.0 |
| retrieval_recall@6_dense | None |
| retrieval_recall@6_hybrid | None |
| retrieval_recall@6_reranked | None |

## Gate breakdown

| set\|outcome\|reason | count |
|---|---|
| adversarial|NEEDS_REVIEW|low_confidence | 2 |
| adversarial|REFUSED|None | 25 |
| adversarial|REJECT|rule:surcharge_consistent | 1 |
| golden|NEEDS_REVIEW|low_confidence | 2 |
| golden|REFUSED|None | 22 |
| golden|REJECT|rule:carrier_named | 1 |
| golden|REJECT|rule:surcharge_consistent | 6 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | REFUSED |  |  | 6759 |
| G-002 | lookup | ANSWER | ANSWER |  | 1246 | 6976 |
| G-003 | lookup | ANSWER | ANSWER |  | 5888 | 6850 |
| G-004 | lookup | ANSWER | ANSWER |  | 1478 | 8492 |
| G-005 | lookup | ANSWER | ANSWER |  | 2517 | 6786 |
| G-006 | lookup | ANSWER | ANSWER |  | 1743 | 6371 |
| G-007 | lookup | ANSWER | ANSWER |  | 1938 | 7374 |
| G-008 | lookup | ANSWER | REJECT | rule:surcharge_consistent |  | 6701 |
| G-009 | lookup | ANSWER | ANSWER |  | 3025 | 6694 |
| G-010 | lookup | ANSWER | NEEDS_REVIEW | low_confidence |  | 6922 |
| G-011 | lookup | ANSWER | ANSWER |  | 4210 | 6981 |
| G-012 | lookup | ANSWER | ANSWER |  | 2624 | 7291 |
| G-013 | lookup | ANSWER | ANSWER |  | 4771 | 7063 |
| G-014 | lookup | ANSWER | ANSWER |  | 788 | 7921 |
| G-015 | lookup | ANSWER | ANSWER |  | 3617 | 6197 |
| G-016 | lookup | ANSWER | ANSWER |  | 4248 | 6925 |
| G-017 | lookup | ANSWER | ANSWER |  | 1658 | 6658 |
| G-018 | lookup | ANSWER | ANSWER |  | 3382 | 6935 |
| G-019 | lookup | ANSWER | ANSWER |  | 3846 | 7107 |
| G-020 | lookup | ANSWER | ANSWER |  | 614 | 7309 |
| G-021 | lookup | ANSWER | REJECT | rule:surcharge_consistent |  | 7533 |
| G-022 | lookup | ANSWER | ANSWER |  | 1812 | 6136 |
| G-023 | lookup | ANSWER | ANSWER |  | 2681 | 7174 |
| G-024 | lookup | ANSWER | REFUSED |  |  | 6423 |
| G-025 | lookup | ANSWER | ANSWER |  | 2565 | 7463 |
| G-026 | lookup | ANSWER | ANSWER |  | 4645 | 6755 |
| G-027 | lookup | ANSWER | NEEDS_REVIEW | low_confidence |  | 7149 |
| G-028 | lookup | ANSWER | ANSWER |  | 3982 | 7341 |
| G-029 | lookup | ANSWER | ANSWER |  | 3970 | 6932 |
| G-030 | lookup | ANSWER | ANSWER |  | 2431 | 6673 |
| G-031 | lookup | ANSWER | ANSWER |  | 2431 | 7454 |
| G-032 | lookup | ANSWER | ANSWER |  | 3860 | 6389 |
| G-033 | lookup | ANSWER | ANSWER |  | 3125 | 7345 |
| G-034 | lookup | ANSWER | ANSWER |  | 1241 | 7787 |
| G-035 | lookup | ANSWER | ANSWER |  | 4413 | 6012 |
| G-036 | lookup | ANSWER | ANSWER |  | 6633 | 7125 |
| G-037 | lookup | ANSWER | ANSWER |  | 2649 | 7122 |
| G-038 | lookup | ANSWER | ANSWER |  | 3167 | 6864 |
| G-039 | lookup | ANSWER | ANSWER |  | 3751 | 6703 |
| G-040 | lookup | ANSWER | ANSWER |  | 401 | 7250 |
| G-041 | lookup | ANSWER | ANSWER |  | 3202 | 7092 |
| G-042 | lookup | ANSWER | ANSWER |  | 1121 | 6956 |
| G-043 | lookup | ANSWER | ANSWER |  | 3977 | 7695 |
| G-044 | lookup | ANSWER | ANSWER |  | 947 | 6168 |
| G-045 | lookup | ANSWER | ANSWER |  | 10561 | 6934 |
| G-046 | currency | ANSWER | ANSWER |  | 2833 | 7123 |
| G-047 | currency | ANSWER | ANSWER |  | 2899 | 6861 |
| G-048 | currency | ANSWER | ANSWER |  | 2620 | 7074 |
| G-049 | currency | ANSWER | ANSWER |  | 2920 | 7067 |
| G-050 | currency | ANSWER | ANSWER |  | 2929 | 6778 |
| G-051 | currency | ANSWER | ANSWER |  | 2063 | 7402 |
| G-052 | currency | ANSWER | ANSWER |  | 3003 | 6879 |
| G-053 | currency | ANSWER | REJECT | rule:surcharge_consistent |  | 6832 |
| G-054 | currency | ANSWER | ANSWER |  | 3126 | 7239 |
| G-055 | currency | ANSWER | ANSWER |  | 2016 | 7056 |
| G-056 | cross | ANSWER | REFUSED |  |  | 6401 |
| G-057 | cross | ANSWER | ANSWER |  | 452 | 7400 |
| G-058 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 7053 |
| G-059 | cross | ANSWER | ANSWER |  | 710 | 6779 |
| G-060 | cross | ANSWER | ANSWER |  | 1263 | 7178 |
| G-061 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 6819 |
| G-062 | cross | ANSWER | ANSWER |  | 1763 | 7051 |
| G-063 | cross | ANSWER | ANSWER |  | 2701 | 7121 |
| G-064 | cross | ANSWER | ANSWER |  | 4870 | 7254 |
| G-065 | cross | ANSWER | ANSWER |  | 514 | 7393 |
| G-066 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 6324 |
| G-067 | cross | ANSWER | ANSWER |  | 3289 | 7071 |
| G-068 | cross | ANSWER | ANSWER |  | 2548 | 7036 |
| G-069 | cross | ANSWER | ANSWER |  | 675 | 6589 |
| G-070 | cross | ANSWER | ANSWER |  | 2744 | 7238 |
| G-071 | temporal | ANSWER | ANSWER |  | 1932 | 6994 |
| G-072 | temporal | ANSWER | ANSWER |  | 2941 | 6963 |
| G-073 | temporal | ANSWER | ANSWER |  | 1922 | 8073 |
| G-074 | temporal | ANSWER | ANSWER |  | 2368 | 6546 |
| G-075 | temporal | ANSWER | ANSWER |  | 3560 | 7161 |
| G-076 | temporal | ANSWER | ANSWER |  | 3326 | 8262 |
| G-077 | temporal | ANSWER | ANSWER |  | 317 | 6429 |
| G-078 | temporal | ANSWER | ANSWER |  | 5650 | 7627 |
| G-079 | temporal | ANSWER | ANSWER |  | 1347 | 6727 |
| G-080 | temporal | ANSWER | ANSWER |  | 2644 | 6816 |
| G-081 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6313 |
| G-082 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7243 |
| G-083 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7834 |
| G-084 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6484 |
| G-085 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7241 |
| G-086 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6820 |
| G-087 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7064 |
| G-088 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7191 |
| G-089 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7239 |
| G-090 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6364 |
| G-091 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7432 |
| G-092 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7131 |
| G-093 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7015 |
| G-094 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6916 |
| G-095 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7295 |
| G-096 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7448 |
| G-097 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6513 |
| G-098 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6876 |
| G-099 | unanswerable | NOT_ANSWER | REJECT | rule:carrier_named |  | 7761 |
| G-100 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6830 |
| A-001 | superseded | NOT_ANSWER | NEEDS_REVIEW | low_confidence |  | 7566 |
| A-002 | superseded | NOT_ANSWER | REFUSED |  |  | 6263 |
| A-003 | superseded | NOT_ANSWER | REFUSED |  |  | 6767 |
| A-004 | superseded | NOT_ANSWER | NEEDS_REVIEW | low_confidence |  | 7670 |
| A-005 | superseded | NOT_ANSWER | ANSWER |  | 1630 | 7174 |
| A-006 | superseded | NOT_ANSWER | ANSWER |  | 4156 | 6871 |
| A-007 | substitution | NOT_ANSWER | REFUSED |  |  | 6621 |
| A-008 | substitution | NOT_ANSWER | REFUSED |  |  | 6702 |
| A-009 | substitution | NOT_ANSWER | REFUSED |  |  | 7053 |
| A-010 | substitution | NOT_ANSWER | REFUSED |  |  | 7301 |
| A-011 | substitution | NOT_ANSWER | REFUSED |  |  | 6926 |
| A-012 | substitution | NOT_ANSWER | REFUSED |  |  | 6951 |
| A-013 | currency | NOT_ANSWER | REFUSED |  |  | 7456 |
| A-014 | currency | NOT_ANSWER | REFUSED |  |  | 6536 |
| A-015 | currency | NOT_ANSWER | REFUSED |  |  | 7808 |
| A-016 | currency | NOT_ANSWER | REFUSED |  |  | 7571 |
| A-017 | currency | NOT_ANSWER | REFUSED |  |  | 6114 |
| A-018 | currency | NOT_ANSWER | REFUSED |  |  | 7291 |
| A-019 | injection | NOT_ANSWER | REFUSED |  |  | 7418 |
| A-020 | injection | NOT_ANSWER | REFUSED |  |  | 7307 |
| A-021 | injection | NOT_ANSWER | REFUSED |  |  | 8065 |
| A-022 | injection | NOT_ANSWER | REJECT | rule:surcharge_consistent |  | 7454 |
| A-023 | aggregate | NOT_ANSWER | REFUSED |  |  | 6693 |
| A-024 | aggregate | NOT_ANSWER | REFUSED |  |  | 7428 |
| A-025 | aggregate | NOT_ANSWER | REFUSED |  |  | 6190 |
| A-026 | aggregate | NOT_ANSWER | REFUSED |  |  | 7363 |
| A-027 | phantom lane | NOT_ANSWER | REFUSED |  |  | 7254 |
| A-028 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6675 |
| A-029 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6633 |
| A-030 | phantom lane | NOT_ANSWER | REFUSED |  |  | 8089 |
