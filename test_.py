from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
import asyncio

async def test_connection():
    uri = settings.mongodb_uri
    print(uri)
    # uri = get_uri()
    print(f"Usando URI: {uri}")

    client = AsyncIOMotorClient(uri)
    db = client[settings.MONGODB_DB_NAME]

    # Documento de prueba
    test_doc = {"name": "Test item", "description": "Testing MongoDB connection"}

    # Insertar
    result = await db.test_items.insert_one(test_doc)
    print("Inserted ID:", result.inserted_id)

    # Leer nuevamente
    saved = await db.test_items.find_one({"_id": result.inserted_id})
    print("Saved document:", saved)

    client.close()


# Ejecutar el test
if __name__ == "__main__":
    asyncio.run(test_connection())