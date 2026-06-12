"""
Recommendations API - Endpoints for fetching AI-generated recommendations.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user
from app.services.recommendation_engine_v2 import financial_recommendation_engine
from app.services.expense_classifier import expense_classifier
from app.models.finance import RecommendationModel
from typing import List, Dict
import json
import os
from datetime import datetime
from bson import ObjectId

router = APIRouter()

# File-based storage paths
RECOMMENDATIONS_FILE = "recommendations.json"
EXPENSES_FILE = "expenses.json"
BUDGETS_FILE = "budgets.json"
INCOMES_FILE = "incomes.json"


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


def get_user_data_key(user):
    """Get user data key for file-based storage."""
    return user.get("email", str(user.get("_id", "")))


@router.get("/recommendations", response_model=Dict)
async def get_recommendations(user=Depends(get_current_user)):
    """
    Get AI-generated recommendations for the user.
    Analyzes spending patterns and generates intelligent suggestions.
    """
    try:
        user_key = get_user_data_key(user)
        expenses_data = load_data(EXPENSES_FILE)
        budgets_data = load_data(BUDGETS_FILE)
        incomes_data = load_data(INCOMES_FILE)

        user_expenses = expenses_data.get(user_key, [])
        user_budgets = budgets_data.get(user_key, [])
        user_incomes = incomes_data.get(user_key, [])

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
        
        # Generate recommendations
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
        
        # Get ethical disclaimer
        ethical_disclaimer = financial_recommendation_engine.get_ethical_disclosure()
        
        return {
            'status': 'success',
            'recommendations': recommendations,
            'total_count': len(recommendations),
            'ethical_disclaimer': ethical_disclaimer,
            'generated_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/recommendations/save")
async def save_recommendation(
    recommendation: Dict,
    user=Depends(get_current_user)
):
    """
    Save a recommendation for the user.
    Allows tracking of which recommendations have been implemented.
    """
    try:
        user_key = get_user_data_key(user)
        recommendations_data = load_data(RECOMMENDATIONS_FILE)
        
        if user_key not in recommendations_data:
            recommendations_data[user_key] = []
        
        # Add metadata
        rec_with_meta = {
            **recommendation,
            '_id': str(ObjectId()),
            'user_id': str(user.get('_id', '')),
            'saved_at': datetime.utcnow().isoformat()
        }
        
        recommendations_data[user_key].append(rec_with_meta)
        save_data(RECOMMENDATIONS_FILE, recommendations_data)
        
        return {
            'status': 'success',
            'message': 'Recommendation saved',
            'recommendation_id': rec_with_meta['_id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving recommendation: {str(e)}")


@router.get("/recommendations/history")
async def get_recommendations_history(user=Depends(get_current_user)):
    """
    Get historical recommendations for the user.
    """
    try:
        user_key = get_user_data_key(user)
        recommendations_data = load_data(RECOMMENDATIONS_FILE)
        
        user_recommendations = recommendations_data.get(user_key, [])
        
        return {
            'status': 'success',
            'recommendations': user_recommendations,
            'total_count': len(user_recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations history: {str(e)}")


@router.get("/categories")
async def get_expense_categories(user=Depends(get_current_user)):
    """
    Get all available expense categories for classification.
    """
    try:
        categories = expense_classifier.get_all_categories()
        
        return {
            'status': 'success',
            'categories': categories,
            'total_count': len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")


@router.post("/classify-expense")
async def classify_expense(
    body: dict,
    user=Depends(get_current_user)
):
    """
    Classify an expense into a category using rule-based logic.
    
    Returns:
        {
            'classified_category': str,
            'confidence': float (0-1),
            'suggestions': List[str]
        }
    """
    try:
        title = body.get("title", body.get("description", ""))
        description = body.get("description", "")
        # Get classification
        classified_category, confidence = expense_classifier.classify_expense(title, description)
        
        # Get all categories as suggestions
        all_categories = expense_classifier.get_all_categories()
        
        return {
            'status': 'success',
            'classified_category': classified_category,
            'confidence': confidence,
            'suggestions': all_categories,
            'explanation': (
                f'Based on keywords in "{title}", this expense is classified as {classified_category} '
                f'with {confidence*100:.0f}% confidence.'
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying expense: {str(e)}")


@router.get("/how-it-works")
async def get_how_it_works(user=Depends(get_current_user)):
    """
    Get explanation of how the recommendation engine works.
    Transparency layer for users.
    """
    return {
        'status': 'success',
        'how_it_works': {
            'title': 'How the AI Advisor Works',
            'sections': [
                {
                    'title': '1. Expense Tracking',
                    'description': (
                        'The system tracks your expenses by category (Food, Transportation, '
                        'Housing, Entertainment, etc.). Each expense is automatically classified '
                        'using keyword matching and machine learning.'
                    )
                },
                {
                    'title': '2. Budget Analysis',
                    'description': (
                        'Your spending is compared against your monthly budgets. The system alerts '
                        'you when you approach or exceed budget limits (80%, 95%, 100%).'
                    )
                },
                {
                    'title': '3. Financial Health Assessment',
                    'description': (
                        'The system calculates key metrics: savings rate, expense ratio, budget '
                        'compliance. These metrics are used to assess your overall financial health.'
                    )
                },
                {
                    'title': '4. Rule-Based Recommendations',
                    'description': (
                        'Recommendations are generated using clear, transparent rules: '
                        'IF (condition) THEN (recommendation). '
                        'Examples: "IF entertainment > 30% of income, THEN suggest reducing". '
                        'All recommendations include detailed explanations of the reasoning.'
                    )
                },
                {
                    'title': '5. Action Steps',
                    'description': (
                        'Each recommendation comes with specific, actionable steps you can take '
                        'to improve your financial situation.'
                    )
                },
                {
                    'title': '6. Educational Content',
                    'description': (
                        'The system explains financial concepts and best practices, helping you '
                        'understand why certain behaviors are recommended.'
                    )
                }
            ],
            'ethical_guidelines': [
                '✅ All recommendations are transparent and explainable',
                '✅ You control which recommendations to implement',
                '✅ Your financial data is private and secure',
                '✅ Recommendations are educational, not financial advice',
                '✅ No risky or high-risk financial advice is given',
                '✅ You should consult a professional before major financial decisions'
            ],
            'disclaimer': financial_recommendation_engine.get_ethical_disclosure()
        }
    }
