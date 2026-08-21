from phoenix.otel import register

from app.core.config import get_settings


def setup_tracing():
    settings = get_settings()

    return register(
        project_name="project-12-ai-evaluation",
        endpoint=settings.phoenix_collector_endpoint,
        auto_instrument=True,
    )