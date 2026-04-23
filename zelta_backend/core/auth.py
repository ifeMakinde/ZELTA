# core/auth.py

from typing import Optional, Dict, Any

from fastapi import Request, HTTPException, status, Depends
from firebase_admin import auth

from zelta_backend.core.firebase import FirebaseClient


class AuthService:
    """
    Handles Firebase Authentication verification.
    """

    def __init__(self):
        self.firebase = FirebaseClient()

    # ─────────────────────────────────────────────

    def _extract_token(self, request: Request) -> str:
        """
        Extract Bearer token from Authorization header
        """
        auth_header: Optional[str] = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
            )

        return auth_header.split(" ")[1]

    # ─────────────────────────────────────────────

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token
        """
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    # ─────────────────────────────────────────────

    def get_current_user(self, request: Request) -> Dict[str, Any]:
        """
        Full auth flow:
        - Extract token
        - Verify token
        - Return user payload
        """
        token = self._extract_token(request)
        decoded = self.verify_token(token)

        return {
            "uid": decoded.get("uid"),
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "picture": decoded.get("picture"),
        }


# ─────────────────────────────────────────────
# FastAPI Dependency (THIS IS WHAT YOU USE)
# ─────────────────────────────────────────────

auth_service = AuthService()


def get_current_user(request: Request):
    return auth_service.get_current_user(request)