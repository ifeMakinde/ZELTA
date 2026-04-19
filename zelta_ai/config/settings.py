import os
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)


class Settings:
    BAYSE_PUBLIC_KEY: str
    BAYSE_PRIVATE_KEY: str

    def __init__(self):
        self.BAYSE_PUBLIC_KEY = self._get_env("BAYSE_PUBLIC_KEY")
        self.BAYSE_PRIVATE_KEY = self._get_env("BAYSE_PRIVATE_KEY")

        logger.info("BAYSE keys loaded successfully")

    def _get_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing {key} in environment")
        return value


settings = Settings()