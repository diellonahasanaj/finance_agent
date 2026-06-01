"""
Finance service logic for income, expense, budget, and debt operations.
Handles file-based storage for financial data.
"""
import json
import os
from datetime import datetime
from app.schemas.finance import IncomeCreate, ExpenseCreate, BudgetCreate, DebtCreate
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
    """
    expenses = load_data(EXPENSES_FILE)
    
    expense_dict = expense.dict()
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
