from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from app.schemas.finance import IncomeCreate, ExpenseCreate, BudgetCreate, DebtCreate, DebtUpdate, IncomeUpdate, ExpenseUpdate
from app.services.finance_service import (
    add_income, add_expense, set_budget, add_debt,
    get_user_incomes, get_user_expenses, get_user_budgets, get_user_debts,
    build_dashboard_data, build_analytics_data,
    update_expense, delete_expense, update_income, delete_income,
    update_debt, delete_debt,
    get_transactions, get_category_statistics,
    load_data, INCOMES_FILE, EXPENSES_FILE, BUDGETS_FILE,
)
from app.services.data_handling import data_handler
from app.services.expense_analysis import expense_analyzer
from app.services.decision_engine import decision_engine
from app.services.financial_planning_service import debt_repayment_planner, savings_goal_planner, financial_health_analyzer
from app.services.alerts_service import alerts_manager
from app.utils.auth import get_current_user
from typing import Optional
from datetime import datetime
import os

router = APIRouter()

# Basic CRUD operations
@router.post("/income")
async def create_income(income: IncomeCreate, user=Depends(get_current_user)):
    return await add_income(user, income)

@router.get("/income")
async def get_incomes(user=Depends(get_current_user)):
    """Get all user's income records."""
    return await get_user_incomes(user)

@router.put("/income/{income_id}")
async def update_income_record(income_id: str, update: IncomeUpdate, user=Depends(get_current_user)):
    """Update an income record."""
    result = await update_income(user, income_id, update)
    if not result:
        raise HTTPException(status_code=404, detail="Income not found")
    return result

