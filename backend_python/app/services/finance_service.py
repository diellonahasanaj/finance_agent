"""
Finance service logic for income, expense, budget, and debt operations.
Handles file-based storage for financial data.
"""
import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional
from app.schemas.finance import IncomeCreate, ExpenseCreate, BudgetCreate, DebtCreate, IncomeUpdate, ExpenseUpdate
from app.services.expense_classifier import expense_classifier
from bson import ObjectId

# File-based storage for financial data
INCOMES_FILE = "incomes.json"
EXPENSES_FILE = "expenses.json"
BUDGETS_FILE = "budgets.json"
DEBTS_FILE = "debts.json"

def load_data(filename):
    """Load data from file."""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    """Save data to file."""
    with open(filename, 'w') as f:
        json.dump(data, f, default=str)

async def add_income(user, income: IncomeCreate):
    """
    Add a new income record for the user.
    """
    incomes = load_data(INCOMES_FILE)
    
    income_dict = income.dict()
    income_dict["_id"] = str(ObjectId())
    income_dict["user_id"] = str(user["_id"])
    income_dict["created_at"] = datetime.utcnow()
    
    # Use user email as key since we're using file storage
    user_key = user.get("email", str(user["_id"]))
    if user_key not in incomes:
        incomes[user_key] = []
    
    incomes[user_key].append(income_dict)
    save_data(INCOMES_FILE, incomes)
    
    return income_dict

async def add_expense(user, expense: ExpenseCreate):
    """
    Add a new expense record for the user.
    Auto-classifies category from description when not provided or set to Other.
    """
    expenses = load_data(EXPENSES_FILE)

    expense_dict = expense.dict()
    title = expense_dict.get("description") or expense_dict.get("category") or ""
    classified_category, confidence = expense_classifier.classify_expense(
        title, expense_dict.get("description") or ""
    )
    if not expense_dict.get("category") or expense_dict.get("category") in ("Other", "General"):
        expense_dict["category"] = classified_category
    expense_dict["classification_confidence"] = confidence
    expense_dict["auto_classified"] = expense_dict["category"] == classified_category

    expense_dict["_id"] = str(ObjectId())
    expense_dict["user_id"] = str(user["_id"])
    expense_dict["created_at"] = datetime.utcnow()
    
    user_key = user.get("email", str(user["_id"]))
    if user_key not in expenses:
        expenses[user_key] = []
    
    expenses[user_key].append(expense_dict)
    save_data(EXPENSES_FILE, expenses)
    
    return expense_dict

async def set_budget(user, budget: BudgetCreate):
    """
    Set or update a budget for a category and month.
    """
    budgets = load_data(BUDGETS_FILE)
    
    budget_dict = budget.dict()
    budget_dict["_id"] = str(ObjectId())
    budget_dict["user_id"] = str(user["_id"])
    budget_dict["created_at"] = datetime.utcnow()
    
    user_key = user.get("email", str(user["_id"]))
    if user_key not in budgets:
        budgets[user_key] = []
    
    # Check if budget for this category and month already exists
    existing_index = None
    for i, b in enumerate(budgets[user_key]):
        if b.get("category") == budget_dict["category"] and b.get("month") == budget_dict["month"]:
            existing_index = i
            break
    
    if existing_index is not None:
        budgets[user_key][existing_index] = budget_dict
    else:
        budgets[user_key].append(budget_dict)
    
    save_data(BUDGETS_FILE, budgets)
    
    return budget_dict

async def add_debt(user, debt: DebtCreate):
    """
    Add a new debt record for the user.
    """
    debts = load_data(DEBTS_FILE)
    
    debt_dict = debt.dict()
    debt_dict["_id"] = str(ObjectId())
    debt_dict["user_id"] = str(user["_id"])
    debt_dict["created_at"] = datetime.utcnow()
    
    user_key = user.get("email", str(user["_id"]))
    if user_key not in debts:
        debts[user_key] = []
    
    debts[user_key].append(debt_dict)
    save_data(DEBTS_FILE, debts)
    
    return debt_dict

