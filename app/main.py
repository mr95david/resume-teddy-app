
from fastapi import FastAPI
#
from app.core.config import settings
from app.utils.utils_funcs import lifespan
#
from app.api.health     import health_router
from app.api.process    import process_router

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI + MongoDB using env-based configuration.",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Include routes section
app.include_router(router=health_router)
app.include_router(prefix="/process", router=process_router)

# print(">>> MAIN CARGADO <<<")
# print("Rutas registradas:", [r.path for r in app.routes])
