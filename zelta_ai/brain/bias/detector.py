# bias/detector.py

from typing import Dict, Optional


class ZeltaBiasDetector:
    """
    Identifies the active cognitive bias from stress + wallet patterns.
    Five biases: loss aversion, present bias, overconfidence,
                 herd behavior, mental accounting.
    Output feeds directly into brain/pipeline.py and BQ Co-Pilot.
    """

    def detect(
        self,
        stress_data: Dict,
        sentiment_score: float,
        wallet_data: Optional[Dict] = None,
    ) -> Dict:

        stress_score = stress_data.get("score", stress_data.get("stress_score", 50))
        market_prob = stress_data.get("components", {}).get("market_probability", 0.5)

        wallet_data = wallet_data or {
            "spending_spike": False,
            "cash_withdrawal": False,
            "impulse_buy": False,
            "side_hustle_income_recent": False,
        }

        bias = "Rational"
        confidence = "Low"
        explanation = "Market appears stable. Your decisions are likely logical."

        if stress_score >= 60 and wallet_data.get("cash_withdrawal"):
            bias = "Loss Aversion"
            confidence = "High"
            explanation = (
                "Market fear is high and you withdrew cash. "
                "You are hoarding out of panic, not logic. "
                "ZELTA corrected this — the rational action is different."
            )

        elif wallet_data.get("impulse_buy"):
            bias = "Present Bias"
            confidence = "High"
            explanation = (
                "You made an impulse purchase. "
                "Your upcoming obligations are at risk. "
                "ZELTA recommends reviewing your obligation map."
            )

        elif stress_score < 30 and sentiment_score > 0.3:
            bias = "Overconfidence"
            confidence = "Medium"
            explanation = (
                "Market is calm and sentiment is very positive. "
                "Overconfidence risk is active — "
                "you may be over-allocating to risky decisions."
            )

        elif 40 <= stress_score < 70 and abs(market_prob - 0.5) > 0.35:
            bias = "Herd Behavior"
            confidence = "Medium"
            explanation = (
                "Bayse crowd is positioned heavily to one side. "
                "You may be following the crowd without your own analysis. "
                "ZELTA separates your data from crowd noise."
            )

        elif (
            wallet_data.get("spending_spike")
            and wallet_data.get("side_hustle_income_recent")
        ):
            bias = "Mental Accounting"
            confidence = "Medium"
            explanation = (
                "You received side hustle income and spending spiked. "
                "You may be treating this as free money. "
                "ZELTA sees all naira equally — every naira has the same value."
            )

        elif wallet_data.get("spending_spike") and stress_score < 60:
            bias = "Mental Accounting"
            confidence = "Low"
            explanation = (
                "Spending is elevated without a clear stress trigger. "
                "Review your unified wallet view."
            )

        return {
            "bias": bias,
            "active_bias": bias,  # alias for compatibility
            "confidence": confidence,
            "explanation": explanation,
            "inputs": {
                "stress_score": stress_score,
                "sentiment": sentiment_score,
                "market_probability": market_prob,
            },
        }

    def run(
        self,
        stress_data: Dict,
        sentiment_score: float,
        wallet_data: Dict = None,
    ) -> Dict:
        """Entry point called by brain/pipeline.py"""
        return self.detect(stress_data, sentiment_score, wallet_data)