@router.delete("/income/{income_id}")
async def delete_income_record(income_id: str, user=Depends(get_current_user)):
    """Delete an income record."""
    deleted = await delete_income(user, income_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income deleted successfully"}

@router.post("/expense")
async def create_expense(expense: ExpenseCreate, user=Depends(get_current_user)):
    return await add_expense(user, expense)

@router.get("/expense")
async def get_expenses(user=Depends(get_current_user)):
    """Get all user's expense records."""
    return await get_user_expenses(user)

@router.put("/expense/{expense_id}")
async def update_expense_record(expense_id: str, update: ExpenseUpdate, user=Depends(get_current_user)):
    """Update an expense record."""
    result = await update_expense(user, expense_id, update)
    if not result:
        raise HTTPException(status_code=404, detail="Expense not found")
    return result

@router.delete("/expense/{expense_id}")
async def delete_expense_record(expense_id: str, user=Depends(get_current_user)):
    """Delete an expense record."""
    deleted = await delete_expense(user, expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

@router.post("/budget")
async def create_budget(budget: BudgetCreate, user=Depends(get_current_user)):
    return await set_budget(user, budget)

@router.get("/budget")
async def get_budgets(user=Depends(get_current_user)):
    """Get all user's budget records."""
    return await get_user_budgets(user)

@router.post("/debt")
async def create_debt(debt: DebtCreate, user=Depends(get_current_user)):
    return await add_debt(user, debt)

@router.get("/debt")
async def get_debts(user=Depends(get_current_user)):
    """Get all user's debt records."""
    return await get_user_debts(user)

@router.put("/debt/{debt_id}")
async def update_debt_record(debt_id: str, update: DebtUpdate, user=Depends(get_current_user)):
    """Update a debt record."""
    result = await update_debt(user, debt_id, update)
    return result

@router.delete("/debt/{debt_id}")
async def delete_debt_record(debt_id: str, user=Depends(get_current_user)):
    """Delete a debt record."""
    deleted = await delete_debt(user, debt_id)
    return deleted

@router.get("/dashboard")
async def get_dashboard_data(
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    user=Depends(get_current_user),
):
    """Get comprehensive dashboard data with alerts and recommendations."""
    try:
        return await build_dashboard_data(user, month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics_data(
    months: int = Query(default=6, description="Number of months for trend analysis"),
    user=Depends(get_current_user),
):
    """Get analytics data for charts and visualizations."""
    try:
        return await build_analytics_data(user, months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions")
async def list_transactions(
    type: Optional[str] = Query(None, description="Filter by type: income or expense"),
    search: Optional[str] = Query(None, description="Search in description, category, source"),
    category: Optional[str] = Query(None, description="Filter by category or source"),
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user=Depends(get_current_user),
):
    """Get paginated, searchable transaction list."""
    return await get_transactions(user, type, search, category, month, page, page_size)


@router.get("/categories/statistics")
async def category_statistics(
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    user=Depends(get_current_user),
):
    """Get category statistics for expenses and income."""
    return await get_category_statistics(user, month)


@router.post("/ai-chat")
async def ai_chat(query: dict, user=Depends(get_current_user)):
    """Real-time AI chat endpoint that processes natural language and generates dynamic responses."""
    try:
        user_message = query.get('message', '').lower()
        
        # Get current financial data
        incomes = await get_user_incomes(user)
        expenses = await get_user_expenses(user)
        budgets = await get_user_budgets(user)
        
        total_income = sum(income.get('amount', 0) for income in incomes)
        total_expenses = sum(expense.get('amount', 0) for expense in expenses)
        balance = total_income - total_expenses
        
        # Analyze spending patterns
        spending_by_category = {}
        for expense in expenses:
            category = expense.get('category', 'Other')
            amount = expense.get('amount', 0)
            spending_by_category[category] = spending_by_category.get(category, 0) + amount
        
        # Get top spending categories
        top_categories = sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Budget analysis
        budget_analysis = []
        for budget in budgets:
            category_expenses = sum(
                expense.get('amount', 0) 
                for expense in expenses 
                if expense.get('category') == budget.get('category')
            )
            budget_limit = budget.get('limit', 0)
            percentage_used = (category_expenses / budget_limit * 100) if budget_limit > 0 else 0
            
            budget_analysis.append({
                'category': budget.get('category'),
                'limit': budget_limit,
                'spent': category_expenses,
                'percentage_used': percentage_used,
                'status': 'over_budget' if percentage_used > 100 else 'on_track' if percentage_used <= 100 else 'warning'
            })
        
        # Real-time natural language processing
        response = process_natural_language_query(user_message, {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'spending_by_category': spending_by_category,
            'top_categories': top_categories,
            'budget_analysis': budget_analysis,
            'incomes': incomes,
            'expenses': expenses,
            'budgets': budgets
        })
        
        return {
            'response': response,
            'data': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'balance': balance,
                'budget_count': len(budgets),
                'expense_count': len(expenses),
                'top_categories': top_categories,
                'budget_analysis': budget_analysis,
                'spending_by_category': spending_by_category
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_natural_language_query(message: str, financial_data: dict) -> str:
    """Process natural language queries and generate dynamic responses."""
    
    # Extract key information from the message
    words = message.split()
    
    # Financial calculations and data extraction
    total_income = financial_data['total_income']
    total_expenses = financial_data['total_expenses']
    balance = financial_data['balance']
    spending_by_category = financial_data['spending_by_category']
    top_categories = financial_data['top_categories']
    budget_analysis = financial_data['budget_analysis']
    
    # Dynamic response generation based on natural language patterns
    
    # Question patterns
    if any(word in words for word in ['how', 'what', 'why', 'when', 'where', 'who']):
        return answer_question(message, financial_data)
    
    # Request patterns
    elif any(word in words for word in ['show', 'tell', 'give', 'explain', 'calculate']):
        return handle_request(message, financial_data)
    
    # Comparison patterns
    elif any(word in words for word in ['compare', 'versus', 'vs', 'better', 'worse']):
        return handle_comparison(message, financial_data)
    
    # Advice patterns
    elif any(word in words for word in ['should', 'recommend', 'suggest', 'advise']):
        return give_advice(message, financial_data)
    
    # Problem patterns
    elif any(word in words for word in ['problem', 'issue', 'trouble', 'help', 'fix']):
        return solve_problem(message, financial_data)
    
    # Default intelligent response
    else:
        return generate_intelligent_response(message, financial_data)

def answer_question(message: str, data: dict) -> str:
    """Answer specific questions about finances."""
    words = message.split()
    
    # Income questions
    if any(word in words for word in ['income', 'earn', 'make', 'salary']):
        if data['total_income'] > 0:
            return f"💰 Your current total income is ${data['total_income']:.2f}. Based on your financial records, this comes from {len(data['incomes'])} income source(s). Your monthly income flow {'looks healthy' if data['total_income'] > data['total_expenses'] else 'needs attention as it\'s less than your expenses'}."
        else:
            return "📊 I don't see any income records in your account. Adding your income sources will help me provide better financial analysis."
    
    # Expense questions
    elif any(word in words for word in ['expense', 'spend', 'cost', 'pay']):
        if data['total_expenses'] > 0:
            top_cat = data['top_categories'][0] if data['top_categories'] else ('None', 0)
            return f"💳 Your total expenses are ${data['total_expenses']:.2f}. Your highest spending category is {top_cat[0]} at ${top_cat[1]:.2f}. You have {len(data['expenses'])} expense transactions recorded."
        else:
            return "📝 No expenses recorded yet. Start tracking your expenses to see spending patterns and get budget recommendations."
    
    # Balance questions
    elif any(word in words for word in ['balance', 'left', 'remaining', 'net']):
        if data['balance'] >= 0:
            return f"✅ Your current balance is ${data['balance']:.2f}. This means you're living within your means and have {'a surplus to save or invest' if data['balance'] > 0 else 'break-even finances'}."
        else:
            return f"⚠️ Your balance is negative at ${abs(data['balance']):.2f}. This indicates you're spending more than you earn. I recommend reviewing your expenses and finding areas to cut back."
    
    # Budget questions
    elif any(word in words for word in ['budget', 'limit', 'allocation']):
        if data['budget_analysis']:
            over_budget = [b for b in data['budget_analysis'] if b['status'] == 'over_budget']
            if over_budget:
                return f"📊 You have {len(data['budget_analysis'])} budgets set. {len(over_budget)} are over budget. {over_budget[0]['category']} is ${over_budget[0]['spent'] - over_budget[0]['limit']:.2f} over limit."
            else:
                return f"🎯 Great job! All {len(data['budget_analysis'])} budgets are on track. Your budget discipline is helping you maintain financial stability."
        else:
            return "📋 No budgets set yet. I recommend setting budgets for your top spending categories to control your spending."
    
    # Category-specific questions
    elif any(word in words for word in ['category', 'food', 'transport', 'shopping', 'entertainment']):
        mentioned_category = None
        for category in data['spending_by_category'].keys():
            if any(word in message.lower() for word in category.split()):
                mentioned_category = category
                break
        
        if mentioned_category:
            amount = data['spending_by_category'][mentioned_category]
            percentage = (amount / data['total_expenses'] * 100) if data['total_expenses'] > 0 else 0
            return f"📈 You spent ${amount:.2f} on {mentioned_category}, which is {percentage:.1f}% of your total expenses. {'This seems reasonable' if percentage < 20 else 'This is a significant portion of your spending'}."
        else:
            return f"🔍 I can analyze any spending category. Your top categories are: {', '.join([cat[0] for cat in data['top_categories']])}. Ask me about any of these!"
    
    # Default question response
    else:
        return f"🤔 I can answer questions about your income, expenses, budget, spending categories, and balance. Try asking something like 'How much do I spend on food?' or 'What's my current balance?'"

def handle_request(message: str, data: dict) -> str:
    """Handle specific requests for information or actions."""
    words = message.split()
    
    # Show requests
    if any(word in words for word in ['show', 'tell', 'display']):
        if any(word in words for word in ['spending', 'expenses']):
            return f"📊 **Your Spending Breakdown:**\n\n" + "\n".join([f"• {cat}: ${amount:.2f}" for cat, amount in data['top_categories']])
        
        elif any(word in words for word in ['budget', 'budgets']):
            if data['budget_analysis']:
                return f"📋 **Budget Status:**\n\n" + "\n".join([f"• {b['category']}: ${b['spent']:.2f}/${b['limit']:.2f} ({b['percentage_used']:.1f}%)" for b in data['budget_analysis']])
            else:
                return "No budgets set. Would you like help creating one?"
        
        elif any(word in words for word in ['income', 'earnings']):
            return f"💰 **Income Overview:**\n\nTotal: ${data['total_income']:.2f}\nSources: {len(data['incomes'])}"
    
    # Calculate requests
    elif any(word in words for word in ['calculate', 'compute']):
        if any(word in words for word in ['save', 'saving']):
            if data['balance'] > 0:
                return f"💡 **Savings Calculation:**\n\nMonthly surplus: ${data['balance']:.2f}\nAnnual savings potential: ${data['balance'] * 12:.2f}\n5-year savings: ${data['balance'] * 60:.2f}"
            else:
                return f"📊 **Savings Analysis:**\n\nCurrently no surplus to save. Reducing expenses by ${abs(data['balance']) + 100:.2f} would enable monthly savings of $100."
        
        elif any(word in words for word in ['budget', 'budgets']):
            if data['total_expenses'] > 0:
                return f"📋 **Recommended Budgets:**\n\n" + "\n".join([f"• {cat}: ${amount * 1.1:.2f} (10% buffer)" for cat, amount in data['top_categories']])
    
    # Explain requests
    elif any(word in words for word in ['explain', 'why']):
        if data['balance'] < 0:
            return f"🔍 **Deficit Explanation:**\n\nYour expenses (${data['total_expenses']:.2f}) exceed income (${data['total_income']:.2f}) by ${abs(data['balance']):.2f}. Main contributors: {', '.join([cat[0] for cat in data['top_categories'][:2]])}."
        elif data['balance'] > 0:
            return f"✅ **Surplus Explanation:**\n\nYour income (${data['total_income']:.2f}) exceeds expenses (${data['total_expenses']:.2f}) by ${data['balance']:.2f}. This creates opportunities for savings and investments."
    
    return "🤔 I'm not sure how to handle that request. Try asking me to show, calculate, or explain something specific about your finances."

def handle_comparison(message: str, data: dict) -> str:
    """Handle comparison requests."""
    words = message.split()
    
    # Income vs expenses
    if any(word in words for word in ['income', 'expense']):
        if data['total_income'] > data['total_expenses']:
            ratio = data['total_expenses'] / data['total_income'] * 100
            return f"📊 **Income vs Expenses:**\n\nIncome: ${data['total_income']:.2f}\nExpenses: ${data['total_expenses']:.2f}\nRatio: {ratio:.1f}%\n\n✅ You're spending {ratio:.1f}% of your income, which is {'excellent' if ratio < 70 else 'good' if ratio < 90 else 'concerning'}."
        else:
            return f"📊 **Income vs Expenses:**\n\nIncome: ${data['total_income']:.2f}\nExpenses: ${data['total_expenses']:.2f}\n\n⚠️ Expenses exceed income by ${abs(data['balance']):.2f}. This needs immediate attention."
    
    # Category comparisons
    elif any(word in words for word in ['category', 'categories']):
        if len(data['top_categories']) >= 2:
            cat1, cat2 = data['top_categories'][0], data['top_categories'][1]
            return f"📈 **Category Comparison:**\n\n{cat1[0]}: ${cat1[1]:.2f}\n{cat2[0]}: ${cat2[1]:.2f}\n\n{cat1[0]} is ${cat1[1] - cat2[1]:.2f} {'higher' if cat1[1] > cat2[1] else 'lower'} than {cat2[0]}."
    
    return "📊 I can compare income vs expenses, or different spending categories. What would you like me to compare?"

def give_advice(message: str, data: dict) -> str:
    """Provide personalized advice based on financial situation."""
    words = message.split()
    
    # General advice
    if any(word in words for word in ['general', 'overall', 'advice']):
        advice = []
        if data['balance'] < 0:
            advice.append("🔴 **Priority 1:** Fix negative cash flow by reducing expenses or increasing income")
        if len([b for b in data['budget_analysis'] if b['status'] == 'over_budget']) > 0:
            advice.append("🟡 **Priority 2:** Review and adjust over-budget categories")
        if data['balance'] > 0:
            advice.append(f"🟢 **Priority 3:** Use ${data['balance']:.2f} surplus for savings/debt reduction")
        
        return "\n\n".join(advice) if advice else "✅ Your finances look good! Keep maintaining your current habits."
    
    # Specific advice
    elif any(word in words for word in ['save', 'saving']):
        if data['balance'] > 0:
            return f"💡 **Savings Advice:**\n\nWith a ${data['balance']:.2f} monthly surplus:\n• Emergency fund: ${data['balance'] * 3:.2f} (3 months)\n• Retirement: ${data['balance'] * 0.3:.2f}/month\n• Investments: ${data['balance'] * 0.2:.2f}/month"
        else:
            return "💡 **Savings Advice:**\n\nFirst, achieve positive cash flow. Then start with $1,000 emergency fund before other savings goals."
    
    elif any(word in words for word in ['budget', 'budgeting']):
        return f"📋 **Budgeting Advice:**\n\nBased on your spending:\n" + "\n".join([f"• {cat}: ${amount * 1.1:.2f} (with 10% buffer)" for cat, amount in data['top_categories']])
    
    return "🎯 I can give advice on saving, budgeting, debt reduction, or general financial planning. What specific area would you like advice on?"

def solve_problem(message: str, data: dict) -> str:
    """Help solve financial problems."""
    words = message.split()
    
    # Overspending problem
    if any(word in words for word in ['overspend', 'over', 'too much']):
        over_budget = [b for b in data['budget_analysis'] if b['status'] == 'over_budget']
        if over_budget:
            return f"🔧 **Overspending Solution:**\n\nProblem areas: {', '.join([b['category'] for b in over_budget])}\n\nAction plan:\n" + "\n".join([f"• {b['category']}: Reduce by ${(b['spent'] - b['limit']):.2f}" for b in over_budget])
        else:
            return "✅ No overspending detected. Your budget discipline is working well!"
    
    # Low income problem
    elif any(word in words for word in ['income', 'low', 'increase']):
        return f"📈 **Income Improvement:**\n\nCurrent income: ${data['total_income']:.2f}\n\nSuggestions:\n• Negotiate salary raise\n• Develop new skills\n• Side hustle/freelance\n• Passive income streams\n\nTarget: Increase by ${data['total_expenses'] - data['total_income'] + 500:.2f} to achieve healthy surplus"
    
    # High expenses problem
    elif any(word in words for word in ['expense', 'cost', 'reduce', 'cut']):
        categories_str = "\n".join([f"{i+1}. {cat}: ${amount:.2f}" for i, (cat, amount) in enumerate(data.get('top_categories', []))])
        return f"✂️ **Expense Reduction:**\n\nTop 3 expense categories:\n{categories_str}\n\nFocus on reducing the top category by 20-30% for maximum impact."
    
    return "🔧 I can help with overspending, low income, or high expense problems. What specific financial challenge are you facing?"

def generate_intelligent_response(message: str, data: dict) -> str:
    """Generate intelligent responses for general queries."""
    
    # Analyze the message content and financial context
    if data['balance'] < 0:
        return f"💬 I notice you're currently operating with a deficit of ${abs(data['balance']):.2f}. This requires immediate attention. Would you like me to help you create a plan to get back on track?"
    
    elif len([b for b in data['budget_analysis'] if b['status'] == 'over_budget']) > 0:
        count = len([b for b in data['budget_analysis'] if b['status'] == 'over_budget'])
        return f"💬 You have {count} budget category{'s' if count > 1 else ''} that need attention. I can help you analyze these and create a recovery plan. Shall we look at the details?"
    
    elif data['balance'] > 0:
        return f"💬 Great news! You have a monthly surplus of ${data['balance']:.2f}. This puts you in a strong position to build wealth. Would you like guidance on optimal allocation strategies?"
    
    else:
        return f"💬 I'm here to help with your financial questions. You can ask me about spending analysis, budget optimization, savings strategies, or any other financial topic. What's on your mind?"

# Data import and handling
@router.post("/import/csv")
async def import_csv_data(
    file: UploadFile = File(...),
    data_type: str = Query(..., description="Type of data: expenses, income, budgets, debts"),
    user=Depends(get_current_user)
):
    """Import financial data from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    content_str = content.decode('utf-8')
    
    result = await data_handler.import_csv_data(user["_id"], content_str, data_type)
    return result

@router.post("/import/json")
async def import_json_data(
    file: UploadFile = File(...),
    data_type: str = Query(..., description="Type of data: expenses, income, budgets, debts"),
    user=Depends(get_current_user)
):
    """Import financial data from JSON file."""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must be a JSON")
    
    content = await file.read()
    content_str = content.decode('utf-8')
    
    result = await data_handler.import_json_data(user["_id"], content_str, data_type)
    return result

@router.post("/generate-sample-data")
async def generate_sample_data(
    months: int = Query(default=6, description="Number of months of sample data"),
    user=Depends(get_current_user)
):
    """Generate realistic sample financial data for testing."""
    result = await data_handler.generate_sample_data(user["_id"], months)
    return result

# Expense analysis endpoints
@router.get("/analysis/monthly")
async def get_monthly_analysis(
    month: str = Query(..., description="Month in YYYY-MM format"),
    user=Depends(get_current_user)
):
    """Get comprehensive monthly financial analysis."""
    analysis = await expense_analyzer.analyze_monthly_expenses(user["_id"], month)
    return analysis

@router.get("/analysis/trends")
async def get_spending_trends(
    months: int = Query(default=6, description="Number of months to analyze"),
    user=Depends(get_current_user)
):
    """Get spending trends over multiple months."""
    trends = await expense_analyzer.analyze_spending_trends(user["_id"], months)
    return trends

@router.get("/analysis/anomalies")
async def detect_anomalies(
    month: str = Query(..., description="Month in YYYY-MM format"),
    user=Depends(get_current_user)
):
    """Detect spending anomalies and unusual patterns."""
    anomalies = await expense_analyzer.detect_anomalies(user["_id"], month)
    return {"anomalies": anomalies, "month": month}

@router.get("/analysis/budget-recommendations")
async def get_budget_recommendations(user=Depends(get_current_user)):
    """Get intelligent budget recommendations."""
    recommendations = await expense_analyzer.generate_budget_recommendations(user["_id"])
    return {"recommendations": recommendations}

@router.get("/recommendations")
async def get_recommendations(user=Depends(get_current_user)):
    """Get personalized financial recommendations."""
    try:
        from app.services.recommendation_engine_v2 import financial_recommendation_engine
    except ImportError as e:
        import traceback
        raise HTTPException(status_code=503, detail=f"Recommendation engine import failed: {str(e)}\nTraceback: {traceback.format_exc()}")
    
    try:
        user_key = user.get("email", str(user.get("_id", "")))
        
        # Load data from JSON files
        incomes_data = load_data(INCOMES_FILE)
        expenses_data = load_data(EXPENSES_FILE)
        budgets_data = load_data(BUDGETS_FILE)
        
        user_incomes = incomes_data.get(user_key, [])
        user_expenses = expenses_data.get(user_key, [])
        user_budgets = budgets_data.get(user_key, [])
        
        total_income = sum(i.get('amount', 0) for i in user_incomes)
        total_expenses = sum(e.get('amount', 0) for e in user_expenses)
        
        category_breakdown = {}
        for expense in user_expenses:
            category = expense.get('category', 'Other')
            category_breakdown[category] = category_breakdown.get(category, 0) + expense.get('amount', 0)
        
        # Create budget dict
        budget_dict = {}
        for budget in user_budgets:
            category = budget.get('category', '')
            limit = budget.get('limit', 0)
            if category:
                budget_dict[category] = limit
        
        # Generate recommendations using JSON-based engine
        financial_data = {
            'totalIncome': total_income,
            'totalExpenses': total_expenses,
            'categoryBreakdown': category_breakdown
        }
        
        recommendations = await financial_recommendation_engine.generate_recommendations(
            user_id=user_key,
            financial_data=financial_data,
            budget_data=budget_dict
        )
        
        # Convert enum objects to strings for JSON serialization
        for rec in recommendations:
            if 'type' in rec and hasattr(rec['type'], 'value'):
                rec['type'] = rec['type'].value
            if 'priority' in rec and hasattr(rec['priority'], 'value'):
                rec['priority'] = rec['priority'].value
        
        return {"recommendations": recommendations}
    except Exception as e:
        import traceback
        error_detail = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail[:1000])

# Financial health endpoints
@router.get("/health/score")
async def get_financial_health_score(
    month: str = Query(..., description="Month in YYYY-MM format"),
    user=Depends(get_current_user)
):
    """Get comprehensive financial health score."""
    analysis = await expense_analyzer.analyze_monthly_expenses(user["_id"], month)
    return {
        "health_score": analysis["financial_health_score"],
        "month": month,
        "summary": analysis["summary"]
    }

@router.get("/health/dashboard")
async def get_health_dashboard(
    months: int = Query(default=6, description="Number of months to analyze"),
    user=Depends(get_current_user)
):
    """Get comprehensive financial health dashboard."""
    # Get trends
    trends = await expense_analyzer.analyze_spending_trends(user["_id"], months)
    
    # Get latest month analysis
    current_month = datetime.now().strftime('%Y-%m')
    latest_analysis = await expense_analyzer.analyze_monthly_expenses(user["_id"], current_month)
    
    # Get recommendations
    recommendations = await decision_engine.generate_recommendations(user["_id"])
    
    return {
        "trends": trends,
        "latest_analysis": latest_analysis,
        "recommendations": recommendations[:5],  # Top 5 recommendations
        "health_score": latest_analysis["financial_health_score"]
    }

# Privacy and transparency endpoints
@router.get("/privacy/data-summary")
async def get_data_summary(user=Depends(get_current_user)):
    """Get summary of user's data for transparency."""
    from app.services.finance_service import load_data, INCOMES_FILE, EXPENSES_FILE, BUDGETS_FILE, DEBTS_FILE

    user_key = user.get("email", str(user["_id"]))
    summary = {
        "expenses": len(load_data(EXPENSES_FILE).get(user_key, [])),
        "incomes": len(load_data(INCOMES_FILE).get(user_key, [])),
        "budgets": len(load_data(BUDGETS_FILE).get(user_key, [])),
        "debts": len(load_data(DEBTS_FILE).get(user_key, [])),
    }
    rec_file = "recommendations.json"
    if os.path.exists(rec_file):
        summary["recommendations"] = len(load_data(rec_file).get(user_key, []))

    return {
        "data_summary": summary,
        "total_records": sum(summary.values()),
        "privacy_policy": "Your data is used only to provide personalized financial recommendations and is never shared with third parties.",
        "data_retention": "Data is retained for as long as you use the service. You can request deletion at any time.",
    }

@router.delete("/privacy/delete-data")
async def delete_user_data(user=Depends(get_current_user)):
    """Delete all user financial data (GDPR compliance)."""
    from app.services.finance_service import (
        load_data, save_data, INCOMES_FILE, EXPENSES_FILE, BUDGETS_FILE, DEBTS_FILE,
    )

    user_key = user.get("email", str(user["_id"]))
    deleted_counts = {}

    for filename in [INCOMES_FILE, EXPENSES_FILE, BUDGETS_FILE, DEBTS_FILE]:
        data = load_data(filename)
        count = len(data.get(user_key, []))
        data[user_key] = []
        save_data(filename, data)
        deleted_counts[filename.replace(".json", "")] = count

    rec_file = "recommendations.json"
    if os.path.exists(rec_file):
        rec_data = load_data(rec_file)
        rec_count = len(rec_data.get(user_key, []))
        rec_data[user_key] = []
        save_data(rec_file, rec_data)
        deleted_counts["recommendations"] = rec_count

    return {
        "message": "All your financial data has been deleted successfully",
        "deleted_records": deleted_counts,
        "total_deleted": sum(deleted_counts.values()),
    }
