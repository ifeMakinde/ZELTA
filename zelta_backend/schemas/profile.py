from pydantic import BaseModel
from typing import Optional

class NotificationSettings(BaseModel):
    decision_alerts: bool = True
    stress_updates: bool = True
    market_signals: bool = True
    goal_progress: bool = True
    behavioral_insights: bool = True

class FinancialProfile(BaseModel):
    capital_range: Optional[str] = "₦10,000 - ₦50,000"
    risk_preference: Optional[str] = "moderate"
    monthly_income: Optional[float] = None

class UserPreferences(BaseModel):
    primary_goal: Optional[str] = "Build Emergency Fund"
    decision_aggressiveness: Optional[int] = 50
    stress_sensitivity: Optional[int] = 60

class UserProfile(BaseModel):
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: Optional[str] = None

    financial: FinancialProfile = FinancialProfile()
    preferences: UserPreferences = UserPreferences()
    notifications: NotificationSettings = NotificationSettings()

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    financial: Optional[FinancialProfile] = None
    preferences: Optional[UserPreferences] = None
    notifications: Optional[NotificationSettings] = None