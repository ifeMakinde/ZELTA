from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class StressLevel(str, Enum):
    CALM = "CALM"
    MODERATE = "MODERATE"
    HIGH_STRESS = "HIGH_STRESS"
    CRISIS = "CRISIS"


class BiasType(str, Enum):
    LOSS_AVERSION = "LOSS_AVERSION"
    PRESENT_BIAS = "PRESENT_BIAS"
    OVERCONFIDENCE = "OVERCONFIDENCE"
    HERD_BEHAVIOR = "HERD_BEHAVIOR"
    MENTAL_ACCOUNTING = "MENTAL_ACCOUNTING"
    NONE = "NONE"


class BQVerdict(str, Enum):
    SAVE = "SAVE"
    INVEST = "INVEST"
    HOLD = "HOLD"


class BayseSignal(BaseModel):
    naira_weakness_probability: float = Field(..., ge=0, le=100)
    cbn_rate_fear_index: float = Field(..., ge=0, le=100)
    inflation_anxiety_score: float = Field(..., ge=0, le=100)
    usd_ngn_threshold_probability: float = Field(..., ge=0, le=100)
    raw_crowd_stress: float = Field(..., ge=0, le=100)


class StressSignal(BaseModel):
    bayse_primary: float = Field(..., ge=0, le=100)
    nlp_secondary: float = Field(..., ge=0, le=100)
    combined_index: float = Field(..., ge=0, le=100)
    level: StressLevel
    label: str
    bayse_signal: Optional[BayseSignal] = None


class BiasSnapshot(BaseModel):
    active_bias: BiasType
    confidence: float = Field(..., ge=0, le=100)
    evidence: str
    rational_percentage: float
    behavioral_percentage: float
    confidence_gap: float


class DecisionAllocation(BaseModel):
    verdict: BQVerdict
    invest_amount: float
    save_amount: float
    hold_amount: float
    kelly_cap: float
    rationale: str
    plain_english: str


class Insight(BaseModel):
    title: str
    body: str
    severity: str  # "info", "warning", "danger"


class BrainResponse(BaseModel):
    stress: StressSignal
    bias: BiasSnapshot
    allocation: DecisionAllocation
    insights: List[Insight]
    suggestions: List[str]
    bayse_vs_model_gap: float
    decision_score: float


class IntelligenceResponse(BaseModel):
    success: bool
    data: BrainResponse