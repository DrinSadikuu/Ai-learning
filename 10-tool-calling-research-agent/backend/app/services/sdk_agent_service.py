from agents import Agent, Runner, function_tool

from app.core.config import get_settings
from app.tools.search_documents import SearchDocumentsInput, search_documents
from app.tools.list_documents import ListDocumentsInput, list_documents
from app.tools.summarize_document import (
    SummarizeDocumentInput,
    summarize_document,
)
from app.tools.compare_documents import (
    CompareDocumentsInput,
    compare_documents,
)
from app.tools.fetch_conversation_history import (
    FetchConversationHistoryInput,
    fetch_conversation_history,
)


@function_tool
async def sdk_search_documents(query: str) -> str:
    input_data = SearchDocumentsInput(
        query=query
    )

    return await search_documents(input_data)


@function_tool
def sdk_list_documents() -> str:
    return list_documents(
        ListDocumentsInput()
    )


@function_tool
async def sdk_summarize_document(
    document_id: str,
) -> str:
    return await summarize_document(
        SummarizeDocumentInput(
            document_id=document_id
        )
    )


@function_tool
async def sdk_compare_documents(
    first_document_id: str,
    second_document_id: str,
) -> str:
    return await compare_documents(
        CompareDocumentsInput(
            first_document_id=first_document_id,
            second_document_id=second_document_id,
        )
    )


@function_tool
def sdk_fetch_conversation_history(
    limit: int = 10,
) -> str:
    return fetch_conversation_history(
        FetchConversationHistoryInput(
            limit=limit
        )
    )


settings = get_settings()


research_agent = Agent(
    name="Research Agent",
    instructions=(
        "Use the available tools when needed. "
        "Search documents for factual questions, "
        "list documents when asked what is available, "
        "summarize documents when requested, "
        "compare documents when requested, "
        "and use conversation history when relevant."
    ),
    model=settings.openai_model,
    tools=[
        sdk_search_documents,
        sdk_list_documents,
        sdk_summarize_document,
        sdk_compare_documents,
        sdk_fetch_conversation_history,
    ],
)


class SDKAgentService:
    async def run(self, message: str) -> str:
        result = await Runner.run(
            research_agent,
            message,
        )

        return result.final_output


sdk_agent_service = SDKAgentService()