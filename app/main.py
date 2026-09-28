from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.dependencies import set_document_service
from app.index.elastic import (
    ElasticsearchIndex,
    create_elasticsearch_client,
)
from app.db.postgres_connection import initialize_database
from app.routes.searcher import router as searcher_router
from app.services.document_service import DocumentService


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine, session_factory = await initialize_database()

    elasticsearch_client = create_elasticsearch_client()
    elasticsearch_index = ElasticsearchIndex(elasticsearch_client)

    await elasticsearch_client.info()
    await elasticsearch_index.ensure_index()

    set_document_service(
        DocumentService(
            session_factory=session_factory,
            search_index=elasticsearch_index,
        )
    )

    try:
        yield
    finally:
        await elasticsearch_client.close()
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Simple Finder",
        version="1.0.0",
        description="Simple text search service using PostgreSQL and Elasticsearch.",
        lifespan=lifespan,
    )

    app.include_router(searcher_router)

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