async def get_user_incomes(user):
    """Get all incomes for a user."""
    incomes = load_data(INCOMES_FILE)
    user_key = user.get("email", str(user["_id"]))
    return incomes.get(user_key, [])

async def get_user_expenses(user):
    """Get all expenses for a user."""
    expenses = load_data(EXPENSES_FILE)
    user_key = user.get("email", str(user["_id"]))
    return expenses.get(user_key, [])

async def get_user_budgets(user):
    """Get all budgets for a user."""
    budgets = load_data(BUDGETS_FILE)
    user_key = user.get("email", str(user["_id"]))
    return budgets.get(user_key, [])

async def get_user_debts(user):
    """Get all debts for a user."""
    debts = load_data(DEBTS_FILE)
    user_key = user.get("email", str(user["_id"]))
    return debts.get(user_key, [])


def _user_key(user) -> str:
    return user.get("email", str(user["_id"]))


async def update_expense(user, expense_id: str, update: ExpenseUpdate):
    """Update an existing expense record."""
    expenses = load_data(EXPENSES_FILE)
    user_key = _user_key(user)
    user_expenses = expenses.get(user_key, [])

    for i, expense in enumerate(user_expenses):
        if expense.get("_id") == expense_id:
            updated = {**expense}
            for field, value in update.dict(exclude_unset=True).items():
                if value is not None:
                    updated[field] = value
            if update.description or update.category:
                title = updated.get("description") or updated.get("category") or ""
                classified_category, confidence = expense_classifier.classify_expense(
                    title, updated.get("description") or ""
                )
                if update.category in (None, "Other", "General"):
                    updated["category"] = classified_category
                updated["classification_confidence"] = confidence
            updated["updated_at"] = datetime.utcnow()
            user_expenses[i] = updated
            expenses[user_key] = user_expenses
            save_data(EXPENSES_FILE, expenses)
            return updated

    return None


async def delete_expense(user, expense_id: str) -> bool:
    """Delete an expense record."""
    expenses = load_data(EXPENSES_FILE)
    user_key = _user_key(user)
    user_expenses = expenses.get(user_key, [])
    filtered = [e for e in user_expenses if e.get("_id") != expense_id]
    if len(filtered) == len(user_expenses):
        return False
    expenses[user_key] = filtered
    save_data(EXPENSES_FILE, expenses)
    return True


async def update_income(user, income_id: str, update: IncomeUpdate):
    """Update an existing income record."""
    incomes = load_data(INCOMES_FILE)
    user_key = _user_key(user)
    user_incomes = incomes.get(user_key, [])

    for i, income in enumerate(user_incomes):
        if income.get("_id") == income_id:
            updated = {**income}
            for field, value in update.dict(exclude_unset=True).items():
                if value is not None:
                    updated[field] = value
            updated["updated_at"] = datetime.utcnow()
            user_incomes[i] = updated
            incomes[user_key] = user_incomes
            save_data(INCOMES_FILE, incomes)
            return updated

    return None


async def delete_income(user, income_id: str) -> bool:
    """Delete an income record."""
    incomes = load_data(INCOMES_FILE)
    user_key = _user_key(user)
    user_incomes = incomes.get(user_key, [])
    filtered = [i for i in user_incomes if i.get("_id") != income_id]
    if len(filtered) == len(user_incomes):
        return False
    incomes[user_key] = filtered
    save_data(INCOMES_FILE, incomes)
    return True


async def get_category_statistics(user, month: Optional[str] = None) -> dict:
    """Get expense and income category statistics."""
    expenses = _filter_by_month(await get_user_expenses(user), month)
    incomes = _filter_by_month(await get_user_incomes(user), month)

    expense_stats = _category_breakdown(expenses)
    income_stats: Dict[str, float] = defaultdict(float)
    for income in incomes:
        source = income.get("source", "Other")
        income_stats[source] += income.get("amount", 0)

    return {
        "expense_categories": [
            {"category": k, "amount": v, "type": "expense"}
            for k, v in sorted(expense_stats.items(), key=lambda x: x[1], reverse=True)
        ],
        "income_categories": [
            {"category": k, "amount": v, "type": "income"}
            for k, v in sorted(income_stats.items(), key=lambda x: x[1], reverse=True)
        ],
        "total_expenses": sum(expense_stats.values()),
        "total_income": sum(income_stats.values()),
    }


