from fastapi import FastAPI

from routes.searcher import router as searcher_router
import uvicorn


def create_app() -> FastAPI:
    app = FastAPI(
        title="Searching system",
        version="1.0.0",
        description="FastAPI app for searching",
    )

    app.include_router(searcher_router)

    return app

app = create_app()


if __name__ == '__main__':
    uvicorn.run("app.main:app", reload=True)