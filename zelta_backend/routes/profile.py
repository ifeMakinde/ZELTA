from fastapi import APIRouter, HTTPException, status
from core.dependencies import CurrentUser, DB
from services.profile_service import get_profile, create_or_update_profile, initialize_profile_on_first_login
from schemas.profile import UpdateProfileRequest, ProfileResponse
from schemas.common import APIResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
async def get_user_profile(current_user: CurrentUser, db: DB):
    """
    Get full user profile: financial settings, preferences, notification config.
    Auto-initializes profile on first call if it doesn't exist.
    """
    try:
        profile = await initialize_profile_on_first_login(db, current_user["uid"], current_user)
        return ProfileResponse(success=True, data=profile)
    except Exception as e:
        logger.error(f"Profile GET error for {current_user['uid']}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("", response_model=ProfileResponse)
async def update_user_profile(
    current_user: CurrentUser,
    db: DB,
    request: UpdateProfileRequest,
):
    """
    Update user profile. Supports partial nested updates.
    Send only the fields you want to change — existing data is preserved.

    Updatable sections:
    - Top-level: name, university, department, level
    - financial: monthly_budget, fee_obligations, risk_tolerance, hostel_fee, etc.
    - preferences: currency, stress_alert_threshold, auto_lock_on_crisis, etc.
    - notifications: stress_alerts, weekly_bq_report, frequency, etc.
    """
    try:
        profile = await create_or_update_profile(db, current_user["uid"], current_user, request)
        return ProfileResponse(success=True, data=profile)
    except Exception as e:
        logger.error(f"Profile UPDATE error for {current_user['uid']}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))