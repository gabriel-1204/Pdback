from pydantic_settings import BaseSettings
from pathlib import Path
# Base_Diractory
BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    # Gemini API
    GEMINI_API_KEY: str = ""

    #JWT
    SECRET_KEY: str = ""
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "pdback"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5500"

    # App
    DEBUG: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    
    #templates
    TEMPLATES_DIR: str = str(BASE_DIR / "frontend")

    #static
    STATIC_DIR: str = str(BASE_DIR / "frontend" / "css")

settings = Settings()
