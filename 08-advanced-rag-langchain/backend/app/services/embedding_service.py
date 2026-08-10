from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
        )

    async def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        embeddings = await self.embeddings.aembed_documents(texts)

        return embeddings


embedding_service = EmbeddingService()