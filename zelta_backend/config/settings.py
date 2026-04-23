# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # AI Brain
    AI_BRAIN_URL: str = os.getenv("AI_BRAIN_URL", "https://zelta-ai-990094999937.us-central1.run.app")
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "")
    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    # App
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8080"))

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")

settings = Settings()