import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

apiKey = os.getenv("OPENAI_API_KEY")

if not apiKey:
    raise Exception("OPENAI_API_KEY is not set")

openai = OpenAI(api_key=apiKey)
