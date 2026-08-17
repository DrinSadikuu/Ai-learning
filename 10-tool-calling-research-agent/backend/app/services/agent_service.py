import json

from openai import AsyncOpenAI

from app.core.config import get_settings

from app.tools.search_documents import (
    SEARCH_DOCUMENTS_TOOL,
    SearchDocumentsInput,
    search_documents,
)

from app.tools.list_documents import (
    LIST_DOCUMENTS_TOOL,
    ListDocumentsInput,
    list_documents,
)

from app.tools.summarize_document import (
    SUMMARIZE_DOCUMENT_TOOL,
    SummarizeDocumentInput,
    summarize_document,
)

from app.tools.compare_documents import (
    COMPARE_DOCUMENTS_TOOL,
    CompareDocumentsInput,
    compare_documents,
)

from app.tools.fetch_conversation_history import (
    FETCH_CONVERSATION_HISTORY_TOOL,
    FetchConversationHistoryInput,
    fetch_conversation_history,
    conversation_history,
)


class AgentService:
    def __init__(self):
        settings = get_settings()

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

        self.model = settings.openai_model

    async def run(self, message: str) -> str:
        conversation_history.append(
            {
                "role": "user",
                "content": message,
            }
        )

        response = await self.client.responses.create(
            model=self.model,
            input=message,
            tools=[
                SEARCH_DOCUMENTS_TOOL,
                LIST_DOCUMENTS_TOOL,
                SUMMARIZE_DOCUMENT_TOOL,
                COMPARE_DOCUMENTS_TOOL,
                FETCH_CONVERSATION_HISTORY_TOOL,
            ],
        )

        for _ in range(5):
            tool_outputs = []

            for item in response.output:
                if item.type != "function_call":
                    continue

                if item.name == "search_documents":
                    arguments = json.loads(item.arguments)

                    tool_input = SearchDocumentsInput(
                        query=arguments["query"]
                    )

                    tool_result = await search_documents(
                        tool_input
                    )

                elif item.name == "list_documents":
                    tool_input = ListDocumentsInput()

                    tool_result = list_documents(
                        tool_input
                    )

                elif item.name == "summarize_document":
                    arguments = json.loads(item.arguments)

                    tool_input = SummarizeDocumentInput(
                        document_id=arguments["document_id"]
                    )

                    tool_result = await summarize_document(
                        tool_input
                    )

                elif item.name == "compare_documents":
                    arguments = json.loads(item.arguments)

                    tool_input = CompareDocumentsInput(
                        first_document_id=arguments["first_document_id"],
                        second_document_id=arguments["second_document_id"],
                    )

                    tool_result = await compare_documents(
                        tool_input
                    )

                elif item.name == "fetch_conversation_history":
                    arguments = json.loads(item.arguments)

                    tool_input = FetchConversationHistoryInput(
                        limit=arguments.get("limit", 10)
                    )

                    tool_result = fetch_conversation_history(
                        tool_input
                    )

                else:
                    continue

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": tool_result,
                    }
                )

            if not tool_outputs:
                answer = response.output_text

                conversation_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                return answer

            response = await self.client.responses.create(
                model=self.model,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=[
                    SEARCH_DOCUMENTS_TOOL,
                    LIST_DOCUMENTS_TOOL,
                    SUMMARIZE_DOCUMENT_TOOL,
                    COMPARE_DOCUMENTS_TOOL,
                    FETCH_CONVERSATION_HISTORY_TOOL,
                ],
            )

        answer = response.output_text

        conversation_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        return answer


agent_service = AgentService()