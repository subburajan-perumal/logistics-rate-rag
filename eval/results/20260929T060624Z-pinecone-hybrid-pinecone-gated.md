# 20260929T060624Z-pinecone-hybrid-pinecone-gated

Created: 2026-09-29T06:06:24Z · 27 live calls, 3 cache hits, $0.1161

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
| latency_p50_ms | 8193 |
| latency_p95_ms | 14906 |
| cache_hit_rate | 0.1 |
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
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 8740 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 14906 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 7288 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 7298 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 11185 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 9171 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 7005 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 10175 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 7518 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 8798 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 7045 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 8617 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 8107 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 3788 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 7223 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 7942 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 10800 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 7307 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 8193 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 8881 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 10079 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 7739 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 7629 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 13167 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 7915 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 8446 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 15254 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 8066 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 6986 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 5192 |
