"""
Comprehensive rule-based recommendation engine with detailed explanations.
Provides intelligent financial recommendations with transparency and ethics.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

class RecommendationType(str, Enum):
    """Types of recommendations."""
    SAVINGS = "Savings"
    DEBT_REDUCTION = "Debt Reduction"
    SPENDING_OPTIMIZATION = "Spending Optimization"
    WARNING = "Warning"
    BUDGET_ALERT = "Budget Alert"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FinancialRecommendationEngine:
    """
    Rule-based financial recommendation engine.
    Generates recommendations based on spending patterns and budget analysis.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.ethical_disclaimer = (
            "This system provides educational financial suggestions and does not replace "
            "professional financial advice. All recommendations are based on rule-based analysis "
            "of your spending patterns. Consult a financial advisor before making major decisions."
        )
        
        # Category spending thresholds (percentage of total income)
        self.category_thresholds = {
            'Food': 0.15,           # Max 15% of income
            'Transportation': 0.10,  # Max 10% of income
            'Housing': 0.30,        # Max 30% of income
            'Utilities': 0.08,      # Max 8% of income
            'Entertainment': 0.10,  # Max 10% of income
            'Health': 0.08,         # Max 8% of income
            'Education': 0.10,      # Max 10% of income
            'Shopping': 0.10,       # Max 10% of income
        }
        
        # Savings target (percentage of income)
        self.savings_target = 0.20  # Target 20% savings rate
    
    async def generate_recommendations(
        self,
        user_id: str,
        financial_data: Dict,
        budget_data: Dict
    ) -> List[Dict]:
        """
        Generate comprehensive recommendations based on financial data.
        
        Args:
            user_id: User ID
            financial_data: Dict with totalIncome, totalExpenses, categoryBreakdown
            budget_data: Dict with budget limits and current spending
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        total_income = financial_data.get('totalIncome', 0)
        total_expenses = financial_data.get('totalExpenses', 0)
        category_breakdown = financial_data.get('categoryBreakdown', {})
        savings = total_income - total_expenses
        
        if total_income <= 0:
            return recommendations
        
        # 1. Budget Overrun Recommendations
        budget_recs = self._check_budget_violations(budget_data, category_breakdown, total_income)
        recommendations.extend(budget_recs)
        
        # 2. Spending Pattern Recommendations
        spending_recs = self._analyze_spending_patterns(category_breakdown, total_income)
        recommendations.extend(spending_recs)
        
        # 3. Savings Recommendations
        if savings < total_income * self.savings_target:
            savings_recs = self._generate_savings_recommendations(category_breakdown, total_income, savings)
            recommendations.extend(savings_recs)
        
        # 4. Financial Health Recommendations
        if total_expenses > total_income:
            health_recs = self._generate_financial_health_warnings(total_income, total_expenses)
            recommendations.extend(health_recs)
        
        # 5. Category-Specific Recommendations
        category_recs = self._analyze_category_spending(category_breakdown, total_income)
        recommendations.extend(category_recs)
        
        # Sort by priority
        recommendations.sort(key=lambda x: self._priority_to_score(x['priority']), reverse=True)
        
        return recommendations
    
    def _check_budget_violations(self, budget_data: Dict, category_breakdown: Dict, total_income: float) -> List[Dict]:
        """Check for budget violations and generate recommendations."""
        recommendations = []
        
        for category, limit in budget_data.items():
            spent = category_breakdown.get(category, 0)
            percentage_used = (spent / limit * 100) if limit > 0 else 0
            
            if spent > limit:
                # Budget exceeded
                recommendations.append({
                    'id': f'budget_exceed_{category}',
                    'type': RecommendationType.BUDGET_ALERT,
                    'title': f'{category} Budget Exceeded',
                    'recommendation': f'You have exceeded your {category} budget limit.',
                    'explanation': (
                        f'You spent ${spent:.2f} of your ${limit:.2f} {category} budget. '
                        f'This represents {percentage_used:.1f}% of your budget. '
                        f'Consider reducing {category} expenses or adjusting your budget.'
                    ),
                    'potential_savings': spent - limit,
                    'priority': RecommendationPriority.HIGH,
                    'category': category,
                    'action_steps': [
                        f'Review your {category} transactions',
                        f'Identify unnecessary {category} expenses',
                        f'Create an action plan to reduce {category} spending',
                        f'Update your budget if needed'
                    ]
                })
            elif spent > limit * 0.80:
                # Budget approaching limit (80%)
                recommendations.append({
                    'id': f'budget_warn_{category}',
                    'type': RecommendationType.WARNING,
                    'title': f'{category} Budget Warning',
                    'recommendation': f'You are approaching your {category} budget limit.',
                    'explanation': (
                        f'You have spent ${spent:.2f} of your ${limit:.2f} {category} budget '
                        f'({percentage_used:.1f}%). Only ${limit - spent:.2f} remaining. '
                        f'Be cautious with remaining {category} expenses this month.'
                    ),
                    'potential_savings': (limit - spent) * 0.5,
                    'priority': RecommendationPriority.MEDIUM,
                    'category': category,
                    'action_steps': [
                        f'Monitor {category} spending closely',
                        f'Defer non-essential {category} purchases',
                        f'Track daily {category} expenses'
                    ]
                })
        
        return recommendations
    
    def _analyze_spending_patterns(self, category_breakdown: Dict, total_income: float) -> List[Dict]:
        """Analyze spending patterns and generate recommendations."""
        recommendations = []
        
        for category, amount in category_breakdown.items():
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            threshold = self.category_thresholds.get(category, 0.15)
            threshold_percentage = threshold * 100
            
            if percentage > threshold_percentage:
                excess = amount - (total_income * threshold)
                recommendations.append({
                    'id': f'pattern_{category}',
                    'type': RecommendationType.SPENDING_OPTIMIZATION,
                    'title': f'Optimize {category} Spending',
                    'recommendation': f'Your {category} spending is higher than recommended.',
                    'explanation': (
                        f'{category} represents {percentage:.1f}% of your income. '
                        f'Financial experts recommend limiting {category} to {threshold_percentage:.0f}%. '
                        f'Reducing {category} spending by ${excess:.2f} could improve your financial health.'
                    ),
                    'potential_savings': excess,
                    'priority': RecommendationPriority.MEDIUM,
                    'category': category,
                    'action_steps': [
                        f'Review all {category} purchases',
                        f'Identify items you could reduce or eliminate',
                        f'Look for ways to cut {category} expenses',
                        f'Track progress over next month'
                    ]
                })
        
        return recommendations
    
    def _generate_savings_recommendations(self, category_breakdown: Dict, total_income: float, savings: float) -> List[Dict]:
        """Generate recommendations to improve savings."""
        recommendations = []
        
        target_savings = total_income * self.savings_target
        savings_gap = target_savings - savings
        
        if savings_gap > 0:
            recommendations.append({
                'id': 'savings_target',
                'type': RecommendationType.SAVINGS,
                'title': 'Increase Your Savings Rate',
                'recommendation': 'Your current savings rate is below the recommended 20%.',
                'explanation': (
                    f'You are currently saving ${savings:.2f} per month ({(savings/total_income*100):.1f}% of income). '
                    f'To reach the recommended 20% savings rate, you need to save an additional ${savings_gap:.2f}. '
                    f'This can be achieved by reducing discretionary spending or increasing income.'
                ),
                'potential_savings': savings_gap,
                'priority': RecommendationPriority.HIGH,
                'category': 'Savings',
                'action_steps': [
                    'Calculate your target monthly savings amount',
                    'Identify discretionary expenses to reduce',
                    'Set up automatic transfers to savings account',
                    'Monitor savings progress monthly'
                ]
            })
            
            # Find top spending categories to reduce
            sorted_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
            top_categories = sorted_categories[:3]
            
            potential_reductions = [
                f"Reduce {cat}: ${amount * 0.1:.2f}/month (10% cut)"
                for cat, amount in top_categories
            ]
            
            recommendations.append({
                'id': 'reduce_discretionary',
                'type': RecommendationType.SPENDING_OPTIMIZATION,
                'title': 'Reduce Discretionary Spending',
                'recommendation': 'Cut discretionary expenses to reach your savings target.',
                'explanation': (
                    f'By reducing your top spending categories by just 10%, you could save an additional '
                    f'${sum(amount * 0.1 for _, amount in top_categories):.2f} per month. '
                    f'This includes: {", ".join(potential_reductions)}.'
                ),
                'potential_savings': sum(amount * 0.1 for _, amount in top_categories),
                'priority': RecommendationPriority.MEDIUM,
                'category': 'Discretionary',
                'action_steps': [
                    'Review entertainment and shopping expenses',
                    'Look for subscription services to cancel',
                    'Reduce dining out frequency',
                    'Set limits on non-essential purchases'
                ]
            })
        
        return recommendations
    
    def _generate_financial_health_warnings(self, total_income: float, total_expenses: float) -> List[Dict]:
        """Generate warnings for poor financial health."""
        recommendations = []
        
        deficit = total_expenses - total_income
        
        recommendations.append({
            'id': 'financial_deficit',
            'type': RecommendationType.WARNING,
            'title': 'Critical: Expenses Exceed Income',
            'recommendation': 'Your monthly expenses exceed your income. Immediate action required.',
            'explanation': (
                f'Your monthly expenses (${total_expenses:.2f}) exceed your income (${total_income:.2f}) '
                f'by ${deficit:.2f}. This is unsustainable and requires immediate action. '
                f'You must either increase income or reduce expenses.'
            ),
            'potential_savings': deficit,
            'priority': RecommendationPriority.HIGH,
            'category': 'Financial Health',
            'action_steps': [
                'Review all expenses and identify cuts immediately',
                'Prioritize essential expenses (housing, food, utilities)',
                'Consider additional income sources',
                'Create an emergency action plan',
                'Seek professional financial guidance'
            ]
        })
        
        return recommendations
    
    def _analyze_category_spending(self, category_breakdown: Dict, total_income: float) -> List[Dict]:
        """Analyze individual category spending patterns."""
        recommendations = []
        
        # Entertainment spending analysis
        entertainment = category_breakdown.get('Entertainment', 0)
        entertainment_pct = (entertainment / total_income * 100) if total_income > 0 else 0
        
        if entertainment_pct > 15:
            recommendations.append({
                'id': 'high_entertainment',
                'type': RecommendationType.SPENDING_OPTIMIZATION,
                'title': 'Reduce Entertainment Spending',
                'recommendation': 'You are spending a large percentage on entertainment.',
                'explanation': (
                    f'Entertainment represents {entertainment_pct:.1f}% of your income. '
                    f'Consider reducing subscriptions, dining out, or entertainment expenses.'
                ),
                'potential_savings': entertainment * 0.2,
                'priority': RecommendationPriority.MEDIUM,
                'category': 'Entertainment',
                'action_steps': [
                    'Review all subscriptions (streaming, music, etc.)',
                    'Cancel unused subscriptions',
                    'Reduce restaurant/dining out frequency',
                    'Look for free entertainment options'
                ]
            })
        
        # Shopping spending analysis
        shopping = category_breakdown.get('Shopping', 0)
        shopping_pct = (shopping / total_income * 100) if total_income > 0 else 0
        
        if shopping_pct > 12:
            recommendations.append({
                'id': 'high_shopping',
                'type': RecommendationType.SPENDING_OPTIMIZATION,
                'title': 'Control Shopping Expenses',
                'recommendation': 'Your shopping expenses are higher than recommended.',
                'explanation': (
                    f'Shopping represents {shopping_pct:.1f}% of your income. '
                    f'Implement strategies like 30-day rule, avoid impulse purchases, and use shopping lists.'
                ),
                'potential_savings': shopping * 0.15,
                'priority': RecommendationPriority.MEDIUM,
                'category': 'Shopping',
                'action_steps': [
                    'Use the 30-day rule for purchases',
                    'Shop with a list only',
                    'Avoid impulse buying',
                    'Unsubscribe from marketing emails',
                    'Use cashback and rewards programs'
                ]
            })
        
        return recommendations
    
    def _priority_to_score(self, priority: str) -> int:
        """Convert priority string to numeric score for sorting."""
        priority_map = {
            RecommendationPriority.HIGH: 3,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 1,
        }
        return priority_map.get(priority, 1)
    
    def get_ethical_disclosure(self) -> str:
        """Get the ethical disclosure text."""
        return self.ethical_disclaimer


# Singleton instance
financial_recommendation_engine = FinancialRecommendationEngine()
