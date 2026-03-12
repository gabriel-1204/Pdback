import google.generativeai as genai

from app.config import settings


def configure_gemini():
    genai.configure(api_key=settings.GEMINI_API_KEY)


def get_model(model_name: str = "gemini-2.0-flash") -> genai.GenerativeModel:
    return genai.GenerativeModel(model_name)
