from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from app.core.config import get_settings


class VectorStoreService:
    def __init__(self):
        self.vector_store: PGVector | None = None

    async def initialize(self):
        settings = get_settings()

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key,
        )

        self.vector_store = PGVector(
            embeddings=embeddings,
            collection_name="documents",
            connection=settings.database_url,
            use_jsonb=True,
            async_mode=True,
        )

    async def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        if self.vector_store is None:
            raise RuntimeError(
                "Vector store is not initialized"
            )

        await self.vector_store.aadd_documents(
            documents=documents,
        )

    async def search(
        self,
        query: str,
        k: int = 4,
    ) -> list[Document]:
        if self.vector_store is None:
            raise RuntimeError(
                "Vector store is not initialized"
            )

        results = await self.vector_store.asimilarity_search(
            query=query,
            k=k,
        )

        return results


vector_store_service = VectorStoreService()