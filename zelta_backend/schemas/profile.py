from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from enum import Enum


class RiskTolerance(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class NotificationFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    REAL_TIME = "real_time"
    OFF = "off"


class FinancialProfile(BaseModel):
    monthly_budget: Optional[float] = None
    fee_obligations: Optional[List[dict]] = []  # [{label, amount, due_date}]
    income_sources: Optional[List[str]] = []
    side_hustle_type: Optional[str] = None
    hostel_fee: Optional[float] = None
    tuition_amount: Optional[float] = None
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE


class PreferencesProfile(BaseModel):
    currency: str = "NGN"
    language: str = "en"
    stress_alert_threshold: int = Field(60, ge=0, le=100)
    auto_lock_on_crisis: bool = True
    show_bayse_prices: bool = True
    plain_english_mode: bool = True


class NotificationsProfile(BaseModel):
    stress_alerts: bool = True
    weekly_bq_report: bool = True
    decision_reminders: bool = True
    bayse_spike_alerts: bool = True
    frequency: NotificationFrequency = NotificationFrequency.DAILY


class UserProfile(BaseModel):
    uid: str
    email: str
    name: str
    picture: Optional[str] = None
    university: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None
    financial: FinancialProfile = FinancialProfile()
    preferences: PreferencesProfile = PreferencesProfile()
    notifications: NotificationsProfile = NotificationsProfile()


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    university: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None
    financial: Optional[FinancialProfile] = None
    preferences: Optional[PreferencesProfile] = None
    notifications: Optional[NotificationsProfile] = None


class ProfileResponse(BaseModel):
    success: bool
    data: UserProfile