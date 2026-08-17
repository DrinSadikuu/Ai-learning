from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from langchain_core.documents import Document

from app.core.config import get_settings


class VectorStoreService:
    def __init__(self):
        self.engine: PGEngine | None = None
        self.vector_store: PGVectorStore | None = None

    async def initialize(self):
        settings = get_settings()

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key,
        )

        self.engine = PGEngine.from_connection_string(
            settings.database_url
        )

        await self.engine.ainit_vectorstore_table(
            table_name="documents",
            vector_size=1536,
        )

        self.vector_store = await PGVectorStore.create(
            engine=self.engine,
            table_name="documents",
            embedding_service=embeddings,
        )

    async def add_documents(self, documents: list[Document])-> None:
        if self.vector_store is None:
            raise RuntimeError(
                "Vector store is not initialized"
            )
        await self.vector_store.aadd_documents(documents=documents)

    async def search(
            self,
            query: str,
            k: int = 4,
            filter: dict | None = None,
    ) -> list[Document]:
        if self.vector_store is None:
            raise RuntimeError(
                "Vector store is not initialized"
            )

        results = await self.vector_store.asimilarity_search(
            query=query,
            k=k,
            filter=filter,
        )

        return results

vector_store_service = VectorStoreService()