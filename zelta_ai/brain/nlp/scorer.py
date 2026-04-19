from typing import List, Dict, Any
from transformers import pipeline

# ── Singleton — loads model ONCE at import time ───────────────────────────────
_pipeline = None

def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        print("Loading RoBERTa sentiment model...")
        _pipeline = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
        )
        print("Model loaded.")
    return _pipeline


class ZeltaSentimentScorer:
    """
    NLP Sentiment Engine for QUELO.
    Scores Nigerian financial headlines for fear level.
    Feeds into stress/index.py as SECONDARY signal (Bayse is PRIMARY).
    """

    def __init__(self):
        self.pipe = _get_pipeline()

        # Correct label map for twitter-roberta-base-sentiment-latest
        self.label_map = {
            "negative": -1.0,
            "neutral":   0.0,
            "positive":  1.0,
        }

        # Campus amplifiers — 1.5x weight for OAU student context
        self.campus_amplifiers = [
            "asuu", "strike", "tuition", "hostel",
            "oau", "fee", "student", "university"
        ]

    def score_headline(self, item: Dict[str, Any]) -> Dict[str, Any]:
        title = item.get("title", "")
        title_lower = title.lower()

        is_campus_relevant = any(
            amp in title_lower for amp in self.campus_amplifiers
        )
        weight = 1.5 if is_campus_relevant else 1.0

        try:
            result = self.pipe(title[:512])[0]  # Truncate to model max
            label = result["label"].lower()     # Model returns lowercase
            confidence = result["score"]
            sentiment_value = self.label_map.get(label, 0.0)

            return {
                **item,
                "sentiment": sentiment_value,
                "confidence": round(confidence, 4),
                "sentiment_label": label,
                "is_campus_relevant": is_campus_relevant,
                "weight": weight,
            }

        except Exception as e:
            print(f"Scoring error on: {title[:50]} — {e}")
            return {
                **item,
                "sentiment": 0.0,
                "confidence": 0.0,
                "sentiment_label": "neutral",
                "is_campus_relevant": is_campus_relevant,
                "weight": weight,
            }

    def score_batch(self, payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.score_headline(item) for item in payload]

    def aggregate_score(self, scored_data: List[Dict[str, Any]]) -> float:
        """
        Weighted average sentiment: -1.0 (very negative) to +1.0 (very positive).
        More negative = more fear in the market.
        """
        if not scored_data:
            return 0.0
        total_weight = sum(item.get("weight", 1.0) for item in scored_data)
        if total_weight == 0:
            return 0.0
        weighted_sum = sum(
            item["sentiment"] * item.get("weight", 1.0)
            for item in scored_data
        )
        return round(float(weighted_sum / total_weight), 3)

    def run(self, news_payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Entry point called by stress/index.py"""

        scored = self.score_batch(news_payload)
        aggregate = self.aggregate_score(scored)
        print(f"[QUELO NLP] Aggregate sentiment: {aggregate:.3f}")
        return {
            "scored_headlines": scored,
            "aggregate_sentiment": aggregate,
        }