async def get_transactions(
    user,
    type_filter: Optional[str] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
    month: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """Get paginated, filterable list of all transactions."""
    incomes = await get_user_incomes(user)
    expenses = await get_user_expenses(user)

    transactions = []
    for income in incomes:
        transactions.append({**income, "type": "income", "label": income.get("source", "Income")})
    for expense in expenses:
        transactions.append({
            **expense,
            "type": "expense",
            "label": expense.get("description") or expense.get("category", "Expense"),
        })

    if type_filter in ("income", "expense"):
        transactions = [t for t in transactions if t["type"] == type_filter]

    if month:
        transactions = [t for t in transactions if str(t.get("date", "")).startswith(month)]

    if category:
        transactions = [
            t for t in transactions
            if t.get("category", "").lower() == category.lower()
            or t.get("source", "").lower() == category.lower()
        ]

    if search:
        query = search.lower()
        transactions = [
            t for t in transactions
            if query in str(t.get("label", "")).lower()
            or query in str(t.get("category", "")).lower()
            or query in str(t.get("source", "")).lower()
            or query in str(t.get("description", "")).lower()
            or query in str(t.get("amount", ""))
        ]

    transactions.sort(key=lambda x: x.get("date", ""), reverse=True)

    total = len(transactions)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": transactions[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


def _filter_by_month(records: List[dict], month: Optional[str]) -> List[dict]:
    if not month:
        return records
    return [r for r in records if str(r.get("date", "")).startswith(month)]


def _category_breakdown(expenses: List[dict]) -> Dict[str, float]:
    breakdown: Dict[str, float] = defaultdict(float)
    for expense in expenses:
        category = expense.get("category", "Other")
        breakdown[category] += expense.get("amount", 0)
    return dict(breakdown)


def _monthly_trends(
    incomes: List[dict], expenses: List[dict], months: int = 6
) -> List[dict]:
    month_keys: Dict[str, dict] = {}
    for record in incomes:
        date = str(record.get("date", ""))
        if len(date) >= 7:
            month = date[:7]
            if month not in month_keys:
                month_keys[month] = {"month": month, "income": 0.0, "expenses": 0.0}
            month_keys[month]["income"] += record.get("amount", 0)
    for record in expenses:
        date = str(record.get("date", ""))
        if len(date) >= 7:
            month = date[:7]
            if month not in month_keys:
                month_keys[month] = {"month": month, "income": 0.0, "expenses": 0.0}
            month_keys[month]["expenses"] += record.get("amount", 0)

    sorted_months = sorted(month_keys.keys())[-months:]
    trends = []
    for month in sorted_months:
        data = month_keys[month]
        trends.append(
            {
                "month": month,
                "income": data["income"],
                "expenses": data["expenses"],
                "savings": data["income"] - data["expenses"],
            }
        )
    return trends


async def build_dashboard_data(user, month: Optional[str] = None) -> dict:
    """Build unified dashboard payload from file-based financial records."""
    incomes = _filter_by_month(await get_user_incomes(user), month)
    expenses = _filter_by_month(await get_user_expenses(user), month)
    budgets = await get_user_budgets(user)
    debts = await get_user_debts(user)

    if month:
        budgets = [b for b in budgets if b.get("month") == month]

    total_income = sum(i.get("amount", 0) for i in incomes)
    total_expenses = sum(e.get("amount", 0) for e in expenses)
    balance = total_income - total_expenses
    total_debts = sum(d.get("amount", 0) for d in debts if not d.get("is_paid_off", False))
    category_breakdown = _category_breakdown(expenses)

    budget_status = []
    for budget in budgets:
        category = budget.get("category")
        category_expenses = category_breakdown.get(category, 0)
        budget_limit = budget.get("limit", 0)
        percentage_used = (category_expenses / budget_limit * 100) if budget_limit > 0 else 0
        budget_status.append(
            {
                "category": category,
                "limit": budget_limit,
                "spent": category_expenses,
                "remaining": budget_limit - category_expenses,
                "percentage_used": percentage_used,
                "percentage": percentage_used,
                "month": budget.get("month"),
            }
        )

    alerts = []
    if balance < 0:
        alerts.append(
            {
                "type": "error",
                "message": "Monthly balance is negative",
                "reason": f"Total expenses (${total_expenses:.2f}) exceed total income (${total_income:.2f})",
                "impact": f"You are spending ${abs(balance):.2f} more than you earn this month",
            }
        )

    for budget_stat in budget_status:
        if budget_stat["percentage_used"] > 100:
            alerts.append(
                {
                    "type": "warning",
                    "message": f"{budget_stat['category']} budget exceeded",
                    "reason": f"Spent ${budget_stat['spent']:.2f} of ${budget_stat['limit']:.2f} budget",
                    "impact": f"Over budget by ${budget_stat['spent'] - budget_stat['limit']:.2f}",
                }
            )
        elif budget_stat["percentage_used"] >= 80:
            alerts.append(
                {
                    "type": "info",
                    "message": f"{budget_stat['category']} budget nearly exceeded",
                    "reason": f"Used {budget_stat['percentage_used']:.1f}% of budget",
                    "impact": f"Only ${budget_stat['remaining']:.2f} remaining",
                }
            )

    recommendations = []
    for budget_stat in budget_status:
        if budget_stat["percentage_used"] > 100:
            recommendations.append(
                {
                    "category": budget_stat["category"],
                    "title": f"Reduce {budget_stat['category']} spending",
                    "description": f"Cut back on {budget_stat['category']} by ${budget_stat['spent'] - budget_stat['limit']:.2f}",
                    "priority": "high",
                    "reasoning": (
                        f"You spent ${budget_stat['spent']:.2f} on {budget_stat['category']}, "
                        f"which exceeds your ${budget_stat['limit']:.2f} budget."
                    ),
                }
            )

    if balance > 0:
        recommendations.append(
            {
                "category": "Savings",
                "title": "Increase savings",
                "description": f"You have a surplus of ${balance:.2f}. Consider adding it to savings.",
                "priority": "medium",
                "reasoning": f"Your positive balance of ${balance:.2f} can improve financial security.",
            }
        )

    savings_target = user.get("savings_goal") or (total_income * 0.20)
    savings_progress = min((balance / savings_target * 100) if savings_target > 0 else 0, 100)

    recent = sorted(
        expenses + incomes,
        key=lambda x: x.get("date", ""),
        reverse=True,
    )[:8]

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "net_income": balance,
        "total_debts": total_debts,
        "budget_status": budget_status,
        "budgets": budget_status,
        "categoryBreakdown": category_breakdown,
        "alerts": alerts,
        "recommendations": recommendations,
        "recent_transactions": recent[:5],
        "income_count": len(incomes),
        "expense_count": len(expenses),
        "budget_count": len(budgets),
        "debt_count": len([d for d in debts if not d.get("is_paid_off", False)]),
        "savings_rate": (balance / total_income * 100) if total_income > 0 else 0,
        "savings_goal_progress": max(savings_progress, 0),
        "month": month,
    }


async def build_analytics_data(user, months: int = 6) -> dict:
    """Build analytics payload with real category and trend data."""
    incomes = await get_user_incomes(user)
    expenses = await get_user_expenses(user)
    budgets = await get_user_budgets(user)
    dashboard = await build_dashboard_data(user)

    category_breakdown = [
        {"category": cat, "amount": amt}
        for cat, amt in sorted(
            _category_breakdown(expenses).items(), key=lambda x: x[1], reverse=True
        )
    ]

    total_budget = sum(b.get("limit", 0) for b in budgets)
    total_spent = sum(e.get("amount", 0) for e in expenses)

    return {
        "categoryBreakdown": category_breakdown,
        "monthlyTrends": _monthly_trends(incomes, expenses, months),
        "budgetStatus": {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "percentage": (total_spent / total_budget * 100) if total_budget > 0 else 0,
        },
        "savingsRate": dashboard["savings_rate"],
        "total_income": dashboard["total_income"],
        "total_expenses": dashboard["total_expenses"],
    }
