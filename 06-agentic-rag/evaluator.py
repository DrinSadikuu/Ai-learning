import json

from config import create_openai_client


MODEL = "gpt-5"


EVALUATOR_INSTRUCTIONS = """
You evaluate whether retrieved document chunks are sufficient to answer
a user's question.

Return valid JSON with exactly these fields:
{
  "is_relevant": true or false,
  "confidence": number between 0 and 1,
  "reason": "brief explanation"
}

Rules:
1. Mark is_relevant true only when the retrieved context directly supports
   an answer to the user's exact question.
2. Semantic similarity alone is not enough.
3. Do not use outside knowledge.
4. Do not answer the user's question.
5. Return only JSON.
"""


def evaluate_retrieval(
    question: str,
    results: list[dict],
) -> dict:
    """
    Evaluate whether retrieved chunks are sufficient for answering.
    """

    if not results:
        return {
            "is_relevant": False,
            "confidence": 1.0,
            "reason": "No document chunks were retrieved.",
        }

    client = create_openai_client()

    evaluation_input = {
        "question": question,
        "retrieved_results": results,
    }

    response = client.responses.create(
        model=MODEL,
        instructions=EVALUATOR_INSTRUCTIONS,
        input=json.dumps(
            evaluation_input,
            ensure_ascii=False,
        ),
    )

    raw_output = response.output_text.strip()

    try:
        evaluation = json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "is_relevant": False,
            "confidence": 0.0,
            "reason": (
                "The evaluator did not return valid JSON."
            ),
        }

    return {
        "is_relevant": bool(
            evaluation.get("is_relevant", False)
        ),
        "confidence": float(
            evaluation.get("confidence", 0.0)
        ),
        "reason": str(
            evaluation.get(
                "reason",
                "No reason was provided.",
            )
        ),
    }