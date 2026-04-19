from typing import Any, Dict, List, Optional
import uuid
import time

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from security import verify_internal_request
from brain.pipeline import ZeltaPipeline
from brain.bayse.stress_signal import monitor

router = APIRouter(prefix="/brain", tags=["AI Brain"])

# Shared pipeline — loaded once at startup
pipeline = ZeltaPipeline()


# ── MODELS ────────────────────────────────────────────────────────────────────

class WalletData(BaseModel):
    """
    Wallet data sent by the ZELTA backend.
    Defaults match Tunde's demo scenario.
    """
    free_cash:     float = Field(default=26500.0, ge=0)
    locked_total:  float = Field(default=18500.0, ge=0)
    total_balance: float = Field(default=45000.0, ge=0)

class Transaction(BaseModel):
    amount:      float
    category:    str
    type:        str            # "income" | "expense"
    description: Optional[str] = None

class BrainRequest(BaseModel):
    wallet_data:  WalletData = Field(default_factory=WalletData)
    transactions: List[Transaction] = Field(default_factory=list)
    user_context: Dict[str, Any]    = Field(default_factory=dict)


# ── HEALTH ────────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {
        "status":          "ok",
        "service":         "ZELTA AI Brain",
        "bayse_connected": monitor.ws.connected,
        "current_stress":  monitor.current_signal.get("score", 0),
        "stress_level":    monitor.current_signal.get("status", "UNKNOWN"),
        "mode":            "stateless",
        "version":         "1.0.0",
    }


# ── PRIMARY BRAIN ENDPOINT ────────────────────────────────────────────────────

@router.post("/intelligence")
async def get_intelligence(
    request: BrainRequest,
    raw_request: Request,
    _: None = Depends(verify_internal_request),
):
    """
    Core AI Brain endpoint.

    Called by: ZELTA backend VertexAIOptimizer
    Never called by: frontend directly

    Flow:
    Backend receives frontend request
    → Backend calls this endpoint
    → Brain runs full pipeline
    → Backend formats response for frontend
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        wallet_dict  = request.wallet_data.model_dump()
        transactions = [t.model_dump() for t in request.transactions]
        user_context = request.user_context or {}

        # Enrich wallet with transaction context
        enriched_wallet = {
            **wallet_dict,
            "transaction_count": len(transactions),
            "has_expenses":      any(t["type"] == "expense" for t in transactions),
            "has_income":        any(t["type"] == "income" for t in transactions),
            "user_flags":        user_context.get("flags", []),
        }

        # Run the full ZELTA AI pipeline
        result = await pipeline.run_async(enriched_wallet)

        if result.get("meta", {}).get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result["meta"].get("error", "Brain processing failed"),
            )

        latency = round(time.time() - start_time, 3)

        # Return both nested (preferred) and flat (fallback) format
        # This makes VertexAIOptimizer and direct callers both work
        return {
            "success":     True,
            "request_id":  request_id,
            "latency_sec": latency,
            "data":        result,    # nested — preferred
            **result,                 # flat — fallback access
            "meta": {
                "status":           "success",
                "brain_latency_sec": latency,
                "request_id":       request_id,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        latency = round(time.time() - start_time, 3)
        print(f"[ZELTA Brain] Pipeline error: {e}")

        # Structured error with safe fallback data
        # Backend can still serve a degraded response
        return {
            "success":     False,
            "request_id":  request_id,
            "latency_sec": latency,
            "error":       str(e),
            "meta": {
                "status": "error",
            },
            # Safe fallback — brain failed but backend gets usable data
            "data": {
                "allocation": {
                    "verdict":       "HOLD",
                    "invest_ngn":    0,
                    "save_ngn":      0,
                    "hold_ngn":      0,
                    "plain_english": "System error. Holding funds for safety.",
                },
                "confidence": {
                    "confidence_score_100": 0,
                    "is_actionable":        False,
                },
                "stress": {
                    "score": 50,
                    "level": "UNKNOWN",
                },
                "bias": {
                    "bias":       "Unknown",
                    "confidence": "Low",
                },
            },
        }