from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SimulationType(str, Enum):
    SIDE_HUSTLE = "side_hustle"
    SAVINGS = "savings"


class SideHustleSimRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "investment_amount": 50000,
                "hustle_type": "reselling",
                "expected_revenue_min": 70000,
                "expected_revenue_max": 120000,
                "time_horizon_weeks": 4,
                "fixed_costs": 15000,
            }
        },
    )

    investment_amount: float = Field(..., gt=0, description="Amount to invest in NGN")
    hustle_type: str = Field(..., description="Type of side hustle e.g. catering, reselling")
    expected_revenue_min: float = Field(..., gt=0)
    expected_revenue_max: float = Field(..., gt=0)
    time_horizon_weeks: int = Field(..., ge=1, le=52)
    fixed_costs: Optional[float] = Field(0.0, ge=0)


class SavingsSimRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    weekly_savings_amount: float = Field(..., gt=0)
    target_amount: float = Field(..., gt=0)
    upcoming_obligations: List[dict] = Field(default_factory=list)


class WeekOutcome(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    week: int
    projected_balance: float
    status: str  # green / amber / red
    risk_level: float


class MonteCarloResult(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    p10: float
    p50: float
    p90: float
    mean: float
    std_dev: float
    success_probability: float


class SideHustleSimResult(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    recommended_investment: float
    kelly_adjusted_amount: float
    decision_score: float
    expected_return_min: float
    expected_return_max: float
    expected_return_mean: float
    roi_percentage: float
    monte_carlo: MonteCarloResult
    stress_adjusted: bool
    verdict: str
    plain_english: str
    sharpe_score: float


class SavingsSimResult(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    weeks_to_target: int
    weekly_surplus: float
    obligation_risk_map: List[WeekOutcome]
    projected_shortfall: float
    savings_score: float
    green_weeks: int
    amber_weeks: int
    red_weeks: int
    verdict: str
    plain_english: str


class SimulationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool
    simulation_type: SimulationType
    data: dict
