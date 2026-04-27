from fastapi import APIRouter, HTTPException, status
import logging

from core.dependencies import CurrentUser, DB
from services.wallet_service import add_income, add_expense, lock_savings, get_wallet_summary
from services.intelligence_service import get_stress_only
from schemas.wallet import AddIncomeRequest, AddExpenseRequest, LockSavingsRequest, WalletResponse
from schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])


@router.get("", response_model=WalletResponse)
async def get_wallet(current_user: CurrentUser, db: DB):
    """
    Get unified wallet: balance, free cash, locked goals, spending heat map, BQ alerts.
    """
    uid = current_user["uid"]

    try:
        try:
            stress = await get_stress_only(db, uid)
            stress_index = stress.stress_index
        except Exception as e:
            logger.warning("Stress lookup failed for wallet uid=%s: %s", uid, e)
            stress_index = 50.0

        summary = await get_wallet_summary(db, uid, stress_index)
        return WalletResponse(success=True, data=summary)
    except Exception as e:
        logger.error("Wallet GET error uid=%s: %s", uid, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/income")
async def income(current_user: CurrentUser, db: DB, request: AddIncomeRequest):
    """
    Add an income transaction. Auto-categorizes and updates balance.
    Sources: parent_transfer, side_hustle, bursary, other.
    """
    uid = current_user["uid"]

    try:
        tx = await add_income(db, uid, request)
        return APIResponse(
            success=True,
            message="Income added successfully.",
            data=tx,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Add income error uid=%s: %s", uid, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/expense")
async def expense(current_user: CurrentUser, db: DB, request: AddExpenseRequest):
    """
    Add an expense transaction. Checks sufficient free cash before allowing.
    """
    uid = current_user["uid"]

    try:
        tx = await add_expense(db, uid, request)
        return APIResponse(
            success=True,
            message="Expense recorded.",
            data=tx,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Add expense error uid=%s: %s", uid, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/lock")
async def lock(current_user: CurrentUser, db: DB, request: LockSavingsRequest):
    """
    Lock a savings goal. Removes amount from free cash.
    Kelly model will never allocate locked funds.
    """
    uid = current_user["uid"]

    try:
        goal = await lock_savings(db, uid, request)
        return APIResponse(
            success=True,
            message=f"₦{request.amount:,.0f} locked for '{request.label}'.",
            data=goal,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Lock savings error uid=%s: %s", uid, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
