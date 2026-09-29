# LATEST

Regenerated from the newest run per configuration.

## Before / after the guardrails

**chroma · dense · reranker none** (`20260923T070638Z-chroma-dense-none-baseline` vs `20260923T074853Z-chroma-dense-none-gated`)

| Metric | Baseline (gates off) | Gated | Target |
|---|---|---|---|
| golden_accuracy | 0.958 | 0.958 | ≥ 0.90 |
| golden_abstention | 0.000 | 0.042 | reported |
| refusal_correctness | 1.000 | 1.000 | 1.00 |
| fabricated_values_surfaced | 0 | 0 | 0 |
| wrong_values_surfaced | 4 | 1 | 0 |
| adversarial_rejection_rate | 0.000 | 0.133 | ≥ 0.90 |
| injection_leak | 2 | 0 | 0 |
| latency_p50_ms | 7063 | - | reported |

## Every configuration (newest run each)

| store | retrieval | reranker | mode | golden_accuracy | wrong | fabricated | adversarial_rejection | cost_usd | run |
|---|---|---|---|---|---|---|---|---|---|
| chroma | dense | none | baseline | 0.958 | 4 | 0 | 0.000 | 0.0000 | `20260923T070638Z-chroma-dense-none-baseline` |
| chroma | dense | none | gated | 0.958 | 1 | 0 | 0.133 | 0.0000 | `20260923T074853Z-chroma-dense-none-gated` |

## Retrieval ladder (LLM-free recall over golden ANSWER questions)

| store | dense | hybrid | reranked | run |
|---|---|---|---|---|
| chroma | 1.000 | 1.000 | 1.000 | `20260929T044811Z-chroma-recall` |

## Lifts and parity (gated golden accuracy)

| Metric | Value | Definition |
|---|---|---|
| store_parity | - | abs(chroma - pinecone), hybrid + flashrank; target <= 0.05 |
| rerank_lift | - | chroma hybrid: flashrank - none |
| hybrid_lift | - | chroma flashrank: hybrid - dense |

Total LLM cost across the runs above: **$0.0000**.
