"""Load the sample freight-rate documents, split them, embed them, and
persist a Chroma vector store. Run once (or whenever the source documents
change) before asking questions with rag_chain.py.
"""

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_DIR,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    PERSIST_DIR,
    require_api_key,
)


def load_documents():
    loader = DirectoryLoader(
        str(DATA_DIR),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    return loader.load()


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def build_vector_store():
    require_api_key()
    documents = load_documents()
    print(f"Loaded {len(documents)} source document(s) from {DATA_DIR}")

    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunks "
          f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL, output_dimensionality=EMBEDDING_DIM
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
        collection_metadata={"hnsw:space": "cosine"},
    )
    print(f"Persisted vector store to {PERSIST_DIR} "
          f"({vector_store._collection.count()} vectors)")
    return vector_store


if __name__ == "__main__":
    build_vector_store()
