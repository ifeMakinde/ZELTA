from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    LOCK = "lock"
    UNLOCK = "unlock"


class TransactionCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    DATA = "data"
    EDUCATION = "education"
    SIDE_HUSTLE = "side_hustle"
    PARENT_TRANSFER = "parent_transfer"
    BURSARY = "bursary"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    OTHER = "other"


class AddIncomeRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in NGN")
    source: TransactionCategory
    description: Optional[str] = None
    date: Optional[datetime] = None


class AddExpenseRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in NGN")
    category: TransactionCategory
    description: Optional[str] = None
    date: Optional[datetime] = None


class LockSavingsRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in NGN to lock")
    label: str = Field(..., min_length=1, max_length=100)
    unlock_date: datetime
    description: Optional[str] = None


class Transaction(BaseModel):
    id: str
    type: TransactionType
    amount: float
    category: TransactionCategory
    description: Optional[str] = None
    date: datetime
    balance_after: float


class SavingsGoal(BaseModel):
    id: str
    label: str
    amount: float
    unlock_date: datetime
    description: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class SpendingHeatItem(BaseModel):
    category: TransactionCategory
    amount: float
    percentage: float
    status: str  # "green", "amber", "red"


class WalletSummary(BaseModel):
    total_balance: float
    free_cash: float
    locked_amount: float
    total_income: float
    total_expenses: float
    weekly_burn_rate: float
    savings_goals: List[SavingsGoal]
    recent_transactions: List[Transaction]
    spending_heat: List[SpendingHeatItem]
    bq_alerts: List[str]


class WalletResponse(BaseModel):
    success: bool
    data: WalletSummary