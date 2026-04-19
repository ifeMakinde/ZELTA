# tests/test_bayesian_engine.py

import pytest
from bayesian.engine import ZeltaBayesianEngine


@pytest.fixture
def engine():
    return ZeltaBayesianEngine()


def test_likelihood_ratio_loss_aversion(engine):
    # Loss aversion/panic should discount the crowd (LR < 1.0)
    lr = engine.compute_likelihood_ratio("Loss Aversion", stress_score=80)
    assert lr < 1.0
    assert lr == max(0.2, 1.0 - (0.8 * 0.8))  # 1.0 - 0.64 = 0.36


def test_likelihood_ratio_overconfidence(engine):
    # Overconfidence should inflate the evidence (LR > 1.0)
    lr = engine.compute_likelihood_ratio("Overconfidence", stress_score=20)
    assert lr > 1.0


def test_adjust_probability(engine):
    # Test a scenario where the market is panicking (High stress, Loss Aversion)
    market_prob = 0.80  # Crowd thinks 80% chance of bad outcome
    bias = "Loss Aversion"
    stress_score = 90

    rational_prob = engine.adjust_probability(market_prob, bias, stress_score)
    # The rational probability should be lower than the market's panicking probability
    assert rational_prob < market_prob


def test_decide_invest(engine):
    # High rational prob and positive edge
    decision = engine.decide(edge=0.10, rational_prob=0.60)
    assert decision == "INVEST"


def test_decide_save(engine):
    # Low rational prob and negative edge
    decision = engine.decide(edge=-0.10, rational_prob=0.40)
    assert decision == "SAVE"


def test_engine_run(engine):
    stress_data = {"stress_score": 85, "components": {"market_probability": 0.7}}
    bias_data = {"bias": "Panic Selling"}

    result = engine.run(stress_data, bias_data)
    assert "market_probability" in result
    assert "rational_probability" in result
    assert "edge" in result
    assert result["decision"] in ["INVEST", "SAVE", "HOLD"]