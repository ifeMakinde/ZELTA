import os
import json
import logging
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, auth, firestore as admin_firestore

from config.settings import settings

logger = logging.getLogger(__name__)

# Track Firestore client globally
_firestore_client: Optional[Any] = None


# ─────────────────────────────────────────────────────────────
# CREDENTIAL BUILDER
# ─────────────────────────────────────────────────────────────
def _build_firebase_credential():
    """
    Build Firebase credentials in this order:
    1. JSON string from env/settings
    2. Service account file path
    3. Application Default Credentials
    """
    service_account_json = getattr(settings, "firebase_service_account_json", "").strip()
    service_account_path = getattr(settings, "firebase_service_account_path", "").strip()

    if service_account_json:
        logger.info("Using Firebase service account from JSON env var.")
        try:
            cred_dict = json.loads(service_account_json)
            return credentials.Certificate(cred_dict)
        except json.JSONDecodeError as e:
            logger.error("Invalid FIREBASE_SERVICE_ACCOUNT_JSON format.")
            raise ValueError("Invalid Firebase JSON credentials") from e

    if service_account_path and os.path.exists(service_account_path):
        logger.info(f"Using Firebase service account file: {service_account_path}")
        return credentials.Certificate(service_account_path)

    logger.info("Using Application Default Credentials.")
    return credentials.ApplicationDefault()


# ─────────────────────────────────────────────────────────────
# INITIALIZE FIREBASE
# ─────────────────────────────────────────────────────────────
def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK safely."""
    global _firestore_client

    # Initialize app once
    if not firebase_admin._apps:
        try:
            cred = _build_firebase_credential()
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}", exc_info=True)
            raise

    # Initialize Firestore client
    if _firestore_client is None:
        try:
            # 1. Get the DB ID from settings. 
            # Note: Your console showed 'default', so ensure your env var matches that.
            db_id = getattr(settings, "firebase_database_id", "(default)").strip()
            
            # 2. Use 'database_id' keyword for named databases.
            # If using the standard system default, call client() without arguments.
            if db_id == "(default)":
                _firestore_client = admin_firestore.client()
            else:
                # CRITICAL FIX: The parameter name is 'database_id'
                _firestore_client = admin_firestore.client(database_id=db_id)
            
            logger.info(f"Firestore client connected to database: {db_id}")
            
        except TypeError as e:
            logger.error(
                "TypeError in Firestore init. Ensure 'firebase-admin' is version 6.6.0 or higher "
                "to support the 'database_id' argument."
            )
            raise e
        except Exception as e:
            logger.info(f"Firestore initialization failed: {e}")
            raise


# ─────────────────────────────────────────────────────────────
# FIRESTORE ACCESS
# ─────────────────────────────────────────────────────────────
def get_firestore():
    """Return Firestore client (Firebase Admin SDK version)."""
    global _firestore_client

    if _firestore_client is None:
        initialize_firebase()

    return _firestore_client


# ─────────────────────────────────────────────────────────────
# AUTH ACCESS
# ─────────────────────────────────────────────────────────────
def get_auth() -> Any:
    """Return Firebase Auth module."""
    if not firebase_admin._apps:
        initialize_firebase()

    return auth
