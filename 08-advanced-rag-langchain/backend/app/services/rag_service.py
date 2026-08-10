from app.services.llm_service import llm_service
from app.services.vector_store_service import vector_store_service


class RAGService:
    MIN_RELEVANCE_SCORE = 0.7

    async def answer_question(
        self,
        question: str,
        document_id: str | None = None,
    ) -> tuple[str, list[dict]]:

        results = await vector_store_service.search(
            query=question,
            k=4,
            document_id=document_id,
        )

        relevant_results = [
            (document, score)
            for document, score in results
            if score >= self.MIN_RELEVANCE_SCORE
        ]

        if not relevant_results:
            return (
                "I could not find enough information in the documents.",
                [],
            )

        context_parts = []

        for document, score in relevant_results:
            page = document.metadata.get("page")

            page_number = (
                page + 1
                if page is not None
                else "Unknown"
            )

            context_parts.append(
                f"""
Source: {document.metadata.get("filename", "Unknown")}
Page: {page_number}

{document.page_content}
"""
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a document question-answering assistant.

Answer the user's question using only the
provided document context.

Do not use information that is not present
in the context.

If the context does not contain enough
information to answer the question, say:

"I could not find enough information in the documents."

Context:
{context}

Question:
{question}
"""

        answer = await llm_service.generate_response(
            prompt
        )

        sources = []

        for document, score in relevant_results:
            page = document.metadata.get("page")

            sources.append(
                {
                    "document_id":
                        document.metadata.get(
                            "document_id"
                        ),
                    "filename":
                        document.metadata.get(
                            "filename"
                        ),
                    "page": (
                        page + 1
                        if page is not None
                        else None
                    ),
                    "score": score,
                }
            )

        return answer, sources


rag_service = RAGService()