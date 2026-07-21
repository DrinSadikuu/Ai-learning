import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found "
        "in the .env file."
    )

client = OpenAI(api_key=api_key)


def answer_question(
    question: str,
    retrieved_chunks: list[dict],
) -> str:
    context = "\n\n".join(
        (
            f"File: {chunk['file']}\n"
            f"Page: {chunk['page']}\n"
            f"Chunk: {chunk['id']}\n"
            f"Text:\n{chunk['text']}"
        )
        for chunk in retrieved_chunks
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "Answer the user's question using only "
            "the provided document context. "
            "Do not use outside knowledge. "
            "If the answer is not contained in the "
            "context, say that the documents do not "
            "contain enough information. "
            "Keep the answer clear and concise."
        ),
        input=(
            f"Document context:\n\n{context}\n\n"
            f"Question:\n{question}"
        ),
    )

    return response.output_text