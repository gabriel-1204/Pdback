from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.config import settings
from app.database import close_db, connect_db
from app.services.gemini import configure_gemini


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    await connect_db()
    configure_gemini()
    yield
    # 종료 시
    await close_db()


app = FastAPI(
    title="P:dback API",
    description="Vision AI와 STT가 결합된 개발자 맞춤형 실전 화상 면접 솔루션",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(v1_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
