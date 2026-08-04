from openai import AsyncOpenAI

from app.core.config import get_settings
from app.db.models.message import Message


class AIService:
    def __init__(self):
        settings = get_settings()

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )
        self.model = settings.openai_model

    async def generate_response(
        self,
        messages: list[Message],
    ) -> str:
        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        response = await self.client.responses.create(
            model=self.model,
            instructions=(
                "You are a helpful assistant inside an AI Knowledge Workspace. "
                "Answer clearly and concisely."
            ),
            input=conversation_history,
        )

        return response.output_text

    async def generate_response_from_prompt(
        self,
        prompt: str,
    ) -> str:
        response = await self.client.responses.create(
            model=self.model,
            instructions=(
                "You are a helpful assistant inside an AI Knowledge Workspace. "
                "Answer using only the provided document context. "
                "If the answer is not in the context, say you could not find it."
            ),
            input=prompt,
        )

        return response.output_text