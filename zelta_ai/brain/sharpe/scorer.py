from typing import Dict


class ZeltaDecisionScorer:
    """
    Scores decision quality on a 0-5 Sharpe-style scale.
    Higher = better risk-adjusted signal quality.

    Input:  bayesian/engine.py output
    Output: Feeds brain/pipeline.py unified JSON
    """

    def score_edge(self, edge: float) -> float:
        """Edge quality — 0.0 to 3.0 points"""
        abs_edge = abs(edge)
        if abs_edge >= 0.20:   return 3.0
        elif abs_edge >= 0.15: return 2.5
        elif abs_edge >= 0.10: return 2.0
        elif abs_edge >= 0.05: return 1.5
        elif abs_edge >= 0.02: return 0.8
        return 0.3

    def score_confidence(self, confidence: str) -> float:
        """Confidence bonus — 0.0 to 1.0 points"""
        return {
            "Very High": 1.0,
            "High":      0.8,
            "Medium":    0.5,
            "Low":       0.2,
        }.get(confidence, 0.2)

    def score_verdict(self, verdict: str) -> float:
        """Verdict bonus — INVEST/SAVE score higher than HOLD"""
        return 0.5 if verdict == "HOLD" else 1.0

    def clamp(self, score: float) -> float:
        return round(max(0.0, min(5.0, score)), 2)

    def interpret(self, score: float) -> str:
        if score >= 4.5:   return "Excellent"
        elif score >= 3.5: return "Strong"
        elif score >= 2.5: return "Decent"
        elif score >= 1.5: return "Weak"
        return "Poor"

    def run(self, bayesian_output: Dict) -> Dict:
        edge       = bayesian_output.get("edge", 0.0)
        confidence = bayesian_output.get("confidence", "Low")
        verdict    = bayesian_output.get("verdict", "HOLD")

        edge_score       = self.score_edge(edge)
        confidence_score = self.score_confidence(confidence)
        verdict_score    = self.score_verdict(verdict)

        total = self.clamp(
            edge_score + confidence_score + verdict_score
        )

        return {
            "score":          total,
            "decision_score": total,   # alias — used by confidence scorer
            "rating":         self.interpret(total),
            "components": {
                "edge_score":       edge_score,
                "confidence_score": confidence_score,
                "verdict_score":    verdict_score,
            }
        }


def run_decision_scoring(bayesian_output: Dict) -> Dict:
    """Called by brain/pipeline.py"""
    scorer = ZeltaDecisionScorer()
    result = scorer.run(bayesian_output)
    print(f"[ZELTA Sharpe] Score: {result['score']} ({result['rating']})")
    return result