import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_DIRECTORY = Path("logs")
LOG_FILE_PATH = LOG_DIRECTORY / "agent_logs.jsonl"


def write_log(log_data: dict[str, Any]) -> None:
    """
    Append one agent interaction to a JSONL log file.

    JSONL means that every line is a separate JSON object.
    """

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_entry = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        **log_data,
    }

    with LOG_FILE_PATH.open(
        "a",
        encoding="utf-8",
    ) as log_file:
        log_file.write(
            json.dumps(
                log_entry,
                ensure_ascii=False,
            )
        )

        log_file.write("\n")