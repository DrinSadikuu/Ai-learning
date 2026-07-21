import json
from pathlib import Path


VECTOR_STORE_PATH = Path("vector_store.json")


def save_chunks(chunks: list[dict]) -> None:
    with open(
        VECTOR_STORE_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_chunks() -> list[dict]:
    if not VECTOR_STORE_PATH.exists():
        return []

    with open(
        VECTOR_STORE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)