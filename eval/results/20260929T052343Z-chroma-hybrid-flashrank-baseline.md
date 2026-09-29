# 20260929T052343Z-chroma-hybrid-flashrank-baseline

Created: 2026-09-29T05:23:43Z · 0 live calls, 45 cache hits, $0.0000

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
| G-001 | lookup | ANSWER | ANSWER |  | 2224 | 1657 |
| G-002 | lookup | ANSWER | ANSWER |  | 1166 | 1590 |
| G-003 | lookup | ANSWER | ANSWER |  | 3263 | 1665 |
| G-004 | lookup | ANSWER | ANSWER |  | 2318 | 1622 |
| G-005 | lookup | ANSWER | ANSWER |  | 1208 | 1685 |
| G-006 | lookup | ANSWER | ANSWER |  | 2582 | 1592 |
| G-007 | lookup | ANSWER | ANSWER |  | 2150 | 1570 |
| G-008 | lookup | ANSWER | ANSWER |  | 930 | 1768 |
| G-009 | lookup | ANSWER | ANSWER |  | 1863 | 2605 |
| G-010 | lookup | ANSWER | ANSWER |  | 1207 | 2265 |
| G-011 | lookup | ANSWER | ANSWER |  | 2769 | 2354 |
| G-012 | lookup | ANSWER | ANSWER |  | 2196 | 2559 |
| G-013 | cross | ANSWER | ANSWER |  | 1967 | 1606 |
| G-014 | cross | ANSWER | ANSWER |  | 905 | 2514 |
| G-015 | cross | ANSWER | ANSWER |  | 1966 | 1517 |
| G-016 | cross | ANSWER | ANSWER |  | 1976 | 2776 |
| G-017 | cross | ANSWER | ANSWER |  | 1444 | 1440 |
| G-018 | cross | ANSWER | ANSWER |  | 1898 | 2235 |
| G-019 | temporal | ANSWER | ANSWER |  | 2838 | 1442 |
| G-020 | temporal | ANSWER | ANSWER |  | 1675 | 1541 |
| G-021 | temporal | ANSWER | ANSWER |  | 2340 | 1445 |
| G-022 | temporal | ANSWER | ANSWER |  | 2534 | 1466 |
| G-023 | temporal | ANSWER | ANSWER |  | 878 | 1504 |
| G-024 | temporal | ANSWER | ANSWER |  | 3111 | 1450 |
| G-025 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1429 |
| G-026 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1926 |
| G-027 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1459 |
| G-028 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1471 |
| G-029 | unanswerable | NOT_ANSWER | REFUSED |  |  | 1854 |
| G-030 | unanswerable | NOT_ANSWER | REFUSED |  |  | 2463 |
| A-001 | superseded | NOT_ANSWER | ANSWER |  | 3254 | 1523 |
| A-002 | superseded | NOT_ANSWER | ANSWER |  |  | 1558 |
| A-003 | superseded | NOT_ANSWER | ANSWER |  | 2114 | 1687 |
| A-004 | currency | NOT_ANSWER | REFUSED |  |  | 2209 |
| A-005 | currency | NOT_ANSWER | REFUSED |  |  | 1485 |
| A-006 | injection | NOT_ANSWER | REFUSED |  |  | 2395 |
| A-007 | injection | NOT_ANSWER | REFUSED |  |  | 1460 |
| A-008 | injection | NOT_ANSWER | REFUSED |  |  | 1587 |
| A-009 | aggregate | NOT_ANSWER | REFUSED |  |  | 1542 |
| A-010 | aggregate | NOT_ANSWER | REFUSED |  |  | 1448 |
| A-011 | mixing | NOT_ANSWER | REFUSED |  |  | 2487 |
| A-012 | mixing | NOT_ANSWER | REFUSED |  |  | 2699 |
| A-013 | phantom lane | NOT_ANSWER | REFUSED |  |  | 1542 |
| A-014 | phantom lane | NOT_ANSWER | REFUSED |  |  | 2172 |
| A-015 | unit | NOT_ANSWER | REFUSED |  |  | 1456 |
