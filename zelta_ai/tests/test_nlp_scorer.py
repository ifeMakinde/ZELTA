# tests/test_nlp_scorer.py

import pytest
from unittest.mock import patch, MagicMock
from nlp.scorer import ZeltaSentimentScorer


@pytest.fixture
def scorer():
    # Patch the HuggingFace pipeline so we don't load the massive model in unit tests
    with patch('nlp.scorer.pipeline') as mock_pipeline:
        mock_instance = MagicMock()
        # Mocking a negative sentiment return
        mock_instance.return_value = [{"label": "LABEL_0", "score": 0.9}]
        mock_pipeline.return_value = mock_instance
        yield ZeltaSentimentScorer()


def test_campus_amplifier_weight(scorer):
    # This headline contains "ASUU", a campus amplifier
    item = {"title": "ASUU declares 2-week warning strike at OAU"}
    result = scorer.score_headline(item)

    assert result["is_campus_relevant"] is True
    assert result["weight"] == 1.5


def test_standard_news_weight(scorer):
    # Standard macro news
    item = {"title": "CBN adjusts naira exchange rate"}
    result = scorer.score_headline(item)

    assert result["is_campus_relevant"] is False
    assert result["weight"] == 1.0


def test_aggregate_score_weighted(scorer):
    scored_data = [
        {"sentiment": -1.0, "weight": 1.5},  # Campus negative news
        {"sentiment": 1.0, "weight": 1.0}  # Standard positive news
    ]

    aggregate = scorer.aggregate_score(scored_data)
    # (-1.5 + 1.0) / 2.5 = -0.5 / 2.5 = -0.2
    assert round(aggregate, 2) == -0.20