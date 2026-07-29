SEARCH_DOCUMENTS_TOOL = {
    "type": "function",
    "name": "search_documents",
    "description": (
        "Search the uploaded documents when the user asks a question "
        "that requires information from those documents."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "A clear and specific search query used to find "
                    "relevant document passages."
                ),
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    "strict": True,
}