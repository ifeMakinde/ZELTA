from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class APIResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool = False
    message: str
    detail: Optional[str] = None


class TimestampMixin(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaginationParams(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    page: int = 1
    limit: int = 20


class StressLevel(str, Enum):
    CALM = "CALM"
    MODERATE = "MODERATE"
    HIGH_STRESS = "HIGH_STRESS"
    CRISIS = "CRISIS"


class BQVerdict(str, Enum):
    SAVE = "SAVE"
    INVEST = "INVEST"
    HOLD = "HOLD"


class BiasType(str, Enum):
    LOSS_AVERSION = "LOSS_AVERSION"
    PRESENT_BIAS = "PRESENT_BIAS"
    OVERCONFIDENCE = "OVERCONFIDENCE"
    HERD_BEHAVIOR = "HERD_BEHAVIOR"
    MENTAL_ACCOUNTING = "MENTAL_ACCOUNTING"
    NONE = "NONE"
