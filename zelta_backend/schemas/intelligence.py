"""
Intelligence schemas — shaped to match the deployed AI Brain response exactly.

Brain response top-level keys:
  bayse, nlp, stress, bias, decision, confidence, allocation, score, explanation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any


# ─── Bayse ────────────────────────────────────────────────────────────────────

class BayseSchema(BaseModel):
    score: float
    status: str                       # CALM / MODERATE / HIGH_STRESS / CRISIS
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
    # Aliased convenience fields
    raw_crowd_stress: float = 50.0
    naira_weakness_probability: float = 50.0


# ─── NLP ──────────────────────────────────────────────────────────────────────

class ScoredHeadline(BaseModel):
    source: str = ""
    title: str = ""
    url: str = ""
    timestamp: Optional[str] = None
    sentiment: int = 0               # -1, 0, 1
    confidence: float = 0.0
    sentiment_label: str = "neutral"
    is_campus_relevant: bool = False
    weight: float = 1.0


class NLPSchema(BaseModel):
    scored_headlines: List[ScoredHeadline] = []
    aggregate_sentiment: float = 0.0


# ─── Stress ───────────────────────────────────────────────────────────────────

class StressComponents(BaseModel):
    bayse_stress: float = 0.0
    nlp_stress: float = 0.0
    market_probability: float = 0.5
    bayse_weight: float = 0.6
    nlp_weight: float = 0.4


class StressSchema(BaseModel):
    combined_index: float             # 0-100
    level: str                        # CALM / MODERATE / HIGH_STRESS / CRISIS
    label: str                        # Plain English description
    bayse_primary: float = 0.0        # Bayse component (scaled 0-100)
    nlp_secondary: float = 0.0        # NLP component (scaled 0-100)
    market_probability: float = 0.5
    bayse_weight: float = 0.6
    nlp_weight: float = 0.4


# ─── Bias ─────────────────────────────────────────────────────────────────────

class BiasSchema(BaseModel):
    active_bias: str                  # e.g. "Rational", "LOSS_AVERSION"
    confidence: str                   # "Low" / "Moderate" / "High"
    explanation: str = ""
    inputs: dict = {}


# ─── Decision ─────────────────────────────────────────────────────────────────

class DecisionSchema(BaseModel):
    verdict: str                      # HOLD / INVEST / SAVE
    market_probability: float = 0.5
    rational_probability: float = 0.5
    edge: float = 0.0
    confidence: str = "Low"
    win_probability: float = 0.5
    bias_applied: str = "Rational"
    plain_english: str = ""


# ─── Confidence ───────────────────────────────────────────────────────────────

class ConfidenceMetrics(BaseModel):
    edge_contribution: float = 0.0
    stress_penalty: float = 0.0
    conviction_contribution: float = 0.0


class ConfidenceSchema(BaseModel):
    rational_pct: float               # % of decision that is rational
    behavioral_pct: float             # % that is emotional/behavioral
    gap: float                        # |rational - behavioral|
    confidence_score: float           # 0-100
    confidence_tier: str              # Low / Moderate / High
    score_label: str                  # WEAK / MODERATE / STRONG
    intervention_urgency: str         # LOW / MODERATE / HIGH
    is_actionable: bool = False
    plain_english: str = ""
    metrics: ConfidenceMetrics = ConfidenceMetrics()


# ─── Allocation ───────────────────────────────────────────────────────────────

class AllocationSchema(BaseModel):
    verdict: str                      # HOLD / INVEST / SAVE
    invest_amount: float = 0.0        # NGN (mapped from invest_ngn)
    save_amount: float = 0.0          # NGN (mapped from save_ngn)
    hold_amount: float = 0.0          # NGN (mapped from hold_ngn)
    allocation_pct: float = 0.0
    allocator_notes: str = ""
    plain_english: str = ""


# ─── Score ────────────────────────────────────────────────────────────────────

class ScoreComponents(BaseModel):
    edge_score: float = 0.0
    confidence_score: float = 0.0
    verdict_score: float = 0.0


class ScoreSchema(BaseModel):
    score: float                      # 0-5 (or 0-100 in some versions)
    decision_score: float
    rating: str                       # Poor / Fair / Good / Strong / Excellent
    components: ScoreComponents = ScoreComponents()


# ─── Explanation ──────────────────────────────────────────────────────────────

class ExplanationSchema(BaseModel):
    summary: str = ""
    reasoning: str = ""
    action: str = ""
    confidence_note: str = ""
    bq_alert: str = ""
    context_summary: str = ""


# ─── Top-level BrainResponse ──────────────────────────────────────────────────

class BrainResponse(BaseModel):
    """
    Normalised response from the deployed ZELTA AI Brain.
    All field names match the normaliser output in optimizer.py.
    """
    bayse: BayseSchema
    nlp: NLPSchema = NLPSchema()
    stress: StressSchema
    bias: BiasSchema
    decision: DecisionSchema
    confidence: ConfidenceSchema
    allocation: AllocationSchema
    score: ScoreSchema
    explanation: ExplanationSchema = ExplanationSchema()


class IntelligenceResponse(BaseModel):
    success: bool
    data: BrainResponse


# ─── Lightweight endpoint schemas ─────────────────────────────────────────────

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