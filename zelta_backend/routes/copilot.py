from fastapi import APIRouter, HTTPException, status
from core.dependencies import CurrentUser, DB
from services.copilot_service import answer_question
from services.intelligence_service import get_intelligence
from services.wallet_service import get_wallet_summary
from schemas.copilot import CopilotRequest, CopilotAPIResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/copilot", tags=["BQ Co-Pilot"])


@router.post("", response_model=CopilotAPIResponse)
async def ask_copilot(
    current_user: CurrentUser,
    db: DB,
    request: CopilotRequest,
):
    """
    BQ Co-Pilot: Gemini-powered plain-English financial advisor.

    Sends the user's question to Gemini with full BQ context:
    - Bayse stress signal
    - Active behavioral bias
    - Wallet state
    - Upcoming obligations

    Always returns a SAVE / INVEST / HOLD verdict in NGN.
    Max response: 120 words. No jargon.
    """
    try:
        uid = current_user["uid"]

        # Load current BQ brain state
        try:
            brain = await get_intelligence(db, uid)
            brain_context = {
                "stress": brain.stress.model_dump(),
                "bias": brain.bias.model_dump(),
                "allocation": brain.allocation.model_dump(),
                "decision_score": brain.decision_score,
                "bayse_vs_model_gap": brain.bayse_vs_model_gap,
            }
        except Exception as e:
            logger.warning(f"Brain context load failed for copilot: {e}")
            brain_context = {}

        # Load wallet state
        try:
            wallet = await get_wallet_summary(db, uid)
            wallet_context = {
                "total_balance": wallet.total_balance,
                "free_cash": wallet.free_cash,
                "locked_amount": wallet.locked_amount,
                "weekly_burn_rate": wallet.weekly_burn_rate,
            }
        except Exception as e:
            logger.warning(f"Wallet context load failed for copilot: {e}")
            wallet_context = {}

        response = await answer_question(
            db=db,
            uid=uid,
            request=request,
            brain_context=brain_context,
            wallet_context=wallet_context,
        )

        return CopilotAPIResponse(success=True, data=response)

    except Exception as e:
        logger.error(f"Copilot error for {current_user['uid']}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))