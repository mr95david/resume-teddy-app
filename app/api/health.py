from fastapi import APIRouter
from app.db.mongo import ping_mongo

health_router = APIRouter(tags=["health"])

@health_router.get(
    "/",
    summary="Health check básico",
    description="Retorna informações básicas sobre o status geral da aplicação."
)
async def root():
    return {
        "status": "ok", 
        "message": "resume-teddy-app em execução"
    }


@health_router.get("/info", 
    summary="Informações da aplicação",
    description="Retorna informações gerais como versão e ambiente atual."
)
async def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": "development",
    }


@health_router.get(
    "/db-health",
    summary="Verificação de saúde do banco de dados",
    description="Executa um ping na instância do MongoDB para verificar conectividade."
)
async def db_health():
    return await ping_mongo()