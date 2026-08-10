async def search(
    self,
    query: str,
    k: int = 4,
    document_id: str | None = None,
):
    if self.vector_store is None:
        raise RuntimeError(
            "Vector store is not initialized"
        )

    metadata_filter = None

    if document_id is not None:
        metadata_filter = {
            "document_id": document_id,
        }

    results = (
        await self.vector_store
        .asimilarity_search_with_relevance_scores(
            query=query,
            k=k,
            filter=metadata_filter,
        )
    )

    return results