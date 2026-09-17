"""Streamlit demo over the existing RAG chain in `src/` — a thin wrapper, not
a second implementation. Shows the answer *and* the retrieved chunks so a
reader can check whether the answer is grounded in the sources.

Status: this is the Phase 0 baseline chain (retriever → prompt → Gemini →
parser with source attribution). The deterministic guardrail gates the
project is about — schema-enforced output, business-rule validation,
grounding/confidence — are the next phases and are NOT in this demo yet.
"""

import os
import sys
from pathlib import Path

import streamlit as st

# Streamlit Community Cloud exposes secrets via st.secrets, not the
# environment; config.py reads the environment at import time.
try:
    if "GOOGLE_API_KEY" in st.secrets and not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception:  # no secrets file locally — .env is loaded by config.py
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config import CHAT_MODEL, DATA_DIR, EMBEDDING_MODEL, PERSIST_DIR, RETRIEVAL_K  # noqa: E402
from ingest import build_vector_store  # noqa: E402
from rag_chain import build_chain, load_vector_store  # noqa: E402

REPO = "https://github.com/subburajan-perumal/logistics-rate-rag"
MAX_QUESTIONS_PER_SESSION = 15

EXAMPLES = [
    "What is the 40HC base rate from Chennai to Rotterdam, and until when is it valid?",
    "What is the destination terminal handling charge for a 20GP, and is it included in the base rate?",
    "How many free days do I get at destination, and what is the detention charge on day 7?",
    "What is the cargo cutoff before vessel ETD?",
    # Not in the corpus — the chain should say so instead of guessing.
    "What is the 40GP rate from Chennai to Los Angeles?",
    "Does Meridian Ocean Lines offer a discount for booking 50 containers?",
]

st.set_page_config(page_title="logistics-rate-rag — ask the rate desk", layout="wide")


@st.cache_resource(show_spinner="Building the vector index from the sample documents (one-time)…")
def get_chain():
    # Build when the store is missing *or* empty — an interrupted build leaves
    # the directory behind with zero vectors, which retrieves nothing.
    if not Path(PERSIST_DIR).exists() or load_vector_store()._collection.count() == 0:
        build_vector_store()
    return build_chain()


st.title("logistics-rate-rag — ask the rate desk")
st.caption(
    f"RAG Q&A over three **synthetic** freight-rate documents (a Chennai→Rotterdam rate sheet, a "
    f"surcharge tariff, a shipping-terms policy). LangChain LCEL · Gemini `{CHAT_MODEL}` · "
    f"`{EMBEDDING_MODEL}` · Chroma (cosine, top-{RETRIEVAL_K}). [Code]({REPO})"
)
st.info(
    "**Where this project is:** this is the Phase 0 baseline chain with source attribution. "
    "The deterministic guardrail layer the project is building — schema-enforced output, "
    "business-rule validation, source-grounding/confidence gate, measured on an adversarial "
    "eval set — is the next phase and is not in this demo yet. Documents are invented; "
    "no employer data.",
    icon="ℹ️",
)

with st.sidebar:
    st.subheader("Corpus")
    for f in sorted(Path(DATA_DIR).glob("*.txt")):
        with st.expander(f.name):
            st.code(f.read_text(encoding="utf-8"), language=None)
    st.subheader("Try one")
    for i, q in enumerate(EXAMPLES):
        if st.button(q, key=f"ex{i}", width="stretch"):
            st.session_state["question"] = q

if "asked" not in st.session_state:
    st.session_state["asked"] = 0

question = st.text_input(
    "Question",
    value=st.session_state.get("question", ""),
    placeholder="e.g. What is the 40HC base rate from Chennai to Rotterdam?",
)
go = st.button("Ask", type="primary")

if go and question.strip():
    if st.session_state["asked"] >= MAX_QUESTIONS_PER_SESSION:
        st.warning("This demo is capped at 15 questions per session to stay inside the free API quota. Reload to start a new session.")
        st.stop()
    st.session_state["asked"] += 1
    try:
        chain = get_chain()
        with st.spinner("Retrieving and answering…"):
            result = chain.invoke({"question": question.strip()})
    except Exception as e:  # surface quota / key errors instead of a blank page
        st.error(f"The chain failed: {type(e).__name__}: {e}")
        st.stop()

    st.subheader("Answer")
    st.markdown(result["answer"])

    docs = result["docs"]
    sources = sorted({d.metadata.get("source", "unknown") for d in docs})
    st.caption("Sources: " + ", ".join(Path(s).name for s in sources))

    st.subheader(f"Retrieved context (top-{len(docs)} chunks the model was given)")
    st.caption(
        "This is the whole point of showing the chunks: if a number in the answer is not in "
        "these chunks, the model made it up. The upcoming grounding gate automates that check."
    )
    for i, d in enumerate(docs, 1):
        with st.expander(f"{i}. {Path(d.metadata.get('source', 'unknown')).name}"):
            st.code(d.page_content, language=None)

st.caption(
    f"{st.session_state['asked']}/{MAX_QUESTIONS_PER_SESSION} questions this session · "
    "free Gemini tier, so a burst of visitors may hit the rate limit — try again in a minute."
)
