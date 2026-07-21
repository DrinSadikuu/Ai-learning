from embedding import create_embedding
from notes import load_notes
from search import search_notes
from storage import load_embeddings, save_embeddings


def synchronize_embeddings(
    notes: list[str],
    stored_notes: list[dict],
) -> list[dict]:
    existing_embeddings = {
        item["text"]: item["embedding"]
        for item in stored_notes
        if "text" in item and "embedding" in item
    }

    synchronized_notes = []

    for note in notes:
        if note in existing_embeddings:
            embedding = existing_embeddings[note]
            print(f"Using saved embedding: {note}")
        else:
            print(f"Creating new embedding: {note}")
            embedding = create_embedding(note)

        synchronized_notes.append(
            {
                "text": note,
                "embedding": embedding,
            }
        )

    return synchronized_notes


def main() -> None:
    try:
        notes = load_notes("notes.txt")
        stored_notes = load_embeddings()

        print("Synchronizing notes...\n")

        synchronized_notes = synchronize_embeddings(
            notes=notes,
            stored_notes=stored_notes,
        )

        save_embeddings(synchronized_notes)

        print(
            f"\nReady with {len(synchronized_notes)} notes.\n"
        )

        print("Semantic Search")
        print("Type 'exit' to stop.\n")

        while True:
            query = input("Search: ").strip()

            if query.lower() == "exit":
                print("Goodbye.")
                break

            if not query:
                continue

            results = search_notes(
                query=query,
                stored_notes=synchronized_notes,
                top_k=3,
                minimum_score=0.3,
            )

            print("\nTop results:\n")

            for index, result in enumerate(results, start=1):
                print(f"{index}. {result['text']}")
                print(
                    f"   Similarity: "
                    f"{result['score']:.4f}\n"
                )

    except FileNotFoundError as error:
        print(f"File error: {error}")
    except ValueError as error:
        print(f"Value error: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()