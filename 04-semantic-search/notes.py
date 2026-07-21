from pathlib import Path


def load_notes(file_path: str) -> list[str]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Notes file was not found: {file_path}")

    notes = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            note = line.strip()

            if note:
                notes.append(note)

    return notes