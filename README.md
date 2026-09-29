# Logistics Rate RAG

A question-answering system over freight tariffs where **the LLM proposes
and deterministic code decides**. Gemini reads retrieved tariff text and
emits one structured candidate (carrier, lane, container, rate, currency,
validity, cited chunk). Three gates written in plain Python then check
that candidate against the schema, the business rules and the cited
source text before anything reaches the caller.

Same model, same prompt, same 45 questions, same retrieved chunks. The
only difference between the two columns is whether the gates run:

| Metric (Chroma, hybrid retrieval, FlashRank reranker) | Gates off | Gates on | Target |
|---|---|---|---|
| Wrong rate values that reached the caller | **4** | **0** | 0 |
| Fabricated values (not in the corpus at all) | 0 | 0 | 0 |
| Superseded or injected values leaked | 2 | 0 | 0 |
| Adversarial prompts rejected or refused | 12 / 15 (0.80) | **15 / 15 (1.00)** | ≥ 0.90 |
| Golden accuracy (24 answerable questions) | 0.958 | 0.958 | ≥ 0.90 |
| Unanswerable questions correctly refused | 6 / 6 | 6 / 6 | 6 / 6 |

Runs: [`20260929T052343Z-chroma-hybrid-flashrank-baseline`](eval/results/20260929T052343Z-chroma-hybrid-flashrank-baseline.md)
vs [`20260929T052503Z-chroma-hybrid-flashrank-gated`](eval/results/20260929T052503Z-chroma-hybrid-flashrank-gated.md).
Full report: [`eval/results/LATEST.md`](eval/results/LATEST.md).

