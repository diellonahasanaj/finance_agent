from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime

class IncomeModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    amount: float
    source: Optional[str]
    date: str
    frequency: Optional[str] = Field(default="one-time", description="monthly, weekly, one-time")
    is_recurring: bool = False
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class ExpenseModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    amount: float
    category: str
    description: Optional[str]
    date: str
    subcategory: Optional[str] = None
    payment_method: Optional[str] = None
    is_essential: bool = False
    tags: List[str] = []
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class BudgetModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    category: str
    limit: float
    month: str
    spent: float = 0.0
    warning_threshold: float = 0.8  # 80% warning
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class DebtModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    amount: float
    creditor: Optional[str]
    date: str
    interest_rate: Optional[float] = 0.0
    minimum_payment: Optional[float] = 0.0
    due_date: Optional[str] = None
    debt_type: Optional[str] = "other"  # credit_card, loan, mortgage, other
    is_paid_off: bool = False
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class FinancialGoalModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: str
    priority: str = "medium"  # low, medium, high
    category: str = "savings"
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class RecommendationModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    title: str
    description: str
    category: str  # savings, debt, budget, investment
    priority: str = "medium"
    potential_savings: Optional[float] = None
    confidence_score: float = 0.0  # 0-1 confidence in recommendation
    explanation: str
    action_steps: List[str] = []
    is_implemented: bool = False
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True
