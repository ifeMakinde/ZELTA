from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # App Logic
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    allowed_origins: str = "*"

    # Firebase
    firebase_project_id: str = "zelta-77e9c"
    firebase_api_key: str = Field(default="", alias="FIREBASE_API_KEY")
    firebase_service_account_json: str = Field(default="", alias="FIREBASE_SERVICE_ACCOUNT_JSON")

    # Google Cloud / Vertex AI
    google_cloud_project: str = "zelta"
    google_cloud_region: str = "us-central1"
    vertex_ai_endpoint: str = "https://us-central1-aiplatform.googleapis.com"

    # Gemini & AI Brain
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = "gemini-2.5-flash"
    ai_brain_url: str = "https://zelta-ai-990094999937.us-central1.run.app"
    internal_api_key: str = Field(default="", alias="INTERNAL_API_KEY")

    # Financial Constants
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
