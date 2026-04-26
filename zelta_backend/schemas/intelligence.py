"""
Intelligence schemas — aligned with deployed ZELTA AI Brain + Co-Pilot output.

Top-level keys:
  bayse, nlp, stress, bias, decision, confidence, allocation, score, explanation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ─────────────────────────────────────────────────────────────────────────────
# BAYSE
# ─────────────────────────────────────────────────────────────────────────────

class BayseSchema(BaseModel):
    score: float
    status: str  # CALM / MODERATE / HIGH_STRESS / CRISIS

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

    # Derived / alias fields
    raw_crowd_stress: float = 50.0
    naira_weakness_probability: float = 50.0


# ─────────────────────────────────────────────────────────────────────────────
# NLP
# ─────────────────────────────────────────────────────────────────────────────

class ScoredHeadline(BaseModel):
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
    scored_headlines: List[ScoredHeadline] = Field(default_factory=list)
    aggregate_sentiment: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# STRESS
# ─────────────────────────────────────────────────────────────────────────────

class StressComponents(BaseModel):
    bayse_stress: float = 0.0
    nlp_stress: float = 0.0
    market_probability: float = 0.5
    bayse_weight: float = 0.6
    nlp_weight: float = 0.4


class StressSchema(BaseModel):
    combined_index: float  # 0-100
    level: str             # CALM / MODERATE / HIGH_STRESS / CRISIS
    label: str

    bayse_primary: float = 0.0
    nlp_secondary: float = 0.0

    market_probability: float = 0.5
    bayse_weight: float = 0.6
    nlp_weight: float = 0.4


# ─────────────────────────────────────────────────────────────────────────────
# BIAS
# ─────────────────────────────────────────────────────────────────────────────

class BiasSchema(BaseModel):
    active_bias: str
    confidence: str  # Low / Moderate / High
    explanation: str = ""

    inputs: Dict = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# DECISION
# ─────────────────────────────────────────────────────────────────────────────

class DecisionSchema(BaseModel):
    verdict: str  # HOLD / INVEST / SAVE

    market_probability: float = 0.5
    rational_probability: float = 0.5

    edge: float = 0.0
    confidence: str = "Low"

    win_probability: float = 0.5
    bias_applied: str = "Rational"

    plain_english: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE
# ─────────────────────────────────────────────────────────────────────────────

class ConfidenceMetrics(BaseModel):
    edge_contribution: float = 0.0
    stress_penalty: float = 0.0
    conviction_contribution: float = 0.0


class ConfidenceSchema(BaseModel):
    rational_pct: float
    behavioral_pct: float
    gap: float

    confidence_score: float  # 0-100
    confidence_tier: str

    score_label: str
    intervention_urgency: str

    is_actionable: bool = False
    plain_english: str = ""

    metrics: ConfidenceMetrics = Field(default_factory=ConfidenceMetrics)


# ─────────────────────────────────────────────────────────────────────────────
# ALLOCATION
# ─────────────────────────────────────────────────────────────────────────────

class AllocationSchema(BaseModel):
    verdict: str

    # Support BOTH naming styles (service already handles mapping)
    invest_amount: float = 0.0
    save_amount: float = 0.0
    hold_amount: float = 0.0

    allocation_pct: float = 0.0
    allocator_notes: str = ""

    plain_english: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# SCORE
# ─────────────────────────────────────────────────────────────────────────────

class ScoreComponents(BaseModel):
    edge_score: float = 0.0
    confidence_score: float = 0.0
    verdict_score: float = 0.0


class ScoreSchema(BaseModel):
    score: float
    decision_score: float
    rating: str

    components: ScoreComponents = Field(default_factory=ScoreComponents)


# ─────────────────────────────────────────────────────────────────────────────
# EXPLANATION (UPDATED FOR COPILOT)
# ─────────────────────────────────────────────────────────────────────────────

class ExplanationSchema(BaseModel):
    summary: str = ""
    reasoning: str = ""
    action: str = ""

    # ✅ NEW (from your Copilot upgrade)
    what_this_means_for_you: Optional[str] = None
    bias_explanation: Optional[str] = None

    confidence_note: Optional[str] = None
    bq_alert: Optional[str] = None
    context_summary: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# TOP LEVEL
# ─────────────────────────────────────────────────────────────────────────────

class BrainResponse(BaseModel):
    """
    Normalised response from the deployed ZELTA AI Brain.
    """

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
    success: bool
    data: BrainResponse


# ─────────────────────────────────────────────────────────────────────────────
# LIGHTWEIGHT RESPONSES
# ─────────────────────────────────────────────────────────────────────────────

class StressOnlyResponse(BaseModel):
    stress_index: float
    level: str
    label: str

    bayse_primary: float
    nlp_secondary: float
    market_probability: float


class BayseMarketItem(BaseModel):
    name: str
    probability: float
    description: str


class BayseMarketsResponse(BaseModel):
    markets: List[BayseMarketItem]

    composite_stress: float
    bayse_available: bool

    market_title: str = ""
    verdict: str = ""
