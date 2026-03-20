from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from app.api.v1.router import v1_router
from app.config import settings
from app.database import close_db, connect_db

#탬플릿 설정
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    await connect_db()
    yield
    # 종료 시
    await close_db()


app = FastAPI(
    title="P:dback API",
    description="Vision AI와 STT가 결합된 개발자 맞춤형 실전 화상 면접 솔루션",
    version="0.1.0",
    lifespan=lifespan,
)

#css 파일 마운트
app.mount("/css", StaticFiles(directory=settings.STATIC_DIR), name="css")
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

#인터뷰 html
@app.get("/interview")
async def index(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request, "db_name": settings.MONGODB_DB_NAME})

# 면접 시작 버튼 누르면 interview-setup.html 로 들어감.
@app.get("/start")
async def index(request: Request):
    return templates.TemplateResponse("interview-setup.html", {"request": request, "db_name": settings.MONGODB_DB_NAME})