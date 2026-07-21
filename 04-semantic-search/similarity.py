import math


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same length.")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)