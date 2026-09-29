# 20260929T071328Z-chroma-hybrid-flashrank-gated

Created: 2026-09-29T07:13:28Z · 45 live calls, 0 cache hits, $0.1841

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9583333333333334 |
| golden_abstention | 0.041666666666666664 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 0 |
| adversarial_rejection_rate | 1.0 |
| injection_leak | 0 |
| latency_p50_ms | 6914 |
| latency_p95_ms | 7679 |
| cache_hit_rate | 0.0 |
| retrieval_recall@6_dense | None |
| retrieval_recall@6_hybrid | None |
| retrieval_recall@6_reranked | None |

## Gate breakdown

| set\|outcome\|reason | count |
|---|---|
| adversarial|REFUSED|None | 12 |
| adversarial|REJECT|parse_error | 1 |
| adversarial|REJECT|rule:not_expired | 2 |
| golden|REFUSED|None | 6 |
| golden|REJECT|rule:surcharge_consistent | 1 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 5843 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 6784 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 6306 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 7607 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 7861 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 6082 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 6193 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 7360 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 6903 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 9255 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 7240 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 5894 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 6563 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 6914 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 6569 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 7123 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 7298 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 6856 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 7064 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 6846 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 7244 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 7143 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 6765 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 6752 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6963 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6491 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7650 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6949 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6549 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7318 |
| A-001 | superseded | NOT_ANSWER | REJECT | rule:not_expired |  | 7065 |
| A-002 | superseded | NOT_ANSWER | REJECT | parse_error |  | 6617 |
| A-003 | superseded | NOT_ANSWER | REJECT | rule:not_expired |  | 7679 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 6473 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 6761 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 7148 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 7355 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 6438 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 7339 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 7276 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 6363 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 7611 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6978 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 6904 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 6950 |
