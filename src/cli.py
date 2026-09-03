"""Interactive CLI: ask questions about the sample freight-rate documents."""

from pathlib import Path

from config import PERSIST_DIR
from ingest import build_vector_store
from rag_chain import ask


def ensure_index():
    if not Path(PERSIST_DIR).exists():
        print("No vector store found yet -- building one from the sample docs...")
        build_vector_store()
        print()


def main():
    ensure_index()
    print("=" * 60)
    print("Logistics Rate RAG -- ask about the sample carrier rate sheet,")
    print("surcharge tariff, and shipping policy documents.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    while True:
        question = input("\nQuestion: ").strip()
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Bye.")
            break

        answer, sources = ask(question)
        print(f"\nAnswer:\n{answer}")
        print(f"\nSources: {', '.join(sources)}")


if __name__ == "__main__":
    main()
