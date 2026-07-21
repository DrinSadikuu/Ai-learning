from chunking import split_text
from embedding import create_embedding
from pdf_loader import extract_pages_from_folder
from vector_store import save_chunks


DOCUMENTS_FOLDER = "documents"


def main() -> None:
    try:
        print("Loading PDF documents...\n")

        pages = extract_pages_from_folder(
            DOCUMENTS_FOLDER
        )

        if not pages:
            print(
                "No readable text was found "
                "in the PDF documents."
            )
            return

        total_characters = sum(
            len(page["text"])
            for page in pages
        )

        print()
        print(
            f"Extracted {total_characters} "
            "characters in total."
        )
        print(
            f"Found {len(pages)} readable pages.\n"
        )

        stored_chunks = []
        chunk_id = 1

        for page in pages:
            filename = page["file"]
            page_number = page["page"]
            page_text = page["text"]

            chunks = split_text(
                text=page_text,
                chunk_size=500,
                overlap_sentences=1,
            )

            for chunk in chunks:
                print(
                    f"Creating embedding {chunk_id} "
                    f"from {filename}, "
                    f"page {page_number}"
                )

                embedding = create_embedding(chunk)

                stored_chunks.append(
                    {
                        "id": chunk_id,
                        "file": filename,
                        "page": page_number,
                        "text": chunk,
                        "embedding": embedding,
                    }
                )

                chunk_id += 1

        save_chunks(stored_chunks)

        print("\nDone!")
        print(
            f"Saved {len(stored_chunks)} chunks "
            "to vector_store.json"
        )

    except FileNotFoundError as error:
        print(f"File error: {error}")

    except ValueError as error:
        print(f"Value error: {error}")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()