from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.auth import verify_firebase_token
from core.firebase import get_firestore
from google.cloud import firestore
from typing import Annotated
import logging

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
) -> dict:
    """
    Extract and verify Firebase token from Authorization header.
    Returns current_user dict: { uid, email, name, picture, email_verified }
    """
    token = credentials.credentials
    return verify_firebase_token(token)


def get_db() -> firestore.Client:
    """Provide the Firestore client as a FastAPI dependency."""
    return get_firestore()


CurrentUser = Annotated[dict, Depends(get_current_user)]
DB = Annotated[firestore.Client, Depends(get_db)]