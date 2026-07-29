import json
from pathlib import Path

import numpy as np

from config import create_openai_client


VECTOR_STORE_PATH = Path("data/vector_store.json")
EMBEDDING_MODEL = "text-embedding-3-small"


def load_vector_store() -> list[dict]:
    """
    Load all document chunks and embeddings from vector_store.json.
    """

    if not VECTOR_STORE_PATH.exists():
        raise FileNotFoundError(
            f"Vector store was not found at: "
            f"{VECTOR_STORE_PATH.resolve()}"
        )

    with VECTOR_STORE_PATH.open("r", encoding="utf-8") as file:
        vector_store = json.load(file)

    if not isinstance(vector_store, list):
        raise ValueError(
            "vector_store.json must contain a JSON list."
        )

    return vector_store


def create_query_embedding(query: str) -> list[float]:
    """
    Convert the user's search query into an embedding.
    """

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("Search query cannot be empty.")

    client = create_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=cleaned_query,
    )

    return response.data[0].embedding


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.
    """

    a = np.array(vector_a, dtype=np.float32)
    b = np.array(vector_b, dtype=np.float32)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    similarity = np.dot(a, b) / denominator

    return float(similarity)


def clean_text(text: str) -> str:
    """
    Clean common PDF extraction artifacts.
    """

    cleaned_text = text.replace("\x7f", "•")
    cleaned_text = cleaned_text.replace("\uf0b7", "•")

    return " ".join(cleaned_text.split())


def search_documents(
    query: str,
    top_k: int = 5,
    minimum_score: float = 0.25,
) -> list[dict]:
    """
    Search vector_store.json and return the most relevant chunks.
    """

    vector_store = load_vector_store()
    query_embedding = create_query_embedding(query)

    results = []

    for chunk in vector_store:
        chunk_embedding = chunk.get("embedding")

        if not chunk_embedding:
            continue

        score = cosine_similarity(
            query_embedding,
            chunk_embedding,
        )

        if score < minimum_score:
            continue

        result = {
            "id": chunk.get("id"),
            "filename": chunk.get(
                "file",
                "Unknown document",
            ),
            "page": chunk.get("page"),
            "text": clean_text(
                chunk.get("text", "")
            ),
            "score": round(score, 4),
        }

        results.append(result)

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return results[:top_k]