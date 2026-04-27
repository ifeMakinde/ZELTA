import os
import logging
from typing import Any
import firebase_admin
from firebase_admin import credentials,auth,firestore
from google.cloud.firestore import Client
from config.settings import settings

logger = logging.getLogger(__name__)

# We only need to track the Firestore client globally
_firestore_client = None


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK. Safe to call concurrently."""
    global _firestore_client

    # Safely check if Firebase is already initialized to prevent ValueErrors
    try:
        firebase_admin.get_app()
    except ValueError:
        # App is not initialized, proceed with initialization
        try:
            service_account_path = settings.firebase_service_account_path

            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
            else:
                # Explicitly use Application Default Credentials
                cred = credentials.ApplicationDefault()

            firebase_admin.initialize_app(cred, {
                "projectId": settings.firebase_project_id,
            })

            logger.info("Firebase initialized successfully.")

        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            raise

    # Initialize Firestore client if it hasn't been set yet
    if _firestore_client is None:
        _firestore_client = firestore.client()


def get_firestore() -> Client: # Use the imported Client type here
    """Return the Firestore client, initializing Firebase if necessary."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
    return _firestore_client


def get_auth() -> Any:
    """Return Firebase Auth module."""
    try:
        firebase_admin.get_app()
    except ValueError:
        initialize_firebase()

    return auth
