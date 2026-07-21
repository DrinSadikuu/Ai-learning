from assistant import answer_question
from retrieval import retrieve_chunks
from vector_store import load_chunks


def main() -> None:
    try:
        stored_chunks = load_chunks()

        if not stored_chunks:
            print("No vector store was found.")
            print(
                "Run build_vector_store.py first."
            )
            return

        print(
            f"Loaded {len(stored_chunks)} chunks."
        )
        print("PDF RAG Assistant")
        print("Type 'exit' to stop.\n")

        while True:
            question = input(
                "Question: "
            ).strip()

            if question.lower() == "exit":
                print("Goodbye.")
                break

            if not question:
                continue

            retrieved_chunks = retrieve_chunks(
                query=question,
                stored_chunks=stored_chunks,
                top_k=5,
                minimum_score=0.25,
                relative_threshold=0.90,
            )

            if not retrieved_chunks:
                print(
                    "\nAnswer: The documents do not "
                    "contain enough relevant "
                    "information.\n"
                )
                continue

            answer = answer_question(
                question=question,
                retrieved_chunks=retrieved_chunks,
            )

            print(f"\nAnswer: {answer}\n")

            print("Sources:")

            for chunk in retrieved_chunks:
                print(
                    f"- {chunk['file']}, "
                    f"page {chunk['page']}, "
                    f"chunk {chunk['id']} "
                    f"(similarity "
                    f"{chunk['score']:.4f})"
                )

            print()

    except ValueError as error:
        print(f"Value error: {error}")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()