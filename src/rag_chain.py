"""The actual RAG chain: retriever -> prompt -> Gemini -> parsed answer,
built with LangChain's Expression Language (LCEL) rather than the older
RetrievalQA wrapper, plus source attribution so answers are traceable back
to a specific document.
"""

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from config import CHAT_MODEL, EMBEDDING_MODEL, PERSIST_DIR, RETRIEVAL_K, require_api_key

SYSTEM_PROMPT = """You are a logistics rate-desk assistant. Answer the \
question using ONLY the context below, which comes from carrier rate \
sheets, surcharge tariffs, and shipping policy documents.

If the context doesn't contain the answer, say so plainly instead of \
guessing. Cite the source file for any specific number or policy you \
state.

Context:
{context}"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
)


def format_docs_with_sources(docs) -> str:
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def load_vector_store() -> Chroma:
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(persist_directory=str(PERSIST_DIR), embedding_function=embeddings)


def build_chain():
    require_api_key()
    vector_store = load_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVAL_K})
    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)

    # RunnablePassthrough.assign keeps the retrieved docs available downstream
    # (for source citation) while also feeding the formatted context into the
    # prompt -- one retrieval call does both jobs.
    chain = (
        RunnablePassthrough.assign(docs=lambda x: retriever.invoke(x["question"]))
        | RunnablePassthrough.assign(
            context=lambda x: format_docs_with_sources(x["docs"])
        )
        | {
            "answer": PROMPT | llm | StrOutputParser(),
            "docs": lambda x: x["docs"],
        }
    )
    return chain


def ask(question: str):
    chain = build_chain()
    result = chain.invoke({"question": question})
    sources = sorted({doc.metadata.get("source", "unknown") for doc in result["docs"]})
    return result["answer"], sources
