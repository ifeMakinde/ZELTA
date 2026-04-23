import time
import uuid
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from security import verify_internal_request
from brain.pipeline import ZeltaPipeline
from brain.bayse.stress_signal import monitor

logger = logging.getLogger("zelta.api")

router = APIRouter(prefix="/brain", tags=["AI Brain"])
public_router = APIRouter(tags=["Public API"])

pipeline = ZeltaPipeline()


class WalletData(BaseModel):
    free_cash: float = Field(default=26500.0, ge=0)
    locked_total: float = Field(default=18500.0, ge=0)
    total_balance: float = Field(default=45000.0, ge=0)


class Transaction(BaseModel):
    amount: float
    category: str
    type: str
    description: Optional[str] = None


class BrainRequest(BaseModel):
    wallet_data: WalletData = Field(default_factory=WalletData)
    transactions: List[Transaction] = Field(default_factory=list)
    user_context: Dict[str, Any] = Field(default_factory=dict)


def _safe_event_title(event: Dict[str, Any]) -> str:
    return event.get("title") or event.get("name") or event.get("description") or "Unknown"


def _safe_market_id(market: Dict[str, Any]) -> Optional[str]:
    return market.get("id") or market.get("marketId")


@router.get("/health")
def health():
    signal = monitor.get_signal()

    return {
        "status": "ok",
        "service": "ZELTA AI Brain",
        "bayse_connected": True,
        "current_stress": signal.get("score", 50),
        "stress_level": signal.get("status", "UNKNOWN"),
        "mode": "stateless",
        "version": "1.0.0",
    }


@router.post("/intelligence")
async def get_intelligence(
    request: BrainRequest,
    _: None = Depends(verify_internal_request),
):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        wallet_dict = request.wallet_data.model_dump()
        transactions = [t.model_dump() for t in request.transactions]
        user_context = request.user_context or {}

        enriched_wallet = {
            **wallet_dict,
            "transaction_count": len(transactions),
            "has_expenses": any(t["type"] == "expense" for t in transactions),
            "has_income": any(t["type"] == "income" for t in transactions),
            "user_flags": user_context.get("flags", []),
        }

        result = await pipeline.run_async(
            wallet_data=enriched_wallet,
            transactions=transactions,
            user_context=user_context,
        )

        if result.get("meta", {}).get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result["meta"].get("error", "Brain processing failed"),
            )

        latency = round(time.time() - start_time, 3)

        return {
            "success": True,
            "request_id": request_id,
            "latency_sec": latency,
            "data": result,
            "meta": {
                "status": "success",
                "brain_latency_sec": latency,
                "request_id": request_id,
            },
        }

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("get_intelligence failed: %s", exc)
        latency = round(time.time() - start_time, 3)

        return {
            "success": False,
            "request_id": request_id,
            "latency_sec": latency,
            "error": str(exc),
            "meta": {"status": "error"},
            "data": {
                "allocation": {
                    "verdict": "HOLD",
                    "invest_ngn": 0,
                    "save_ngn": 0,
                    "hold_ngn": 0,
                    "plain_english": "System error. Holding funds for safety.",
                },
                "confidence": {
                    "confidence_score_100": 0,
                    "is_actionable": False,
                },
                "stress": {
                    "score": 50,
                    "level": "UNKNOWN",
                },
                "bias": {
                    "bias": "Unknown",
                    "confidence": "Low",
                },
            },
        }


@public_router.get("/api/stress")
async def get_stress():
    signal = monitor.get_signal()

    return {
        "score": signal.get("score", 50),
        "status": signal.get("status", "UNKNOWN"),
        "crowd_yes_price": signal.get("crowd_yes_price"),
        "crowd_no_price": signal.get("crowd_no_price"),
        "spread": signal.get("spread"),
        "imbalance": signal.get("imbalance"),
        "market_title": signal.get("market_title"),
        "market_id": signal.get("market_id"),
        "outcome": signal.get("outcome"),
        "mid_price": signal.get("mid_price"),
        "best_bid": signal.get("best_bid"),
        "best_ask": signal.get("best_ask"),
        "last_price": signal.get("last_price"),
        "volume24h": signal.get("volume24h"),
        "trade_count_24h": signal.get("trade_count_24h"),
        "updated_at": signal.get("updated_at"),
        "source": "Bayse Prediction Markets",
    }


@public_router.get("/api/markets")
async def get_markets():
    try:
        events = await monitor.client.get_events()

        markets = []
        for event in events[:25]:
            event_title = _safe_event_title(event)
            category = event.get("category")
            liquidity = event.get("liquidity")
            created_at = event.get("createdAt")

            for market in event.get("markets", []):
                market_id = _safe_market_id(market)
                if not market_id:
                    continue

                markets.append(
                    {
                        "event_title": event_title,
                        "event_category": category,
                        "event_created_at": created_at,
                        "event_liquidity": liquidity,
                        "market_id": market_id,
                        "market_title": market.get("title") or market.get("name") or "Unknown",
                        "fee_percentage": market.get("feePercentage"),
                    }
                )

        return {
            "count": len(markets),
            "markets": markets,
        }

    except Exception as exc:
        logger.exception("get_markets failed: %s", exc)
        return {
            "count": 0,
            "markets": [],
            "error": str(exc),
        }