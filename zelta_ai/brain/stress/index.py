# stress/index.py

from typing import Dict


class ZeltaBayseStressIndex:
    """
    Combines Bayse market signal (PRIMARY) + NLP sentiment (SECONDARY)
    to produce the ZELTA Student Stress Index (0-100).

    Weights:
    - Bayse crowd market signal: 60% (PRIMARY — real money crowd fear)
    - NLP campus sentiment:      40% (SECONDARY — news headlines)

    Output feeds directly into bayesian/engine.py and brain/pipeline.py
    """

    def __init__(
        self,
        weight_bayse: float = 0.6,
        weight_nlp: float = 0.4,
    ):
        self.weight_bayse = weight_bayse
        self.weight_nlp = weight_nlp

    def extract_market_probability(self, bayse_signal: Dict) -> float:
        """
        Extracts crowd probability from Bayse data.

        Bayse returns prices as 0.0 to 1.0 (e.g. 0.68 = 68% YES crowd belief).
        Falls back to spread-based score if ticker unavailable.
        """
        if "crowd_yes_price" in bayse_signal:
            return float(bayse_signal["crowd_yes_price"])

        if "yes_price" in bayse_signal:
            price = float(bayse_signal["yes_price"])
            if price > 1.0:
                price = price / 100.0
            return max(0.01, min(0.99, price))

        return 0.5

    def compute_bayse_stress(self, market_prob: float) -> float:
        """
        Converts crowd probability to a stress intensity value (0.0-1.0).

        Logic: extremes = high stress.
        - 0.90 YES crowd = 90% certain of bad outcome = PANIC
        - 0.50 YES crowd = uncertain = MODERATE
        - 0.10 YES crowd = 90% certain of good outcome = CALM but overconfident
        """
        return abs(market_prob - 0.5) * 2.0

    def compute_nlp_stress(self, sentiment_score: float) -> float:
        """
        Converts NLP aggregate sentiment to stress intensity (0.0-1.0).

        sentiment_score range: -1.0 (very negative) to +1.0 (very positive)
        More negative = more fear = more stress.
        """
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        return (1.0 - sentiment_score) / 2.0

    def combine(
        self,
        bayse_stress: float,
        nlp_stress: float,
    ) -> float:
        """Weighted combination of both signals"""
        return (
            bayse_stress * self.weight_bayse
            + nlp_stress * self.weight_nlp
        )

    def scale_to_100(self, value: float) -> int:
        return int(round(min(1.0, max(0.0, value)) * 100))

    def classify(self, score: int) -> str:
        """ZELTA four-level stress classification"""
        if score >= 80:
            return "CRISIS"
        elif score >= 60:
            return "HIGH STRESS"
        elif score >= 30:
            return "MODERATE"
        return "CALM"

    def get_plain_english(self, level: str, market_prob: float) -> str:
        """Plain English explanation for BQ Co-Pilot and dashboard"""
        crowd_pct = round(market_prob * 100)

        if level == "CRISIS":
            return (
                f"Financial environment is in crisis mode. "
                f"Bayse crowds are pricing {crowd_pct}% probability of negative outcome. "
                f"Extreme panic detected. ZELTA is applying strong behavioral correction."
            )
        elif level == "HIGH STRESS":
            return (
                f"Markets are anxious right now. "
                f"Bayse crowd pricing: {crowd_pct}%. "
                f"Your decisions this week may be driven by fear, not logic."
            )
        elif level == "MODERATE":
            return (
                f"Market environment is balanced. "
                f"Bayse crowd pricing: {crowd_pct}%. "
                f"Decisions are closest to rational — good time to review your plan."
            )
        return (
            f"Financial environment is calm. "
            f"Bayse crowd pricing: {crowd_pct}%. "
            f"Watch for overconfidence — calm markets can create complacency."
        )

    def compute(
        self,
        bayse_signal: Dict,
        sentiment_score: float,
    ) -> Dict:
        """
        Main computation. Called by brain/pipeline.py.

        Args:
            bayse_signal: Dict from LiveStressMonitor or REST ticker
            sentiment_score: Float from nlp/scorer.py aggregate (-1.0 to 1.0)

        Returns:
            Unified stress dict consumed by bayesian/engine.py
        """
        market_prob = self.extract_market_probability(bayse_signal)
        bayse_stress = self.compute_bayse_stress(market_prob)
        nlp_stress = self.compute_nlp_stress(sentiment_score)
        combined = self.combine(bayse_stress, nlp_stress)
        score = self.scale_to_100(combined)
        level = self.classify(score)

        return {
            "score": score,
            "stress_score": score,  # alias for compatibility
            "level": level,
            "plain_english": self.get_plain_english(level, market_prob),
            "components": {
                "bayse_stress": round(bayse_stress, 3),
                "nlp_stress": round(nlp_stress, 3),
                "market_probability": round(market_prob, 3),
                "bayse_weight": self.weight_bayse,
                "nlp_weight": self.weight_nlp,
            },
            "raw": {
                "sentiment_score": round(sentiment_score, 3),
                "bayse_signal": bayse_signal,
            },
        }

def run_stress_index(bayse_signal: Dict, sentiment_score: float) -> Dict:
    computer = ZeltaBayseStressIndex()
    return computer.compute(bayse_signal, sentiment_score)