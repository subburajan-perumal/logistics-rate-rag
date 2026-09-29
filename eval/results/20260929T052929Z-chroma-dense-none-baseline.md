# 20260929T052929Z-chroma-dense-none-baseline

Created: 2026-09-29T05:29:29Z · 0 live calls, 45 cache hits, $0.0000

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
| golden|REFUSED|None | 6 |

## Per-question

| id | tag | expected | outcome | reason | rate_value | ms |
|---|---|---|---|---|---|---|
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 1618 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 489 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 496 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 474 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 501 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 527 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 537 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 565 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 583 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 1198 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 537 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 490 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 495 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 715 |
| G-015 | cross | ANSWER | ANSWER |  | 1966 | 588 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 624 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 614 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 551 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 516 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 617 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 1399 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 614 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 570 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 511 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 833 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 472 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 464 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 485 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 482 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 523 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 2838 | 484 |
| A-002 | superseded | NOT_ANSWER | ANSWER |  | 1882 | 498 |
| A-003 | superseded | NOT_ANSWER | ANSWER |  | 2114 | 479 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 507 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 617 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 1035 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 481 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 477 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 485 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 508 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 489 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 476 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 484 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 496 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 507 |
