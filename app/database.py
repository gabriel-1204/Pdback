from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

client: AsyncIOMotorClient | None = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)


async def close_db():
    global client
    if client:
        client.close()
        client = None


def get_database() -> AsyncIOMotorDatabase:
    if client is None:
        raise RuntimeError("Database client is not initialized. Call connect_db() first.")
    return client[settings.MONGODB_DB_NAME]
