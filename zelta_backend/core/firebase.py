import os
import json
import logging
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, auth
from google.cloud import firestore
from google.cloud.firestore import Client

from config.settings import settings

logger = logging.getLogger(__name__)

# Track the Firestore client globally
_firestore_client: Optional[Client] = None


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
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_JSON is not valid JSON.") from e

    if service_account_path and os.path.exists(service_account_path):
        logger.info("Using Firebase service account from file: %s", service_account_path)
        return credentials.Certificate(service_account_path)

    logger.info("Service account not found. Using Application Default Credentials.")
    return credentials.ApplicationDefault()


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK. Safe to call multiple times."""
    global _firestore_client

    # 1. Initialize Firebase App
    try:
        firebase_admin.get_app()
    except ValueError:
        try:
            cred = _build_firebase_credential()

            firebase_admin.initialize_app(cred, {
                "projectId": settings.firebase_project_id,
            })
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error("Firebase initialization failed: %s", e, exc_info=True)
            raise

    # 2. Initialize Firestore Client
    if _firestore_client is None:
        try:
            _firestore_client = firestore.Client(project=settings.firebase_project_id)
            logger.info("Firestore client initialized.")
        except Exception as e:
            logger.error("Firestore Client initialization failed: %s", e, exc_info=True)
            raise


def get_firestore() -> Client:
    """Return the Firestore client, initializing Firebase if necessary."""
    global _firestore_client

    if _firestore_client is None:
        initialize_firebase()

    return _firestore_client  # type: ignore[return-value]


def get_auth() -> Any:
    """Return Firebase Auth module."""
    try:
        firebase_admin.get_app()
    except ValueError:
        initialize_firebase()

    return auth
