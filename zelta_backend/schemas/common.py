from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None


class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20


class StressLevel(str):
    CALM = "CALM"
    MODERATE = "MODERATE"
    HIGH_STRESS = "HIGH_STRESS"
    CRISIS = "CRISIS"


class BQVerdict(str):
    SAVE = "SAVE"
    INVEST = "INVEST"
    HOLD = "HOLD"


class BiasType(str):
    LOSS_AVERSION = "LOSS_AVERSION"
    PRESENT_BIAS = "PRESENT_BIAS"
    OVERCONFIDENCE = "OVERCONFIDENCE"
    HERD_BEHAVIOR = "HERD_BEHAVIOR"
    MENTAL_ACCOUNTING = "MENTAL_ACCOUNTING"
    NONE = "NONE"