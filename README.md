# Logistics Rate RAG

A small Retrieval-Augmented Generation system that answers questions about
freight rate sheets, surcharge tariffs, and shipping policy documents.

## Why this exists

Built to close a real, confirmed gap: RAG and LangChain showed up as
explicit "0 years, not on record" answers across several job applications
in 2026 (6 of 12 postings asked about RAG specifically, 4 of 12 about
LangChain). Rather than a generic "chat with a PDF" tutorial project, this
deliberately reuses the freight/logistics domain from my day job
(an AI agent that extracts freight rates from carrier
documents) — the *problem domain* is the same, this project adds the
*retrieval* layer on top instead of just extraction.

**The documents in `data/sample_docs/` are synthetic** — written for this
project, not real carrier data. The day-job codebase itself is
proprietary and isn't reused here.

**Try it:** [live demo](https://logistics-rate-rag.streamlit.app) — ask a question, see the answer and the exact chunks the model was given (Streamlit Community Cloud; may take a minute to wake). It is the Phase 0 baseline chain; the guardrail gates land in later phases.

## What it does

- Loads the sample rate/tariff/policy documents
- Splits them into chunks and embeds them with Gemini's embedding model
- Stores the embeddings in a local Chroma vector store
- On a question: retrieves the most relevant chunks, and asks Gemini to
  answer using only that context, citing which document it came from

Built with LangChain's Expression Language (LCEL) — `retriever | prompt |
llm | parser` — rather than the older `RetrievalQA` wrapper, since LCEL
is the current idiomatic way to compose LangChain pipelines.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env          # then edit .env and add your own key
```

Get a free Gemini API key at <https://aistudio.google.com/apikey>. Never
commit `.env` — it's already gitignored.

## Run it

```bash
cd src
python cli.py
```

First run builds the vector store automatically (takes a few seconds).
Subsequent runs reuse the persisted store in `chroma_db/` (gitignored —
regenerate with `python ingest.py` if the sample docs change).

Example questions to try:
- "What's the base rate for a 40HC container from Chennai to Rotterdam?"
- "How much free time do I get at destination before demurrage kicks in?"
- "What's the difference between OTHC and DTHC?"
- "Is hazardous cargo covered under this rate sheet?"

## Project structure

```
data/sample_docs/   synthetic freight-rate/tariff/policy documents
src/config.py        env vars, model names, chunking parameters
src/ingest.py         load -> split -> embed -> persist (Chroma)
src/rag_chain.py      the actual LCEL RAG chain, with source citation
src/cli.py            interactive question loop
```

## Roadmap

This is the first of two planned extensions from the same base:
1. **This project** — RAG + LangChain (done)
2. **Agentic layer** — a planner/retriever multi-agent split using
   LangGraph or CrewAI on top of this same retrieval pipeline
3. **Amazon Bedrock** — a second LLM backend alongside Gemini, to show
   cross-cloud GenAI competence

Tracked in my second-brain vault under `2 Upskilling/Skills Roadmap/`.
