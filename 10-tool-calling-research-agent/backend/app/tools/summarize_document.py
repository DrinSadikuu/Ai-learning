from pydantic import BaseModel

from app.services.vector_store_service import vector_store_service


class SummarizeDocumentInput(BaseModel):
    document_id: str


async def summarize_document(
    input_data: SummarizeDocumentInput,
) -> str:
    documents = await vector_store_service.search(
        query="summary overview main topics",
        k=8,
        filter={
            "document_id": input_data.document_id
        },
    )

    if not documents:
        return "No document found with that document_id."

    return "\n\n".join(
        document.page_content
        for document in documents
    )

SUMMARIZE_DOCUMENT_TOOL = {
    "type": "function",
    "name": "summarize_document",
    "description": "Retrieve content from one document so the agent can summarize it.",
    "parameters": {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "The unique ID of the document to summarize.",
            }
        },
        "required": ["document_id"],
        "additionalProperties": False,
    },
}