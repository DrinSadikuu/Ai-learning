import json
from typing import Any

from config import create_openai_client
from evaluator import evaluate_retrieval
from logger import write_log
from query_rewriter import rewrite_query
from retrieval import search_documents
from tools import SEARCH_DOCUMENTS_TOOL


MODEL = "gpt-5"
MAX_TOOL_ROUNDS = 3


AGENT_INSTRUCTIONS = """
You are an AI assistant with access to uploaded documents and conversation
history.

Decide whether the user's latest question requires information from the
uploaded documents.

Rules:
1. Use conversation history to understand follow-up questions.
2. Call search_documents when the latest user question requires information
   that may be contained in the uploaded documents.
3. Do not call search_documents for greetings, casual conversation, general
   explanations, or questions that do not require the documents.
4. When document results are provided, answer only from those results.
5. Check whether the retrieved context explicitly answers the user's exact
   question.
6. A retrieval result contains an evaluation object.
7. Use document results only when evaluation.is_relevant is true.
8. If evaluation.is_relevant is false, do not use or cite the chunks.
9. If the documents do not contain enough information, respond with exactly:
   "The uploaded documents do not provide enough information to answer that."
   Do not add explanations or ask follow-up questions.
10. Include citations using this format:
    [filename, page X]
11. Never invent document facts, personal facts, or citations.
12. Do not repeatedly search using the same query.
"""


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    original_question: str,
) -> dict[str, Any]:
    """
    Execute a tool requested by the model.
    """

    if tool_name != "search_documents":
        raise ValueError(
            f"Unknown tool requested: {tool_name}"
        )

    model_query = str(
        arguments.get("query", "")
    ).strip()

    query_to_rewrite = (
        model_query or original_question
    )

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


def get_function_calls(
    response: Any,
) -> list[Any]:
    """
    Extract function calls from an OpenAI response.
    """

    return [
        output_item
        for output_item in response.output
        if output_item.type == "function_call"
    ]


def build_conversation_input(
    conversation_history: list[dict[str, str]],
    current_question: str,
) -> list[dict[str, str]]:
    """
    Combine previous messages with the current question.
    """

    conversation_input = list(
        conversation_history
    )

    conversation_input.append(
        {
            "role": "user",
            "content": current_question,
        }
    )

    return conversation_input


def run_agent(
    question: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """
    Run the agent and log its decisions.
    """

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError(
            "Question cannot be empty."
        )

    if conversation_history is None:
        conversation_history = []

    client = create_openai_client()

    conversation_input = build_conversation_input(
        conversation_history=conversation_history,
        current_question=cleaned_question,
    )

    response = client.responses.create(
        model=MODEL,
        instructions=AGENT_INSTRUCTIONS,
        input=conversation_input,
        tools=[SEARCH_DOCUMENTS_TOOL],
    )

    used_queries: set[str] = set()
    tool_rounds = 0
    tool_logs: list[dict[str, Any]] = []

    for _ in range(MAX_TOOL_ROUNDS):
        function_calls = get_function_calls(
            response
        )

        if not function_calls:
            answer = response.output_text.strip()

            if not answer:
                answer = (
                    "The assistant did not produce "
                    "a text response."
                )

            write_log(
                {
                    "question": cleaned_question,
                    "tool_rounds": tool_rounds,
                    "tools": tool_logs,
                    "final_answer": answer,
                }
            )

            return answer

        tool_rounds += 1
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
                rewritten_query.casefold()
            )

            if normalized_query in used_queries:
                tool_result = {
                    "original_question": cleaned_question,
                    "rewritten_query": rewritten_query,
                    "evaluation": {
                        "is_relevant": False,
                        "confidence": 1.0,
                        "reason": (
                            "This query was already searched."
                        ),
                    },
                    "results": [],
                }
            else:
                used_queries.add(
                    normalized_query
                )

            tool_logs.append(
                {
                    "tool_name": function_call.name,
                    "arguments": arguments,
                    "rewritten_query": tool_result.get(
                        "rewritten_query"
                    ),
                    "evaluation": tool_result.get(
                        "evaluation"
                    ),
                    "retrieved_results": tool_result.get(
                        "results",
                        [],
                    ),
                }
            )

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
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

    final_answer = response.output_text.strip()

    if not final_answer:
        final_answer = (
            "The uploaded documents do not provide "
            "enough information to answer that."
        )

    write_log(
        {
            "question": cleaned_question,
            "tool_rounds": tool_rounds,
            "tools": tool_logs,
            "final_answer": final_answer,
            "max_tool_rounds_reached": True,
        }
    )

    return final_answer