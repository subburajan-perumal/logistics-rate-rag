# LATEST

Regenerated from the newest run per configuration.

## Before / after the guardrails

**chroma · dense · reranker none** (`20260929T052929Z-chroma-dense-none-baseline` vs `20260929T053001Z-chroma-dense-none-gated`)

| Metric | Baseline (gates off) | Gated | Target |
|---|---|---|---|
| golden_accuracy | 0.958 | 0.958 | ≥ 0.90 |
| golden_abstention | 0.000 | 0.042 | reported |
| refusal_correctness | 1.000 | 1.000 | 1.00 |
| fabricated_values_surfaced | 0 | 0 | 0 |
| wrong_values_surfaced | 4 | 1 | 0 |
| adversarial_rejection_rate | 0.800 | 0.933 | ≥ 0.90 |
| injection_leak | 2 | 0 | 0 |
| latency_p50_ms | - | - | reported |

**chroma · hybrid · reranker flashrank** (`20260929T052343Z-chroma-hybrid-flashrank-baseline` vs `20260929T052503Z-chroma-hybrid-flashrank-gated`)

| Metric | Baseline (gates off) | Gated | Target |
|---|---|---|---|
| golden_accuracy | 0.958 | 0.958 | ≥ 0.90 |
| golden_abstention | 0.000 | 0.042 | reported |
| refusal_correctness | 1.000 | 1.000 | 1.00 |
| fabricated_values_surfaced | 0 | 0 | 0 |
| wrong_values_surfaced | 4 | 0 | 0 |
| adversarial_rejection_rate | 0.800 | 1.000 | ≥ 0.90 |
| injection_leak | 2 | 0 | 0 |
| latency_p50_ms | - | - | reported |

## Every configuration (newest run each)

| store | retrieval | reranker | mode | sets | golden_accuracy | wrong | fabricated | adversarial_rejection | run |
|---|---|---|---|---|---|---|---|---|---|
| chroma | dense | flashrank | gated | golden | 0.958 | 0 | 0 | - | `20260929T052712Z-chroma-dense-flashrank-gated` |
| chroma | dense | none | baseline | adversarial, golden | 0.958 | 4 | 0 | 0.800 | `20260929T052929Z-chroma-dense-none-baseline` |
| chroma | dense | none | gated | adversarial, golden | 0.958 | 1 | 0 | 0.933 | `20260929T053001Z-chroma-dense-none-gated` |
| chroma | hybrid | flashrank | baseline | adversarial, golden | 0.958 | 4 | 0 | 0.800 | `20260929T052343Z-chroma-hybrid-flashrank-baseline` |
| chroma | hybrid | flashrank | gated | adversarial, golden | 0.958 | 0 | 0 | 1.000 | `20260929T052503Z-chroma-hybrid-flashrank-gated` |
| chroma | hybrid | flashrank | gated | golden | 0.958 | 0 | 0 | - | `20260929T052805Z-chroma-hybrid-flashrank-gated` |
| chroma | hybrid | none | gated | golden | 0.958 | 0 | 0 | - | `20260929T052523Z-chroma-hybrid-none-gated` |

## Retrieval ladder (LLM-free recall over golden ANSWER questions)

| store | chunks | dense | hybrid | reranked | run |
|---|---|---|---|---|---|
| chroma | raw | 1.000 | 1.000 | 1.000 | `20260929T044811Z-chroma-recall` |
| chroma | enriched | 1.000 | 1.000 | 1.000 | `20260929T051554Z-chroma-recall-enriched` |

## Lifts and parity (gated golden accuracy)

| Metric | Value | Definition |
|---|---|---|
| store_parity | - | abs(chroma - pinecone), hybrid + flashrank; target <= 0.05 |
| rerank_lift | 0.000 | chroma hybrid: flashrank - none |
| hybrid_lift | 0.000 | chroma flashrank: hybrid - dense |
| enrichment_lift | 0.000 | chroma hybrid recall: enriched - raw |

Recorded LLM spend across all 17 eval run files: **$0.2753** (answer generation only; cost tracking started 2026-09-29).
