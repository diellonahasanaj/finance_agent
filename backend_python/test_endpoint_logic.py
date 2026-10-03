import asyncio
import json
import os
from app.services.finance_service import load_data, INCOMES_FILE, EXPENSES_FILE, BUDGETS_FILE
from app.services.recommendation_engine_v2 import financial_recommendation_engine

async def test_recommendations():
    user_key = "thesis_test@example.com"
    
    # Load data from JSON files
    incomes_data = load_data(INCOMES_FILE)
    expenses_data = load_data(EXPENSES_FILE)
    budgets_data = load_data(BUDGETS_FILE)
    
    user_incomes = incomes_data.get(user_key, [])
    user_expenses = expenses_data.get(user_key, [])
    user_budgets = budgets_data.get(user_key, [])
    
    print(f"User incomes: {len(user_incomes)}")
    print(f"User expenses: {len(user_expenses)}")
    print(f"User budgets: {len(user_budgets)}")
    
    total_income = sum(i.get('amount', 0) for i in user_incomes)
    total_expenses = sum(e.get('amount', 0) for e in user_expenses)
    
    print(f"Total income: {total_income}")
    print(f"Total expenses: {total_expenses}")
    
    category_breakdown = {}
    for expense in user_expenses:
        category = expense.get('category', 'Other')
        category_breakdown[category] = category_breakdown.get(category, 0) + expense.get('amount', 0)
    
    print(f"Category breakdown: {category_breakdown}")
    
    # Create budget dict
    budget_dict = {}
    for budget in user_budgets:
        category = budget.get('category', '')
        limit = budget.get('limit', 0)
        if category:
            budget_dict[category] = limit
    
    print(f"Budget dict: {budget_dict}")
    
    # Generate recommendations using JSON-based engine
    financial_data = {
        'totalIncome': total_income,
        'totalExpenses': total_expenses,
        'categoryBreakdown': category_breakdown
    }
    
    print("Calling generate_recommendations...")
    recommendations = await financial_recommendation_engine.generate_recommendations(
        user_id=user_key,
        financial_data=financial_data,
        budget_data=budget_dict
    )
    
    print(f"Recommendations generated: {len(recommendations)}")
    
    # Convert enum objects to strings for JSON serialization
    for rec in recommendations:
        if 'type' in rec and hasattr(rec['type'], 'value'):
            rec['type'] = rec['type'].value
        if 'priority' in rec and hasattr(rec['priority'], 'value'):
            rec['priority'] = rec['priority'].value
    
    result = {"recommendations": recommendations}
    print(f"Result: {json.dumps(result, indent=2)}")
    return result

if __name__ == "__main__":
    asyncio.run(test_recommendations())
