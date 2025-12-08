from fastapi    import FastAPI
from contextlib import asynccontextmanager
# 
from app.db.mongo    import connect_to_mongo
from app.db.mongo    import close_mongo_connection

from app.services.ai_client import localAi_client

#
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await connect_to_mongo()
    status = await localAi_client.status()
    print(f"Status LocalAi Connection: {status}")

    yield
    
    await close_mongo_connection()
    await localAi_client.close()

