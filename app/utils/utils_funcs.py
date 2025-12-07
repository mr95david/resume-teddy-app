from fastapi    import FastAPI
from contextlib import asynccontextmanager
# 
from app.db.mongo    import connect_to_mongo
from app.db.mongo    import close_mongo_connection

#
@asynccontextmanager
async def lifespan(app: FastAPI):

    await connect_to_mongo()

    yield
    
    await close_mongo_connection()

