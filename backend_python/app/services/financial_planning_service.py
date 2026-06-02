"""
Comprehensive financial planning service.
Handles debt repayment planning, savings goals, and financial planning recommendations.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import math


class DebtRepaymentPlanner:
    """Plans debt repayment strategies."""
    
    STRATEGIES = {
        'avalanche': 'Pay off highest interest rate first (mathematical advantage)',
        'snowball': 'Pay off smallest balance first (psychological wins)',
        'interest_minimization': 'Focus on minimizing total interest paid',
        'timeline': 'Pay off by specific target date'
    }
    
    def calculate_payoff_plan(
        self,
        debts: List[Dict],
        monthly_surplus: float,
        strategy: str = 'avalanche',
        target_months: Optional[int] = None
    ) -> Dict:
        """
        Calculate debt payoff plan.
        
        Args:
            debts: List of debt dictionaries with amount, interest_rate, minimum_payment
            monthly_surplus: Monthly amount available for debt repayment
            strategy: 'avalanche', 'snowball', 'interest_minimization', or 'timeline'
            target_months: For timeline strategy, target payoff in months
            
        Returns:
            Dict with payoff plan and analysis
        """
        if not debts or monthly_surplus <= 0:
            return {'error': 'Invalid input', 'plan': []}
        
        # Prepare debt data
        working_debts = [
            {
                'id': d.get('_id', str(debts.index(d))),
                'amount': d.get('amount', 0),
                'interest_rate': d.get('interest_rate', 0) / 100 / 12,  # Monthly rate
                'min_payment': d.get('minimum_payment', d.get('amount', 0) * 0.02),
                'name': d.get('creditor', f"Debt {debts.index(d) + 1}")
            }
            for d in debts if d.get('amount', 0) > 0
        ]
        
        if not working_debts:
            return {'error': 'No valid debts to plan', 'plan': []}
        
        # Calculate required minimum payments
        total_min_payments = sum(d['min_payment'] for d in working_debts)
        extra_payment = monthly_surplus - total_min_payments
        
        if extra_payment <= 0:
            return {
                'status': 'warning',
                'message': f'Monthly surplus (${monthly_surplus:.2f}) is less than minimum debt payments (${total_min_payments:.2f})',
                'recommendation': 'Consider increasing income or reducing expenses to allocate more to debt',
                'total_debt': sum(d['amount'] for d in working_debts),
                'minimum_payments': total_min_payments,
                'surplus': extra_payment
            }
        
        # Generate payoff plan based on strategy
        if strategy == 'avalanche':
            plan = self._avalanche_strategy(working_debts, extra_payment)
        elif strategy == 'snowball':
            plan = self._snowball_strategy(working_debts, extra_payment)
        elif strategy == 'interest_minimization':
            plan = self._interest_minimization_strategy(working_debts, extra_payment)
        elif strategy == 'timeline' and target_months:
            plan = self._timeline_strategy(working_debts, monthly_surplus, target_months)
        else:
            plan = self._avalanche_strategy(working_debts, extra_payment)
        
        return plan
    
    def _avalanche_strategy(self, debts: List[Dict], extra_payment: float) -> Dict:
        """Highest interest rate first."""
        sorted_debts = sorted(debts, key=lambda x: x['interest_rate'], reverse=True)
        return self._calculate_payoff(sorted_debts, extra_payment, 'avalanche')
    
    def _snowball_strategy(self, debts: List[Dict], extra_payment: float) -> Dict:
        """Smallest balance first."""
        sorted_debts = sorted(debts, key=lambda x: x['amount'])
        return self._calculate_payoff(sorted_debts, extra_payment, 'snowball')
    
    def _interest_minimization_strategy(self, debts: List[Dict], extra_payment: float) -> Dict:
        """Minimize total interest paid."""
        # Calculate interest potential for each debt
        for debt in debts:
            debt['interest_potential'] = debt['amount'] * debt['interest_rate'] * 12
        
        sorted_debts = sorted(debts, key=lambda x: x['interest_potential'], reverse=True)
        return self._calculate_payoff(sorted_debts, extra_payment, 'interest_minimization')
    
    def _timeline_strategy(
        self,
        debts: List[Dict],
        monthly_payment: float,
        target_months: int
    ) -> Dict:
        """Achieve payoff within specific timeline."""
        total_debt = sum(d['amount'] for d in debts)
        
        # Calculate if timeline is achievable
        theoretical_min = total_debt / target_months
        if theoretical_min > monthly_payment:
            return {
                'status': 'impossible',
                'message': f'Target payoff in {target_months} months requires ${theoretical_min:.2f}/month',
                'actual_capable': monthly_payment,
                'required_payment': theoretical_min
            }
        
        # Use avalanche for optimal timeline
        sorted_debts = sorted(debts, key=lambda x: x['interest_rate'], reverse=True)
        return self._calculate_payoff(sorted_debts, monthly_payment, f'timeline_{target_months}m')
    
    def _calculate_payoff(
        self,
        sorted_debts: List[Dict],
        monthly_payment: float,
        strategy_name: str
    ) -> Dict:
        """Calculate month-by-month payoff schedule."""
        months = 0
        total_interest = 0
        schedule = []
        
        # Create working copy
        debts = [d.copy() for d in sorted_debts]
        
        while any(d['amount'] > 0 for d in debts) and months < 360:  # Max 30 years
            months += 1
            month_data = {
                'month': months,
                'date': (datetime.now() + timedelta(days=30*months)).strftime('%Y-%m'),
                'payments': [],
                'total_payment': 0,
                'total_interest': 0,
                'remaining_balance': 0
            }
            
            available = monthly_payment
            
            # Make minimum payments
            for debt in debts:
                if debt['amount'] > 0:
                    interest = debt['amount'] * debt['interest_rate']
                    total_interest += interest
                    month_data['total_interest'] += interest
                    debt['amount'] += interest
            
            # Allocate extra payment to prioritized debt
            for i, debt in enumerate(debts):
                if debt['amount'] <= 0:
                    continue
                
                payment = min(debt['amount'], available)
                debt['amount'] -= payment
                available -= payment
                
                month_data['payments'].append({
                    'debt': debt['name'],
                    'payment': payment,
                    'interest': debt['amount'] * debt['interest_rate'],
                    'remaining': max(0, debt['amount'])
                })
                
                if available <= 0:
                    break
            
            month_data['total_payment'] = monthly_payment
            month_data['remaining_balance'] = sum(d['amount'] for d in debts if d['amount'] > 0)
            schedule.append(month_data)
        
        # Calculate final metrics
        monthly_avg = monthly_payment
        payoff_months = months
        payoff_date = (datetime.now() + timedelta(days=30*months)).strftime('%Y-%m')
        
        return {
            'strategy': strategy_name,
            'status': 'success',
            'payoff_months': payoff_months,
            'payoff_date': payoff_date,
            'total_interest': total_interest,
            'monthly_payment': monthly_avg,
            'savings_potential': total_interest,  # Amount saved vs minimum payments
            'schedule': schedule[:12],  # First 12 months
            'summary': {
                'debts': sorted_debts,
                'total_debt': sum(d['amount'] for d in sorted_debts),
                'months_to_payoff': payoff_months,
                'total_interest_paid': total_interest,
                'monthly_payment': monthly_avg
            }
        }


class SavingsGoalPlanner:
    """Plans and tracks savings goals."""
    
    def calculate_goal_plan(
        self,
        goal_amount: float,
        current_savings: float,
        monthly_contribution: float,
        target_months: Optional[int] = None
    ) -> Dict:
        """
        Calculate plan to reach savings goal.
        
        Args:
            goal_amount: Target amount to save
            current_savings: Current amount saved
            monthly_contribution: Monthly amount to contribute
            target_months: Optional target months to reach goal
            
        Returns:
            Dict with savings plan
        """
        remaining = goal_amount - current_savings
        
        if remaining <= 0:
            return {
                'status': 'achieved',
                'message': 'Goal already achieved!',
                'current': current_savings,
                'goal': goal_amount,
                'progress': 100
            }
        
        if monthly_contribution <= 0:
            return {
                'status': 'impossible',
                'message': 'Monthly contribution must be positive',
                'required_contribution': 0
            }
        
        months_needed = math.ceil(remaining / monthly_contribution)
        
        plan = {
            'goal_amount': goal_amount,
            'current_savings': current_savings,
            'remaining': remaining,
            'monthly_contribution': monthly_contribution,
            'months_to_goal': months_needed,
            'target_date': (datetime.now() + timedelta(days=30*months_needed)).strftime('%Y-%m'),
            'progress_percentage': (current_savings / goal_amount * 100),
            'milestones': []
        }
        
        # Create quarterly milestones
        for quarter in range(0, months_needed + 1, 3):
            milestone_amount = min(
                current_savings + (monthly_contribution * quarter),
                goal_amount
            )
            plan['milestones'].append({
                'month': quarter,
                'date': (datetime.now() + timedelta(days=30*quarter)).strftime('%Y-%m'),
                'target_amount': milestone_amount,
                'progress': milestone_amount / goal_amount * 100
            })
        
        return plan
    
    def calculate_compound_savings(
        self,
        monthly_contribution: float,
        months: int,
        annual_interest_rate: float = 0.0
    ) -> Dict:
        """Calculate savings with compound interest."""
        total = 0
        monthly_rate = annual_interest_rate / 100 / 12
        
        contributions = []
        for month in range(1, months + 1):
            total = total * (1 + monthly_rate) + monthly_contribution
            contributions.append({
                'month': month,
                'amount': total,
                'date': (datetime.now() + timedelta(days=30*month)).strftime('%Y-%m')
            })
        
        total_contributed = monthly_contribution * months
        interest_earned = total - total_contributed
        
        return {
            'total_savings': total,
            'total_contributed': total_contributed,
            'interest_earned': interest_earned,
            'monthly_contribution': monthly_contribution,
            'annual_rate': annual_interest_rate,
            'timeline': contributions[-12:] if len(contributions) > 12 else contributions  # Last 12 months
        }


class FinancialHealthAnalyzer:
    """Analyzes overall financial health and provides recommendations."""
    
    # Thresholds for financial health
    HEALTH_BENCHMARKS = {
        'savings_rate': 0.20,  # 20% of income
        'debt_to_income': 0.36,  # 36% max
        'emergency_fund_months': 3,  # Months of expenses
        'housing_ratio': 0.30,  # 30% of income
        'debt_free_years': 10  # Target years to be debt-free
    }
    
    def analyze_financial_health(self, financial_data: Dict) -> Dict:
        """
        Comprehensive financial health analysis.
        
        Args:
            financial_data: Dict with income, expenses, debts, savings
            
        Returns:
            Dict with health score and recommendations
        """
        total_income = financial_data.get('totalIncome', 0)
        total_expenses = financial_data.get('totalExpenses', 0)
        total_debt = financial_data.get('totalDebt', 0)
        savings = financial_data.get('savings', 0)
        
        if total_income <= 0:
            return {'status': 'incomplete', 'message': 'Add income to analyze health'}
        
        health_metrics = {
            'savings_rate': (total_income - total_expenses) / total_income,
            'expense_ratio': total_expenses / total_income,
            'debt_to_income': total_debt / total_income if total_income > 0 else 1,
            'emergency_fund_ratio': savings / total_expenses if total_expenses > 0 else 0
        }
        
        # Calculate health score (0-100)
        score = 100
        recommendations = []
        
        # Savings rate analysis
        if health_metrics['savings_rate'] < self.HEALTH_BENCHMARKS['savings_rate']:
            score -= 25
            shortage = (self.HEALTH_BENCHMARKS['savings_rate'] - health_metrics['savings_rate']) * total_income
            recommendations.append({
                'category': 'savings',
                'priority': 'high',
                'title': 'Increase savings rate',
                'description': f'Target 20% of income for savings. Currently {health_metrics["savings_rate"]*100:.1f}%',
                'action': f'Increase monthly savings by ${shortage:.2f}',
                'potential_savings': shortage * 12
            })
        
        # Debt to income analysis
        if health_metrics['debt_to_income'] > self.HEALTH_BENCHMARKS['debt_to_income']:
            score -= 25
            max_debt = self.HEALTH_BENCHMARKS['debt_to_income'] * total_income
            excess = total_debt - max_debt
            recommendations.append({
                'category': 'debt',
                'priority': 'high',
                'title': 'Reduce debt levels',
                'description': f'Debt should be max 36% of income. Currently {health_metrics["debt_to_income"]*100:.1f}%',
                'action': f'Reduce debt by ${excess:.2f}',
                'timeline_months': 24
            })
        
        # Emergency fund analysis
        if health_metrics['emergency_fund_ratio'] < self.HEALTH_BENCHMARKS['emergency_fund_months']:
            score -= 15
            target_emergency = total_expenses * self.HEALTH_BENCHMARKS['emergency_fund_months']
            shortfall = target_emergency - savings
            recommendations.append({
                'category': 'emergency_fund',
                'priority': 'high',
                'title': 'Build emergency fund',
                'description': f'Need {self.HEALTH_BENCHMARKS["emergency_fund_months"]} months of expenses',
                'action': f'Save ${shortfall:.2f}',
                'target_amount': target_emergency
            })
        
        # Expense ratio analysis
        if health_metrics['expense_ratio'] > 0.95:
            score -= 10
            recommendations.append({
                'category': 'expenses',
                'priority': 'medium',
                'title': 'Reduce expenses',
                'description': 'Expenses are too close to income',
                'action': 'Reduce discretionary spending by 5-10%',
                'target_ratio': 0.85
            })
        
        # Score interpretation
        if score >= 80:
            health_status = 'excellent'
            health_message = 'Your financial health is excellent!'
        elif score >= 60:
            health_status = 'good'
            health_message = 'Your financial health is good with some areas to improve.'
        elif score >= 40:
            health_status = 'fair'
            health_message = 'Your financial health needs improvement in several areas.'
        else:
            health_status = 'poor'
            health_message = 'Your financial health requires immediate attention.'
        
        return {
            'score': score,
            'status': health_status,
            'message': health_message,
            'metrics': health_metrics,
            'recommendations': recommendations,
            'benchmarks': self.HEALTH_BENCHMARKS
        }


# Singleton instances
debt_repayment_planner = DebtRepaymentPlanner()
savings_goal_planner = SavingsGoalPlanner()
financial_health_analyzer = FinancialHealthAnalyzer()
