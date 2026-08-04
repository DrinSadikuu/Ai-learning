from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.auth import router as auth_router
from app.api.routes.conversation_rag import router as conversation_rag_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.documents import router as documents_router
from app.api.routes.messages import router as messages_router
from app.api.routes.rag import router as rag_router
from app.api.routes.search import router as search_router
from app.api.routes.users import router as users_router
from app.core.config import get_settings
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(conversations_router)
app.include_router(messages_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(rag_router)
app.include_router(conversation_rag_router)


@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.app_version,
    }


@app.get("/api/v1/health/database", tags=["Health"])
async def database_health_check() -> dict[str, str]:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "database": "disconnected",
        }

    return {
        "status": "healthy",
        "database": "connected",
    }