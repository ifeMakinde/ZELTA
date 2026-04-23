from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Firebase
    # Pydantic will automatically map FIREBASE_PROJECT_ID from env to this
    firebase_project_id: str = "zelta-77e9c"
    firebase_service_account_path: str = "./serviceAccountKey.json"

    # Google Cloud / Vertex AI
    google_cloud_project: str = "zelta-backend"
    google_cloud_region: str = "us-central1"
    vertex_ai_endpoint: str = "https://us-central1-aiplatform.googleapis.com"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash" # Use a stable identifier

    # Centralised AI Brain
    ai_brain_url: str = "https://zelta-ai-990094999937.us-central1.run.app"
    internal_api_key: str = ""

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins: str = "*"

    # Constants
    kelly_fraction: float = 0.5
    max_invest_ratio: float = 0.25
    savings_floor_ratio: float = 0.60
    buffer_reserve_ngn: float = 5000.0
    stress_high_threshold: int = 60
    stress_crisis_threshold: int = 80

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        # This tells Pydantic to read from .env if it exists
        env_file = ".env"
        extra = "ignore" # Ignores extra env vars in your .env file

settings = Settings()