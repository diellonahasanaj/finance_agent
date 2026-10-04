from pydantic import BaseModel, Field
from typing import Optional

class IncomeCreate(BaseModel):
    amount: float = Field(gt=0)
    source: Optional[str] = "Salary"
    date: str

class IncomeUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    source: Optional[str] = None
    date: Optional[str] = None

class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: str
    description: Optional[str] = None
    date: str

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

class BudgetCreate(BaseModel):
    category: str
    limit: float = Field(gt=0)
    month: str

class DebtCreate(BaseModel):
    amount: float = Field(gt=0)
    creditor: Optional[str] = None
    date: Optional[str] = None
    interest_rate: Optional[float] = Field(default=None, ge=0)
    monthly_payment: Optional[float] = Field(default=None, ge=0)
    due_date: Optional[str] = None
    description: Optional[str] = None
    is_paid_off: Optional[bool] = False

class DebtUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    creditor: Optional[str] = None
    date: Optional[str] = None
    interest_rate: Optional[float] = Field(default=None, ge=0)
    monthly_payment: Optional[float] = Field(default=None, ge=0)
    due_date: Optional[str] = None
    description: Optional[str] = None
    is_paid_off: Optional[bool] = None
