import firebase_admin
from fastapi import HTTPException, status
from core.firebase import get_auth
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


def verify_firebase_token(token: str) -> dict:
    """
    Verify a Firebase ID token and return decoded user claims.

    Returns:
        dict: {uid, email, name, picture, email_verified}

    Raises:
        HTTPException(401) if token is invalid, expired, or revoked.
    """

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        firebase_auth = get_auth()
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)

        return {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email", ""),
            "name": decoded_token.get("name", ""),
            "picture": decoded_token.get("picture", ""),
            "email_verified": decoded_token.get("email_verified", False),
        }

    except firebase_admin.auth.RevokedIdTokenError:
        logger.warning("Revoked Firebase token used.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except firebase_admin.auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase token used.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except firebase_admin.auth.InvalidIdTokenError as e:
        logger.warning(f"Invalid Firebase token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token." if not settings.debug else str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        logger.error("Unexpected token verification error", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed." if not settings.debug else str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
