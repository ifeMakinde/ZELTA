from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    # ─── App Logic ────────────────────────────────────────────────────────────
    app_env: str = "development"
    debug: bool = True  # Added this to support your main.py logic
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    allowed_origins: str = "*"

    # ─── Firebase ─────────────────────────────────────────────────────────────
    firebase_project_id: str = "zelta-77e9c"
    firebase_service_account_path: str = "./serviceAccountKey.json"
    firebase_api_key: str = ""

    # ─── Google Cloud / Vertex AI ─────────────────────────────────────────────
    google_cloud_project: str = "zelta"
    google_cloud_region: str = "us-central1"
    vertex_ai_endpoint: str = "https://us-central1-aiplatform.googleapis.com"

    # ─── Gemini & AI Brain ────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash" 
    ai_brain_url: str = "https://zelta-ai-990094999937.us-central1.run.app"
    internal_api_key: str = ""

    # ─── Financial Constants ──────────────────────────────────────────────────
    kelly_fraction: float = 0.5
    max_invest_ratio: float = 0.25
    savings_floor_ratio: float = 0.60
    buffer_reserve_ngn: float = 5000.0
    stress_high_threshold: int = 60
    stress_crisis_threshold: int = 80

    @property
    def allowed_origins_list(self) -> List[str]:
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # ─── Pydantic Config ──────────────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignores extra env vars in your .env file
    )

settings = Settings()
