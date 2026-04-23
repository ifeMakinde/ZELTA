import firebase_admin
from firebase_admin import credentials, firestore, auth
from config.settings import settings
import os
import logging

logger = logging.getLogger(__name__)

_firebase_app = None
_firestore_client = None


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK. Safe to call multiple times."""
    global _firebase_app, _firestore_client

    if _firebase_app is not None:
        return

    try:
        service_account_path = settings.firebase_service_account_path

        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            _firebase_app = firebase_admin.initialize_app(cred, {
                "projectId": settings.firebase_project_id,
            })
        else:
            # Use Application Default Credentials (for Cloud Run)
            _firebase_app = firebase_admin.initialize_app(options={
                "projectId": settings.firebase_project_id,
            })

        _firestore_client = firestore.client()
        logger.info("Firebase initialized successfully.")

    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        raise


def get_firestore() -> firestore.Client:
    """Return the Firestore client, initializing Firebase if necessary."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
    return _firestore_client


def get_auth() -> auth:
    """Return Firebase Auth module."""
    if _firebase_app is None:
        initialize_firebase()
    return auth