# services/profile_service.py

from typing import Dict, Any
from datetime import datetime, timezone


class ProfileService:
    def __init__(self, db):
        self.db = db

    def get_profile(self, user: Dict[str, Any]):
        ref = self.db.collection("users").document(user["uid"])
        doc = ref.get()

        if doc.exists:
            return doc.to_dict()

        # Default profile (matches frontend)
        profile = {
            "uid": user["uid"],
            "email": user.get("email"),
            "name": user.get("name", "New User"),
            "picture": user.get("picture"),
            "created_at": datetime.now(timezone.utc).isoformat(),

            "financial": {
                "capital_range": "₦10,000 - ₦50,000",
                "risk_preference": "moderate",
                "monthly_income": None,
            },

            "preferences": {
                "primary_goal": "Build Emergency Fund",
                "decision_aggressiveness": 50,
                "stress_sensitivity": 60,
            },

            "notifications": {
                "decision_alerts": True,
                "stress_updates": True,
                "market_signals": False,
                "goal_progress": True,
                "behavioral_insights": True,
            }
        }

        ref.set(profile)
        return profile

    # ─────────────────────────────

    def update_profile(self, uid: str, data: Dict[str, Any]):
        ref = self.db.collection("users").document(uid)

        # Merge nested fields properly
        update_data = {}

        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_val in value.items():
                    update_data[f"{key}.{sub_key}"] = sub_val
            else:
                update_data[key] = value

        ref.update(update_data)

        return {
            "success": True,
            "updated": update_data
        }