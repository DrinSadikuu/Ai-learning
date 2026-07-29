from config import create_openai_client


MODEL = "gpt-5"


REWRITER_INSTRUCTIONS = """
You rewrite user questions into effective semantic-search queries.

Rules:
1. Preserve the exact intent of the original question.
2. Preserve all important names, entities, project numbers, technologies,
   attributes and relationships.
3. Never change the subject of the question.
4. Never reinterpret a person's name as a river, location, acronym,
   organization or another entity unless the original question clearly
   indicates that meaning.
5. Make vague wording clearer only when the meaning is available from the
   original question.
6. Remove unnecessary conversational wording.
7. Add useful synonyms only when they preserve the original meaning.
8. Do not answer the question.
9. Do not invent facts or missing context.
10. Return only one plain semantic-search query.
11. Do not use quotation marks, Boolean operators, labels or explanations.
"""


def rewrite_query(question: str) -> str:
    """
    Rewrite a user question into a clear semantic-search query.
    """

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    client = create_openai_client()

    response = client.responses.create(
        model=MODEL,
        instructions=REWRITER_INSTRUCTIONS,
        input=cleaned_question,
    )

    rewritten_query = response.output_text.strip()

    if not rewritten_query:
        return cleaned_question

    return rewritten_query