import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found in the .env file."
    )

client = OpenAI(api_key=api_key)


def create_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Text cannot be empty.")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )

    return response.data[0].embedding