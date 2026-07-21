import json
from pathlib import Path


DATABASE_FILE = "embeddings.json"


def save_embeddings(stored_notes: list[dict]) -> None:
    path = Path(DATABASE_FILE)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            stored_notes,
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_embeddings() -> list[dict]:
    path = Path(DATABASE_FILE)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return data