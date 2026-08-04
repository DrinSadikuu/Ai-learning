from openai import AsyncOpenAI

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self):
        settings = get_settings()

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

        self.model = "text-embedding-3-small"

    async def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        return [item.embedding for item in response.data]