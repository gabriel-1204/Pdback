from datetime import timedelta, timezone
from pathlib import Path

from pydantic_settings import BaseSettings

# 한국 표준시 (KST = UTC+9)
KST = timezone(timedelta(hours=9))
# Base_Diractory
BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    # Gemini API
    GEMINI_API_KEY: str = ""

    # JWT
    # 기본값 제거, .env에 값이 있어야 작동
    SECRET_KEY: str

    # Token
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 #MINUTES로 관리하면 조금 더 세밀하게 조절가능

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "pdback"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5500"

    # App
    DEBUG: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    #templates
    TEMPLATES_DIR: str = str(BASE_DIR / "frontend")

    #static
    STATIC_DIR: str = str(BASE_DIR / "frontend" / "css")

settings = Settings()
