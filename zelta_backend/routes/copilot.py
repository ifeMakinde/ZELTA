from fastapi import APIRouter, HTTPException, status
import logging

from core.dependencies import CurrentUser, DB
from services.copilot_service import answer_question
from services.intelligence_service import get_intelligence
from services.wallet_service import get_wallet_summary
from schemas.copilot import CopilotRequest, CopilotAPIResponse

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
    uid = current_user["uid"]

    try:
        try:
            brain = await get_intelligence(db, uid)
            brain_context = brain.model_dump()
        except Exception as e:
            logger.warning("Brain context load failed for copilot uid=%s: %s", uid, e)
            brain_context = {}

        try:
            wallet = await get_wallet_summary(db, uid)
            wallet_context = wallet.model_dump()
        except Exception as e:
            logger.warning("Wallet context load failed for copilot uid=%s: %s", uid, e)
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
        logger.error("Copilot error for %s: %s", uid, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
