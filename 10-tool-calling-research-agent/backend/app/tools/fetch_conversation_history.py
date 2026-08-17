from pydantic import BaseModel


conversation_history: list[dict[str, str]] = []


class FetchConversationHistoryInput(BaseModel):
    limit: int = 10


def fetch_conversation_history(
    input_data: FetchConversationHistoryInput,
) -> str:
    history = conversation_history[-input_data.limit:]

    if not history:
        return "No conversation history available."

    return "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history
    )


FETCH_CONVERSATION_HISTORY_TOOL = {
    "type": "function",
    "name": "fetch_conversation_history",
    "description": "Retrieve recent conversation history.",
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of recent messages to return.",
                "minimum": 1,
                "maximum": 50,
            }
        },
        "required": [],
        "additionalProperties": False,
    },
}