// ─── /api/brain ──────────────────────────────────────────────────

export type Verdict = "SAVE" | "INVEST" | "HOLD";
export type StressLevel = "CALM" | "MODERATE" | "CRISIS";
export type ConfidenceTier = "Low" | "Medium" | "High";
export type ScoreLabel = "WEAK" | "MODERATE" | "STRONG";
export type ScoreRating = "Poor" | "Fair" | "Good" | "Excellent";
export type BiasType =
  | "Rational"
  | "Loss Aversion"
  | "Overconfidence"
  | "Anchoring";
export type Urgency = "LOW" | "MODERATE" | "HIGH";

export interface BrainData {
  bayse: {
    score: number;
    status: StressLevel;
    market_title: string;
    market_id: string;
    crowd_yes_price: number;
    crowd_no_price: number;
    mid_price: number;
    best_bid: number;
    best_ask: number;
    spread: number;
    imbalance: number;
    volume24h: number;
    trade_count_24h: number;
    available: boolean;
    raw_crowd_stress: number;
    naira_weakness_probability: number;
    outcome: string | null;
    last_price: number;
    source: string;
    updated_at: string | null;
  };
  nlp: {
    scored_headlines: {
      source: string;
      title: string;
      url: string;
      timestamp: string;
      sentiment: number;
      confidence: number;
      sentiment_label: "positive" | "negative" | "neutral";
      is_campus_relevant: boolean;
      weight: number;
    }[];
    aggregate_sentiment: number;
  };
  stress: {
    combined_index: number;
    level: StressLevel;
    label: string;
    bayse_primary: number;
    nlp_secondary: number;
    market_probability: number;
    bayse_weight: number;
    nlp_weight: number;
    plain_english: string;
    score: number;
    stress_score: number;
  };
  bias: {
    active_bias: BiasType;
    confidence: ConfidenceTier;
    explanation: string;
    inputs: Record<string, unknown>;
    bias: string | null;
  };
  decision: {
    verdict: Verdict;
    market_probability: number;
    rational_probability: number;
    edge: number;
    confidence: ConfidenceTier;
    win_probability: number;
    bias_applied: string;
    plain_english: string;
  };
  confidence: {
    rational_pct: number;
    behavioral_pct: number;
    gap: number;
    confidence_score: number;
    confidence_tier: ConfidenceTier;
    score_label: ScoreLabel;
    intervention_urgency: Urgency;
    is_actionable: boolean;
    plain_english: string;
    metrics: {
      edge_contribution: number;
      stress_penalty: number;
      conviction_contribution: number;
    };
    confidence_score_100: number;
    confidence_label: string;
  };
  allocation: {
    verdict: Verdict;
    invest_ngn: number;
    save_ngn: number;
    hold_ngn: number;
    allocation_pct: number;
    allocator_notes: string;
    plain_english: string;
    invest_amount: number;
    save_amount: number;
    hold_amount: number;
  };
  score: {
    score: number;
    decision_score: number;
    rating: ScoreRating;
    components: {
      edge_score: number;
      confidence_score: number;
      verdict_score: number;
    };
  };
  explanation: {
    summary: string;
    reasoning: string;
    action: string;
    what_this_means_for_you: string;
    bias_explanation: string;
    confidence_note: string;
    bq_alert: string | null;
    context_summary: string;
  };
}

// ─── /api/intelligence ───────────────────────────────────────────

export interface IntelligenceData {
  stress_index: number;
  stress_level: StressLevel;
  stress_label: string;
  bayse_primary: number;
  nlp_secondary: number;
  market_probability?: number;
  bayse_score: number;
  bayse_status: StressLevel;
  bayse_market: string;
  crowd_yes?: number;
  crowd_no: number;
  mid_price: number;
  spread: number;
  active_bias: string;
  bias_confidence: string;
  bias_explanation: string;
  decision_verdict: Verdict;
  edge: number;
  win_probability: number;
  decision_plain: string;
  rational_pct: number;
  behavioral_pct: number;
  confidence_gap: number;
  confidence_score: number;
  confidence_tier: ConfidenceTier;
  score_label: ScoreLabel;
  is_actionable: boolean;
  intervention_urgency: Urgency;
  confidence_plain: string;
  verdict: Verdict;
  invest_ngn?: number;
  save_ngn: number;
  hold_ngn: number;
  allocation_pct: number;
  allocation_plain: string;
  decision_score: number;
  score_rating: ScoreRating;
  summary: string;
  bq_alert: string | null;
  action: string;
  nlp_sentiment: number;
  headlines: unknown[];
}

// ─── /api/stress ─────────────────────────────────────────────────

export interface StressData {
  stress_index: number;
  level: StressLevel;
  label: string;
  bayse_primary: number;
  nlp_secondary: number;
  market_probability: number;
}

// ─── /api/bayse/markets ──────────────────────────────────────────

export interface BayseMarket {
  name: string;
  probability: number;
  description: string;
}

export interface MarketsData {
  markets: BayseMarket[];
  composite_stress: number;
  bayse_available: boolean;
  market_title: string;
  verdict: StressLevel;
}

// ─── /api/bayse/stress ───────────────────────────────────────────

export interface BayseStressData {
  crowd_stress: number;
  bayse_score: number;
  bayse_status: StressLevel;
  market_title: string;
  mid_price: number;
  spread: number;
  available: boolean;
}

// ─── /api/bayse/sentiment ────────────────────────────────────────

export interface BayseSentimentData {
  panic_score: number;
  interpretation: StressLevel;
  crowd_yes_price: number;
  imbalance: number;
  volume24h: number;
}

// ─── combined bayse signals ──────────────────────────────────────

export interface BayseSignalsData {
  stress: BayseStressData;
  sentiment: BayseSentimentData;
}
