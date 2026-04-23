from fastapi import APIRouter, HTTPException, status
from core.dependencies import CurrentUser, DB
from services.portfolio_service import log_decision, update_outcome, get_portfolio_summary
from schemas.portfolio import LogDecisionRequest, UpdateOutcomeRequest, PortfolioResponse
from schemas.common import APIResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(current_user: CurrentUser, db: DB):
    """
    Get full portfolio: performance metrics, recent decisions, behavioral pattern summary.
    """
    try:
        summary = await get_portfolio_summary(db, current_user["uid"])
        return PortfolioResponse(success=True, data=summary)
    except Exception as e:
        logger.error(f"Portfolio GET error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/decisions")
async def log_new_decision(
    current_user: CurrentUser,
    db: DB,
    request: LogDecisionRequest,
):
    """
    Log a ZELTA decision recommendation to the portfolio for outcome tracking.
    """
    try:
        record = await log_decision(db, current_user["uid"], request)
        return APIResponse(
            success=True,
            message="Decision logged. ZELTA will track the outcome.",
            data=record.model_dump(),
        )
    except Exception as e:
        logger.error(f"Log decision error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/decisions/outcome")
async def record_outcome(
    current_user: CurrentUser,
    db: DB,
    request: UpdateOutcomeRequest,
):
    """
    Update the actual outcome of a previously logged decision.
    Enables accuracy tracking and behavioral learning.
    """
    try:
        record = await update_outcome(db, current_user["uid"], request)
        return APIResponse(
            success=True,
            message="Decision outcome recorded.",
            data=record.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Update outcome error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))