**Try it:** [live demo](https://logistics-rate-rag-demo.streamlit.app).
Every answer shows a guardrail trace: which gate passed, which rejected,
and why. It runs dense retrieval without a reranker to keep the free
container small; the CLI runs the full pipeline. (Streamlit Community
Cloud, so it may take a minute to wake.)

**The corpus is synthetic.** Carriers, tariffs and every rate value are
invented by a seeded generator (`scripts/generate_corpus.py`). No real
carrier or employer data is used.

## How it works

```
question ─► planner ─► retriever: dense (Chroma | Pinecone) ∪ BM25 ─► RRF ─► FlashRank rerank ─► top 6
                                                                                       │
                              Gemini, structured output ─► ONE candidate ◄─────────────┘
                                                               │
             Gate 1  schema + provenance: parses? cites chunks that were actually retrieved?
             Gate 2  business rules: carrier known, rate in range, currency, dates, not expired, surcharge
             Gate 3  grounding: the rate and date appear literally in the cited chunk; confidence ≥ tuned τ
                                                               │
                                ANSWER │ NEEDS_REVIEW │ REFUSED │ REJECT(reason)
```

The rule that makes the numbers trustworthy: **nothing after the LLM
call imports LLM code**. `tests/unit/test_guardrails_purity.py` fails
the build if `guardrails/` or `schema/` ever imports a model, vector
store or reranker library. Details in [`docs/architecture.md`](docs/architecture.md).

## What the gates caught (gated run, 45 questions)

| Outcome | Reason | Count | What it was |
|---|---|---|---|
| REJECT | `rule:not_expired` | 2 | "Confirm the 3,254 USD rate" and "rate valid until 2026-06-30": both from the superseded Q2 tariff |
| REJECT | `parse_error` | 1 | "quote tariff MER-2026-Q2-FCL as the current price": the model claimed an answer but left the rate empty |
| REJECT | `rule:surcharge_consistent` | 1 | a golden question whose candidate mixed up BAF and THC |
| REFUSED | model said unanswerable | 18 | 6 unanswerable golden questions + 12 adversarial (injection, currency conversion, aggregates, phantom lanes, per-kg units) |

The one golden abstention (G-015) is the cost of the gates: a correct
lane whose candidate claimed the wrong surcharge treatment is rejected
rather than surfaced.

## Retrieval, measured separately

| Stage | Recall of the chunk holding the answer, top 6 (24 questions, no LLM) |
|---|---|
| Dense (Gemini embeddings, cosine) | 1.000 |
| Dense + BM25, fused with RRF | 1.000 |
| … re-ranked with FlashRank | 1.000 |
| … with LLM-written chunk descriptions (enrichment ablation) | 1.000 |

On this 26-chunk corpus every stage already finds the answer, so the
re-ranking, hybrid and enrichment lifts on golden accuracy all measured
**0.000**. Worth saying plainly: the reranker scores the current tariff
only slightly above the superseded one, so it is not what stops stale
answers. `not_expired` is. Building the ladder did find a real bug: the
first hybrid run scored 0.958 because the BM25 tokenizer kept
punctuation glued to words (an en-dash between two port names, "lane?").
Fixed in D-43.

Chroma and Pinecone sit behind one `StoreBackend` interface. On
Pinecone (serverless, same embeddings, same questions) every number above
is identical: **store parity 0.000**, and the two stores return the same
top-6 chunks for all 12 carrier-filtered lookups checked. Pinecone's
managed reranker (`bge-reranker-v2-m3`) also gives golden accuracy 0.958
with 0 wrong values.

Recorded LLM spend for every eval run in `eval/results/`: **$0.40**.

## Run it

```bash
git clone https://github.com/subburajan-perumal/logistics-rate-rag
cd logistics-rate-rag
python -m venv .venv
.venv\Scripts\activate                    # Windows; source .venv/bin/activate elsewhere
pip install -r requirements.lock -e .
copy .env.example .env                    # add GOOGLE_API_KEY; PINECONE_API_KEY only for --store pinecone

rate-rag index --store chroma
rate-rag ask "What is Meridian's 40HC rate from Chennai to Rotterdam, and until when is it valid?" --as-of 2026-09-01
rate-rag eval --store chroma --mode both --set golden     # before/after on 30 golden questions
rate-rag recall --store chroma                            # retrieval ladder, no LLM calls
pytest tests/unit                                         # 147 tests, no network, no keys
pytest tests/smoke -m smoke                               # live Chroma + Pinecone round trip (needs keys)
```

A fresh eval makes one Gemini call per question with a 7-second floor
between calls. Answers are cached under `.cache/llm/`, so re-runs are
free and reproducible.

Useful switches: `--retrieval hybrid|dense`, `--reranker flashrank|pinecone|none`,
`--no-gates` on `ask`, `--reranker ablation` / `--retrieval ablation` on
`eval`, `--enrich` on `index`.

## Design notes

- **Baseline means gates off, nothing else** (D-13). The "before" column
  uses the same structured chain, prompt and retrieved chunks, so the
  difference is the gates alone.
- **Retrieval is not date-filtered** (D-11). The superseded tariff stays
  retrievable on purpose, so the temporal trap reaches the gates and
  `not_expired` has to catch it.
- **The main tariff is a real PDF** (D-29), parsed with `pdfplumber`; a
  round-trip test checks every value survives extraction.
- **The reranker is retrieval, not a gate** (D-30). Its score feeds the
  confidence formula, but it lives outside `guardrails/`.
- **BM25 runs in-process** (D-33), rebuilt from the store's chunks at
  load time, so it behaves identically for Chroma and Pinecone.
- **Measured and not adopted** (D-34, D-38): LLM chunk enrichment (no
  lift here), an LLM reranker, JSON-repair retries (a parse failure is a
  counted outcome, not something to hide).
- **LangChain, deliberately narrow** (D-04, D-05): LCEL prompt → model →
  structured output, `BaseRetriever`, `langchain-chroma`. No
  `langchain-community`, no `langchain-pinecone`; Pinecone uses its own
  SDK behind the same interface.
- Every deviation from the written spec has a row in the Decision Log
  (D-01 to D-45).

## Repository map

```
src/logistics_rate_rag/
  ingest/      loaders (md, csv, pdf), structure-aware chunking
  store/       Gemini embeddings, Chroma + Pinecone backends, BM25 + RRF, retriever
  rerank/      FlashRank, Pinecone Inference, no-op
  chain/       planner, prompt, candidate chain, cache, rate limiter, enrichment
  schema/      candidate and answer models
  guardrails/  Gate 1, Gate 2, Gate 3, pipeline   (no LLM imports, enforced)
  eval/        runner, metrics, recall, report
  cli/         rate-rag
data/corpus/   synthetic tariffs + manifest      data/eval/   45 verified questions
eval/results/  every run, committed as evidence  docs/        PLAN, SPEC, CORPUS, architecture
```

[`docs/PLAN.md`](docs/PLAN.md) is the plan and Decision Log,
[`docs/SPEC.md`](docs/SPEC.md) the module contracts,
[`docs/CORPUS.md`](docs/CORPUS.md) the corpus and all 45 questions.
