# 20260923T074853Z-chroma-dense-none-gated

Created: 2026-09-23T07:48:53Z · 0 live calls, 45 cache hits

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9583333333333334 |
| golden_abstention | 0.041666666666666664 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 1 |
| adversarial_rejection_rate | 0.13333333333333333 |
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
| adversarial|REFUSED|None | 12 |
| adversarial|REJECT|rule:carrier_known | 1 |
| adversarial|REJECT|rule:not_expired | 1 |
| golden|REFUSED|None | 6 |
| golden|REJECT|rule:surcharge_consistent | 1 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 619 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 600 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 482 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 487 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 513 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 482 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 468 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 467 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 489 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 508 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 473 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 531 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 466 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 508 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 506 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 480 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 501 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 485 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 560 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 508 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 609 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 524 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 559 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 453 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 492 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 469 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 467 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 471 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 491 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 483 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 2838 | 506 |
| A-002 | superseded | NOT_ANSWER | REJECT | rule:not_expired |  | 490 |
| A-003 | superseded | NOT_ANSWER | REJECT | rule:carrier_known |  | 518 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 503 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 556 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 664 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 565 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 599 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 639 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 567 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 534 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 471 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 466 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 516 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 499 |
