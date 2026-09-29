# 20260929T053001Z-chroma-dense-none-gated

Created: 2026-09-29T05:30:01Z · 0 live calls, 45 cache hits, $0.0000

## Metrics

| Metric | Value |
|---|---|
| golden_accuracy | 0.9583333333333334 |
| golden_abstention | 0.041666666666666664 |
| refusal_correctness | 1.0 |
| fabricated_values_surfaced | 0 |
| wrong_values_surfaced | 1 |
| adversarial_rejection_rate | 0.9333333333333333 |
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
| adversarial|REJECT|rule:not_expired | 2 |
| golden|REFUSED|None | 6 |
| golden|REJECT|rule:surcharge_consistent | 1 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 518 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 544 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 573 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 614 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 455 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 931 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 553 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 486 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 462 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 1304 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 593 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 555 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 567 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 497 |
| G-015 | cross | ANSWER | REJECT | rule:surcharge_consistent |  | 539 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 585 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 589 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 600 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 560 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 2584 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 605 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 581 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 547 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 555 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 484 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1425 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 748 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 591 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2455 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 503 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 2838 | 496 |
| A-002 | superseded | NOT_ANSWER | REJECT | rule:not_expired |  | 483 |
| A-003 | superseded | NOT_ANSWER | REJECT | rule:not_expired |  | 473 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 586 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 479 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 492 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 452 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 469 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 949 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 1170 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 484 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 526 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 462 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 454 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 531 |
