"""
Analysis service for monthly financial summary and recommendations.
Implements rule-based logic for warnings and suggestions.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from bson import ObjectId

# MongoDB client for analysis
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client.get_default_database()

async def get_monthly_summary(user, month: str):
    """
    Return monthly summary and recommendations for the user.
    Applies rule-based logic for budget warnings, savings, and debt.
    """
    user_id = user["_id"]  # Use the _id field directly as string
    incomes = await db["incomes"].find({"user_id": user_id, "date": {"$regex": f"^{month}"}}).to_list(length=None)
    expenses = await db["expenses"].find({"user_id": user_id, "date": {"$regex": f"^{month}"}}).to_list(length=None)
    budgets = await db["budgets"].find({"user_id": user_id, "month": month}).to_list(length=None)
    debts = await db["debts"].find({"user_id": user_id}).to_list(length=None)

    total_income = sum(i["amount"] for i in incomes)
    total_expenses = sum(e["amount"] for e in expenses)
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income else 0
    category_breakdown = {}
    budget_violations = []
    recommendations = []

    # Calculate category breakdown
    for expense in expenses:
        cat = expense["category"]
        category_breakdown[cat] = category_breakdown.get(cat, 0) + expense["amount"]

    # Check for budget violations and add recommendations
    for budget in budgets:
        spent = category_breakdown.get(budget["category"], 0)
        if spent > 0.8 * budget["limit"]:
            budget_violations.append({
                "category": budget["category"],
                "spent": spent,
                "limit": budget["limit"],
                "percent": round(spent / budget["limit"] * 100, 1),
            })
            if spent > budget["limit"]:
                recommendations.append({
                    "type": "warning",
                    "title": "Budget Exceeded",
                    "message": f"You exceeded your {budget['category']} budget!",
                    "reasoning": f"Spent {spent} of {budget['limit']} in {budget['category']}.",
                })
            else:
                recommendations.append({
                    "type": "warning",
                    "title": "Approaching Budget Limit",
                    "message": f"You have spent over 80% of your {budget['category']} budget!",
                    "reasoning": f"Spent {spent} of {budget['limit']} in {budget['category']}.",
                })

    # Financial risk alert
    if total_expenses > total_income:
        recommendations.append({
            "type": "alert",
            "title": "Financial Risk",
            "message": "Your expenses exceed your income this month.",
            "reasoning": f"Expenses: {total_expenses}, Income: {total_income}",
        })

    # Savings suggestion
    if savings_rate < 10:
        recommendations.append({
            "type": "suggestion",
            "title": "Increase Savings",
            "message": "Your savings rate is below 10%. Try to save more.",
            "reasoning": f"Savings rate: {savings_rate:.1f}%",
        })

    # Debt prioritization
    total_debt = sum(d["amount"] for d in debts)
    debt_ratio = (total_debt / total_income * 100) if total_income else 0
    if debt_ratio > 40:
        recommendations.append({
            "type": "suggestion",
            "title": "Prioritize Debt Repayment",
            "message": "Your debt ratio is high. Focus on paying down debt.",
            "reasoning": f"Debt ratio: {debt_ratio:.1f}%",
        })

    return {
        "totalIncome": total_income,
        "totalExpenses": total_expenses,
        "savingsRate": round(savings_rate, 1),
        "categoryBreakdown": category_breakdown,
        "budgetViolations": budget_violations,
        "recommendations": recommendations,
    }
