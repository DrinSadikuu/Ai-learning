import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


RESULTS_FOLDER = Path("results")


def save_result(result: BaseModel, analysis_type: str) -> Path:
    RESULTS_FOLDER.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{analysis_type}_{timestamp}.json"
    file_path = RESULTS_FOLDER / filename

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            result.model_dump(),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return file_path