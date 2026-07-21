from embedding import create_embedding


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(
            vector_a,
            vector_b,
        )
    )

    magnitude_a = sum(
        value * value
        for value in vector_a
    ) ** 0.5

    magnitude_b = sum(
        value * value
        for value in vector_b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def retrieve_chunks(
    query: str,
    stored_chunks: list[dict],
    top_k: int = 5,
    minimum_score: float = 0.25,
    relative_threshold: float = 0.90,
) -> list[dict]:
    if not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    if not 0 < relative_threshold <= 1:
        raise ValueError(
            "relative_threshold must be "
            "between 0 and 1."
        )

    query_embedding = create_embedding(query)

    results = []

    for chunk in stored_chunks:
        score = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        if score >= minimum_score:
            results.append(
                {
                    "id": chunk["id"],
                    "file": chunk["file"],
                    "page": chunk["page"],
                    "text": chunk["text"],
                    "score": score,
                }
            )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    if not results:
        return []

    best_score = results[0]["score"]

    dynamic_minimum_score = (
        best_score * relative_threshold
    )

    relevant_results = [
        result
        for result in results
        if result["score"]
        >= dynamic_minimum_score
    ]

    return relevant_results[:top_k]