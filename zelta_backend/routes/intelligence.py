from fastapi import APIRouter, HTTPException, status
from core.dependencies import CurrentUser, DB
from services.intelligence_service import get_intelligence, get_stress_only, get_bayse_markets
from schemas.intelligence import IntelligenceResponse
from schemas.common import APIResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Intelligence"])


@router.get("/brain", response_model=IntelligenceResponse)
async def brain(current_user: CurrentUser, db: DB):
    """
    PRIMARY — Run the full ZELTA BQ pipeline.
    Returns: stress index, bias snapshot, Kelly allocation, insights, suggestions.
    """
    try:
        result = await get_intelligence(db, current_user["uid"])
        return IntelligenceResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Brain endpoint error for {current_user['uid']}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stress")
async def stress_index(current_user: CurrentUser, db: DB):
    """
    Return the current Student Stress Index (Bayse primary + NLP secondary).
    """
    try:
        result = await get_stress_only(db, current_user["uid"])
        return APIResponse(success=True, message="Stress index retrieved.", data=result)
    except Exception as e:
        logger.error(f"Stress endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/intelligence")
async def intelligence_full(current_user: CurrentUser, db: DB):
    """
    Full BQ intelligence report: stress, bias, confidence score, and verdict.
    Alias for /brain with explicit field selection for frontend convenience.
    """
    try:
        result = await get_intelligence(db, current_user["uid"])
        return APIResponse(
            success=True,
            message="Intelligence report generated.",
            data={
                "stress": result.stress.model_dump(),
                "bias": result.bias.model_dump(),
                "allocation": result.allocation.model_dump(),
                "decision_score": result.decision_score,
                "bayse_vs_model_gap": result.bayse_vs_model_gap,
                "insights": [i.model_dump() for i in result.insights],
                "suggestions": result.suggestions,
            },
        )
    except Exception as e:
        logger.error(f"Intelligence endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/bayse/markets")
async def bayse_markets(current_user: CurrentUser, db: DB):
    """
    Live Bayse market data relevant to student finances.
    Returns crowd probability prices on Nigerian financial events.
    """
    try:
        result = await get_bayse_markets(db)
        return APIResponse(success=True, message="Bayse markets fetched.", data=result)
    except Exception as e:
        logger.error(f"Bayse markets endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/bayse/stress")
async def bayse_stress(current_user: CurrentUser, db: DB):
    """
    Crowd-derived stress signal from Bayse pricing only (no NLP component).
    """
    try:
        from optimizer import fetch_bayse_signal
        signal = await fetch_bayse_signal()
        return APIResponse(
            success=True,
            message="Bayse stress signal fetched.",
            data={
                "crowd_stress": signal["raw_crowd_stress"],
                "naira_weakness": signal["naira_weakness_probability"],
                "available": signal.get("available", False),
            },
        )
    except Exception as e:
        logger.error(f"Bayse stress endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/bayse/sentiment")
async def bayse_sentiment(current_user: CurrentUser, db: DB):
    """
    Behavioral panic score derived from Bayse order book data.
    """
    try:
        from optimizer import fetch_bayse_signal
        signal = await fetch_bayse_signal()
        panic_score = (signal["naira_weakness_probability"] * 0.4 +
                       signal["cbn_rate_fear_index"] * 0.3 +
                       signal["inflation_anxiety_score"] * 0.3)
        return APIResponse(
            success=True,
            message="Bayse sentiment retrieved.",
            data={
                "panic_score": round(panic_score, 2),
                "interpretation": (
                    "EXTREME PANIC" if panic_score >= 75 else
                    "HIGH FEAR" if panic_score >= 55 else
                    "MODERATE" if panic_score >= 35 else "CALM"
                ),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))