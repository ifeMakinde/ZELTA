from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


class BayseSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    score: float = 50.0
    status: str = "MODERATE"  # CALM / MODERATE / HIGH_STRESS / CRISIS

    market_title: str = ""
    market_id: str = ""

    crowd_yes_price: float = 0.5
    crowd_no_price: float = 0.5
    mid_price: float = 0.5

    best_bid: float = 0.0
    best_ask: float = 0.0

    spread: float = 0.0
    imbalance: float = 0.0

    volume24h: float = 0.0
    trade_count_24h: int = 0

    available: bool = True

    # compatibility with your live payload
    raw_crowd_stress: float = 50.0
    naira_weakness_probability: float = 50.0
    outcome: Optional[str] = None
    last_price: float = 0.0
    source: str = ""
    updated_at: Optional[float] = None


class ScoredHeadline(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    source: str = ""
    title: str = ""
    url: str = ""
    timestamp: Optional[str] = None

    sentiment: int = 0  # -1, 0, 1
    confidence: float = 0.0
    sentiment_label: str = "neutral"

    is_campus_relevant: bool = False
    weight: float = 1.0


class NLPSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    scored_headlines: List[ScoredHeadline] = Field(default_factory=list)
    aggregate_sentiment: float = 0.0


class StressSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    combined_index: float = 50.0
    level: str = "MODERATE"
    label: str = ""

    bayse_primary: float = 0.0
    nlp_secondary: float = 0.0

    market_probability: float = 0.5
    bayse_weight: float = 0.6
    nlp_weight: float = 0.4

    plain_english: str = ""

    @computed_field
    @property
    def score(self) -> float:
        return self.combined_index

    @computed_field
    @property
    def stress_score(self) -> float:
        return self.combined_index


class BiasSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    active_bias: str = "Rational"
    confidence: str = "Low"  # Low / Moderate / High
    explanation: str = ""
    inputs: Dict[str, Any] = Field(default_factory=dict)

    # compatibility with payloads that use `bias`
    bias: Optional[str] = None


class DecisionSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    verdict: str = "HOLD"  # HOLD / INVEST / SAVE
    market_probability: float = 0.5
    rational_probability: float = 0.5
    edge: float = 0.0
    confidence: str = "Low"
    win_probability: float = 0.5
    bias_applied: str = "Rational"
    plain_english: str = ""


class ConfidenceMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    edge_contribution: float = 0.0
    stress_penalty: float = 0.0
    conviction_contribution: float = 0.0


class ConfidenceSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    rational_pct: float = 50.0
    behavioral_pct: float = 50.0
    gap: float = 0.0

    confidence_score: float = 50.0
    confidence_tier: str = "Low"

    score_label: str = "WEAK"
    intervention_urgency: str = "MODERATE"

    is_actionable: bool = False
    plain_english: str = ""

    metrics: ConfidenceMetrics = Field(default_factory=ConfidenceMetrics)

    @computed_field
    @property
    def confidence_score_100(self) -> float:
        return self.confidence_score

    @computed_field
    @property
    def confidence_label(self) -> str:
        return self.confidence_tier


class AllocationSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    verdict: str = "HOLD"

    # canonical names used by your route
    invest_ngn: float = 0.0
    save_ngn: float = 0.0
    hold_ngn: float = 0.0

    allocation_pct: float = 0.0
    allocator_notes: str = ""
    plain_english: str = ""

    # compatibility aliases for older code
    @computed_field
    @property
    def invest_amount(self) -> float:
        return self.invest_ngn

    @computed_field
    @property
    def save_amount(self) -> float:
        return self.save_ngn

    @computed_field
    @property
    def hold_amount(self) -> float:
        return self.hold_ngn


class ScoreComponents(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    edge_score: float = 0.0
    confidence_score: float = 0.0
    verdict_score: float = 0.0


class ScoreSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    score: float = 1.0
    decision_score: float = 1.0
    rating: str = "Poor"
    components: ScoreComponents = Field(default_factory=ScoreComponents)


class ExplanationSchema(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    summary: str = ""
    reasoning: str = ""
    action: str = ""

    what_this_means_for_you: Optional[str] = None
    bias_explanation: Optional[str] = None
    confidence_note: Optional[str] = None
    bq_alert: Optional[str] = None
    context_summary: Optional[str] = None


class BrainResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bayse: BayseSchema
    nlp: NLPSchema = Field(default_factory=NLPSchema)
    stress: StressSchema
    bias: BiasSchema
    decision: DecisionSchema
    confidence: ConfidenceSchema
    allocation: AllocationSchema
    score: ScoreSchema
    explanation: ExplanationSchema = Field(default_factory=ExplanationSchema)


class IntelligenceResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool
    data: BrainResponse


class StressOnlyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    stress_index: float
    level: str
    label: str

    bayse_primary: float
    nlp_secondary: float
    market_probability: float


class BayseMarketItem(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: str
    probability: float
    description: str


class BayseMarketsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    markets: List[BayseMarketItem]
    composite_stress: float
    bayse_available: bool
    market_title: str = ""
    verdict: str = ""
