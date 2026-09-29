# 20260929T051820Z-chroma-hybrid-flashrank-gated

Created: 2026-09-29T05:18:20Z · 0 live calls, 30 cache hits, $0.0000

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9166666666666666 |
| golden_abstention | 0.08333333333333333 |
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
| golden|REJECT|rule:carrier_known | 1 |
| golden|REJECT|rule:surcharge_consistent | 1 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 1519 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 1431 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 1473 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 1440 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 1515 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 1762 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 1415 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 1392 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 2260 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 1946 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 2111 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 2271 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 1431 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 2071 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 1515 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 2915 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 1508 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 2080 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 1336 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 1358 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 1339 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 1424 |
| G-023 | temporal | ANSWER | REJECT | rule:carrier_known |  | 1373 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 1345 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1336 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1846 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1364 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1322 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1679 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2225 |
