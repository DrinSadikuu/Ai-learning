from pathlib import Path
from pydantic import BaseModel


class ListDocumentsInput(BaseModel):
    pass


def list_documents(input_data: ListDocumentsInput) -> str:
    uploads_path = Path("uploads")

    files = [
        file.name
        for file in uploads_path.iterdir()
        if file.is_file()
    ]

    if not files:
        return "No documents are available."

    return "\n".join(files)


LIST_DOCUMENTS_TOOL = {
    "type": "function",
    "name": "list_documents",
    "description": "List the documents currently available to the agent.",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}