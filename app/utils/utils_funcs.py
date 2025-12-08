from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.mongo import (connect_to_mongo, close_mongo_connection)
from app.services.ai_client import localAi_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    ai_status = await localAi_client.status()
    print(f"LocalAI status: {ai_status}")

    yield
    # Shutdown
    await close_mongo_connection()
    await localAi_client.close()

