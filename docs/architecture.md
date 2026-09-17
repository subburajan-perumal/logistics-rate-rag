# Architecture

How a question becomes an answer, a review request, a refusal or a
rejection — and which code is allowed to make each decision. Contracts
are in [`SPEC.md`](SPEC.md), data in [`CORPUS.md`](CORPUS.md), decisions
in [`PLAN.md`](PLAN.md) §3.

## 1. The one-sentence design

The LLM produces **one structured candidate** from retrieved text; three
deterministic gates — schema/provenance, business rules, grounding +
confidence — decide whether that candidate may leave the system. Nothing
after the LLM call imports LLM code; a test enforces it.

## 2. Request path

```
question, as_of
   │
   ▼
QueryPlanner (chain/planner.py) ── deterministic ──► QueryPlan{filter by carrier?, as_of override?, mentions_surcharge}
   │
   ▼
RateRetriever (store/retriever.py)
   ├── GeminiEmbedder.embed_query ──► 768-d, L2-normalised
   ├── dense:   StoreBackend.query(vector, k=12, filter)      Chroma (local) │ Pinecone (managed)
   ├── lexical: LexicalIndex.query(question, k=12)            BM25 over the same 26 chunks, in-process
   ├── fuse_rrf(dense, lexical, k=60) ──► top-12
   └── Reranker.rerank(question, top-12, top_n=6)             FlashRank (local ONNX) │ Pinecone bge-reranker-v2-m3 │ none
   │
   ▼  6 RetrievedChunk (rank, similarity_norm, rerank_score, …)
context.py ── order by (doc, chunk index); append pinned policy chunks (scope=global)
   │
   ▼
CandidateChain (chain/candidate_chain.py)
   ├── ResponseCache.get(key)  ── hit ──► cached parsed candidate
   └── miss: RateLimiter.wait(); ChatPromptTemplate | ChatGoogleGenerativeAI(gemini-3.6-flash, thinking minimal, seed 42)
             .with_structured_output(RateCandidate, method="json_schema", include_raw=True)
   │
   ▼  CandidateResult{candidate | parsing_error, retrieved, pinned, usage}
run_gates (guardrails/pipeline.py)          ← pure Python from here on
   ├── Gate 1  gate1_schema      parse? refusal clean? required fields? ports known? cited chunk ids retrieved? doc matches?
   │            fail ──► REJECT(parse_error | unknown_port | unknown_source)      refusal ──► REFUSED
   ├── Gate 2  gate2_rules       carrier_known · rate_in_range · currency_matches_source · dates_ordered · not_expired · surcharge_consistent
   │            fail ──► REJECT(rule:<name>)
   ├── Gate 3a gate3_grounding   rate_value, valid_to and source_span literally present in the cited chunk text
   │            fail ──► REJECT(ungrounded:<field>)
   └── Gate 3b gate3_confidence  0.35·model + 0.25·similarity + 0.30·rerank + 0.10·(1/rank) ≥ τ (tuned)
                fail ──► NEEDS_REVIEW (sources only, no values)
   │
   ▼
ANSWER — RateAnswer with source doc, chunk id, span, score, usage
```

Baseline mode (`GATES_ENABLED=false`) is the same path with `run_gates`
replaced by a pass-through: it is what the "before" column in the eval
report measures.

## 3. Index path

```
data/corpus/*  ──► loaders (md / csv / pdf via pdfplumber) ──► LoadedDocument (canonical text)
               ──► chunking (header block replicated into every table chunk; 4 lanes/chunk md+pdf, 6 rows/chunk csv, 1 section/chunk policy)
               ──► 26 Chunk{chunk_id, text, metadata, content_sha256}
               ──► [optional --enrich: LLM description prepended to index_text only]
               ──► GeminiEmbedder.embed_documents (batches of 100, normalised)
               ──► StoreBackend.upsert (diff by chunk_id + content hash → idempotent)
               ──► Pinecone only: wait until describe_index_stats shows the count
```

`LexicalIndex` is rebuilt from `StoreBackend.all_chunks()` at load time
and never persisted.

## 4. Who may decide what

| Decision | Made by | May use an LLM? |
|---|---|---|
| Which carrier to filter on | `QueryPlanner` (alias regex) | no |
| What the as-of date is | CLI/eval + `QueryPlanner` override | no |
| Which chunks the model sees | retriever + reranker + pinning | no (cross-encoder is a fixed model, not a generator) |
| What the candidate answer is | `CandidateChain` | **yes — the only place** |
| Whether the candidate parses and cites real chunks | Gate 1 | no |
| Whether the candidate obeys business rules | Gate 2 | no |
| Whether the numbers are literally in the cited text | Gate 3a | no |
| Whether to surface, review or reject | Gate 3b + pipeline | no |

`tests/unit/test_guardrails_purity.py` fails the build if any module
under `guardrails/` or `schema/` imports `chain`, `store`, `rerank`, or
any LLM/vector/reranker library.

## 5. Why retrieval is not date-filtered (D-11)

The superseded Q2 tariff is retrievable on purpose. Filtering it out at
retrieval time would make the temporal trap disappear before the
guardrails ever saw it, and the project's claim is that the **rules**
catch it (`not_expired`). The eval's gate breakdown shows exactly how
many candidates Gate 2 stopped for that reason.

## 6. Module dependency graph (arrows = "imports from")

```
cli ──► eval ──► chain ──► store ──► ingest ──► errors/config
 │        │        │         │
 │        │        │         └──► rerank
 │        │        └──► schema
 │        └──► guardrails ──► schema, config, errors     (nothing else)
 └──► ingest, store, rerank, chain, guardrails, schema
```

`schema` and `guardrails` have no arrow to `chain`, `store` or `rerank`
by construction.

## 7. Determinism boundaries

| Component | Deterministic? | Why / how |
|---|---|---|
| Corpus, chunks, chunk ids, hashes | yes | seeded generator; frozen files; content hashes |
| Embeddings | API-dependent | same input → same vector in practice; index is diffed by content hash, not by vector |
| Dense search | yes for a fixed index | cosine over stored vectors |
| BM25, RRF | yes | pure functions, explicit tie-breaks |
| FlashRank | yes | ONNX inference, verified bit-identical |
| Pinecone rerank | API-dependent | used only in the Pinecone runs |
| LLM candidate | **no** (Gemini fixes sampling; thinking minimal, seed set) | response cache makes every re-run reproducible |
| Gates | yes | pure Python, config-driven |
| Eval metrics | yes | pure functions over result rows |

The README claim is therefore: *the guardrails are deterministic and the
evaluation is reproducible; the model is a probabilistic component that
is contained, not trusted.*
