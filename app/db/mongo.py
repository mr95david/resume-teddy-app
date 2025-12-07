# libs
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
#
from app.core.config     import settings
#
from typing              import AsyncGenerator

import time

# Common vars
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    
    if _client is None:
        raise RuntimeError("Mongo client not initialized")
    
    return _client


def get_mongo_db() -> AsyncIOMotorDatabase:
    
    if _db is None:
        raise RuntimeError("Mongo database not initialized")
    
    return _db


async def connect_to_mongo() -> None:
    global _client, _db

    uri = settings.mongodb_uri
    _client = AsyncIOMotorClient(uri)

    _db = _client[settings.MONGODB_DB_NAME]
    
    print("MongoDB connected")


async def close_mongo_connection() -> None:
    global _client
    
    if _client is not None:
        _client.close()
        print("MongoDB connection closed")


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    yield get_mongo_db()

async def ping_mongo() -> dict:
    start   = time.perf_counter()
    latency = 0
    
    try:
        db = get_mongo_db()
        await db.command("ping")

        latency = (time.perf_counter() - start) * 1000
        
        return {
            "status": "ok",
            "message": "MongoDB is reachable and responding to commands.",
            "database": settings.MONGODB_DB_NAME,
            "latency_ms": round(latency, 2),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "MongoDB ping failed. The database may be unreachable or misconfigured.",
            "database": settings.MONGODB_DB_NAME,
            "latency_ms": round(latency, 2),
            "details": str(e),
        }

