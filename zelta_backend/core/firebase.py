import os
import firebase_admin
from firebase_admin import credentials, firestore


class FirebaseClient:
    """
    Singleton Firebase client.

    Handles:
    - App initialization
    - Firestore access
    - Environment-aware auth (local vs cloud)
    """

    _instance = None
    _app = None
    _db = None

    def __new__(cls):
        """
        Ensure only one instance exists (Singleton pattern)
        """
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize Firebase only once
        """
        if self._app:
            return

        self._initialize_app()
        self._initialize_db()

    # ─────────────────────────────────────────────

    def _initialize_app(self):
        """
        Initialize Firebase app
        """
        firebase_key_path = os.getenv("FIREBASE_CREDENTIALS")

        # ── Local development (JSON key) ──
        if firebase_key_path and os.path.exists(firebase_key_path):
            cred = credentials.Certificate(firebase_key_path)

        # ── Cloud Run / Vertex (ADC) ──
        else:
            cred = credentials.ApplicationDefault()

        self._app = firebase_admin.initialize_app(cred)

    # ─────────────────────────────────────────────

    def _initialize_db(self):
        """
        Initialize Firestore client
        """
        self._db = firestore.client()

    # ─────────────────────────────────────────────

    def get_db(self):
        """
        Get Firestore client
        """
        return self._db


# ─────────────────────────────────────────────
# Convenience accessor (clean imports)
# ─────────────────────────────────────────────

def get_firestore():
    return FirebaseClient().get_db()