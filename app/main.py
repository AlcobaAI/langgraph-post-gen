from fastapi import FastAPI

from app.api.routes.generate import router as generate_router
from app.services.generate_content import GenerateContentService


def create_app() -> FastAPI:
    app = FastAPI()
    service = GenerateContentService()

    @app.on_event("startup")
    async def startup() -> None:
        await service.startup()

    app.state.generate_content_service = service
    app.include_router(generate_router)
    return app


app = create_app()