"""
ZELTA Simulation Service

Monte Carlo Bayesian simulation for side hustle and savings scenarios.
Integrates with Bayse stress signal for real-time confidence adjustments.
"""

import numpy as np
import logging
from datetime import datetime, timezone, timedelta
from typing import List
from google.cloud import firestore
from schemas.simulation import (
    SideHustleSimRequest, SavingsSimRequest,
    SideHustleSimResult, SavingsSimResult,
    MonteCarloResult, WeekOutcome,
)
from config.settings import settings
from optimizer import fetch_bayse_signal, fetch_stress_signal

logger = logging.getLogger(__name__)

MONTE_CARLO_RUNS = 10_000


async def run_side_hustle_simulation(
    db: firestore.Client,
    uid: str,
    request: SideHustleSimRequest,
    current_stress_index: float = 50.0,
) -> SideHustleSimResult:
    """
    Run Bayesian Monte Carlo projection for a side hustle investment.

    Steps:
    1. Fetch current Bayse signal to adjust confidence bands
    2. Run 10,000 Monte Carlo iterations
    3. Apply Kelly criterion to recommended investment
    4. Return full result with Decision Score
    """

    bayse_signal = await fetch_bayse_signal()
    bayse_stress = bayse_signal["raw_crowd_stress"]

    # Stress adjusts the uncertainty of outcome distribution
    stress_uncertainty_multiplier = 1.0 + (bayse_stress / 200.0)  # up to 1.5x uncertainty

    revenue_mean = (request.expected_revenue_min + request.expected_revenue_max) / 2
    revenue_range = request.expected_revenue_max - request.expected_revenue_min
    revenue_std = (revenue_range / 4) * stress_uncertainty_multiplier  # 95% CI

    # Monte Carlo simulation
    rng = np.random.default_rng(seed=42)
    simulated_revenues = rng.normal(
        loc=revenue_mean,
        scale=revenue_std,
        size=MONTE_CARLO_RUNS,
    )

    # Apply fixed costs
    net_returns = simulated_revenues - request.fixed_costs - request.investment_amount

    # Compute percentiles
    p10 = float(np.percentile(net_returns, 10))
    p50 = float(np.percentile(net_returns, 50))
    p90 = float(np.percentile(net_returns, 90))
    mean_return = float(np.mean(net_returns))
    std_return = float(np.std(net_returns))

    success_probability = float(np.sum(net_returns > 0) / MONTE_CARLO_RUNS * 100)

    monte_carlo = MonteCarloResult(
        p10=round(p10, 2),
        p50=round(p50, 2),
        p90=round(p90, 2),
        mean=round(mean_return, 2),
        std_dev=round(std_return, 2),
        success_probability=round(success_probability, 1),
    )

    # Kelly-adjusted recommendation
    edge = success_probability / 100
    odds = max(0.1, revenue_mean / max(0.01, request.investment_amount))
    kelly_f = max(0.0, (edge - (1 - edge) / odds) * settings.kelly_fraction)

    # Stress cap on Kelly
    if current_stress_index >= settings.stress_crisis_threshold:
        kelly_f = 0.0
    elif current_stress_index >= settings.stress_high_threshold:
        kelly_f = min(kelly_f, settings.max_invest_ratio)

    kelly_amount = round(request.investment_amount * (kelly_f / max(0.01, kelly_f)), 2)
    kelly_amount = min(kelly_amount, request.investment_amount)

    # Decision score (0-5 Sharpe-style)
    sharpe_score = round(
        (mean_return / max(1.0, std_return)) * (success_probability / 100) * 5, 2
    )
    sharpe_score = max(0.0, min(5.0, sharpe_score))

    roi_pct = round((mean_return / request.investment_amount) * 100, 1) if request.investment_amount > 0 else 0.0

    # Verdict
    if kelly_amount <= 0 or current_stress_index >= settings.stress_crisis_threshold:
        verdict = "HOLD"
        plain_english = f"CRISIS stress ({current_stress_index:.0f}/100). Do not invest now. Wait for markets to calm."
    elif success_probability >= 60 and sharpe_score >= 2.0:
        verdict = "INVEST"
        plain_english = (
            f"Strong signal. {success_probability:.0f}% chance of profit. "
            f"Kelly-safe amount: ₦{kelly_amount:,.0f}. Decision Score: {sharpe_score:.1f}/5. INVEST."
        )
    else:
        verdict = "SAVE"
        plain_english = (
            f"Marginal returns at current stress level ({current_stress_index:.0f}/100). "
            f"Save your ₦{request.investment_amount:,.0f} this week. Revisit next week."
        )

    return SideHustleSimResult(
        recommended_investment=round(request.investment_amount, 2),
        kelly_adjusted_amount=kelly_amount,
        decision_score=sharpe_score,
        expected_return_min=round(p10 + request.investment_amount, 2),
        expected_return_max=round(p90 + request.investment_amount, 2),
        expected_return_mean=round(mean_return + request.investment_amount, 2),
        roi_percentage=roi_pct,
        monte_carlo=monte_carlo,
        stress_adjusted=current_stress_index >= settings.stress_high_threshold,
        verdict=verdict,
        plain_english=plain_english,
        sharpe_score=sharpe_score,
    )


