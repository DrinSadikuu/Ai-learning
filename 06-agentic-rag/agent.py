import json
from typing import Any

from config import create_openai_client
from evaluator import evaluate_retrieval
from query_rewriter import rewrite_query
from retrieval import search_documents
from tools import SEARCH_DOCUMENTS_TOOL


MODEL = "gpt-5"
MAX_TOOL_ROUNDS = 3


AGENT_INSTRUCTIONS = """
You are an AI assistant with access to uploaded documents.

Decide whether the user's question requires information from the documents.

Rules:
1. Call search_documents when the user asks about information that may be
   contained in the uploaded documents.
2. Do not call search_documents for greetings, casual conversation,
   general explanations, or questions that do not require the documents.
3. When document results are provided, answer only from those results.
4. Check whether the retrieved context explicitly answers the user's exact
   question.
5. A retrieval result contains an evaluation object.
6. Use document results only when evaluation.is_relevant is true.
7. If evaluation.is_relevant is false, do not use or cite the retrieved chunks.
8. If the documents do not contain enough information, respond with exactly:
   "The uploaded documents do not provide enough information to answer that."
   Do not add explanations and do not ask a follow-up question.
9. Include citations using this format:
   [filename, page X]
10. Never invent document facts, personal facts, or citations.
11. Do not repeatedly search for the same unsupported information.
"""


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    original_question: str,
) -> dict[str, Any]:
    """
    Execute a tool requested by the model.

    For search_documents:
    1. Read the model's search query.
    2. Rewrite it into a clearer semantic-search query.
    3. Retrieve relevant document chunks.
    4. Evaluate whether the chunks answer the original question.
    5. Return only relevant chunks to the agent.
    """

    if tool_name != "search_documents":
        raise ValueError(
            f"Unknown tool requested: {tool_name}"
        )

    model_query = str(
        arguments.get("query", "")
    ).strip()

    query_to_rewrite = model_query or original_question

    rewritten_query = rewrite_query(
        question=query_to_rewrite
    )

    print(
        f"\n[Rewritten query: {rewritten_query}]"
    )

    results = search_documents(
        query=rewritten_query
    )

    evaluation = evaluate_retrieval(
        question=original_question,
        results=results,
    )

    print(
        "\n[Retrieval evaluation: "
        f"relevant={evaluation['is_relevant']}, "
        f"confidence={evaluation['confidence']}, "
        f"reason={evaluation['reason']}]"
    )

    relevant_results = (
        results
        if evaluation["is_relevant"]
        else []
    )

    return {
        "original_question": original_question,
        "model_query": model_query,
        "rewritten_query": rewritten_query,
        "evaluation": evaluation,
        "results": relevant_results,
    }


def get_function_calls(response: Any) -> list[Any]:
    """
    Extract all function calls from an OpenAI response.
    """

    return [
        output_item
        for output_item in response.output
        if output_item.type == "function_call"
    ]


def run_agent(question: str) -> str:
    """
    Run the agent until it returns a text answer or reaches
    the maximum number of tool-call rounds.
    """

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError(
            "Question cannot be empty."
        )

    client = create_openai_client()

    response = client.responses.create(
        model=MODEL,
        instructions=AGENT_INSTRUCTIONS,
        input=cleaned_question,
        tools=[SEARCH_DOCUMENTS_TOOL],
    )

    used_queries: set[str] = set()

    for _ in range(MAX_TOOL_ROUNDS):
        function_calls = get_function_calls(
            response
        )

        # No function call means the model returned
        # a normal text answer.
        if not function_calls:
            answer = response.output_text.strip()

            if answer:
                return answer

            return (
                "The assistant did not produce "
                "a text response."
            )

        tool_outputs = []

        for function_call in function_calls:
            try:
                arguments = json.loads(
                    function_call.arguments
                )
            except json.JSONDecodeError:
                arguments = {}

            tool_result = execute_tool(
                tool_name=function_call.name,
                arguments=arguments,
                original_question=cleaned_question,
            )

            rewritten_query = str(
                tool_result.get(
                    "rewritten_query",
                    "",
                )
            ).strip()

            normalized_query = (
                rewritten_query.lower()
            )

            if normalized_query in used_queries:
                tool_result = {
                    "original_question": (
                        cleaned_question
                    ),
                    "rewritten_query": (
                        rewritten_query
                    ),
                    "evaluation": {
                        "is_relevant": False,
                        "confidence": 1.0,
                        "reason": (
                            "This query was already "
                            "searched."
                        ),
                    },
                    "results": [],
                    "message": (
                        "Do not search the same "
                        "query again."
                    ),
                }
            else:
                used_queries.add(
                    normalized_query
                )

            tool_outputs.append(
                {
                    "type": (
                        "function_call_output"
                    ),
                    "call_id": (
                        function_call.call_id
                    ),
                    "output": json.dumps(
                        tool_result,
                        ensure_ascii=False,
                    ),
                }
            )

        response = client.responses.create(
            model=MODEL,
            instructions=AGENT_INSTRUCTIONS,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=[SEARCH_DOCUMENTS_TOOL],
        )

    final_answer = (
        response.output_text.strip()
    )

    if final_answer:
        return final_answer

    return (
        "The uploaded documents do not provide "
        "enough information to answer that."
    )