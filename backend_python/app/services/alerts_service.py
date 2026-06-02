"""
Alerts and notifications service.
Generates, stores, and manages financial alerts and notifications.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import json


class AlertType(str, Enum):
    """Types of alerts."""
    BUDGET_WARNING = "budget_warning"
    BUDGET_CRITICAL = "budget_critical"
    NEGATIVE_BALANCE = "negative_balance"
    OVERSPENDING = "overspending"
    SAVINGS_GOAL = "savings_goal"
    DEBT_WARNING = "debt_warning"
    LOW_EMERGENCY_FUND = "low_emergency_fund"
    SPENDING_ANOMALY = "spending_anomaly"
    INCOME_BELOW_TARGET = "income_below_target"
    FINANCIAL_MILESTONE = "financial_milestone"


class AlertSeverity(str, Enum):
    """Severity levels for alerts."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertsManager:
    """Manages financial alerts and notifications."""
    
    # Alert templates with default thresholds
    ALERT_RULES = {
        'budget_80': {
            'type': AlertType.BUDGET_WARNING,
            'severity': AlertSeverity.WARNING,
            'threshold': 0.80,
            'message': '{category} budget is at 80%',
            'template': 'You\'ve used 80% of your {category} budget for {month}'
        },
        'budget_100': {
            'type': AlertType.BUDGET_CRITICAL,
            'severity': AlertSeverity.CRITICAL,
            'threshold': 1.0,
            'message': '{category} budget exceeded',
            'template': 'You\'ve exceeded your {category} budget by ${amount:.2f}'
        },
        'negative_balance': {
            'type': AlertType.NEGATIVE_BALANCE,
            'severity': AlertSeverity.CRITICAL,
            'message': 'Monthly balance is negative',
            'template': 'Your expenses exceed income by ${amount:.2f} this month'
        },
        'high_spending': {
            'type': AlertType.OVERSPENDING,
            'severity': AlertSeverity.WARNING,
            'threshold': 0.30,
            'message': '{category} spending is high',
            'template': '{category} is {percentage:.1f}% of total spending'
        },
        'low_emergency': {
            'type': AlertType.LOW_EMERGENCY_FUND,
            'severity': AlertSeverity.WARNING,
            'threshold': 1,  # 1 month of expenses
            'message': 'Emergency fund is low',
            'template': 'Build emergency fund to {months} months of expenses'
        }
    }
    
    def __init__(self):
        """Initialize alerts manager."""
        self.alert_history: List[Dict] = []
    
    def generate_alerts(
        self,
        user_id: str,
        financial_data: Dict,
        budget_data: Dict
    ) -> List[Dict]:
        """
        Generate alerts based on financial data.
        
        Args:
            user_id: User ID
            financial_data: Dict with totalIncome, totalExpenses, categoryBreakdown
            budget_data: Dict with budget limits and current spending
            
        Returns:
            List of alerts
        """
        alerts = []
        
        total_income = financial_data.get('totalIncome', 0)
        total_expenses = financial_data.get('totalExpenses', 0)
        balance = total_income - total_expenses
        category_breakdown = financial_data.get('categoryBreakdown', {})
        
        # 1. Negative balance alert
        if balance < 0:
            alerts.append(self._create_alert(
                AlertType.NEGATIVE_BALANCE,
                AlertSeverity.CRITICAL,
                f'Monthly balance is negative',
                f'Your expenses (${total_expenses:.2f}) exceed income (${total_income:.2f}) by ${abs(balance):.2f}',
                {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'deficit': abs(balance)
                }
            ))
        
        # 2. Budget alerts
        for budget in budget_data.get('budgets', []):
            category = budget.get('category')
            limit = budget.get('limit', 0)
            spent = category_breakdown.get(category, 0)
            percentage = (spent / limit * 100) if limit > 0 else 0
            
            # Critical budget exceeded
            if percentage >= 100:
                alerts.append(self._create_alert(
                    AlertType.BUDGET_CRITICAL,
                    AlertSeverity.CRITICAL,
                    f'{category} budget exceeded',
                    f'You spent ${spent:.2f} of ${limit:.2f} budget (${spent - limit:.2f} over)',
                    {
                        'category': category,
                        'spent': spent,
                        'limit': limit,
                        'overage': spent - limit,
                        'percentage': percentage
                    }
                ))
            
            # Warning budget near limit (80%)
            elif percentage >= 80:
                alerts.append(self._create_alert(
                    AlertType.BUDGET_WARNING,
                    AlertSeverity.WARNING,
                    f'{category} budget is at {percentage:.0f}%',
                    f'You\'ve used ${spent:.2f} of your ${limit:.2f} {category} budget',
                    {
                        'category': category,
                        'spent': spent,
                        'limit': limit,
                        'remaining': limit - spent,
                        'percentage': percentage
                    }
                ))
        
        # 3. High category spending
        for category, amount in category_breakdown.items():
            percentage_of_total = (amount / total_expenses * 100) if total_expenses > 0 else 0
            
            # Flag if category is over 30% of total spending
            if percentage_of_total > 30 and category not in ['Housing', 'Debt']:
                alerts.append(self._create_alert(
                    AlertType.OVERSPENDING,
                    AlertSeverity.WARNING,
                    f'{category} spending is high',
                    f'{category} accounts for {percentage_of_total:.1f}% of total spending (${amount:.2f})',
                    {
                        'category': category,
                        'amount': amount,
                        'percentage_of_total': percentage_of_total
                    }
                ))
        
        # 4. Spending anomalies (month-over-month changes)
        if len(self.alert_history) > 30:
            alerts.extend(self._detect_spending_anomalies(
                user_id,
                financial_data
            ))
        
        return alerts
    
    def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: Dict
    ) -> Dict:
        """Create an alert dictionary."""
        alert = {
            'type': alert_type.value,
            'severity': severity.value,
            'title': title,
            'message': message,
            'data': data,
            'created_at': datetime.now().isoformat(),
            'id': self._generate_alert_id()
        }
        
        # Store in history
        self.alert_history.append(alert)
        
        return alert
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        return f"alert_{int(datetime.now().timestamp() * 1000)}"
    
    def _detect_spending_anomalies(
        self,
        user_id: str,
        current_data: Dict
    ) -> List[Dict]:
        """Detect unusual spending patterns."""
        alerts = []
        
        # This would require historical data comparison
        # For now, returning empty list
        # In production, compare with previous months
        
        return alerts
    
    def get_alert_summary(self, alerts: List[Dict]) -> Dict:
        """Get summary of alerts by severity."""
        summary = {
            'total': len(alerts),
            'critical': len([a for a in alerts if a['severity'] == AlertSeverity.CRITICAL.value]),
            'warning': len([a for a in alerts if a['severity'] == AlertSeverity.WARNING.value]),
            'info': len([a for a in alerts if a['severity'] == AlertSeverity.INFO.value]),
            'alerts': alerts
        }
        return summary
    
    def prioritize_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Sort alerts by severity and importance."""
        severity_order = {
            AlertSeverity.CRITICAL.value: 0,
            AlertSeverity.WARNING.value: 1,
            AlertSeverity.INFO.value: 2
        }
        
        return sorted(
            alerts,
            key=lambda x: severity_order.get(x.get('severity'), 3)
        )
    
    def dismiss_alert(self, alert_id: str):
        """Mark alert as dismissed."""
        for alert in self.alert_history:
            if alert.get('id') == alert_id:
                alert['dismissed'] = True
                alert['dismissed_at'] = datetime.now().isoformat()
                break
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all non-dismissed alerts."""
        return [a for a in self.alert_history if not a.get('dismissed', False)]
    
    def clear_old_alerts(self, days: int = 30):
        """Remove alerts older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.alert_history = [
            a for a in self.alert_history
            if datetime.fromisoformat(a['created_at']) > cutoff_date
        ]


class NotificationPreferences:
    """Manage user notification preferences."""
    
    DEFAULT_PREFERENCES = {
        'email_alerts': {
            'budget_critical': True,
            'negative_balance': True,
            'savings_milestone': True
        },
        'push_alerts': {
            'budget_warning': True,
            'budget_critical': True,
            'spending_anomaly': False
        },
        'alert_frequency': {
            'daily': True,
            'weekly': True,
            'monthly': True
        },
        'quiet_hours': {
            'enabled': False,
            'start': '22:00',
            'end': '08:00'
        }
    }
    
    def __init__(self, user_preferences: Optional[Dict] = None):
        """Initialize notification preferences."""
        self.preferences = user_preferences or self.DEFAULT_PREFERENCES.copy()
    
    def should_send_notification(
        self,
        alert_type: AlertType,
        method: str = 'email'
    ) -> bool:
        """Check if notification should be sent."""
        alerts_config = self.preferences.get(f'{method}_alerts', {})
        return alerts_config.get(alert_type.value, False)


# Singleton instance
alerts_manager = AlertsManager()