async def run_savings_simulation(
    db: firestore.Client,
    uid: str,
    request: SavingsSimRequest,
    current_stress_index: float = 50.0,
) -> SavingsSimResult:
    """
    Model savings trajectory against upcoming fee obligations.
    Returns week-by-week obligation risk map with green/amber/red status.
    """

    weeks_needed = int(np.ceil(request.target_amount / max(1.0, request.weekly_savings_amount)))
    obligation_risk_map: List[WeekOutcome] = []

    running_balance = 0.0
    green_weeks = amber_weeks = red_weeks = 0

    obligations_by_week: dict = {}
    now = datetime.now(timezone.utc)
    for obl in (request.upcoming_obligations or []):
        due = obl.get("due_date")
        if due:
            if isinstance(due, str):
                due = datetime.fromisoformat(due)
            week_num = max(1, int((due - now).days / 7) + 1)
            obligations_by_week[week_num] = obligations_by_week.get(week_num, 0) + obl.get("amount", 0)

    total_weeks = max(weeks_needed, max(obligations_by_week.keys()) if obligations_by_week else weeks_needed)

    shortfall_total = 0.0
    for week in range(1, total_weeks + 1):
        running_balance += request.weekly_savings_amount
        obligation_this_week = obligations_by_week.get(week, 0.0)
        balance_after_obligation = running_balance - obligation_this_week

        # Risk level based on remaining balance vs obligations ahead
        obligations_remaining = sum(v for k, v in obligations_by_week.items() if k > week)
        balance_to_obligations_ratio = balance_after_obligation / max(1.0, obligations_remaining) if obligations_remaining > 0 else 1.5

        if balance_after_obligation < 0:
            status = "red"
            risk_level = 0.9
            red_weeks += 1
            shortfall_total += abs(balance_after_obligation)
        elif balance_to_obligations_ratio < 0.5:
            status = "amber"
            risk_level = 0.5
            amber_weeks += 1
        else:
            status = "green"
            risk_level = 0.1
            green_weeks += 1

        running_balance = max(0, balance_after_obligation)

        obligation_risk_map.append(WeekOutcome(
            week=week,
            projected_balance=round(running_balance, 2),
            status=status,
            risk_level=risk_level,
        ))

    # Savings quality score (Sharpe-style 0-5)
    if total_weeks > 0:
        savings_score = round(
            (green_weeks / total_weeks) * 5 * (1 - current_stress_index / 200), 2
        )
    else:
        savings_score = 0.0
    savings_score = max(0.0, min(5.0, savings_score))

    weekly_surplus = round(request.weekly_savings_amount - (request.target_amount / max(1, weeks_needed)), 2)

    # Verdict
    if red_weeks > total_weeks * 0.3:
        verdict = "SAVE_MORE"
        plain_english = (
            f"Your savings plan has {red_weeks} red weeks — shortfall risk is HIGH. "
            f"Increase weekly savings by ₦{abs(weekly_surplus):,.0f} to stay on track."
        )
    elif amber_weeks > total_weeks * 0.4:
        verdict = "REVIEW"
        plain_english = (
            f"Your plan is borderline. {amber_weeks} amber weeks detected. "
            f"Small income increase or expense reduction will protect your obligations."
        )
    else:
        verdict = "ON_TRACK"
        plain_english = (
            f"Savings score: {savings_score:.1f}/5. You are on track to meet your ₦{request.target_amount:,.0f} target "
            f"in {weeks_needed} weeks. Keep going."
        )

    return SavingsSimResult(
        weeks_to_target=weeks_needed,
        weekly_surplus=weekly_surplus,
        obligation_risk_map=obligation_risk_map,
        projected_shortfall=round(shortfall_total, 2),
        savings_score=savings_score,
        green_weeks=green_weeks,
        amber_weeks=amber_weeks,
        red_weeks=red_weeks,
        verdict=verdict,
        plain_english=plain_english,
    )