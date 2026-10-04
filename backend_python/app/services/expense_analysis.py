"""
Advanced expense and budget analysis service.
Provides classification, overspending detection, and financial insights.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.finance import ExpenseModel, BudgetModel
import numpy as np
from collections import defaultdict

class ExpenseAnalyzer:
    """Comprehensive expense analysis and budget monitoring."""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.get_default_database()
        
        # Spending patterns and thresholds
        self.spending_patterns = {
            'discretionary_spending_threshold': 0.3,  # 30% of income
            'essential_spending_ratio': 0.5,  # 50% should be essential
            'savings_target_ratio': 0.2,  # 20% savings target
            'emergency_fund_months': 6,  # 6 months of expenses
        }
        
        # Category benchmarks (based on typical spending patterns)
        self.category_benchmarks = {
            'Housing': {'min': 0.25, 'max': 0.35, 'ideal': 0.30},  # % of income
            'Food': {'min': 0.10, 'max': 0.15, 'ideal': 0.12},
            'Transportation': {'min': 0.10, 'max': 0.15, 'ideal': 0.12},
            'Utilities': {'min': 0.05, 'max': 0.10, 'ideal': 0.08},
            'Entertainment': {'min': 0.05, 'max': 0.10, 'ideal': 0.06},
            'Shopping': {'min': 0.05, 'max': 0.10, 'ideal': 0.07},
            'Healthcare': {'min': 0.05, 'max': 0.10, 'ideal': 0.08},
            'Savings': {'min': 0.15, 'max': 0.25, 'ideal': 0.20},
        }

    async def analyze_monthly_expenses(self, user_id: str, month: str) -> Dict:
        """
        Comprehensive monthly expense analysis.
        """
        # Get expenses for the month
        expenses = await self.db["expenses"].find({
            "user_id": user_id,
            "date": {"$regex": f"^{month}"}
        }).to_list(length=None)
        
        # Get income for the month
        incomes = await self.db["incomes"].find({
            "user_id": user_id,
            "date": {"$regex": f"^{month}"}
        }).to_list(length=None)
        
        # Get budgets for the month
        budgets = await self.db["budgets"].find({
            "user_id": user_id,
            "month": month
        }).to_list(length=None)
        
        # Calculate totals
        total_expenses = sum(exp["amount"] for exp in expenses)
        total_income = sum(inc["amount"] for inc in incomes)
        
        # Category breakdown
        category_breakdown = self._calculate_category_breakdown(expenses)
        
        # Budget analysis
        budget_analysis = await self._analyze_budget_performance(expenses, budgets)
        
        # Spending patterns
        spending_patterns = self._analyze_spending_patterns(expenses)
        
        # Financial health score
        health_score = self._calculate_financial_health_score(
            total_income, total_expenses, category_breakdown, budget_analysis
        )
        
        # Overspending alerts
        overspending_alerts = self._detect_overspending(expenses, budgets)
        
        return {
            'month': month,
            'summary': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_savings': total_income - total_expenses,
                'savings_rate': (total_income - total_expenses) / total_income if total_income > 0 else 0
            },
            'category_breakdown': category_breakdown,
            'budget_analysis': budget_analysis,
            'spending_patterns': spending_patterns,
            'financial_health_score': health_score,
            'overspending_alerts': overspending_alerts,
            'expense_count': len(expenses),
            'average_daily_spending': total_expenses / 30 if total_expenses > 0 else 0
        }

    async def analyze_spending_trends(self, user_id: str, months: int = 6) -> Dict:
        """
        Analyze spending trends over multiple months.
        """
        trends = []
        current_date = datetime.now()
        
        for i in range(months):
            month_date = current_date - timedelta(days=30 * i)
            month_str = month_date.strftime('%Y-%m')
            
            monthly_analysis = await self.analyze_monthly_expenses(user_id, month_str)
            trends.append(monthly_analysis)
        
        # Calculate trend metrics
        trend_analysis = self._calculate_trend_metrics(trends)
        
        return {
            'trends': trends,
            'trend_analysis': trend_analysis,
            'period_months': months
        }

    async def detect_anomalies(self, user_id: str, month: str) -> List[Dict]:
        """
        Detect unusual spending patterns and anomalies.
        """
        expenses = await self.db["expenses"].find({
            "user_id": user_id,
            "date": {"$regex": f"^{month}"}
        }).to_list(length=None)
        
        anomalies = []
        
        # Get historical data for comparison
        historical_expenses = await self.db["expenses"].find({
            "user_id": user_id,
            "date": {"$lt": month}
        }).to_list(length=None)
        
        # Category-based anomaly detection
        category_stats = self._calculate_category_statistics(historical_expenses)
        
        for expense in expenses:
            category = expense['category']
            amount = expense['amount']
            
            if category in category_stats:
                stats = category_stats[category]
                # Flag expenses more than 2 standard deviations above mean
                if amount > stats['mean'] + 2 * stats['std']:
                    anomalies.append({
                        'type': 'high_amount',
                        'expense': expense,
                        'reason': f'Amount ${amount:.2f} is unusually high for {category}',
                        'severity': 'high' if amount > stats['mean'] + 3 * stats['std'] else 'medium'
                    })
        
        # Frequency-based anomaly detection
        frequency_anomalies = self._detect_frequency_anomalies(expenses, historical_expenses)
        anomalies.extend(frequency_anomalies)
        
        return anomalies

    async def generate_budget_recommendations(self, user_id: str) -> List[Dict]:
        """
        Generate intelligent budget recommendations based on spending patterns.
        """
        # Get last 3 months of data
        recommendations = []
        current_date = datetime.now()
        
        for i in range(3):
            month_date = current_date - timedelta(days=30 * i)
            month_str = month_date.strftime('%Y-%m')
            
            expenses = await self.db["expenses"].find({
                "user_id": user_id,
                "date": {"$regex": f"^{month_str}"}
            }).to_list(length=None)
            
            incomes = await self.db["incomes"].find({
                "user_id": user_id,
                "date": {"$regex": f"^{month_str}"}
            }).to_list(length=None)
            
            if expenses and incomes:
                total_income = sum(inc["amount"] for inc in incomes)
                category_breakdown = self._calculate_category_breakdown(expenses)
                
                # Generate recommendations for each category
                for category, data in category_breakdown.items():
                    percentage = data['amount'] / total_income if total_income > 0 else 0
                    
                    if category in self.category_benchmarks:
                        benchmark = self.category_benchmarks[category]
                        
                        if percentage > benchmark['max']:
                            recommendations.append({
                                'category': category,
                                'type': 'reduce_spending',
                                'current_percentage': percentage,
                                'recommended_percentage': benchmark['ideal'],
                                'potential_savings': (percentage - benchmark['ideal']) * total_income,
                                'priority': 'high' if percentage > benchmark['max'] * 1.2 else 'medium',
                                'explanation': f'Your {category} spending at {percentage:.1%} of income exceeds the recommended maximum of {benchmark["max"]:.1%}'
                            })
                        elif percentage < benchmark['min']:
                            recommendations.append({
                                'category': category,
                                'type': 'increase_budget',
                                'current_percentage': percentage,
                                'recommended_percentage': benchmark['ideal'],
                                'priority': 'low',
                                'explanation': f'Your {category} spending at {percentage:.1%} is below typical levels'
                            })
        
        return recommendations

    def _calculate_category_breakdown(self, expenses: List[Dict]) -> Dict:
        """Calculate spending breakdown by category."""
        breakdown = defaultdict(lambda: {'amount': 0, 'count': 0, 'essential': 0, 'discretionary': 0})
        
        for expense in expenses:
            category = expense['category']
            amount = expense['amount']
            is_essential = expense.get('is_essential', False)
            
            breakdown[category]['amount'] += amount
            breakdown[category]['count'] += 1
            
            if is_essential:
                breakdown[category]['essential'] += amount
            else:
                breakdown[category]['discretionary'] += amount
        
        return dict(breakdown)

    async def _analyze_budget_performance(self, expenses: List[Dict], budgets: List[Dict]) -> Dict:
        """Analyze budget performance and identify overspending."""
        performance = {
            'total_budget': 0,
            'total_spent': 0,
            'budgets': [],
            'overspending_categories': [],
            'under_budget_categories': []
        }
        
        # Create budget lookup
        budget_lookup = {b['category']: b for b in budgets}
        
        # Calculate spending by category
        category_spending = self._calculate_category_breakdown(expenses)
        
        for category, budget in budget_lookup.items():
            spent = category_spending.get(category, {}).get('amount', 0)
            budget_limit = budget['limit']
            warning_threshold = budget.get('warning_threshold', 0.8)
            
            utilization = spent / budget_limit if budget_limit > 0 else 0
            
            budget_performance = {
                'category': category,
                'budgeted': budget_limit,
                'spent': spent,
                'remaining': budget_limit - spent,
                'utilization': utilization,
                'status': 'over_budget' if utilization > 1 else 'warning' if utilization > warning_threshold else 'on_track'
            }
            
            performance['budgets'].append(budget_performance)
            performance['total_budget'] += budget_limit
            performance['total_spent'] += spent
            
            if utilization > 1:
                performance['overspending_categories'].append(category)
            elif utilization < warning_threshold:
                performance['under_budget_categories'].append(category)
        
        return performance

    def _analyze_spending_patterns(self, expenses: List[Dict]) -> Dict:
        """Analyze spending patterns and behaviors."""
        patterns = {
            'essential_vs_discretionary': {'essential': 0, 'discretionary': 0},
            'weekend_vs_weekday': {'weekend': 0, 'weekday': 0},
            'large_purchases': [],
            'frequent_merchant': defaultdict(int)
        }
        
        for expense in expenses:
            amount = expense['amount']
            is_essential = expense.get('is_essential', False)
            date_str = expense['date']
            
            # Essential vs discretionary
            if is_essential:
                patterns['essential_vs_discretionary']['essential'] += amount
            else:
                patterns['essential_vs_discretionary']['discretionary'] += amount
            
            # Weekend vs weekday
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                if date.weekday() >= 5:  # Saturday or Sunday
                    patterns['weekend_vs_weekday']['weekend'] += amount
                else:
                    patterns['weekend_vs_weekday']['weekday'] += amount
            except:
                pass
            
            # Large purchases (> $200)
            if amount > 200:
                patterns['large_purchases'].append({
                    'amount': amount,
                    'description': expense['description'],
                    'date': date_str
                })
            
            # Frequent merchants (from description)
            merchant = expense['description'].split()[0] if expense['description'] else 'Unknown'
            patterns['frequent_merchant'][merchant] += 1
        
        return patterns

    def _calculate_financial_health_score(self, income: float, expenses: float, 
                                       categories: Dict, budget_analysis: Dict) -> Dict:
        """Calculate comprehensive financial health score (0-100)."""
        score_components = {
            'savings_rate': 0,
            'budget_discipline': 0,
            'spending_balance': 0,
            'essential_spending': 0
        }
        
        # Savings rate score (40% weight)
        savings_rate = (income - expenses) / income if income > 0 else 0
        if savings_rate >= 0.2:
            score_components['savings_rate'] = 40
        elif savings_rate >= 0.1:
            score_components['savings_rate'] = 30
        elif savings_rate >= 0.05:
            score_components['savings_rate'] = 20
        elif savings_rate >= 0:
            score_components['savings_rate'] = 10
        else:
            score_components['savings_rate'] = 0
        
        # Budget discipline score (30% weight)
        total_budget = budget_analysis.get('total_budget', 0)
        total_spent = budget_analysis.get('total_spent', 0)
        
        if total_budget > 0:
            budget_utilization = total_spent / total_budget
            if budget_utilization <= 0.9:
                score_components['budget_discipline'] = 30
            elif budget_utilization <= 1.0:
                score_components['budget_discipline'] = 25
            elif budget_utilization <= 1.1:
                score_components['budget_discipline'] = 15
            else:
                score_components['budget_discipline'] = 0
        else:
            score_components['budget_discipline'] = 15  # Neutral if no budget
        
        # Spending balance score (20% weight)
        total_spending = sum(cat['amount'] for cat in categories.values())
        essential_spending = sum(cat['essential'] for cat in categories.values())
        
        if total_spending > 0:
            essential_ratio = essential_spending / total_spending
            if 0.4 <= essential_ratio <= 0.6:
                score_components['spending_balance'] = 20
            elif 0.3 <= essential_ratio <= 0.7:
                score_components['spending_balance'] = 15
            else:
                score_components['spending_balance'] = 10
        else:
            score_components['spending_balance'] = 10
        
        # Essential spending score (10% weight)
        if income > 0:
            essential_ratio = essential_spending / income
            if 0.3 <= essential_ratio <= 0.5:
                score_components['essential_spending'] = 10
            elif 0.2 <= essential_ratio <= 0.6:
                score_components['essential_spending'] = 8
            else:
                score_components['essential_spending'] = 5
        else:
            score_components['essential_spending'] = 5
        
        total_score = sum(score_components.values())
        
        # Determine health status
        if total_score >= 80:
            health_status = 'excellent'
        elif total_score >= 60:
            health_status = 'good'
        elif total_score >= 40:
            health_status = 'fair'
        else:
            health_status = 'poor'
        
        return {
            'total_score': total_score,
            'health_status': health_status,
            'components': score_components,
            'grade': self._get_grade_from_score(total_score)
        }

    def _detect_overspending(self, expenses: List[Dict], budgets: List[Dict]) -> List[Dict]:
        """Detect overspending and generate alerts."""
        alerts = []
        budget_lookup = {b['category']: b for b in budgets}
        category_spending = self._calculate_category_breakdown(expenses)
        
        for category, budget in budget_lookup.items():
            spent = category_spending.get(category, {}).get('amount', 0)
            budget_limit = budget['limit']
            warning_threshold = budget.get('warning_threshold', 0.8)
            
            utilization = spent / budget_limit if budget_limit > 0 else 0
            
            if utilization > 1:
                alerts.append({
                    'type': 'over_budget',
                    'category': category,
                    'severity': 'high',
                    'message': f'You have exceeded your {category} budget by ${(spent - budget_limit):.2f}',
                    'spent': spent,
                    'budgeted': budget_limit,
                    'overspend_amount': spent - budget_limit
                })
            elif utilization > warning_threshold:
                alerts.append({
                    'type': 'budget_warning',
                    'category': category,
                    'severity': 'medium',
                    'message': f'You have used {utilization:.1%} of your {category} budget',
                    'spent': spent,
                    'budgeted': budget_limit,
                    'remaining': budget_limit - spent
                })
        
        return alerts

    def _calculate_category_statistics(self, expenses: List[Dict]) -> Dict:
        """Calculate statistical measures for each category."""
        category_data = defaultdict(list)
        
        for expense in expenses:
            category_data[expense['category']].append(expense['amount'])
        
        stats = {}
        for category, amounts in category_data.items():
            if amounts:
                stats[category] = {
                    'mean': np.mean(amounts),
                    'std': np.std(amounts),
                    'min': min(amounts),
                    'max': max(amounts),
                    'median': np.median(amounts)
                }
        
        return stats

    def _detect_frequency_anomalies(self, current_expenses: List[Dict], 
                                  historical_expenses: List[Dict]) -> List[Dict]:
        """Detect anomalies in spending frequency."""
        anomalies = []
        
        # Group by description/merchant
        current_frequency = defaultdict(int)
        historical_frequency = defaultdict(int)
        
        for expense in current_expenses:
            merchant = expense['description'].split()[0] if expense['description'] else 'Unknown'
            current_frequency[merchant] += 1
        
        for expense in historical_expenses:
            merchant = expense['description'].split()[0] if expense['description'] else 'Unknown'
            historical_frequency[merchant] += 1
        
        # Compare frequencies
        for merchant, current_count in current_frequency.items():
            historical_count = historical_frequency.get(merchant, 0)
            
            # Flag if frequency increased significantly
            if historical_count > 0 and current_count > historical_count * 2:
                anomalies.append({
                    'type': 'increased_frequency',
                    'merchant': merchant,
                    'current_frequency': current_count,
                    'historical_frequency': historical_count,
                    'severity': 'medium',
                    'message': f'Increased frequency of purchases at {merchant}'
                })
        
        return anomalies

    def _calculate_trend_metrics(self, trends: List[Dict]) -> Dict:
        """Calculate trend metrics from multiple months of data."""
        if len(trends) < 2:
            return {'trend': 'insufficient_data'}
        
        # Extract key metrics
        expenses = [t['summary']['total_expenses'] for t in trends if 'summary' in t]
        incomes = [t['summary']['total_income'] for t in trends if 'summary' in t]
        savings = [t['summary']['net_savings'] for t in trends if 'summary' in t]
        
        # Calculate trends
        expense_trend = self._calculate_linear_trend(expenses) if len(expenses) > 1 else 0
        income_trend = self._calculate_linear_trend(incomes) if len(incomes) > 1 else 0
        savings_trend = self._calculate_linear_trend(savings) if len(savings) > 1 else 0
        
        return {
            'expense_trend': 'increasing' if expense_trend > 0 else 'decreasing' if expense_trend < 0 else 'stable',
            'income_trend': 'increasing' if income_trend > 0 else 'decreasing' if income_trend < 0 else 'stable',
            'savings_trend': 'improving' if savings_trend > 0 else 'declining' if savings_trend < 0 else 'stable',
            'trend_values': {
                'expense_slope': expense_trend,
                'income_slope': income_trend,
                'savings_slope': savings_trend
            }
        }

    def _calculate_linear_trend(self, values: List[float]) -> float:
        """Calculate linear trend (slope) for a series of values."""
        if len(values) < 2:
            return 0
        
        x = list(range(len(values)))
        y = values
        
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        return slope

    def _get_grade_from_score(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

# Global expense analyzer instance
expense_analyzer = ExpenseAnalyzer()
