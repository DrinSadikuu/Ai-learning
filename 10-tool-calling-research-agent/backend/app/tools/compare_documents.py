from pydantic import BaseModel

from app.services.vector_store_service import vector_store_service


class CompareDocumentsInput(BaseModel):
    first_document_id: str
    second_document_id: str


async def compare_documents(
    input_data: CompareDocumentsInput,
) -> str:
    first_documents = await vector_store_service.search(
        query="main topics summary",
        k=8,
        filter={
            "document_id": input_data.first_document_id
        },
    )

    second_documents = await vector_store_service.search(
        query="main topics summary",
        k=8,
        filter={
            "document_id": input_data.second_document_id
        },
    )

    if not first_documents or not second_documents:
        return "One or both documents could not be found."

    first_content = "\n\n".join(
        document.page_content
        for document in first_documents
    )

    second_content = "\n\n".join(
        document.page_content
        for document in second_documents
    )

    return f"""
FIRST DOCUMENT:
{first_content}

SECOND DOCUMENT:
{second_content}
"""

COMPARE_DOCUMENTS_TOOL = {
    "type": "function",
    "name": "compare_documents",
    "description": "Retrieve content from two documents so the agent can compare them.",
    "parameters": {
        "type": "object",
        "properties": {
            "first_document_id": {
                "type": "string",
            },
            "second_document_id": {
                "type": "string",
            },
        },
        "required": [
            "first_document_id",
            "second_document_id",
        ],
        "additionalProperties": False,
    },
}