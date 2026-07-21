from embedding import create_embedding
from similarity import cosine_similarity


def search_notes(
    query: str,
    stored_notes: list[dict],
    top_k: int = 3,
    minimum_score: float = 0.3,
) -> list[dict]:
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    query_embedding = create_embedding(query)

    results = []

    for item in stored_notes:
        score = cosine_similarity(
            query_embedding,
            item["embedding"],
        )

        if score >= minimum_score:
            results.append(
                {
                    "text": item["text"],
                    "score": score,
                }
            )

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return results[:top_k]