"""
Budget Analysis Service - Analyzes spending vs budgets and generates alerts.
Provides detailed budget tracking and financial health metrics.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class BudgetAnalysisService:
    """
    Comprehensive budget analysis service.
    Tracks spending against budgets and detects anomalies.
    """
    
    def __init__(self):
        """Initialize the budget analysis service."""
        self.warning_threshold = 0.80      # 80% - yellow warning
        self.danger_threshold = 0.95       # 95% - red danger
        self.critical_threshold = 1.0      # 100% - critical (over budget)
    
    async def analyze_monthly_budget(
        self,
        budgets: Dict[str, float],
        category_spending: Dict[str, float]
    ) -> Dict:
        """
        Analyze monthly budget performance.
        
        Args:
            budgets: Dict of {category: budget_limit}
            category_spending: Dict of {category: total_spent}
            
        Returns:
            Comprehensive budget analysis with alerts
        """
        total_budget = sum(budgets.values())
        total_spent = sum(category_spending.values())
        
        budget_status = {
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_budget - total_spent,
            'budget_percentage': (total_spent / total_budget * 100) if total_budget > 0 else 0,
            'is_over_budget': total_spent > total_budget,
            'categories': [],
            'alerts': [],
            'summary': None
        }
        
        # Analyze each category
        for category, limit in budgets.items():
            spent = category_spending.get(category, 0)
            percentage = (spent / limit * 100) if limit > 0 else 0
            remaining = limit - spent
            
            category_analysis = {
                'category': category,
                'budget_limit': limit,
                'amount_spent': spent,
                'amount_remaining': remaining,
                'percentage_used': percentage,
                'is_over_budget': spent > limit,
                'status': self._get_budget_status(percentage),
                'alert': None
            }
            
            # Generate alerts for this category
            alert = self._generate_category_alert(category, spent, limit, percentage)
            if alert:
                category_analysis['alert'] = alert
                budget_status['alerts'].append(alert)
            
            budget_status['categories'].append(category_analysis)
        
        # Generate overall budget status summary
        budget_status['summary'] = self._generate_budget_summary(budget_status)
        
        return budget_status
    
    def _get_budget_status(self, percentage: float) -> str:
        """Get status label for a budget percentage."""
        if percentage < self.warning_threshold * 100:
            return 'healthy'
        elif percentage < self.danger_threshold * 100:
            return 'warning'
        elif percentage < self.critical_threshold * 100:
            return 'danger'
        else:
            return 'critical'
    
    def _generate_category_alert(self, category: str, spent: float, limit: float, percentage: float) -> Optional[Dict]:
        """Generate an alert if a budget threshold is exceeded."""
        if percentage < self.warning_threshold * 100:
            return None
        
        remaining = limit - spent
        alert_level = AlertLevel.INFO
        message = ""
        
        if percentage >= self.critical_threshold * 100:
            alert_level = AlertLevel.CRITICAL
            excess = spent - limit
            message = (
                f'⛔ BUDGET EXCEEDED: {category} budget of ${limit:.2f} exceeded by ${excess:.2f} '
                f'({percentage:.1f}% used). Immediate action required.'
            )
        elif percentage >= self.danger_threshold * 100:
            alert_level = AlertLevel.DANGER
            message = (
                f'🔴 CRITICAL WARNING: {category} at {percentage:.1f}% of budget. '
                f'Only ${remaining:.2f} remaining. Reduce spending immediately.'
            )
        elif percentage >= self.warning_threshold * 100:
            alert_level = AlertLevel.WARNING
            message = (
                f'🟡 BUDGET WARNING: {category} at {percentage:.1f}% of budget. '
                f'${remaining:.2f} remaining. Be cautious with further spending.'
            )
        
        return {
            'category': category,
            'level': alert_level,
            'message': message,
            'percentage_used': percentage,
            'amount_remaining': remaining,
            'amount_spent': spent,
            'budget_limit': limit
        }
    
    def _generate_budget_summary(self, budget_status: Dict) -> Dict:
        """Generate overall budget status summary."""
        total_budget = budget_status['total_budget']
        total_spent = budget_status['total_spent']
        total_remaining = budget_status['total_remaining']
        budget_percentage = budget_status['budget_percentage']
        
        # Count categories by status
        status_counts = {}
        for category_status in budget_status['categories']:
            status = category_status['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Determine overall health
        alerts = budget_status['alerts']
        critical_count = len([a for a in alerts if a['level'] == AlertLevel.CRITICAL])
        danger_count = len([a for a in alerts if a['level'] == AlertLevel.DANGER])
        warning_count = len([a for a in alerts if a['level'] == AlertLevel.WARNING])
        
        if critical_count > 0:
            overall_status = 'critical'
            health_message = f'⛔ {critical_count} category(ies) over budget. Immediate action required.'
        elif danger_count > 0:
            overall_status = 'danger'
            health_message = f'🔴 {danger_count} category(ies) critically close to limit.'
        elif warning_count > 0:
            overall_status = 'warning'
            health_message = f'🟡 {warning_count} category(ies) approaching limit.'
        else:
            overall_status = 'healthy'
            health_message = f'✅ All budgets on track. Spending at {budget_percentage:.1f}%.'
        
        # Calculate savings potential
        saving_potential = 0
        for category_status in budget_status['categories']:
            if category_status['is_over_budget']:
                saving_potential += category_status['amount_spent'] - category_status['budget_limit']
        
        return {
            'overall_status': overall_status,
            'health_message': health_message,
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'budget_percentage': budget_percentage,
            'is_over_budget': budget_status['is_over_budget'],
            'status_breakdown': status_counts,
            'alert_counts': {
                'critical': critical_count,
                'danger': danger_count,
                'warning': warning_count
            },
            'saving_potential': saving_potential,
            'recommendation': self._get_budget_recommendation(overall_status, budget_percentage)
        }
    
    def _get_budget_recommendation(self, status: str, percentage: float) -> str:
        """Get a recommendation message based on budget status."""
        if status == 'critical':
            return (
                'Your spending has exceeded your planned budget. Review all expenses immediately, '
                'identify non-essential spending, and take action to reduce costs this month.'
            )
        elif status == 'danger':
            return (
                'You are spending at an unsustainable rate. Consider deferring non-essential purchases '
                'and focusing on essential expenses for the remainder of the month.'
            )
        elif status == 'warning':
            return (
                'You are on track to exceed some budget categories. Monitor spending closely and '
                'be cautious with discretionary expenses.'
            )
        else:
            return (
                f'Great job! You are spending responsibly at {percentage:.1f}% of budget. '
                'Continue monitoring and look for opportunities to save more.'
            )
    
    async def detect_spending_anomalies(
        self,
        current_month_spending: Dict[str, float],
        historical_spending: List[Dict[str, float]]
    ) -> List[Dict]:
        """
        Detect unusual spending patterns compared to historical data.
        
        Args:
            current_month_spending: Current month {category: amount}
            historical_spending: List of previous months' {category: amount}
            
        Returns:
            List of anomalies detected
        """
        anomalies = []
        
        if not historical_spending or len(historical_spending) == 0:
            return anomalies
        
        # Calculate average spending per category
        category_averages = {}
        for category in current_month_spending.keys():
            amounts = [m.get(category, 0) for m in historical_spending]
            if amounts:
                average = sum(amounts) / len(amounts)
                category_averages[category] = average
        
        # Detect anomalies (spending > 150% of average or < 50% of average)
        for category, current_amount in current_month_spending.items():
            average = category_averages.get(category, current_amount)
            
            if average > 0:
                ratio = current_amount / average
                
                if ratio > 1.5:  # Spending 50% more than usual
                    anomalies.append({
                        'category': category,
                        'type': 'increase',
                        'current': current_amount,
                        'average': average,
                        'change_percentage': (ratio - 1) * 100,
                        'message': (
                            f'{category} spending is {(ratio-1)*100:.0f}% higher than usual. '
                            f'Current: ${current_amount:.2f}, Average: ${average:.2f}.'
                        ),
                        'severity': 'warning' if ratio < 2.0 else 'danger'
                    })
                elif ratio < 0.5:  # Spending 50% less than usual
                    anomalies.append({
                        'category': category,
                        'type': 'decrease',
                        'current': current_amount,
                        'average': average,
                        'change_percentage': (1 - ratio) * 100,
                        'message': (
                            f'{category} spending is {(1-ratio)*100:.0f}% lower than usual. '
                            f'Current: ${current_amount:.2f}, Average: ${average:.2f}.'
                        ),
                        'severity': 'info'
                    })
        
        return anomalies
    
    async def get_spending_trends(
        self,
        monthly_spending: List[Tuple[str, Dict[str, float]]]
    ) -> Dict:
        """
        Analyze spending trends over time.
        
        Args:
            monthly_spending: List of (month, {category: amount})
            
        Returns:
            Trend analysis
        """
        if not monthly_spending or len(monthly_spending) < 2:
            return {'trend': 'insufficient_data', 'message': 'Need at least 2 months of data'}
        
        trends = {}
        
        # Analyze each category
        categories = set()
        for month, spending in monthly_spending:
            categories.update(spending.keys())
        
        for category in categories:
            amounts = []
            months = []
            
            for month, spending in monthly_spending:
                amounts.append(spending.get(category, 0))
                months.append(month)
            
            # Calculate trend
            if len(amounts) >= 2:
                first_avg = sum(amounts[:len(amounts)//2]) / (len(amounts)//2)
                last_avg = sum(amounts[len(amounts)//2:]) / (len(amounts) - len(amounts)//2)
                
                trend_direction = 'stable'
                trend_percentage = 0
                
                if first_avg > 0:
                    trend_percentage = ((last_avg - first_avg) / first_avg) * 100
                    
                    if trend_percentage > 10:
                        trend_direction = 'increasing'
                    elif trend_percentage < -10:
                        trend_direction = 'decreasing'
                
                trends[category] = {
                    'direction': trend_direction,
                    'change_percentage': trend_percentage,
                    'current': amounts[-1],
                    'previous': amounts[-2] if len(amounts) >= 2 else None,
                    'average': sum(amounts) / len(amounts),
                    'min': min(amounts),
                    'max': max(amounts)
                }
        
        return {
            'trend': 'analyzed',
            'period': f'{monthly_spending[0][0]} to {monthly_spending[-1][0]}',
            'categories': trends,
            'overall_trend': self._calculate_overall_trend(trends)
        }
    
    def _calculate_overall_trend(self, trends: Dict) -> str:
        """Calculate overall spending trend."""
        if not trends:
            return 'stable'
        
        increasing = len([t for t in trends.values() if t['direction'] == 'increasing'])
        decreasing = len([t for t in trends.values() if t['direction'] == 'decreasing'])
        
        if increasing > decreasing * 1.5:
            return 'increasing'
        elif decreasing > increasing * 1.5:
            return 'decreasing'
        else:
            return 'stable'


# Singleton instance
budget_analysis_service = BudgetAnalysisService()
