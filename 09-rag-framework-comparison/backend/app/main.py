from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.services.vector_store_service import vector_store_service
from app.api.routes.documents import router as documents_router
from app.api.routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await vector_store_service.initialize()
    yield


app = FastAPI(
    title="Project 09 - RAG Framework Comparison",
    lifespan=lifespan,
)

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}