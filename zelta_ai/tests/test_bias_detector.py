# tests/test_bias_detector.py

import pytest
from bias.detector import ZeltaBiasDetector


@pytest.fixture
def detector():
    return ZeltaBiasDetector()


def test_loss_aversion_detection(detector):
    stress_data = {"stress_score": 75, "components": {"market_probability": 0.8}}
    wallet_data = {"cash_withdrawal": True, "impulse_buy": False, "spending_spike": False}

    result = detector.detect(stress_data, sentiment_score=-0.5, wallet_data=wallet_data)
    assert result["bias"] == "Loss Aversion"
    assert result["confidence"] == "High"


def test_present_bias_detection(detector):
    stress_data = {"stress_score": 50, "components": {"market_probability": 0.5}}
    wallet_data = {"cash_withdrawal": False, "impulse_buy": True, "spending_spike": True}

    result = detector.detect(stress_data, sentiment_score=0.1, wallet_data=wallet_data)
    assert result["bias"] == "Present Bias"


def test_overconfidence_detection(detector):
    stress_data = {"stress_score": 20, "components": {"market_probability": 0.5}}

    result = detector.detect(stress_data, sentiment_score=0.5)
    assert result["bias"] == "Overconfidence"


def test_rational_calm_detection(detector):
    stress_data = {"stress_score": 25, "components": {"market_probability": 0.5}}

    result = detector.detect(stress_data, sentiment_score=0.0)
    assert result["bias"] == "Rational"