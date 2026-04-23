# middleware/cors.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


class CORSMiddlewareConfig:
    """
    Central CORS configuration for ZELTA backend.
    Handles:
    - Local dev
    - Vercel frontend
    - Production restrictions
    """

    def __init__(self):
        self.env = os.getenv("ENV", "development")

    def get_allowed_origins(self):
        """
        Dynamically determine allowed origins based on environment
        """

        if self.env == "production":
            return [
                "https://your-frontend.vercel.app",  # 🔥 replace with real domain
            ]

        # ── Development (more permissive) ──
        return [
            "http://localhost:3000",   # React
            "http://localhost:5173",   # Vite
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]

    def apply(self, app: FastAPI):
        """
        Apply CORS middleware to FastAPI app
        """

        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.get_allowed_origins(),

            # 🔥 VERY IMPORTANT
            allow_credentials=True,

            # Allow all methods (GET, POST, etc.)
            allow_methods=["*"],

            # Allow all headers (Authorization, Content-Type, etc.)
            allow_headers=["*"],
        )