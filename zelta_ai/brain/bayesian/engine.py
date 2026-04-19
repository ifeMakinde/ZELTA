from typing import Dict


class ZeltaBayesianEngine:
    """
    Adjusts Bayse crowd probability using formal Bayesian inference.

    Core logic:
    Posterior Odds = Prior Odds × Likelihood Ratio

    The Likelihood Ratio is derived from the active behavioral bias.
    A biased crowd = distorted signal = QUELO corrects it.

    Output feeds into kelly/allocator.py and brain/pipeline.py.
    """

    # Minimum edge to trigger a BUY or SAVE verdict
    EDGE_THRESHOLD = 0.05

    # Probability thresholds for verdict
    INVEST_THRESHOLD = 0.55
    SAVE_THRESHOLD = 0.45

    def compute_likelihood_ratio(
        self,
        bias: str,
        stress_score: int,
    ) -> float:
        """
        How much is the current bias distorting the Bayse crowd signal?

        LR < 1 = crowd is overestimating risk (discount their panic)
        LR = 1 = crowd is rational (trust them)
        LR > 1 = crowd is underestimating risk (amplify the signal)
        """
        stress_factor = stress_score / 100.0

        if bias in ("Loss Aversion", "Panic Selling"):
            # Crowd is irrationally fearful — discount their signal
            # High stress = more discounting
            return max(0.2, 1.0 - (0.8 * stress_factor))

        elif bias in ("Overconfidence", "Present Bias"):
            # Crowd is irrationally optimistic — amplify risk signal
            return min(3.0, 1.0 + (2.0 * stress_factor))

        elif bias == "Herd Behavior":
            # Following momentum without analysis — mild discount
            return max(0.5, 1.0 - (0.4 * stress_factor))

        elif bias == "Mental Accounting":
            # Treating money differently — slight discount
            return max(0.7, 1.0 - (0.2 * stress_factor))

        # Rational — trust the crowd
        return 1.0

    def adjust_probability(
        self,
        market_prob: float,
        bias: str,
        stress_score: int,
    ) -> float:
        """
        Full Bayesian update:
        1. Convert Bayse crowd probability → odds
        2. Apply likelihood ratio (behavioral correction)
        3. Convert posterior odds → rational probability
        """
        # Clamp to avoid division by zero
        market_prob = max(0.01, min(0.99, market_prob))

        # Step 1 — Prior odds from Bayse crowd
        prior_odds = market_prob / (1.0 - market_prob)

        # Step 2 — Likelihood ratio from behavioral bias
        lr = self.compute_likelihood_ratio(bias, stress_score)

        # Step 3 — Posterior odds
        posterior_odds = prior_odds * lr

        # Step 4 — Convert back to probability
        rational_prob = posterior_odds / (1.0 + posterior_odds)

        return round(max(0.01, min(0.99, rational_prob)), 3)

    def compute_edge(
        self,
        market_prob: float,
        rational_prob: float,
    ) -> float:
        """
        Edge = gap between rational belief and crowd belief.
        Positive edge = crowd is too fearful = opportunity.
        Negative edge = crowd is too optimistic = caution.
        """
        return round(rational_prob - market_prob, 3)

    def confidence_level(self, edge: float) -> str:
        abs_edge = abs(edge)
        if abs_edge >= 0.20:
            return "Very High"
        elif abs_edge >= 0.15:
            return "High"
        elif abs_edge >= 0.05:
            return "Medium"
        else:
            return "Low"

    def decide(
        self,
        edge: float,
        rational_prob: float,
        stress_score: int,
    ) -> str:
        """
        QUELO three-verdict system: INVEST / SAVE / HOLD

        INVEST: rational model says positive outcome is likely
                AND there is meaningful edge vs crowd
        SAVE:   rational model says negative outcome is likely
                AND there is meaningful edge (crowd too optimistic)
        HOLD:   edge is too small to act on, or stress is extreme
        """
        # In CRISIS — always HOLD, protect capital first
        if stress_score >= 80:
            return "HOLD"

        if (
            rational_prob >= self.INVEST_THRESHOLD
            and edge >= self.EDGE_THRESHOLD
        ):
            return "INVEST"

        elif (
            rational_prob <= self.SAVE_THRESHOLD
            and edge <= -self.EDGE_THRESHOLD
        ):
            return "SAVE"

        return "HOLD"

    def get_plain_english(
        self,
        verdict: str,
        edge: float,
        market_prob: float,
        rational_prob: float,
        bias: str,
    ) -> str:
        """Plain English explanation for BQ Co-Pilot"""
        crowd_pct = round(market_prob * 100)
        rational_pct = round(rational_prob * 100)
        edge_pct = round(abs(edge) * 100)

        if verdict == "INVEST":
            return (
                f"The Bayse crowd is pricing {crowd_pct}% probability. "
                f"QUELO's Bayesian model says {rational_pct}%. "
                f"That {edge_pct}% gap means the crowd is more fearful than the data warrants. "
                f"Active bias: {bias}. QUELO recommends: INVEST."
            )
        elif verdict == "SAVE":
            return (
                f"The Bayse crowd is pricing {crowd_pct}% probability. "
                f"QUELO's model says {rational_pct}%. "
                f"The crowd is {edge_pct}% too optimistic given your situation. "
                f"Active bias: {bias}. QUELO recommends: SAVE — protect your capital."
            )
        else:
            return (
                f"The gap between crowd pricing ({crowd_pct}%) "
                f"and QUELO model ({rational_pct}%) is too small to act on confidently. "
                f"Active bias: {bias}. QUELO recommends: HOLD for now."
            )

    def run(
        self,
        stress_data: Dict,
        bias_data: Dict,
    ) -> Dict:
        """
        Main entry point called by brain/pipeline.py.

        Args:
            stress_data: Output from stress/index.py
            bias_data:   Output from bias/detector.py

        Returns:
            Bayesian analysis dict consumed by kelly/allocator.py
        """
        # Safe key access — consistent with stress/index.py output
        score = stress_data.get("score", 50)
        market_prob = stress_data.get(
            "components", {}
        ).get("market_probability", 0.5)
        bias = bias_data.get("bias", "Rational")

        rational_prob = self.adjust_probability(market_prob, bias, score)
        edge = self.compute_edge(market_prob, rational_prob)
        verdict = self.decide(edge, rational_prob, score)
        confidence = self.confidence_level(edge)

        return {
            "market_probability": round(market_prob, 3),
            "rational_probability": rational_prob,
            "edge": edge,
            "confidence": confidence,
            "verdict": verdict,
            "plain_english": self.get_plain_english(
                verdict, edge, market_prob, rational_prob, bias
            ),
            # For Kelly allocator
            "win_probability": rational_prob,
            "bias_applied": bias,
            "stress_score": score,
        }


# ── PIPELINE ENTRY POINT ──────────────────────────────────────────────────────

def run_bayesian_engine(stress_data: Dict, bias_data: Dict) -> Dict:
    """Called by brain/pipeline.py"""
    engine = ZeltaBayesianEngine()
    result = engine.run(stress_data, bias_data)
    print(
        f"[QUELO Bayesian] Market: {result['market_probability']} "
        f"→ Rational: {result['rational_probability']} "
        f"| Edge: {result['edge']} "
        f"| Verdict: {result['verdict']}"
    )
    return result
