from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DecisionOutcome(str, Enum):
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"


class LogDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    verdict: str  # SAVE / INVEST / HOLD
    amount: float = Field(..., gt=0)
    rationale: str
    stress_index_at_decision: float
    bayse_fear_at_decision: float
    bias_at_decision: str
    decision_score: float
    category: str
    notes: Optional[str] = None


class UpdateOutcomeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    decision_id: str
    actual_outcome: float
    outcome_label: DecisionOutcome
    notes: Optional[str] = None


class DecisionRecord(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    verdict: str
    amount: float
    rationale: str
    stress_index: float
    bayse_fear: float
    bias: str
    decision_score: float
    category: str
    notes: Optional[str] = None
    actual_outcome: Optional[float] = None
    outcome_label: DecisionOutcome = DecisionOutcome.PENDING
    return_amount: Optional[float] = None
    return_percentage: Optional[float] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class PerformanceMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    total_decisions: int
    correct_decisions: int
    incorrect_decisions: int
    pending_decisions: int
    accuracy_rate: float
    average_decision_score: float
    total_invested: float
    total_returned: float
    net_pnl: float
    best_decision_score: float
    average_bayse_accuracy_gap: float


class PortfolioSummary(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    metrics: PerformanceMetrics
    recent_decisions: List[DecisionRecord] = Field(default_factory=list)
    behavioral_pattern_summary: str


class PortfolioResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool
    data: PortfolioSummary
