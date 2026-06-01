from pydantic import BaseModel, Field
from typing import Optional

class IncomeCreate(BaseModel):
    amount: float
    source: Optional[str]
    date: str

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str]
    date: str

class BudgetCreate(BaseModel):
    category: str
    limit: float
    month: str

class DebtCreate(BaseModel):
    amount: float
    creditor: Optional[str]
    date: str
