from fastapi import FastAPI

from app.core.config import settings
from app.utils.utils_funcs import lifespan

from app.api.health import health_router
from app.api.process import process_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="FastAPI + MongoDB using env-based configuration.",
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Routers
    app.include_router(health_router)
    app.include_router(process_router, prefix="/process")

    return app

app = create_app()

