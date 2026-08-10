from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.services.vector_store_service import vector_store_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await vector_store_service.initialize()

    yield


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(chat_router)
app.include_router(documents_router)