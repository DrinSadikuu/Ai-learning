from openai import AsyncOpenAI

from app.core.config import get_settings


class LLMService:
    def __init__(self):
        settings = get_settings()

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

        self.model = settings.openai_model

    async def generate(self, question: str) -> str:
        response = await self.client.responses.create(
            model=self.model,
            input=question,
        )

        return response.output_text


llm_service = LLMService()