"""
Comprehensive testing and evaluation framework for the personal finance advisor.
Tests system accuracy, recommendation effectiveness, and user satisfaction metrics.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.data_handling import data_handler
from app.services.expense_analysis import expense_analyzer
from app.services.decision_engine import decision_engine
from app.services.recommendation_engine import recommendation_engine
import json
import asyncio
import statistics

class TestingFramework:
    """Comprehensive testing and evaluation system."""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.get_default_database()
        
        # Test scenarios and expected outcomes
        self.test_scenarios = {
            'high_debt_user': {
                'description': 'User with high debt-to-income ratio',
                'expected_recommendations': ['debt', 'budget', 'savings'],
                'expected_priority': 'high'
            },
            'low_savings_user': {
                'description': 'User with insufficient savings rate',
                'expected_recommendations': ['savings', 'emergency_fund'],
                'expected_priority': 'high'
            },
            'budget_violator': {
                'description': 'User who consistently exceeds budget',
                'expected_recommendations': ['budget'],
                'expected_priority': 'medium'
            },
            'healthy_finances': {
                'description': 'User with good financial health',
                'expected_recommendations': ['investment', 'optimization'],
                'expected_priority': 'low'
            }
        }
        
        # Evaluation metrics
        self.evaluation_metrics = {
            'recommendation_accuracy': 0.0,
            'recommendation_relevance': 0.0,
            'system_performance': 0.0,
            'user_satisfaction': 0.0,
            'financial_improvement': 0.0
        }

    async def run_comprehensive_tests(self) -> Dict:
        """Run comprehensive test suite."""
        test_results = {
            'test_date': datetime.now().isoformat(),
            'test_scenarios': {},
            'performance_tests': {},
            'accuracy_tests': {},
            'user_simulation_tests': {},
            'overall_metrics': {}
        }
        
        # Test each scenario
        for scenario_name, scenario_config in self.test_scenarios.items():
            scenario_result = await self._test_scenario(scenario_name, scenario_config)
            test_results['test_scenarios'][scenario_name] = scenario_result
        
        # Performance tests
        test_results['performance_tests'] = await self._run_performance_tests()
        
        # Accuracy tests
        test_results['accuracy_tests'] = await self._run_accuracy_tests()
        
        # User simulation tests
        test_results['user_simulation_tests'] = await self._run_user_simulation_tests()
        
        # Calculate overall metrics
        test_results['overall_metrics'] = self._calculate_overall_metrics(test_results)
        
        # Save test results
        await self._save_test_results(test_results)
        
        return test_results

    async def _test_scenario(self, scenario_name: str, scenario_config: Dict) -> Dict:
        """Test a specific user scenario."""
        # Create test user
        test_user_id = f"test_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate scenario-specific test data
        await self._generate_scenario_data(test_user_id, scenario_name)
        
        # Generate recommendations
        recommendations = await decision_engine.generate_recommendations(test_user_id)
        
        # Evaluate recommendations against expectations
        evaluation = await self._evaluate_recommendations(
            recommendations, 
            scenario_config['expected_recommendations'],
            scenario_config['expected_priority']
        )
        
        # Clean up test data
        await self._cleanup_test_data(test_user_id)
        
        return {
            'scenario': scenario_name,
            'description': scenario_config['description'],
            'recommendations_generated': len(recommendations),
            'evaluation': evaluation,
            'test_passed': evaluation['accuracy_score'] >= 0.7
        }

    async def _generate_scenario_data(self, user_id: str, scenario_name: str):
        """Generate test data for a specific scenario."""
        if scenario_name == 'high_debt_user':
            await self._generate_high_debt_data(user_id)
        elif scenario_name == 'low_savings_user':
            await self._generate_low_savings_data(user_id)
        elif scenario_name == 'budget_violator':
            await self._generate_budget_violator_data(user_id)
        elif scenario_name == 'healthy_finances':
            await self._generate_healthy_finances_data(user_id)

    async def _generate_high_debt_data(self, user_id: str):
        """Generate data for user with high debt-to-income ratio."""
        # Low income
        await self.db["incomes"].insert_many([
            {
                "user_id": user_id,
                "amount": 3000,
                "source": "Salary",
                "date": "2026-01-01",
                "frequency": "monthly",
                "is_recurring": True
            }
        ])
        
        # High debt
        await self.db["debts"].insert_many([
            {
                "user_id": user_id,
                "amount": 15000,
                "creditor": "Credit Card Company",
                "date": "2026-01-01",
                "interest_rate": 22.9,
                "minimum_payment": 450,
                "debt_type": "credit_card"
            },
            {
                "user_id": user_id,
                "amount": 8000,
                "creditor": "Auto Loan",
                "date": "2026-01-01",
                "interest_rate": 6.5,
                "minimum_payment": 250,
                "debt_type": "loan"
            }
        ])
        
        # Normal expenses
        await data_handler.generate_sample_data(user_id, 3)

    async def _generate_low_savings_data(self, user_id: str):
        """Generate data for user with low savings rate."""
        # Good income but high spending
        await self.db["incomes"].insert_many([
            {
                "user_id": user_id,
                "amount": 6000,
                "source": "Salary",
                "date": "2026-01-01",
                "frequency": "monthly",
                "is_recurring": True
            }
        ])
        
        # High expenses (95% of income)
        await self.db["expenses"].insert_many([
            {
                "user_id": user_id,
                "amount": 2500,
                "category": "Housing",
                "description": "Rent",
                "date": "2026-01-01",
                "is_essential": True
            },
            {
                "user_id": user_id,
                "amount": 800,
                "category": "Food",
                "description": "Groceries and dining",
                "date": "2026-01-05",
                "is_essential": True
            },
            {
                "user_id": user_id,
                "amount": 600,
                "category": "Transportation",
                "description": "Car payment and gas",
                "date": "2026-01-10",
                "is_essential": True
            },
            {
                "user_id": user_id,
                "amount": 1800,
                "category": "Shopping",
                "description": "Retail purchases",
                "date": "2026-01-15",
                "is_essential": False
            }
        ])

    async def _generate_budget_violator_data(self, user_id: str):
        """Generate data for user who consistently exceeds budget."""
        # Normal income
        await self.db["incomes"].insert_many([
            {
                "user_id": user_id,
                "amount": 4500,
                "source": "Salary",
                "date": "2026-01-01",
                "frequency": "monthly",
                "is_recurring": True
            }
        ])
        
        # Set low budgets
        await self.db["budgets"].insert_many([
            {
                "user_id": user_id,
                "category": "Food",
                "limit": 300,
                "month": "2026-01",
                "warning_threshold": 0.8
            },
            {
                "user_id": user_id,
                "category": "Entertainment",
                "limit": 100,
                "month": "2026-01",
                "warning_threshold": 0.8
            }
        ])
        
        # Exceed budgets with high spending
        await self.db["expenses"].insert_many([
            {
                "user_id": user_id,
                "amount": 500,
                "category": "Food",
                "description": "Restaurants and groceries",
                "date": "2026-01-15",
                "is_essential": True
            },
            {
                "user_id": user_id,
                "amount": 200,
                "category": "Entertainment",
                "description": "Movies and subscriptions",
                "date": "2026-01-20",
                "is_essential": False
            }
        ])

    async def _generate_healthy_finances_data(self, user_id: str):
        """Generate data for user with good financial health."""
        # Good income
        await self.db["incomes"].insert_many([
            {
                "user_id": user_id,
                "amount": 7000,
                "source": "Salary",
                "date": "2026-01-01",
                "frequency": "monthly",
                "is_recurring": True
            },
            {
                "user_id": user_id,
                "amount": 500,
                "source": "Freelance",
                "date": "2026-01-15",
                "frequency": "monthly",
                "is_recurring": True
            }
        ])
        
        # Reasonable expenses (60% of income)
        await data_handler.generate_sample_data(user_id, 3)
        
        # Good savings (emergency fund)
        await self.db["financial_goals"].insert_one({
            "user_id": user_id,
            "name": "Emergency Fund",
            "target_amount": 21000,  # 3 months expenses
            "current_amount": 15000,
            "target_date": "2026-06-01",
            "priority": "high",
            "category": "savings"
        })

    async def _evaluate_recommendations(self, recommendations: List[Dict], 
                                      expected_types: List[str], 
                                      expected_priority: str) -> Dict:
        """Evaluate recommendations against expected outcomes."""
        if not recommendations:
            return {
                'accuracy_score': 0.0,
                'relevance_score': 0.0,
                'priority_match': False,
                'type_matches': 0,
                'expected_types': expected_types,
                'actual_types': []
            }
        
        # Check type matches
        actual_types = [rec['type'] for rec in recommendations]
        type_matches = len(set(actual_types) & set(expected_types))
        type_accuracy = type_matches / len(expected_types) if expected_types else 0
        
        # Check priority matches
        high_priority_count = len([r for r in recommendations if r['priority'] == 'high'])
        priority_match = (expected_priority == 'high' and high_priority_count > 0) or \
                        (expected_priority != 'high' and high_priority_count == 0)
        
        # Calculate relevance based on confidence scores
        avg_confidence = statistics.mean([r.get('confidence_score', 0) for r in recommendations])
        
        return {
            'accuracy_score': type_accuracy,
            'relevance_score': avg_confidence,
            'priority_match': priority_match,
            'type_matches': type_matches,
            'expected_types': expected_types,
            'actual_types': actual_types,
            'recommendation_count': len(recommendations)
        }

    async def _run_performance_tests(self) -> Dict:
        """Test system performance metrics."""
        performance_results = {}
        
        # Test recommendation generation speed
        start_time = datetime.now()
        test_user_id = f"perf_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate test data
        await data_handler.generate_sample_data(test_user_id, 12)  # 12 months
        
        # Time recommendation generation
        rec_start = datetime.now()
        recommendations = await decision_engine.generate_recommendations(test_user_id)
        rec_end = datetime.now()
        
        # Time comprehensive analysis
        analysis_start = datetime.now()
        comprehensive = await recommendation_engine.generate_comprehensive_recommendations(test_user_id)
        analysis_end = datetime.now()
        
        # Calculate performance metrics
        rec_time = (rec_end - rec_start).total_seconds()
        analysis_time = (analysis_end - analysis_start).total_seconds()
        
        performance_results = {
            'recommendation_generation_time': rec_time,
            'comprehensive_analysis_time': analysis_time,
            'recommendations_generated': len(recommendations),
            'comprehensive_recommendations': len(comprehensive.get('recommendations', [])),
            'performance_rating': 'excellent' if rec_time < 1.0 else 'good' if rec_time < 2.0 else 'needs_improvement'
        }
        
        # Clean up
        await self._cleanup_test_data(test_user_id)
        
        return performance_results

    async def _run_accuracy_tests(self) -> Dict:
        """Test accuracy of financial analysis and recommendations."""
        accuracy_results = {}
        
        # Test expense classification accuracy
        classification_accuracy = await self._test_expense_classification()
        accuracy_results['expense_classification'] = classification_accuracy
        
        # Test budget analysis accuracy
        budget_analysis_accuracy = await self._test_budget_analysis()
        accuracy_results['budget_analysis'] = budget_analysis_accuracy
        
        # Test financial health scoring
        health_score_accuracy = await self._test_financial_health_scoring()
        accuracy_results['financial_health_scoring'] = health_score_accuracy
        
        return accuracy_results

    async def _test_expense_classification(self) -> Dict:
        """Test expense classification accuracy."""
        test_cases = [
            {'description': 'Monthly Rent Payment', 'expected_category': 'Housing'},
            {'description': 'Grocery Store Shopping', 'expected_category': 'Food'},
            {'description': 'Gas Station Fill Up', 'expected_category': 'Transportation'},
            {'description': 'Netflix Subscription', 'expected_category': 'Entertainment'},
            {'description': 'Electric Bill', 'expected_category': 'Utilities'}
        ]
        
        correct_classifications = 0
        
        for test_case in test_cases:
            classified_category = await data_handler.classify_expense(
                test_case['description'], 
                100.0
            )
            if classified_category == test_case['expected_category']:
                correct_classifications += 1
        
        accuracy = correct_classifications / len(test_cases)
        
        return {
            'test_cases': len(test_cases),
            'correct_classifications': correct_classifications,
            'accuracy_score': accuracy,
            'accuracy_rating': 'excellent' if accuracy >= 0.8 else 'good' if accuracy >= 0.6 else 'needs_improvement'
        }

    async def _test_budget_analysis(self) -> Dict:
        """Test budget analysis accuracy."""
        test_user_id = f"budget_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create test data with known budget violations
        await self.db["budgets"].insert_one({
            "user_id": test_user_id,
            "category": "Food",
            "limit": 500,
            "month": "2026-01",
            "warning_threshold": 0.8
        })
        
        # Create expenses that exceed budget
        await self.db["expenses"].insert_many([
            {
                "user_id": test_user_id,
                "amount": 300,
                "category": "Food",
                "description": "Groceries",
                "date": "2026-01-10",
                "is_essential": True
            },
            {
                "user_id": test_user_id,
                "amount": 250,
                "category": "Food",
                "description": "Restaurant",
                "date": "2026-01-15",
                "is_essential": False
            }
        ])
        
        # Test analysis
        analysis = await expense_analyzer.analyze_monthly_expenses(test_user_id, "2026-01")
        
        # Check if overspending was detected
        overspending_detected = len(analysis.get('overspending_alerts', [])) > 0
        budget_performance = analysis.get('budget_analysis', {})
        
        accuracy = 1.0 if overspending_detected else 0.0
        
        # Clean up
        await self._cleanup_test_data(test_user_id)
        
        return {
            'overspending_detected': overspending_detected,
            'budget_performance': budget_performance,
            'accuracy_score': accuracy,
            'test_passed': overspending_detected
        }

    async def _test_financial_health_scoring(self) -> Dict:
        """Test financial health scoring accuracy."""
        test_cases = [
            {
                'income': 5000,
                'expenses': 3000,
                'expected_health_range': 'good'  # 40% savings rate
            },
            {
                'income': 4000,
                'expenses': 3800,
                'expected_health_range': 'poor'  # 5% savings rate
            },
            {
                'income': 6000,
                'expenses': 3000,
                'expected_health_range': 'excellent'  # 50% savings rate
            }
        ]
        
        correct_scores = 0
        
        for i, test_case in enumerate(test_cases):
            test_user_id = f"health_test_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create test data
            await self.db["incomes"].insert_one({
                "user_id": test_user_id,
                "amount": test_case['income'],
                "source": "Salary",
                "date": "2026-01-01",
                "frequency": "monthly",
                "is_recurring": True
            })
            
            await self.db["expenses"].insert_one({
                "user_id": test_user_id,
                "amount": test_case['expenses'],
                "category": "Total",
                "description": "Monthly expenses",
                "date": "2026-01-15",
                "is_essential": True
            })
            
            # Test health scoring
            analysis = await expense_analyzer.analyze_monthly_expenses(test_user_id, "2026-01")
            health_status = analysis.get('financial_health_score', {}).get('health_status', '')
            
            # Check if health status is in expected range
            if test_case['expected_health_range'] in health_status.lower():
                correct_scores += 1
            
            # Clean up
            await self._cleanup_test_data(test_user_id)
        
        accuracy = correct_scores / len(test_cases)
        
        return {
            'test_cases': len(test_cases),
            'correct_scores': correct_scores,
            'accuracy_score': accuracy,
            'accuracy_rating': 'excellent' if accuracy >= 0.8 else 'good' if accuracy >= 0.6 else 'needs_improvement'
        }

    async def _run_user_simulation_tests(self) -> Dict:
        """Simulate user interactions and test system responses."""
        simulation_results = {}
        
        # Test user journey from registration to recommendation implementation
        journey_results = await self._simulate_user_journey()
        simulation_results['user_journey'] = journey_results
        
        # Test recommendation implementation tracking
        implementation_results = await self._simulate_recommendation_implementation()
        simulation_results['recommendation_implementation'] = implementation_results
        
        return simulation_results

    async def _simulate_user_journey(self) -> Dict:
        """Simulate complete user journey."""
        test_user_id = f"journey_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        journey_steps = []
        
        # Step 1: User registers and adds initial data
        await data_handler.generate_sample_data(test_user_id, 3)
        journey_steps.append({
            'step': 'data_import',
            'status': 'completed',
            'data_points': 12  # 3 months of sample data
        })
        
        # Step 2: User requests analysis
        analysis = await expense_analyzer.analyze_monthly_expenses(test_user_id, "2026-01")
        journey_steps.append({
            'step': 'initial_analysis',
            'status': 'completed',
            'health_score': analysis.get('financial_health_score', {}).get('total_score', 0)
        })
        
        # Step 3: User gets recommendations
        recommendations = await decision_engine.generate_recommendations(test_user_id)
        journey_steps.append({
            'step': 'recommendations_generated',
            'status': 'completed',
            'recommendation_count': len(recommendations)
        })
        
        # Step 4: User implements recommendations (simulation)
        implemented_count = len(recommendations) // 2  # Simulate implementing half
        journey_steps.append({
            'step': 'recommendation_implementation',
            'status': 'partially_completed',
            'implemented_count': implemented_count,
            'total_count': len(recommendations)
        })
        
        # Clean up
        await self._cleanup_test_data(test_user_id)
        
        return {
            'journey_completed': True,
            'steps_completed': len(journey_steps),
            'total_steps': 4,
            'journey_steps': journey_steps
        }

    async def _simulate_recommendation_implementation(self) -> Dict:
        """Simulate tracking recommendation implementation and impact."""
        test_user_id = f"implementation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create initial data
        await data_handler.generate_sample_data(test_user_id, 2)
        
        # Get initial recommendations
        initial_recommendations = await decision_engine.generate_recommendations(test_user_id)
        
        # Simulate implementing savings recommendation
        # Add new income source (side hustle)
        await self.db["incomes"].insert_one({
            "user_id": test_user_id,
            "amount": 500,
            "source": "Freelance Work",
            "date": "2026-03-01",
            "frequency": "monthly",
            "is_recurring": True
        })
        
        # Reduce expenses (implement budget cuts)
        await self.db["expenses"].insert_many([
            {
                "user_id": test_user_id,
                "amount": 100,  # Reduced from typical amounts
                "category": "Entertainment",
                "description": "Reduced entertainment spending",
                "date": "2026-03-15",
                "is_essential": False
            }
        ])
        
        # Get new recommendations after implementation
        new_recommendations = await decision_engine.generate_recommendations(test_user_id)
        
        # Calculate improvement
        initial_analysis = await expense_analyzer.analyze_monthly_expenses(test_user_id, "2026-02")
        new_analysis = await expense_analyzer.analyze_monthly_expenses(test_user_id, "2026-03")
        
        initial_health_score = initial_analysis.get('financial_health_score', {}).get('total_score', 0)
        new_health_score = new_analysis.get('financial_health_score', {}).get('total_score', 0)
        
        improvement = new_health_score - initial_health_score
        
        # Clean up
        await self._cleanup_test_data(test_user_id)
        
        return {
            'initial_recommendations': len(initial_recommendations),
            'new_recommendations': len(new_recommendations),
            'initial_health_score': initial_health_score,
            'new_health_score': new_health_score,
            'health_score_improvement': improvement,
            'implementation_successful': improvement > 0
        }

    def _calculate_overall_metrics(self, test_results: Dict) -> Dict:
        """Calculate overall system metrics from test results."""
        scenario_results = test_results.get('test_scenarios', {})
        performance_results = test_results.get('performance_tests', {})
        accuracy_results = test_results.get('accuracy_tests', {})
        
        # Calculate scenario success rate
        scenario_success_rate = sum(
            1 for result in scenario_results.values() 
            if result.get('test_passed', False)
        ) / len(scenario_results) if scenario_results else 0
        
        # Calculate average accuracy
        accuracy_scores = []
        for accuracy_test in accuracy_results.values():
            if isinstance(accuracy_test, dict) and 'accuracy_score' in accuracy_test:
                accuracy_scores.append(accuracy_test['accuracy_score'])
        
        avg_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0
        
        # Performance rating
        performance_rating = performance_results.get('performance_rating', 'unknown')
        
        # Overall system rating
        overall_score = (scenario_success_rate * 0.4 + avg_accuracy * 0.4 + 
                        (1.0 if performance_rating == 'excellent' else 0.7 if performance_rating == 'good' else 0.3) * 0.2)
        
        return {
            'scenario_success_rate': scenario_success_rate,
            'average_accuracy': avg_accuracy,
            'performance_rating': performance_rating,
            'overall_score': overall_score,
            'overall_rating': 'excellent' if overall_score >= 0.8 else 'good' if overall_score >= 0.6 else 'needs_improvement',
            'tests_passed': sum(1 for result in scenario_results.values() if result.get('test_passed', False)),
            'total_tests': len(scenario_results)
        }

    async def _cleanup_test_data(self, user_id: str):
        """Clean up test data for a user."""
        collections = ["expenses", "incomes", "budgets", "debts", "recommendations", "financial_goals"]
        
        for collection_name in collections:
            await self.db[collection_name].delete_many({"user_id": user_id})

    async def _save_test_results(self, test_results: Dict):
        """Save test results to database."""
        await self.db["test_results"].insert_one(test_results)

    async def generate_test_report(self) -> Dict:
        """Generate comprehensive test report for documentation."""
        test_results = await self.run_comprehensive_tests()
        
        report = {
            'report_title': 'Personal Finance Advisor - Test Report',
            'report_date': datetime.now().isoformat(),
            'executive_summary': {
                'overall_rating': test_results['overall_metrics']['overall_rating'],
                'overall_score': test_results['overall_metrics']['overall_score'],
                'tests_passed': test_results['overall_metrics']['tests_passed'],
                'total_tests': test_results['overall_metrics']['total_tests'],
                'key_findings': self._generate_key_findings(test_results),
                'recommendations': self._generate_system_recommendations(test_results)
            },
            'detailed_results': test_results,
            'appendix': {
                'test_methodology': 'Comprehensive testing using simulated user scenarios and performance benchmarks',
                'evaluation_criteria': ['Accuracy', 'Performance', 'User Experience', 'Recommendation Quality'],
                'test_environment': 'Automated testing framework with realistic financial data'
            }
        }
        
        return report

    def _generate_key_findings(self, test_results: Dict) -> List[str]:
        """Generate key findings from test results."""
        findings = []
        
        overall_metrics = test_results.get('overall_metrics', {})
        
        if overall_metrics.get('overall_score', 0) >= 0.8:
            findings.append("System demonstrates excellent performance across all test scenarios")
        elif overall_metrics.get('overall_score', 0) >= 0.6:
            findings.append("System performs well with minor areas for improvement")
        else:
            findings.append("System requires significant improvements to meet quality standards")
        
        # Performance findings
        perf_results = test_results.get('performance_tests', {})
        if perf_results.get('performance_rating') == 'excellent':
            findings.append("System response times are excellent and meet performance requirements")
        
        # Accuracy findings
        accuracy_results = test_results.get('accuracy_tests', {})
        classification_accuracy = accuracy_results.get('expense_classification', {}).get('accuracy_score', 0)
        if classification_accuracy >= 0.8:
            findings.append("Expense classification system is highly accurate")
        
        return findings

    def _generate_system_recommendations(self, test_results: Dict) -> List[str]:
        """Generate system improvement recommendations."""
        recommendations = []
        
        overall_metrics = test_results.get('overall_metrics', {})
        
        if overall_metrics.get('overall_score', 0) < 0.8:
            recommendations.append("Focus on improving recommendation accuracy and relevance")
        
        perf_results = test_results.get('performance_tests', {})
        if perf_results.get('performance_rating') != 'excellent':
            recommendations.append("Optimize system performance for faster response times")
        
        accuracy_results = test_results.get('accuracy_tests', {})
        classification_accuracy = accuracy_results.get('expense_classification', {}).get('accuracy_score', 0)
        if classification_accuracy < 0.8:
            recommendations.append("Enhance expense classification algorithm with more training data")
        
        scenario_results = test_results.get('test_scenarios', {})
        failed_scenarios = [name for name, result in scenario_results.items() if not result.get('test_passed', False)]
        if failed_scenarios:
            recommendations.append(f"Improve handling of specific scenarios: {', '.join(failed_scenarios)}")
        
        return recommendations

# Global testing framework instance
testing_framework = TestingFramework()
