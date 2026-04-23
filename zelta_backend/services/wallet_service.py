"""
ZELTA Wallet Service

Full wallet logic: income tracking, expense tracking, savings goals,
dynamic balance computation, BQ alerts, spending heat map.
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from google.cloud import firestore
from schemas.wallet import (
    AddIncomeRequest, AddExpenseRequest, LockSavingsRequest,
    Transaction, SavingsGoal, SpendingHeatItem, WalletSummary,
    TransactionType, TransactionCategory,
)
from config.settings import settings

logger = logging.getLogger(__name__)

CATEGORY_NORMAL_SPEND: dict = {
    TransactionCategory.FOOD: 15000.0,
    TransactionCategory.TRANSPORT: 5000.0,
    TransactionCategory.DATA: 4500.0,
    TransactionCategory.EDUCATION: 5000.0,
    TransactionCategory.ENTERTAINMENT: 3000.0,
    TransactionCategory.UTILITIES: 2000.0,
    TransactionCategory.OTHER: 3000.0,
}


def _get_wallet_ref(db: firestore.Client, uid: str) -> firestore.DocumentReference:
    return db.collection("wallets").document(uid)


def _get_transactions_ref(db: firestore.Client, uid: str) -> firestore.CollectionReference:
    return db.collection("wallets").document(uid).collection("transactions")


def _get_goals_ref(db: firestore.Client, uid: str) -> firestore.CollectionReference:
    return db.collection("wallets").document(uid).collection("savings_goals")


def _ensure_wallet(db: firestore.Client, uid: str) -> dict:
    """Get or create wallet document for user."""
    ref = _get_wallet_ref(db, uid)
    doc = ref.get()
    if not doc.exists:
        default = {
            "uid": uid,
            "total_income": 0.0,
            "total_expenses": 0.0,
            "locked_amount": 0.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        ref.set(default)
        return default
    return doc.to_dict()


async def add_income(db: firestore.Client, uid: str, request: AddIncomeRequest) -> dict:
    """Add an income transaction to the wallet."""
    wallet = _ensure_wallet(db, uid)

    transaction_id = str(uuid.uuid4())
    now = request.date or datetime.now(timezone.utc)

    new_income = wallet["total_income"] + request.amount
    new_balance = new_income - wallet["total_expenses"] - wallet["locked_amount"]

    transaction = {
        "id": transaction_id,
        "type": TransactionType.INCOME,
        "amount": request.amount,
        "category": request.source,
        "description": request.description or f"Income: {request.source}",
        "date": now,
        "balance_after": new_balance,
        "created_at": datetime.now(timezone.utc),
    }

    # Write transaction
    _get_transactions_ref(db, uid).document(transaction_id).set(transaction)

    # Update wallet summary
    _get_wallet_ref(db, uid).update({
        "total_income": new_income,
        "updated_at": datetime.now(timezone.utc),
    })

    return transaction


async def add_expense(db: firestore.Client, uid: str, request: AddExpenseRequest) -> dict:
    """Add an expense transaction to the wallet."""
    wallet = _ensure_wallet(db, uid)

    free_cash = wallet["total_income"] - wallet["total_expenses"] - wallet["locked_amount"]
    if request.amount > free_cash:
        raise ValueError(
            f"Insufficient free cash. Available: ₦{free_cash:,.0f}, Requested: ₦{request.amount:,.0f}"
        )

    transaction_id = str(uuid.uuid4())
    now = request.date or datetime.now(timezone.utc)

    new_expenses = wallet["total_expenses"] + request.amount
    new_balance = wallet["total_income"] - new_expenses - wallet["locked_amount"]

    transaction = {
        "id": transaction_id,
        "type": TransactionType.EXPENSE,
        "amount": request.amount,
        "category": request.category,
        "description": request.description or f"Expense: {request.category}",
        "date": now,
        "balance_after": new_balance,
        "created_at": datetime.now(timezone.utc),
    }

    _get_transactions_ref(db, uid).document(transaction_id).set(transaction)
    _get_wallet_ref(db, uid).update({
        "total_expenses": new_expenses,
        "updated_at": datetime.now(timezone.utc),
    })

    return transaction


async def lock_savings(db: firestore.Client, uid: str, request: LockSavingsRequest) -> dict:
    """Lock a savings goal — removes amount from free cash."""
    wallet = _ensure_wallet(db, uid)

    free_cash = wallet["total_income"] - wallet["total_expenses"] - wallet["locked_amount"]
    if request.amount > free_cash:
        raise ValueError(
            f"Insufficient free cash to lock. Available: ₦{free_cash:,.0f}, Requested: ₦{request.amount:,.0f}"
        )

    goal_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    goal = {
        "id": goal_id,
        "label": request.label,
        "amount": request.amount,
        "unlock_date": request.unlock_date,
        "description": request.description,
        "created_at": now,
        "is_active": True,
    }

    _get_goals_ref(db, uid).document(goal_id).set(goal)

    new_locked = wallet["locked_amount"] + request.amount
    _get_wallet_ref(db, uid).update({
        "locked_amount": new_locked,
        "updated_at": now,
    })

    # Log lock transaction
    lock_tx_id = str(uuid.uuid4())
    balance_after = wallet["total_income"] - wallet["total_expenses"] - new_locked
    _get_transactions_ref(db, uid).document(lock_tx_id).set({
        "id": lock_tx_id,
        "type": TransactionType.LOCK,
        "amount": request.amount,
        "category": TransactionCategory.SAVINGS,
        "description": f"Locked: {request.label}",
        "date": now,
        "balance_after": balance_after,
        "created_at": now,
    })

    return goal


async def get_wallet_summary(db: firestore.Client, uid: str, stress_index: float = 50.0) -> WalletSummary:
    """
    Build the full wallet summary with BQ alerts, spending heat map, and balance breakdown.
    """
    wallet = _ensure_wallet(db, uid)

    total_income = wallet.get("total_income", 0.0)
    total_expenses = wallet.get("total_expenses", 0.0)
    locked_amount = wallet.get("locked_amount", 0.0)
    free_cash = max(0.0, total_income - total_expenses - locked_amount)
    total_balance = total_income - total_expenses

    # Fetch active savings goals
    goals_docs = _get_goals_ref(db, uid).where("is_active", "==", True).stream()
    savings_goals = [SavingsGoal(**g.to_dict()) for g in goals_docs]

    # Fetch recent transactions (last 30)
    tx_docs = (
        _get_transactions_ref(db, uid)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(30)
        .stream()
    )
    transactions = [Transaction(**t.to_dict()) for t in tx_docs]

    # Weekly burn rate (last 7 days expenses)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    weekly_expenses = sum(
        t.amount
        for t in transactions
        if t.type == TransactionType.EXPENSE and t.date >= seven_days_ago
    )

    # Spending heat map per category
    category_spend: dict = {}
    for t in transactions:
        if t.type == TransactionType.EXPENSE:
            cat = t.category
            category_spend[cat] = category_spend.get(cat, 0.0) + t.amount

    spending_heat: List[SpendingHeatItem] = []
    for cat, amount in category_spend.items():
        normal = CATEGORY_NORMAL_SPEND.get(cat, 5000.0)
        pct = (amount / total_expenses * 100) if total_expenses > 0 else 0
        if amount <= normal * 0.8:
            status = "green"
        elif amount <= normal * 1.2:
            status = "amber"
        else:
            status = "red"

        spending_heat.append(SpendingHeatItem(
            category=cat, amount=amount, percentage=round(pct, 1), status=status
        ))

    # BQ Alerts
    bq_alerts = _generate_bq_alerts(
        free_cash=free_cash,
        weekly_expenses=weekly_expenses,
        stress_index=stress_index,
        spending_heat=spending_heat,
        savings_goals=savings_goals,
    )

    return WalletSummary(
        total_balance=round(total_balance, 2),
        free_cash=round(free_cash, 2),
        locked_amount=round(locked_amount, 2),
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        weekly_burn_rate=round(weekly_expenses, 2),
        savings_goals=savings_goals,
        recent_transactions=transactions[:10],
        spending_heat=sorted(spending_heat, key=lambda x: x.amount, reverse=True),
        bq_alerts=bq_alerts,
    )


def _generate_bq_alerts(
    free_cash: float,
    weekly_expenses: float,
    stress_index: float,
    spending_heat: List[SpendingHeatItem],
    savings_goals: List[SavingsGoal],
) -> List[str]:
    """Generate contextual BQ alerts based on wallet state and stress signal."""
    alerts = []

    if free_cash < settings.buffer_reserve_ngn:
        alerts.append(
            f"⚠️ Free cash below ₦{settings.buffer_reserve_ngn:,.0f} safety reserve. ZELTA will not approve investments."
        )

    red_categories = [h for h in spending_heat if h.status == "red"]
    if red_categories and stress_index >= 60:
        cats = ", ".join(h.category for h in red_categories[:2])
        alerts.append(
            f"🔴 Stress-spending detected in {cats}. This matches {_get_bias_name(stress_index)} pattern driven by Bayse fear spike."
        )

    now = datetime.now(timezone.utc)
    for goal in savings_goals:
        weeks_left = (goal.unlock_date - now).days / 7
        if 0 < weeks_left <= 6:
            alerts.append(
                f"📌 {goal.label} due in {weeks_left:.0f} weeks. ₦{goal.amount:,.0f} locked and protected."
            )

    if weekly_expenses > 20000:
        alerts.append(
            f"📊 Weekly burn rate at ₦{weekly_expenses:,.0f}. Review non-essential spending to protect your savings floor."
        )

    return alerts


def _get_bias_name(stress_index: float) -> str:
    if stress_index >= 60:
        return "loss aversion"
    elif stress_index >= 40:
        return "present bias"
    return "overconfidence"


async def get_transaction_patterns(db: firestore.Client, uid: str) -> dict:
    """Derive spending pattern signals for the bias detector."""
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)

    tx_docs = (
        _get_transactions_ref(db, uid)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(50)
        .stream()
    )
    transactions = [t.to_dict() for t in tx_docs]

    recent_week = [t for t in transactions if t.get("date") and t["date"] >= seven_days_ago]
    prior_week = [t for t in transactions if t.get("date") and fourteen_days_ago <= t["date"] < seven_days_ago]

    recent_cash_withdrawals = sum(
        1 for t in recent_week
        if t.get("type") == TransactionType.LOCK and t.get("category") == TransactionCategory.SAVINGS
    )

    recent_income = sum(t["amount"] for t in recent_week if t.get("type") == TransactionType.INCOME)
    recent_expenses = sum(t["amount"] for t in recent_week if t.get("type") == TransactionType.EXPENSE)
    impulse_spend_ratio = (recent_expenses / recent_income) if recent_income > 0 else 0.0

    prior_expenses = sum(t["amount"] for t in prior_week if t.get("type") == TransactionType.EXPENSE)
    spend_above_normal_pct = max(0.0, (recent_expenses - prior_expenses) / max(prior_expenses, 1.0))

    income_spike = recent_income > (prior_expenses * 1.5)

    return {
        "recent_cash_withdrawals": recent_cash_withdrawals,
        "impulse_spend_ratio": round(impulse_spend_ratio, 3),
        "income_spike": income_spike,
        "spend_above_normal_pct": round(spend_above_normal_pct, 3),
    }