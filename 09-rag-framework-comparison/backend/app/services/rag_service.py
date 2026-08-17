from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.services.vector_store_service import vector_store_service


class RAGService:
    def __init__(self):
        settings = get_settings()

        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )

    async def answer(self, question: str) -> str:
        documents = await vector_store_service.search(
            query=question,
            k=4,
        )

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        prompt = f"""
Answer the question using only the context below.

Context:
{context}

Question:
{question}
"""

        response = await self.llm.ainvoke(prompt)

        return response.content


rag_service = RAGService()