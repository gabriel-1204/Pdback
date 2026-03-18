from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

client: AsyncIOMotorClient | None = None

# motor: 비동기 Mongo DB 드라이버
# 앱 시작할때 Mongo DB 연결 맺기
async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)

# 앱 종료할때 연결 끊기
async def close_db():
    global client
    if client:
        client.close()
        client = None

# service.py에서 DB 필요할때 이 함수 호출
def get_database() -> AsyncIOMotorDatabase:
    if client is None:
        raise RuntimeError("Database client is not initialized. Call connect_db() first.")
    return client[settings.MONGODB_DB_NAME]
