from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


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
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    amount: float = Field(..., gt=0, description="Amount in NGN")
    source: TransactionCategory
    description: Optional[str] = None
    date: Optional[datetime] = None


class AddExpenseRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    amount: float = Field(..., gt=0, description="Amount in NGN")
    category: TransactionCategory
    description: Optional[str] = None
    date: Optional[datetime] = None


class LockSavingsRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    amount: float = Field(..., gt=0, description="Amount in NGN to lock")
    label: str = Field(..., min_length=1, max_length=100)
    unlock_date: datetime
    description: Optional[str] = None


class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    type: TransactionType
    amount: float
    category: TransactionCategory
    description: Optional[str] = None
    date: datetime
    balance_after: float


class SavingsGoal(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    label: str
    amount: float
    unlock_date: datetime
    description: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class SpendingHeatItem(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    category: TransactionCategory
    amount: float
    percentage: float
    status: str  # "green", "amber", "red"


class WalletSummary(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    total_balance: float = 0.0
    free_cash: float = 0.0
    locked_amount: float = 0.0
    total_income: float = 0.0
    total_expenses: float = 0.0
    weekly_burn_rate: float = 0.0
    savings_goals: List[SavingsGoal] = Field(default_factory=list)
    recent_transactions: List[Transaction] = Field(default_factory=list)
    spending_heat: List[SpendingHeatItem] = Field(default_factory=list)
    bq_alerts: List[str] = Field(default_factory=list)

    @computed_field
    @property
    def locked_total(self) -> float:
        return self.locked_amount


class WalletResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool
    data: WalletSummary
