from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SimulationType(str, Enum):
    SIDE_HUSTLE = "side_hustle"
    SAVINGS = "savings"


class SideHustleSimRequest(BaseModel):
    investment_amount: float = Field(..., gt=0, description="Amount to invest in NGN")
    hustle_type: str = Field(..., description="Type of side hustle e.g. catering, reselling")
    expected_revenue_min: float = Field(..., gt=0)
    expected_revenue_max: float = Field(..., gt=0)
    time_horizon_weeks: int = Field(..., ge=1, le=52)
    fixed_costs: Optional[float] = Field(0.0, ge=0)


class SavingsSimRequest(BaseModel):
    weekly_savings_amount: float = Field(..., gt=0)
    target_amount: float = Field(..., gt=0)
    upcoming_obligations: Optional[List[dict]] = []


class WeekOutcome(BaseModel):
    week: int
    projected_balance: float
    status: str  # "green", "amber", "red"
    risk_level: float


class MonteCarloResult(BaseModel):
    p10: float  # 10th percentile outcome
    p50: float  # Median outcome
    p90: float  # 90th percentile outcome
    mean: float
    std_dev: float
    success_probability: float


class SideHustleSimResult(BaseModel):
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
    weeks_to_target: int
    weekly_surplus: float
    obligation_risk_map: List[WeekOutcome]
    projected_shortfall: float
    savings_score: float  # Sharpe-style 0-5
    green_weeks: int
    amber_weeks: int
    red_weeks: int
    verdict: str
    plain_english: str


class SimulationResponse(BaseModel):
    success: bool
    simulation_type: SimulationType
    data: dict