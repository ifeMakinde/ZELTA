import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Bayse Markets
    BAYSE_PUBLIC_KEY:  str = os.getenv("BAYSE_PUBLIC_KEY", "")
    BAYSE_PRIVATE_KEY: str = os.getenv("BAYSE_PRIVATE_KEY", "")

    # Gemini — THIS WAS MISSING
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # News API
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    # Internal security
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "")

    # App
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT:  int  = int(os.getenv("PORT", "8080"))


settings = Settings()