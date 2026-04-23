from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Firebase
    firebase_project_id: str = ""
    firebase_service_account_path: str = "./serviceAccountKey.json"

    # Google Cloud / Vertex AI
    google_cloud_project: str = ""
    google_cloud_region: str = "us-central1"
    vertex_ai_endpoint: str = "https://us-central1-aiplatform.googleapis.com"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"

    # Centralised AI Brain (deployed Cloud Run service)
    ai_brain_url: str = "https://zelta-ai-990094999937.us-central1.run.app"
    internal_api_key: str = ""

    # Bayse Markets API (used directly by AI Brain — kept for reference/fallback)
    bayse_api_key: str = ""
    bayse_base_url: str = "https://api.bayse.markets/v1"

    # News API (used directly by AI Brain — kept for reference/fallback)
    news_api_key: str = ""

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins: str = "http://localhost:3000"

    # ZELTA BQ Engine constants (used by simulation service — brain owns intelligence)
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
        env_file = ".env"
        case_sensitive = False


settings = Settings()