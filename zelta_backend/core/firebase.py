import os
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


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK. Safe to call concurrently."""
    global _firestore_client

    # 1. Initialize Firebase App
    try:
        firebase_admin.get_app()
    except ValueError:
        try:
            service_account_path = settings.firebase_service_account_path

            if os.path.exists(service_account_path):
                logger.info(f"Using service account from: {service_account_path}")
                cred = credentials.Certificate(service_account_path)
            else:
                logger.info("Service account file not found. Using Application Default Credentials.")
                cred = credentials.ApplicationDefault()

            firebase_admin.initialize_app(cred, {
                "projectId": settings.firebase_project_id,
            })
            logger.info("Firebase Admin SDK initialized successfully.")

        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            raise

    # 2. Initialize Firestore Client
    if _firestore_client is None:
        try:
            # We pass the project ID explicitly to avoid environment mismatch
            _firestore_client = firestore.Client(project=settings.firebase_project_id)
            logger.info("Firestore client initialized.")
        except Exception as e:
            logger.error(f"Firestore Client initialization failed: {e}")
            raise


def get_firestore() -> Client:
    """Return the Firestore client, initializing Firebase if necessary."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
    
    # Cast to Client to satisfy type checkers, as we know it's not None here
    return _firestore_client # type: ignore


def get_auth() -> Any:
    """Return Firebase Auth module."""
    try:
        firebase_admin.get_app()
    except ValueError:
        initialize_firebase()

    return auth
