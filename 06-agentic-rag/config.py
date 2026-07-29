import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def create_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found. "
            "Add it to your .env file."
        )

    return OpenAI(api_key=api_key)