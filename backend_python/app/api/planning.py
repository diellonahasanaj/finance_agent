"""
Financial Planning and Alerts API Endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from app.utils.auth import get_current_user
from app.services.financial_planning_service import (
    debt_repayment_planner,
    savings_goal_planner,
    financial_health_analyzer
)
from app.services.alerts_service import alerts_manager
from app.services.finance_service import get_user_incomes, get_user_expenses, get_user_budgets, get_user_debts
from typing import Optional
from datetime import datetime

router = APIRouter()

# ==================== DEBT REPAYMENT PLANNING ====================

@router.post("/planning/debt-repayment")
async def calculate_debt_repayment(
    request: dict,
    user=Depends(get_current_user)
):
    """
    Calculate optimal debt repayment strategy.
    
    Request body:
    {
        "monthly_payment": 1000,
        "strategy": "avalanche" | "snowball" | "interest_minimization" | "timeline",
        "target_months": 24 (optional, for timeline strategy)
    }
    """
    try:
        monthly_payment = request.get('monthly_payment', 0)
        strategy = request.get('strategy', 'avalanche')
        target_months = request.get('target_months')
        
        # Get user's debts
        debts = await get_user_debts(user)
        
        if not debts:
            return {
                'status': 'success',
                'message': 'No debts found',
                'debts': []
            }
        
        # Calculate payoff plan
        plan = debt_repayment_planner.calculate_payoff_plan(
            debts,
            monthly_payment,
            strategy,
            target_months
        )
        
        return {
            'status': 'success',
            'data': plan,
            'disclaimer': 'This is educational guidance. Consult a financial advisor for debt management.'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/planning/debt-repayment/strategies")
async def get_debt_strategies(user=Depends(get_current_user)):
    """Get available debt repayment strategies with explanations."""
    from app.services.financial_planning_service import DebtRepaymentPlanner
    
    strategies = {}
    for name, description in DebtRepaymentPlanner.STRATEGIES.items():
        strategies[name] = description
    
    return {
        'strategies': strategies,
        'recommended': 'avalanche',
        'note': 'Avalanche saves most interest. Snowball provides psychological wins.'
    }


# ==================== SAVINGS GOALS PLANNING ====================

@router.post("/planning/savings-goal")
async def calculate_savings_goal(
    request: dict,
    user=Depends(get_current_user)
):
    """
    Calculate savings plan for a financial goal.
    
    Request body:
    {
        "goal_amount": 10000,
        "current_savings": 2000,
        "monthly_contribution": 500,
        "target_months": 16 (optional)
    }
    """
    try:
        goal_amount = request.get('goal_amount', 0)
        current_savings = request.get('current_savings', 0)
        monthly_contribution = request.get('monthly_contribution', 0)
        target_months = request.get('target_months')
        
        if goal_amount <= 0:
            raise ValueError("Goal amount must be positive")
        
        plan = savings_goal_planner.calculate_goal_plan(
            goal_amount,
            current_savings,
            monthly_contribution,
            target_months
        )
        
        return {
            'status': 'success',
            'data': plan
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/planning/compound-savings")
async def calculate_compound_savings(
    request: dict,
    user=Depends(get_current_user)
):
    """
    Calculate compound savings with interest.
    
    Request body:
    {
        "monthly_contribution": 500,
        "months": 60,
        "annual_interest_rate": 2.5
    }
    """
    try:
        monthly_contribution = request.get('monthly_contribution', 0)
        months = request.get('months', 12)
        annual_rate = request.get('annual_interest_rate', 0)
        
        if monthly_contribution <= 0:
            raise ValueError("Monthly contribution must be positive")
        
        calculation = savings_goal_planner.calculate_compound_savings(
            monthly_contribution,
            months,
            annual_rate
        )
        
        return {
            'status': 'success',
            'data': calculation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== FINANCIAL HEALTH ANALYSIS ====================

@router.get("/planning/financial-health")
async def analyze_financial_health(user=Depends(get_current_user)):
    """Get comprehensive financial health analysis and score."""
    try:
        # Fetch all financial data
        incomes = await get_user_incomes(user)
        expenses = await get_user_expenses(user)
        debts = await get_user_debts(user)
        
        total_income = sum(inc.get('amount', 0) for inc in incomes)
        total_expenses = sum(exp.get('amount', 0) for exp in expenses)
        total_debt = sum(debt.get('amount', 0) for debt in debts)
        
        financial_data = {
            'totalIncome': total_income,
            'totalExpenses': total_expenses,
            'totalDebt': total_debt,
            'savings': 0  # Would need to fetch from savings account/goals
        }
        
        analysis = financial_health_analyzer.analyze_financial_health(financial_data)
        
        return {
            'status': 'success',
            'data': analysis,
            'disclaimer': 'This analysis is based on entered financial data. Consult professionals for major decisions.'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/planning/financial-health/benchmarks")
async def get_health_benchmarks(user=Depends(get_current_user)):
    """Get financial health benchmarks."""
    from app.services.financial_planning_service import FinancialHealthAnalyzer
    
    analyzer = FinancialHealthAnalyzer()
    benchmarks = analyzer.HEALTH_BENCHMARKS
    
    return {
        'benchmarks': {
            'savings_rate': f"{benchmarks['savings_rate']*100:.0f}% of income",
            'debt_to_income': f"{benchmarks['debt_to_income']*100:.0f}% of income",
            'emergency_fund': f"{benchmarks['emergency_fund_months']} months of expenses",
            'housing_ratio': f"{benchmarks['housing_ratio']*100:.0f}% of income",
            'debt_free_target': f"{benchmarks['debt_free_years']} years"
        },
        'description': 'Industry-standard financial health benchmarks'
    }


# ==================== ALERTS & NOTIFICATIONS ====================

@router.get("/alerts")
async def get_alerts(user=Depends(get_current_user)):
    """Get all active financial alerts."""
    try:
        # Fetch financial data
        incomes = await get_user_incomes(user)
        expenses = await get_user_expenses(user)
        budgets = await get_user_budgets(user)
        
        total_income = sum(inc.get('amount', 0) for inc in incomes)
        total_expenses = sum(exp.get('amount', 0) for exp in expenses)
        
        # Build category breakdown
        category_breakdown = {}
        for expense in expenses:
            category = expense.get('category', 'Other')
            amount = expense.get('amount', 0)
            category_breakdown[category] = category_breakdown.get(category, 0) + amount
        
        financial_data = {
            'totalIncome': total_income,
            'totalExpenses': total_expenses,
            'categoryBreakdown': category_breakdown
        }
        
        budget_data = {
            'budgets': budgets
        }
        
        # Generate alerts
        alerts = alerts_manager.generate_alerts(
            str(user.get('_id')),
            financial_data,
            budget_data
        )
        
        # Prioritize and summarize
        prioritized = alerts_manager.prioritize_alerts(alerts)
        summary = alerts_manager.get_alert_summary(prioritized)
        
        return {
            'status': 'success',
            'alerts': summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/dismiss/{alert_id}")
async def dismiss_alert(
    alert_id: str,
    user=Depends(get_current_user)
):
    """Dismiss a specific alert."""
    try:
        alerts_manager.dismiss_alert(alert_id)
        return {
            'status': 'success',
            'message': f'Alert {alert_id} dismissed'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/alerts/summary")
async def get_alerts_summary(user=Depends(get_current_user)):
    """Get alert summary without fetching all alerts."""
    try:
        active_alerts = alerts_manager.get_active_alerts()
        
        summary = {
            'total': len(active_alerts),
            'critical': len([a for a in active_alerts if a['severity'] == 'critical']),
            'warning': len([a for a in active_alerts if a['severity'] == 'warning']),
            'info': len([a for a in active_alerts if a['severity'] == 'info']),
            'last_updated': datetime.now().isoformat()
        }
        
        return {
            'status': 'success',
            'summary': summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FINANCIAL RECOMMENDATIONS ====================

@router.get("/planning/recommendations")
async def get_planning_recommendations(user=Depends(get_current_user)):
    """Get AI-powered financial recommendations."""
    try:
        # Get financial health first
        incomes = await get_user_incomes(user)
        expenses = await get_user_expenses(user)
        budgets = await get_user_budgets(user)
        debts = await get_user_debts(user)
        
        total_income = sum(inc.get('amount', 0) for inc in incomes)
        total_expenses = sum(exp.get('amount', 0) for exp in expenses)
        total_debt = sum(debt.get('amount', 0) for debt in debts)
        
        financial_data = {
            'totalIncome': total_income,
            'totalExpenses': total_expenses,
            'totalDebt': total_debt,
            'savings': 0
        }
        
        health = financial_health_analyzer.analyze_financial_health(financial_data)
        recommendations = health.get('recommendations', [])
        
        return {
            'status': 'success',
            'recommendations': recommendations,
            'health_score': health.get('score'),
            'health_status': health.get('status'),
            'disclaimer': 'This system provides educational financial guidance and does not replace professional financial advice.'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TRANSPARENCY & DISCLAIMER ====================

@router.get("/transparency")
async def get_transparency_info(user=Depends(get_current_user)):
    """Get system transparency information and disclaimers."""
    return {
        'system': 'AI-Powered Personal Finance Advisor Agent',
        'disclaimer': (
            'This system provides educational financial guidance and does not replace professional financial advice. '
            'All recommendations are generated through rule-based analysis of your financial data. '
            'Consult a qualified financial advisor or professional before making major financial decisions, '
            'especially regarding debt, investments, or long-term planning.'
        ),
        'data_handling': {
            'privacy': 'All financial data is encrypted and stored securely.',
            'retention': 'Data is retained for analysis and historical tracking.',
            'sharing': 'Your data is never shared with third parties without consent.'
        },
        'limitations': {
            'no_investment_advice': 'We do not provide investment or trading recommendations.',
            'no_guarantees': 'We cannot guarantee financial outcomes or predictions.',
            'educational_only': 'This system is for educational purposes only.',
            'not_licensed': 'This system is not a licensed financial advisor or service.'
        },
        'confidence_scores': {
            '0.9-1.0': 'High confidence',
            '0.7-0.9': 'Medium confidence',
            '0.5-0.7': 'Lower confidence',
            '<0.5': 'Low confidence - verify before acting'
        }
    }
