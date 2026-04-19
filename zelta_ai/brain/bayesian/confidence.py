# bayesian/confidence.py

from typing import Dict


class ZeltaConfidenceScorer:
    """
    Evaluates the overall reliability of a ZELTA verdict.

    While the Bayesian Engine calculates the mathematical edge,
    this module determines how much we actually trust that edge
    before sending it to the Kelly Allocator.

    Input:  bayesian/engine.py output + stress/index.py output + bias/detector.py output
    Output: Feeds brain/pipeline.py unified JSON
    """

    BASE_SCORE = 50

    def evaluate_edge_strength(self, edge: float) -> int:
        """
        Score the mathematical edge.
        Larger edge = crowd and model disagree more = stronger signal.
        Range: 0 to +30 points.
        """
        abs_edge = abs(edge)
        if abs_edge >= 0.20:
            return 30
        elif abs_edge >= 0.10:
            return 20
        elif abs_edge >= 0.05:
            return 10
        return 0

    def evaluate_market_stress(self, stress_score: int) -> int:
        """
        Penalise confidence when market is chaotic.
        High stress = unpredictable = less trustworthy signal.
        Range: -40 to +10 points.
        """
        if stress_score >= 80:
            return -40
        elif stress_score >= 60:
            return -20
        elif stress_score <= 30:
            return 10
        return 0

    def evaluate_conviction(self, rational_prob: float) -> int:
        """
        Score how definitive the model's belief is.
        Near 0% or 100% = high conviction.
        Near 50% = coin toss = low conviction.
        Range: 0 to +20 points.
        """
        distance_from_center = abs(0.5 - rational_prob)
        if distance_from_center >= 0.30:
            return 20
        elif distance_from_center >= 0.15:
            return 10
        return 0

    def get_confidence_label(self, score: int) -> str:
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        return "Low"

    def get_score_label(self, score: int) -> str:
        """Decision quality label for simulation screen"""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 60:
            return "STRONG"
        elif score >= 40:
            return "MODERATE"
        return "WEAK"

    def get_urgency(self, behavioral_pct: int, stress_score: int) -> str:
        """How urgently does ZELTA need to intervene?"""
        if behavioral_pct >= 70 or stress_score >= 80:
            return "URGENT"
        elif behavioral_pct >= 50 or stress_score >= 60:
            return "MODERATE"
        elif behavioral_pct >= 30:
            return "LOW"
        return "NONE"

    def get_plain_english(
        self,
        rational_pct: int,
        behavioral_pct: int,
        gap: int,
        urgency: str,
        bias: str,
        verdict: str,
    ) -> str:
        """Plain English explanation for Co-Pilot and home screen"""
        if urgency == "URGENT":
            return (
                f"Your decisions right now are {behavioral_pct}% driven by "
                f"{bias} — not logic. The math disagrees with your instincts "
                f"by {gap} points. ZELTA has applied a strong correction. "
                f"Recommended action: {verdict}."
            )
        elif urgency == "MODERATE":
            return (
                f"There is a {gap}% gap between what the data says and what "
                f"your emotional state is pushing you toward. "
                f"Active bias: {bias}. ZELTA has corrected for this. "
                f"Recommended action: {verdict}."
            )
        elif urgency == "LOW":
            return (
                f"Your situation is {rational_pct}% rational right now. "
                f"Minor {bias} detected but within normal range. "
                f"ZELTA recommends: {verdict}."
            )
        return (
            f"Your financial environment is highly rational. "
            f"Decisions are data-driven with minimal emotional distortion. "
            f"ZELTA recommends: {verdict}."
        )

    def run(
        self,
        bayesian_data: Dict,
        stress_data: Dict,
        bias_data: Dict,
    ) -> Dict:
        """
        Main entry point. Called by brain/pipeline.py.

        Args:
            bayesian_data: Output from ZeltaBayesianEngine.run()
            stress_data:   Output from stress/index.py
            bias_data:     Output from bias/detector.py

        Returns:
            Confidence dict consumed by kelly/allocator.py
            and brain/pipeline.py unified JSON
        """
        edge = bayesian_data.get("edge", 0.0)
        rational_prob = bayesian_data.get(
            "rational_probability",
            bayesian_data.get("win_probability", 0.5),
        )
        stress_score = stress_data.get("score", stress_data.get("stress_score", 50))
        verdict = bayesian_data.get("verdict", bayesian_data.get("decision", "HOLD"))
        bias = bias_data.get("bias", bayesian_data.get("bias_applied", "Neutral"))

        edge_points = self.evaluate_edge_strength(edge)
        stress_points = self.evaluate_market_stress(stress_score)
        conviction_points = self.evaluate_conviction(rational_prob)

        raw_score = self.BASE_SCORE + edge_points + stress_points + conviction_points
        final_score = max(0, min(100, raw_score))

        if verdict == "HOLD":
            final_score = min(final_score, 39)

        rational_pct = final_score
        behavioral_pct = 100 - final_score
        gap = abs(rational_pct - behavioral_pct)

        confidence_label = self.get_confidence_label(final_score)
        score_label = self.get_score_label(final_score)
        urgency = self.get_urgency(behavioral_pct, stress_score)

        plain_english = self.get_plain_english(
            rational_pct,
            behavioral_pct,
            gap,
            urgency,
            bias,
            verdict,
        )

        result = {
            "rational_pct": rational_pct,
            "behavioral_pct": behavioral_pct,
            "gap": gap,

            "confidence_score_100": final_score,
            "confidence_score": final_score,   # alias
            "confidence_tier": confidence_label,
            "confidence_label": confidence_label,  # alias
            "score_label": score_label,

            "intervention_urgency": urgency,

            "is_actionable": final_score >= 60,

            "plain_english": plain_english,

            "metrics": {
                "edge_contribution": edge_points,
                "stress_penalty": stress_points,
                "conviction_contribution": conviction_points,
            },
        }

        return result


def run_confidence_scorer(
    bayesian_data: Dict,
    stress_data: Dict,
    bias_data: Dict,
) -> Dict:
    """Called by brain/pipeline.py right after the Bayesian Engine"""
    scorer = ZeltaConfidenceScorer()
    result = scorer.run(bayesian_data, stress_data, bias_data)
    print(
        f"[ZELTA Confidence] Score: {result['confidence_score_100']}/100 "
        f"| Rational: {result['rational_pct']}% "
        f"| Tier: {result['confidence_tier']} "
        f"| Actionable: {result['is_actionable']}"
    )
    return result