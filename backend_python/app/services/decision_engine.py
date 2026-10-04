"""
Decision engine with rule-based and pattern-based logic for financial recommendations.
Combines traditional rule-based systems with statistical analysis for intelligent advice.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.finance import RecommendationModel
import numpy as np
from collections import defaultdict, Counter
import json

class DecisionEngine:
    """Intelligent decision engine for financial recommendations."""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.get_default_database()
        
        # Rule-based decision thresholds
        self.rules = {
            'savings_rate': {
                'excellent': 0.20,
                'good': 0.15,
                'fair': 0.10,
                'poor': 0.05
            },
            'debt_to_income': {
                'excellent': 0.2,
                'good': 0.3,
                'fair': 0.4,
                'poor': 0.5
            },
            'emergency_fund': {
                'target_months': 6,
                'minimum_months': 3
            },
            'budget_variance': {
                'acceptable': 0.1,  # 10% variance
                'warning': 0.2      # 20% variance
            }
        }
        
        # Pattern analysis weights (simplified for demonstration)
        self.pattern_weights = {
            'seasonal_spending': 0.3,
            'recurring_patterns': 0.4,
            'anomaly_detection': 0.3
        }

    async def generate_recommendations(self, user_id: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        Generate comprehensive financial recommendations using rule-based and pattern-based logic.
        """
        recommendations = []

        # Get user's financial data
        financial_data = await self._get_user_financial_data(user_id)

        # Rule-based recommendations
        rule_recommendations = await self._generate_rule_based_recommendations(financial_data)
        recommendations.extend(rule_recommendations)

        # Pattern-based recommendations
        pattern_recommendations = await self._generate_pattern_recommendations(financial_data)
        recommendations.extend(pattern_recommendations)
        
        # Behavioral insights
        behavioral_recommendations = await self._generate_behavioral_recommendations(financial_data)
        recommendations.extend(behavioral_recommendations)
        
        # Prioritize and rank recommendations
        ranked_recommendations = self._rank_recommendations(recommendations)
        
        # Save recommendations to database
        await self._save_recommendations(user_id, ranked_recommendations)
        
        return ranked_recommendations

    async def _get_user_financial_data(self, user_id: str) -> Dict:
        """Gather comprehensive financial data for analysis."""
        # Get recent data (last 6 months)
        current_date = datetime.now()
        six_months_ago = current_date - timedelta(days=180)
        
        # Expenses
        expenses = await self.db["expenses"].find({
            "user_id": user_id,
            "date": {"$gte": six_months_ago.strftime('%Y-%m-%d')}
        }).to_list(length=None)
        
        # Income
        incomes = await self.db["incomes"].find({
            "user_id": user_id,
            "date": {"$gte": six_months_ago.strftime('%Y-%m-%d')}
        }).to_list(length=None)
        
        # Budgets
        budgets = await self.db["budgets"].find({
            "user_id": user_id,
            "month": {"$gte": six_months_ago.strftime('%Y-%m')}
        }).to_list(length=None)
        
        # Debts
        debts = await self.db["debts"].find({
            "user_id": user_id,
            "is_paid_off": False
        }).to_list(length=None)
        
        # Goals
        goals = await self.db["financial_goals"].find({
            "user_id": user_id
        }).to_list(length=None)
        
        # Calculate aggregates
        monthly_income = self._calculate_monthly_average(incomes)
        monthly_expenses = self._calculate_monthly_average(expenses)
        total_debt = sum(debt['amount'] for debt in debts)
        
        return {
            'user_id': user_id,
            'expenses': expenses,
            'incomes': incomes,
            'budgets': budgets,
            'debts': debts,
            'goals': goals,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'total_debt': total_debt,
            'savings_rate': (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0,
            'debt_to_income': total_debt / monthly_income if monthly_income > 0 else 0
        }

    async def _generate_rule_based_recommendations(self, data: Dict) -> List[Dict]:
        """Generate recommendations based on financial rules."""
        recommendations = []
        
        # Savings rate recommendations
        savings_rate = data['savings_rate']
        if savings_rate < self.rules['savings_rate']['poor']:
            recommendations.append({
                'type': 'savings',
                'priority': 'high',
                'title': 'Increase Your Savings Rate',
                'description': f'Your current savings rate is {savings_rate:.1%}, which is below the recommended minimum of 10%.',
                'potential_savings': data['monthly_income'] * 0.1,
                'confidence_score': 0.9,
                'explanation': 'Financial experts recommend saving at least 10% of your income for long-term financial health.',
                'action_steps': [
                    'Review your discretionary spending categories',
                    'Set up automatic transfers to savings',
                    'Consider reducing non-essential expenses by 10-20%'
                ]
            })
        elif savings_rate < self.rules['savings_rate']['fair']:
            recommendations.append({
                'type': 'savings',
                'priority': 'medium',
                'title': 'Improve Your Savings Rate',
                'description': f'Your savings rate of {savings_rate:.1%} is good, but could be improved to 15%.',
                'potential_savings': data['monthly_income'] * 0.05,
                'confidence_score': 0.8,
                'explanation': 'Increasing your savings rate to 15% will help you build wealth faster and provide better financial security.',
                'action_steps': [
                    'Look for opportunities to optimize spending',
                    'Consider additional income sources',
                    'Review and adjust financial goals'
                ]
            })
        
        # Debt-to-income recommendations
        debt_to_income = data['debt_to_income']
        if debt_to_income > self.rules['debt_to_income']['poor']:
            recommendations.append({
                'type': 'debt',
                'priority': 'high',
                'title': 'Reduce Your Debt-to-Income Ratio',
                'description': f'Your debt-to-income ratio is {debt_to_income:.1%}, which is concerning.',
                'potential_savings': None,
                'confidence_score': 0.95,
                'explanation': 'A high debt-to-income ratio can limit your financial flexibility and increase financial stress.',
                'action_steps': [
                    'Focus on paying down high-interest debt first',
                    'Consider debt consolidation options',
                    'Avoid taking on new debt until ratio improves'
                ]
            })
        
        # Emergency fund recommendations
        monthly_expenses = data['monthly_expenses']
        if monthly_expenses > 0:
            # Calculate current emergency fund (savings)
            current_savings = await self._calculate_emergency_fund(data['user_id'])
            months_covered = current_savings / monthly_expenses
            
            if months_covered < self.rules['emergency_fund']['minimum_months']:
                recommendations.append({
                    'type': 'emergency_fund',
                    'priority': 'high',
                    'title': 'Build Your Emergency Fund',
                    'description': f'You currently have {months_covered:.1f} months of expenses saved. Aim for 3-6 months.',
                    'potential_savings': None,
                    'confidence_score': 0.9,
                    'explanation': 'An emergency fund protects you from unexpected expenses and financial setbacks.',
                    'action_steps': [
                        f'Save ${monthly_expenses * 3:.0f} for minimum emergency fund',
                        'Set up automatic monthly savings',
                        'Use windfalls (bonuses, tax refunds) to boost emergency fund'
                    ]
                })
        
        # Budget adherence recommendations
        budget_violations = await self._analyze_budget_adherence(data['user_id'])
        if budget_violations['frequent_violations']:
            recommendations.append({
                'type': 'budget',
                'priority': 'medium',
                'title': 'Review Your Budget Categories',
                'description': f'You frequently exceed budget in {len(budget_violations["violated_categories"])} categories.',
                'potential_savings': budget_violations['potential_savings'],
                'confidence_score': 0.85,
                'explanation': 'Consistent budget violations indicate unrealistic limits or spending patterns that need attention.',
                'action_steps': [
                    'Review and adjust budget limits for realistic targets',
                    'Identify triggers for overspending in these categories',
                    'Implement spending alerts for problem categories'
                ]
            })
        
        return recommendations

    async def _generate_pattern_recommendations(self, data: Dict) -> List[Dict]:
        """Generate recommendations using pattern-based analysis."""
        recommendations = []
        
        # Seasonal spending patterns
        seasonal_insights = await self._analyze_seasonal_patterns(data['expenses'])
        if seasonal_insights['high_seasonal_spending']:
            recommendations.append({
                'type': 'seasonal',
                'priority': 'medium',
                'title': 'Prepare for Seasonal Spending',
                'description': f'Your spending increases by {seasonal_insights["increase_percentage"]:.1%} during {seasonal_insights["peak_season"]}.',
                'potential_savings': seasonal_insights['potential_savings'],
                'confidence_score': 0.75,
                'explanation': 'Based on your historical spending patterns, we can predict seasonal variations.',
                'action_steps': [
                    f'Create a seasonal budget for {seasonal_insights["peak_season"]}',
                    'Save extra in months leading up to peak season',
                    'Look for seasonal deals and discounts'
                ]
            })
        
        # Recurring pattern analysis
        recurring_patterns = await self._analyze_recurring_patterns(data['expenses'])
        if recurring_patterns['unusual_recurring']:
            recommendations.append({
                'type': 'recurring',
                'priority': 'low',
                'title': 'Review Recurring Expenses',
                'description': f'Found {len(recurring_patterns["unusual_recurring"])} recurring expenses that may need review.',
                'potential_savings': recurring_patterns['potential_savings'],
                'confidence_score': 0.7,
                'explanation': 'Pattern-based analysis identified recurring expenses that might be optimized or eliminated.',
                'action_steps': [
                    'Review subscription services and memberships',
                    'Cancel unused or underutilized recurring services',
                    'Negotiate better rates for essential recurring expenses'
                ]
            })
        
        # Spending anomaly recommendations
        anomalies = await self._detect_spending_anomalies(data['expenses'])
        if anomalies['high_frequency_anomalies']:
            recommendations.append({
                'type': 'anomaly',
                'priority': 'medium',
                'title': 'Address Spending Anomalies',
                'description': f'Detected {len(anomalies["anomalies"])} unusual spending patterns.',
                'potential_savings': anomalies['potential_savings'],
                'confidence_score': 0.8,
                'explanation': 'Our algorithms detected spending patterns that deviate significantly from your normal behavior.',
                'action_steps': [
                    'Review recent large or unusual purchases',
                    'Set up spending alerts for anomaly detection',
                    'Consider if unusual expenses are one-time or recurring'
                ]
            })
        
        return recommendations

    async def _generate_behavioral_recommendations(self, data: Dict) -> List[Dict]:
        """Generate recommendations based on behavioral finance principles."""
        recommendations = []
        
        # Spending timing analysis
        timing_analysis = await self._analyze_spending_timing(data['expenses'])
        if timing_analysis['impulse_spending_high']:
            recommendations.append({
                'type': 'behavioral',
                'priority': 'medium',
                'title': 'Reduce Impulse Spending',
                'description': f'{timing_analysis["impulse_percentage"]:.1%} of your spending appears to be impulse purchases.',
                'potential_savings': timing_analysis['potential_savings'],
                'confidence_score': 0.75,
                'explanation': 'Impulse spending often leads to regret and can significantly impact your financial goals.',
                'action_steps': [
                    'Implement a 24-hour rule for non-essential purchases',
                    'Use cash for discretionary spending',
                    'Unsubscribe from marketing emails and notifications'
                ]
            })
        
        # Merchant loyalty analysis
        merchant_analysis = await self._analyze_merchant_patterns(data['expenses'])
        if merchant_analysis['concentrated_spending']:
            recommendations.append({
                'type': 'behavioral',
                'priority': 'low',
                'title': 'Diversify Your Spending',
                'description': f'{merchant_analysis["concentration_percentage"]:.1%} of your spending is with {merchant_analysis["top_merchant"]}.',
                'potential_savings': merchant_analysis['potential_savings'],
                'confidence_score': 0.6,
                'explanation': 'Diversifying spending can help you find better deals and reduce dependency on single providers.',
                'action_steps': [
                    'Compare prices with alternative providers',
                    'Look for loyalty programs with other merchants',
                    'Consider bulk purchases or subscription alternatives'
                ]
            })
        
        return recommendations

    def _rank_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Rank recommendations by priority, confidence, and potential impact."""
        # Calculate composite score for each recommendation
        for rec in recommendations:
            priority_scores = {'high': 3, 'medium': 2, 'low': 1}
            priority_score = priority_scores.get(rec['priority'], 1)
            
            # Weight the components
            composite_score = (
                priority_score * 0.4 +
                rec['confidence_score'] * 0.3 +
                (rec.get('potential_savings', 0) / 1000) * 0.3  # Normalize savings
            )
            
            rec['composite_score'] = composite_score
        
        # Sort by composite score (descending)
        ranked_recommendations = sorted(recommendations, key=lambda x: x['composite_score'], reverse=True)
        
        # Add rank
        for i, rec in enumerate(ranked_recommendations, 1):
            rec['rank'] = i
        
        return ranked_recommendations

    async def _save_recommendations(self, user_id: str, recommendations: List[Dict]):
        """Save recommendations to database."""
        # Clear old recommendations
        await self.db["recommendations"].delete_many({"user_id": user_id})
        
        # Save new recommendations
        if recommendations:
            # Add timestamps and user_id
            current_time = datetime.now()
            for rec in recommendations:
                rec['user_id'] = user_id
                rec['created_at'] = current_time
                rec['is_implemented'] = False
            
            await self.db["recommendations"].insert_many(recommendations)

    # Helper methods
    def _calculate_monthly_average(self, transactions: List[Dict]) -> float:
        """Calculate average monthly amount from transactions."""
        if not transactions:
            return 0
        
        total = sum(t['amount'] for t in transactions)
        # Simple average (could be improved with actual date calculations)
        return total / 6  # Assuming 6 months of data

    async def _calculate_emergency_fund(self, user_id: str) -> float:
        """Calculate current emergency fund (savings)."""
        # This would typically include savings accounts, investments, etc.
        # For now, we'll use a simplified calculation
        return 0  # Placeholder

    async def _analyze_budget_adherence(self, user_id: str) -> Dict:
        """Analyze how well user adheres to budget."""
        # Simplified analysis - would need more sophisticated logic
        return {
            'frequent_violations': False,
            'violated_categories': [],
            'potential_savings': 0
        }

    async def _analyze_seasonal_patterns(self, expenses: List[Dict]) -> Dict:
        """Analyze seasonal spending patterns."""
        # Simplified seasonal analysis
        return {
            'high_seasonal_spending': False,
            'peak_season': 'December',
            'increase_percentage': 15.0,
            'potential_savings': 100
        }

    async def _analyze_recurring_patterns(self, expenses: List[Dict]) -> Dict:
        """Analyze recurring expense patterns."""
        # Simplified recurring analysis
        return {
            'unusual_recurring': [],
            'potential_savings': 50
        }

    async def _detect_spending_anomalies(self, expenses: List[Dict]) -> Dict:
        """Detect spending anomalies using statistical analysis."""
        # Simplified anomaly detection
        return {
            'high_frequency_anomalies': False,
            'anomalies': [],
            'potential_savings': 0
        }

    async def _analyze_spending_timing(self, expenses: List[Dict]) -> Dict:
        """Analyze spending timing for impulse detection."""
        # Simplified timing analysis
        return {
            'impulse_spending_high': False,
            'impulse_percentage': 20.0,
            'potential_savings': 75
        }

    async def _analyze_merchant_patterns(self, expenses: List[Dict]) -> Dict:
        """Analyze merchant concentration patterns."""
        # Simplified merchant analysis
        return {
            'concentrated_spending': False,
            'top_merchant': 'Amazon',
            'concentration_percentage': 25.0,
            'potential_savings': 50
        }

# Global decision engine instance
decision_engine = DecisionEngine()
