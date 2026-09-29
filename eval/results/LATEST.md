# LATEST

Regenerated from the newest run per configuration on corpus v3. Runs on older corpus versions stay in this folder as history.

## Before / after the guardrails

**chroma · hybrid · reranker flashrank** (`20260929T105344Z-chroma-hybrid-flashrank-baseline` vs `20260929T110856Z-chroma-hybrid-flashrank-gated`)

| Metric | Baseline (gates off) | Gated | Target |
|---|---|---|---|
| golden_accuracy | 0.925 | 0.838 | ≥ 0.90 |
| golden_abstention | 0.037 | 0.163 | reported |
| refusal_correctness | 0.950 | 1.000 | 1.00 |
| fabricated_values_surfaced | 0 | 0 | 0 |
| wrong_values_surfaced | 8 | 1 | 0 |
| adversarial_rejection_rate | 0.867 | 0.967 | ≥ 0.90 |
| injection_leak | 2 | 0 | 0 |
| latency_p50_ms | 7085 | 6964 | reported |

**pinecone · hybrid · reranker flashrank** (`20260929T105344Z-pinecone-hybrid-flashrank-baseline` vs `20260929T110904Z-pinecone-hybrid-flashrank-gated`)

| Metric | Baseline (gates off) | Gated | Target |
|---|---|---|---|
| golden_accuracy | 0.925 | 0.863 | ≥ 0.90 |
| golden_abstention | 0.037 | 0.138 | reported |
| refusal_correctness | 0.950 | 1.000 | 1.00 |
| fabricated_values_surfaced | 0 | 0 | 0 |
| wrong_values_surfaced | 9 | 2 | 0 |
| adversarial_rejection_rate | 0.833 | 0.933 | ≥ 0.90 |
| injection_leak | 0 | 0 | 0 |
| latency_p50_ms | 7109 | 7053 | reported |

## Every configuration (newest run each)

| store | retrieval | reranker | mode | sets | golden_accuracy | wrong | fabricated | adversarial_rejection | run |
|---|---|---|---|---|---|---|---|---|---|
| chroma | hybrid | flashrank | baseline | adversarial, golden | 0.925 | 8 | 0 | 0.867 | `20260929T105344Z-chroma-hybrid-flashrank-baseline` |
| chroma | hybrid | flashrank | gated | adversarial, golden | 0.838 | 1 | 0 | 0.967 | `20260929T110856Z-chroma-hybrid-flashrank-gated` |
| pinecone | hybrid | flashrank | baseline | adversarial, golden | 0.925 | 9 | 0 | 0.833 | `20260929T105344Z-pinecone-hybrid-flashrank-baseline` |
| pinecone | hybrid | flashrank | gated | adversarial, golden | 0.863 | 2 | 0 | 0.933 | `20260929T110904Z-pinecone-hybrid-flashrank-gated` |

## Retrieval ladder (LLM-free recall over golden ANSWER questions)

| store | chunks | BM25 query expansion | dense | hybrid | reranked | run |
|---|---|---|---|---|---|---|
| chroma | raw | off | 0.963 | 0.988 | 0.988 | `20260929T093902Z-chroma-recall-noexpand` |
| chroma | raw | on | 0.963 | 1.000 | 1.000 | `20260929T093732Z-chroma-recall` |
| pinecone | raw | off | 0.963 | 0.963 | 0.975 | `20260929T094434Z-pinecone-recall-noexpand` |
| pinecone | raw | on | 0.963 | 0.988 | 1.000 | `20260929T094254Z-pinecone-recall` |

## Lifts and parity (gated golden accuracy)

| Metric | Value | Definition |
|---|---|---|
| store_parity | 0.025 | abs(chroma - pinecone), hybrid + flashrank; target <= 0.05 |
| rerank_lift | - | chroma hybrid: flashrank - none |
| hybrid_lift | - | chroma flashrank: hybrid - dense |
| enrichment_lift | - | chroma hybrid recall: enriched - raw |
| query_expansion_lift | 0.013 | chroma hybrid recall: expansion on - off (D-48) |

Recorded LLM spend on corpus v3: **$2.7915**; across all 28 eval run files: $3.9234 (answer generation only; cost tracking started 2026-09-29).
