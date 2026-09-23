"""Streamlit demo. Phase 0's baseline chain lived directly on top of the old
flat `src/` scaffold; Phase 2 replaced that scaffold with the real
`logistics_rate_rag` package (ingestion + Chroma store only — no answering
chain yet). This page is a maintenance-mode placeholder until Phase 3 ships
`chain/candidate_chain.py` and this demo is repointed at it.
"""

import streamlit as st

REPO = "https://github.com/subburajan-perumal/logistics-rate-rag"

st.set_page_config(page_title="logistics-rate-rag — ask the rate desk", layout="wide")

st.title("logistics-rate-rag — ask the rate desk")
st.warning(
    "**Temporarily rebuilding.** The Phase 0 baseline chain this demo ran on has been "
    "replaced by the real package (`src/logistics_rate_rag/`) as the project moves through "
    "its build phases — ingestion and the Chroma store are done (Phase 2), but the "
    "answering chain and the deterministic guardrail layer (schema validation, business "
    "rules, grounding/confidence) haven't shipped yet. This page will come back once "
    "Phase 3 wires the new chain in. Meanwhile, the phase-by-phase build is tracked "
    f"transparently in [`docs/PLAN.md`]({REPO}/blob/main/docs/PLAN.md).",
    icon="🛠️",
)
st.caption(f"[Code]({REPO})")
