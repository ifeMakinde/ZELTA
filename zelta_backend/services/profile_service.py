"""
ZELTA Profile Service

GET and UPDATE user profile with nested financial, preferences, and notifications sections.
"""

import logging
from datetime import datetime, timezone
from google.cloud import firestore
from schemas.profile import UserProfile, UpdateProfileRequest, FinancialProfile, PreferencesProfile, NotificationsProfile

logger = logging.getLogger(__name__)


def _get_profile_ref(db: firestore.Client, uid: str) -> firestore.DocumentReference:
    return db.collection("users").document(uid)


async def get_profile(db: firestore.Client, uid: str) -> UserProfile:
    """Fetch user profile from Firestore. Returns defaults if not yet created."""
    ref = _get_profile_ref(db, uid)
    doc = ref.get()

    if not doc.exists:
        return UserProfile(uid=uid, email="", name="")

    data = doc.to_dict()

    # Deserialize nested objects
    financial_data = data.get("financial", {})
    prefs_data = data.get("preferences", {})
    notif_data = data.get("notifications", {})

    return UserProfile(
        uid=uid,
        email=data.get("email", ""),
        name=data.get("name", ""),
        picture=data.get("picture"),
        university=data.get("university"),
        department=data.get("department"),
        level=data.get("level"),
        financial=FinancialProfile(**financial_data) if financial_data else FinancialProfile(),
        preferences=PreferencesProfile(**prefs_data) if prefs_data else PreferencesProfile(),
        notifications=NotificationsProfile(**notif_data) if notif_data else NotificationsProfile(),
    )


async def create_or_update_profile(
    db: firestore.Client, uid: str, current_user: dict, request: UpdateProfileRequest
) -> UserProfile:
    """
    Create or update user profile. Supports partial nested updates.
    Merges incoming changes with existing profile.
    """
    ref = _get_profile_ref(db, uid)
    doc = ref.get()
    existing = doc.to_dict() if doc.exists else {}

    now = datetime.now(timezone.utc)
    updates: dict = {
        "uid": uid,
        "email": current_user.get("email", existing.get("email", "")),
        "name": request.name or existing.get("name", current_user.get("name", "")),
        "picture": current_user.get("picture", existing.get("picture")),
        "updated_at": now,
    }

    if not doc.exists:
        updates["created_at"] = now

    if request.university is not None:
        updates["university"] = request.university
    if request.department is not None:
        updates["department"] = request.department
    if request.level is not None:
        updates["level"] = request.level

    # Nested partial merge for financial
    if request.financial is not None:
        existing_financial = existing.get("financial", {})
        new_financial = {**existing_financial, **request.financial.model_dump(exclude_none=True)}
        updates["financial"] = new_financial
    elif "financial" not in existing:
        updates["financial"] = {}

    # Nested partial merge for preferences
    if request.preferences is not None:
        existing_prefs = existing.get("preferences", {})
        new_prefs = {**existing_prefs, **request.preferences.model_dump(exclude_none=True)}
        updates["preferences"] = new_prefs
    elif "preferences" not in existing:
        updates["preferences"] = {}

    # Nested partial merge for notifications
    if request.notifications is not None:
        existing_notif = existing.get("notifications", {})
        new_notif = {**existing_notif, **request.notifications.model_dump(exclude_none=True)}
        updates["notifications"] = new_notif
    elif "notifications" not in existing:
        updates["notifications"] = {}

    ref.set(updates, merge=True)

    return await get_profile(db, uid)


async def initialize_profile_on_first_login(
    db: firestore.Client, uid: str, current_user: dict
) -> UserProfile:
    """
    Called on first login or if profile doesn't exist.
    Creates a default profile from Firebase Auth data.
    """
    ref = _get_profile_ref(db, uid)
    doc = ref.get()

    if doc.exists:
        return await get_profile(db, uid)

    now = datetime.now(timezone.utc)
    default_profile = {
        "uid": uid,
        "email": current_user.get("email", ""),
        "name": current_user.get("name", ""),
        "picture": current_user.get("picture", ""),
        "financial": {},
        "preferences": {},
        "notifications": {},
        "created_at": now,
        "updated_at": now,
    }

    ref.set(default_profile)
    logger.info(f"Created default profile for user {uid}")

    return await get_profile(db, uid)