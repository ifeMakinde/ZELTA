# core/dependencies.py

from fastapi import Depends, Request
from typing import Dict, Any

from core.auth import get_current_user
from core.firebase import FirebaseClient


# ─────────────────────────────────────────────
# FIREBASE / DATABASE
# ─────────────────────────────────────────────

def get_db():
    """
    Firestore database dependency.
    Ensures singleton usage via FirebaseClient.
    """
    firebase = FirebaseClient()
    return firebase.get_firestore()


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

def get_user(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns full authenticated user object.
    """
    return user


def get_user_id(user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Shortcut: directly inject user UID.
    """
    return user["uid"]


# ─────────────────────────────────────────────
# OPTIONAL: REQUEST CONTEXT
# ─────────────────────────────────────────────

def get_request_id(request: Request) -> str:
    """
    Extract request ID if you add one later (for logging/tracing).
    Falls back to None.
    """
    return request.headers.get("X-Request-ID", "")


def get_user_context(
    user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None,
) -> Dict[str, Any]:
    """
    Combined context (useful for logging, analytics, AI input later)
    """
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "ip": request.client.host if request else None,
        "user_agent": request.headers.get("User-Agent") if request else None,
    }