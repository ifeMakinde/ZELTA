# tests/test_stress_index.py

import pytest
from stress.index import ZeltaStressIndex


@pytest.fixture
def indexer():
    return ZeltaStressIndex()


def test_stress_classification_calm(indexer):
    assert indexer.classify(25) == "CALM"


def test_stress_classification_moderate(indexer):
    assert indexer.classify(45) == "MODERATE"


def test_stress_classification_high_stress(indexer):
    assert indexer.classify(70) == "HIGH STRESS"


def test_stress_classification_crisis(indexer):
    assert indexer.classify(85) == "CRISIS"


def test_compute_stress(indexer):
    # Severe market panic (Bayse YES price = 90) + Negative sentiment
    bayse_data = {"yes_price": 90}
    sentiment = -0.8

    result = indexer.compute(bayse_data, sentiment)

    assert "stress_score" in result
    assert result["level"] in ["HIGH STRESS", "CRISIS"]
    assert result["components"]["market_probability"] == 0.90