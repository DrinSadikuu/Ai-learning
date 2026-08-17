from pydantic import BaseModel

from app.services.vector_store_service import vector_store_service


class SearchDocumentsInput(BaseModel):
    query : str

async def search_documents(input_data: SearchDocumentsInput) -> str:
    documents = await vector_store_service.search(
        query=input_data.query,
        k=4,
    )
    if not documents:
        return "No relevant documents found"

    return "\n\n".join(
        document.page_content
        for document in documents
    )


SEARCH_DOCUMENTS_TOOL = {
    "type": "function",
    "name": "search_documents",
    "description": "Search uploaded documents for information relevant to a user query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to use against the documents."
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


