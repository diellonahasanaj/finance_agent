"""
Comprehensive recommendation engine with detailed explanations and action steps.
Provides actionable financial advice with transparency and ethical considerations.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.finance import RecommendationModel
from app.services.decision_engine import DecisionEngine
from app.services.expense_analysis import ExpenseAnalyzer
import json

class RecommendationEngine:
    """Advanced recommendation engine with explanations and transparency."""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.get_default_database()
        self.decision_engine = DecisionEngine()
        self.expense_analyzer = ExpenseAnalyzer()
        
        # Recommendation categories with detailed explanations
        self.recommendation_templates = {
            'savings': {
                'icon': '💰',
                'color': '#4CAF50',
                'urgency_levels': {
                    'high': 'Critical: Immediate action required',
                    'medium': 'Important: Address within 30 days',
                    'low': 'Suggestion: Consider for improvement'
                }
            },
            'debt': {
                'icon': '💳',
                'color': '#FF9800',
                'urgency_levels': {
                    'high': 'Urgent: High-interest debt needs attention',
                    'medium': 'Important: Debt management strategy needed',
                    'low': 'Opportunity: Optimize debt structure'
                }
            },
            'budget': {
                'icon': '📊',
                'color': '#2196F3',
                'urgency_levels': {
                    'high': 'Alert: Budget consistently exceeded',
                    'medium': 'Warning: Budget adjustments needed',
                    'low': 'Tip: Budget optimization available'
                }
            },
            'investment': {
                'icon': '📈',
                'color': '#9C27B0',
                'urgency_levels': {
                    'high': 'Action: Investment opportunities available',
                    'medium': 'Consider: Investment strategy review',
                    'low': 'Future: Plan for investment growth'
                }
            },
            'emergency_fund': {
                'icon': '🛡️',
                'color': '#F44336',
                'urgency_levels': {
                    'high': 'Critical: Emergency fund insufficient',
                    'medium': 'Important: Build emergency fund',
                    'low': 'Good: Maintain emergency fund'
                }
            }
        }
        
        # Ethical guidelines for recommendations
        self.ethical_guidelines = {
            'transparency': 'All recommendations must explain the reasoning',
            'user_control': 'Users must have final decision authority',
            'privacy': 'No personal data sharing without consent',
            'fairness': 'Recommendations must be unbiased and equitable',
            'safety': 'Avoid high-risk financial advice'
        }

    async def generate_comprehensive_recommendations(self, user_id: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate comprehensive recommendations with detailed explanations.
        """
        # Get base recommendations from decision engine
        base_recommendations = await self.decision_engine.generate_recommendations(user_id, context)
        
        # Enhance with detailed explanations
        enhanced_recommendations = []
        
        for rec in base_recommendations:
            enhanced_rec = await self._enhance_recommendation(rec, user_id)
            enhanced_recommendations.append(enhanced_rec)
        
        # Add educational content
        educational_content = await self._generate_educational_content(enhanced_recommendations)
        
        # Calculate implementation difficulty
        recommendations_with_difficulty = await self._calculate_implementation_difficulty(enhanced_recommendations)
        
        # Add success stories and case studies
        success_stories = await self._get_relevant_success_stories(enhanced_recommendations)
        
        # Generate personalized action plan
        action_plan = await self._create_action_plan(recommendations_with_difficulty, user_id)
        
        return {
            'recommendations': recommendations_with_difficulty,
            'educational_content': educational_content,
            'success_stories': success_stories,
            'action_plan': action_plan,
            'summary': {
                'total_recommendations': len(recommendations_with_difficulty),
                'high_priority': len([r for r in recommendations_with_difficulty if r['priority'] == 'high']),
                'potential_monthly_savings': sum(r.get('potential_savings', 0) for r in recommendations_with_difficulty),
                'implementation_timeline': self._calculate_implementation_timeline(recommendations_with_difficulty)
            },
            'ethical_disclosure': self._generate_ethical_disclosure()
        }

    async def _enhance_recommendation(self, recommendation: Dict, user_id: str) -> Dict:
        """Enhance a recommendation with detailed explanations and context."""
        enhanced = recommendation.copy()
        
        # Add visual elements
        template = self.recommendation_templates.get(recommendation['type'], {})
        enhanced['icon'] = template.get('icon', '💡')
        enhanced['color'] = template.get('color', '#666666')
        
        # Add urgency explanation
        urgency_levels = template.get('urgency_levels', {})
        enhanced['urgency_explanation'] = urgency_levels.get(recommendation['priority'], 'Standard priority')
        
        # Add detailed explanation
        enhanced['detailed_explanation'] = await self._generate_detailed_explanation(recommendation, user_id)
        
        # Add risk assessment
        enhanced['risk_assessment'] = self._assess_recommendation_risk(recommendation)
        
        # Add expected timeline
        enhanced['expected_timeline'] = self._estimate_implementation_timeline(recommendation)
        
        # Add success metrics
        enhanced['success_metrics'] = self._define_success_metrics(recommendation)
        
        # Add alternatives
        enhanced['alternatives'] = await self._suggest_alternatives(recommendation, user_id)
        
        # Add resources
        enhanced['resources'] = await self._find_relevant_resources(recommendation)
        
        return enhanced

    async def _generate_detailed_explanation(self, recommendation: Dict, user_id: str) -> str:
        """Generate detailed explanation for why this recommendation matters."""
        explanations = {
            'savings': {
                'high': 'Building adequate savings is crucial for financial security. With your current savings rate, you may be vulnerable to unexpected expenses and miss opportunities for wealth building. Increasing your savings rate will provide a safety net and enable long-term financial goals.',
                'medium': 'Your savings rate is decent but could be improved. By optimizing your spending and increasing savings, you\'ll build wealth faster and have more flexibility for future opportunities.',
                'low': 'You have a good savings foundation. Small improvements could accelerate your path to financial independence and provide additional security.'
            },
            'debt': {
                'high': 'High debt levels can significantly impact your financial health through interest payments and limited borrowing capacity. Addressing debt now will save you money and reduce financial stress.',
                'medium': 'Your debt level is manageable but could be optimized. Strategic debt management can save you money and improve your financial flexibility.',
                'low': 'Your debt is under control. Consider opportunities to optimize interest rates or payment strategies.'
            },
            'budget': {
                'high': 'Consistent budget overspending indicates that your current budget may not reflect your actual spending patterns or lifestyle. This can lead to financial stress and missed savings opportunities.',
                'medium': 'Some budget adjustments are needed to align your spending with your financial goals. This will help you stay on track and avoid surprises.',
                'low': 'Your budget is generally on track. Minor optimizations could improve your financial efficiency.'
            },
            'emergency_fund': {
                'high': 'Without an adequate emergency fund, you\'re at risk of financial hardship from unexpected expenses. Medical bills, car repairs, or job loss could become major crises.',
                'medium': 'Building your emergency fund will provide peace of mind and protect you from financial setbacks. It\'s a fundamental step in financial security.',
                'low': 'You have a good emergency fund foundation. Maintaining and gradually increasing it will strengthen your financial position.'
            }
        }
        
        rec_type = recommendation['type']
        priority = recommendation['priority']
        
        base_explanation = explanations.get(rec_type, {}).get(priority, 'This recommendation is based on your financial patterns and goals.')
        
        # Add personalized context
        if 'potential_savings' in recommendation and recommendation['potential_savings']:
            savings_text = f' This could save you approximately ${recommendation["potential_savings"]:.2f} per month.'
            base_explanation += savings_text
        
        return base_explanation

    def _assess_recommendation_risk(self, recommendation: Dict) -> Dict:
        """Assess the risk level and potential downsides of a recommendation."""
        risk_assessments = {
            'savings': {
                'risk_level': 'low',
                'potential_downsides': [
                    'May require lifestyle adjustments',
                    'Could reduce short-term discretionary spending'
                ],
                'mitigation_strategies': [
                    'Start with small increases',
                    'Automate savings to reduce decision fatigue',
                    'Track progress to stay motivated'
                ]
            },
            'debt': {
                'risk_level': 'medium',
                'potential_downsides': [
                    'May require temporary lifestyle changes',
                    'Could impact credit score if not managed properly'
                ],
                'mitigation_strategies': [
                    'Create a structured repayment plan',
                    'Maintain minimum payments on all debts',
                    'Consider professional financial advice'
                ]
            },
            'budget': {
                'risk_level': 'low',
                'potential_downsides': [
                    'May require tracking expenses more carefully',
                    'Could feel restrictive initially'
                ],
                'mitigation_strategies': [
                    'Use budgeting apps for easier tracking',
                    'Include discretionary spending in budget',
                    'Review and adjust budget monthly'
                ]
            },
            'emergency_fund': {
                'risk_level': 'very_low',
                'potential_downsides': [
                    'Opportunity cost of money in low-yield savings'
                ],
                'mitigation_strategies': [
                    'Use high-yield savings accounts',
                    'Keep emergency fund separate from other savings',
                    'Rebuild fund after any withdrawals'
                ]
            }
        }
        
        return risk_assessments.get(recommendation['type'], {
            'risk_level': 'medium',
            'potential_downsides': ['Requires discipline and commitment'],
            'mitigation_strategies': ['Start small and build momentum']
        })

    def _estimate_implementation_timeline(self, recommendation: Dict) -> Dict:
        """Estimate the timeline for implementing the recommendation."""
        timelines = {
            'savings': {
                'quick_wins': '1-2 weeks',
                'full_implementation': '2-3 months',
                'ongoing_maintenance': 'continuous'
            },
            'debt': {
                'quick_wins': '2-4 weeks',
                'full_implementation': '6-24 months',
                'ongoing_maintenance': 'monthly reviews'
            },
            'budget': {
                'quick_wins': '1 week',
                'full_implementation': '1-2 months',
                'ongoing_maintenance': 'monthly reviews'
            },
            'emergency_fund': {
                'quick_wins': '2-4 weeks',
                'full_implementation': '3-12 months',
                'ongoing_maintenance': 'quarterly reviews'
            }
        }
        
        return timelines.get(recommendation['type'], {
            'quick_wins': '2-4 weeks',
            'full_implementation': '1-3 months',
            'ongoing_maintenance': 'monthly reviews'
        })

    def _define_success_metrics(self, recommendation: Dict) -> List[Dict]:
        """Define measurable success metrics for the recommendation."""
        metrics = {
            'savings': [
                {
                    'metric': 'Savings Rate',
                    'target': '15-20% of income',
                    'measurement': 'monthly',
                    'success_criteria': 'Consistently meeting or exceeding target'
                },
                {
                    'metric': 'Emergency Fund Balance',
                    'target': '3-6 months of expenses',
                    'measurement': 'monthly',
                    'success_criteria': 'Reaching and maintaining target balance'
                }
            ],
            'debt': [
                {
                    'metric': 'Debt-to-Income Ratio',
                    'target': 'Below 30%',
                    'measurement': 'monthly',
                    'success_criteria': 'Consistent reduction over time'
                },
                {
                    'metric': 'Total Interest Paid',
                    'target': 'Minimize interest costs',
                    'measurement': 'quarterly',
                    'success_criteria': 'Reducing interest payments through strategic payments'
                }
            ],
            'budget': [
                {
                    'metric': 'Budget Adherence',
                    'target': '90% or better adherence',
                    'measurement': 'monthly',
                    'success_criteria': 'Staying within budget limits most months'
                }
            ],
            'emergency_fund': [
                {
                    'metric': 'Emergency Fund Coverage',
                    'target': '3-6 months of expenses',
                    'measurement': 'monthly',
                    'success_criteria': 'Maintaining adequate coverage'
                }
            ]
        }
        
        return metrics.get(recommendation['type'], [
            {
                'metric': 'Progress',
                'target': 'Steady improvement',
                'measurement': 'monthly',
                'success_criteria': 'Consistent positive changes'
            }
        ])

    async def _suggest_alternatives(self, recommendation: Dict, user_id: str) -> List[Dict]:
        """Suggest alternative approaches to the same goal."""
        alternatives = {
            'savings': [
                {
                    'title': 'Round-up Savings',
                    'description': 'Automatically round up purchases to the nearest dollar and save the difference',
                    'pros': ['Easy to implement', 'Small impact on daily life'],
                    'cons': ['Slower savings accumulation']
                },
                {
                    'title': 'Side Hustle Income',
                    'description': 'Generate additional income through freelance work or part-time jobs',
                    'pros': ['Increases total income', 'Can accelerate goals'],
                    'cons': ['Requires time and effort', 'May have startup costs']
                }
            ],
            'debt': [
                {
                    'title': 'Debt Consolidation',
                    'description': 'Combine multiple debts into a single loan with better terms',
                    'pros': ['Simplified payments', 'Potentially lower interest'],
                    'cons': ['May require good credit', 'Could have fees']
                },
                {
                    'title': 'Snowball Method',
                    'description': 'Pay smallest debts first for psychological momentum',
                    'pros': ['Motivating quick wins', 'Simple to follow'],
                    'cons': ['May cost more in interest']
                }
            ],
            'budget': [
                {
                    'title': 'Zero-Based Budgeting',
                    'description': 'Assign every dollar a purpose before the month begins',
                    'pros': ['Complete control', 'Eliminates waste'],
                    'cons': ['Time-consuming', 'Rigid structure']
                },
                {
                    'title': '50/30/20 Rule',
                    'description': 'Allocate 50% to needs, 30% to wants, 20% to savings',
                    'pros': ['Simple framework', 'Balanced approach'],
                    'cons': ['May not fit all situations']
                }
            ]
        }
        
        return alternatives.get(recommendation['type'], [])

    async def _find_relevant_resources(self, recommendation: Dict) -> List[Dict]:
        """Find relevant educational resources and tools."""
        resources = {
            'savings': [
                {
                    'title': 'High-Yield Savings Accounts',
                    'type': 'tool',
                    'description': 'Compare and find the best savings rates',
                    'url': '#savings-accounts'
                },
                {
                    'title': 'Automated Savings Apps',
                    'type': 'app',
                    'description': 'Apps that help automate your savings',
                    'url': '#savings-apps'
                }
            ],
            'debt': [
                {
                    'title': 'Debt Payoff Calculator',
                    'type': 'tool',
                    'description': 'Calculate optimal debt repayment strategies',
                    'url': '#debt-calculator'
                },
                {
                    'title': 'Credit Score Monitoring',
                    'type': 'service',
                    'description': 'Track and improve your credit score',
                    'url': '#credit-monitoring'
                }
            ],
            'budget': [
                {
                    'title': 'Budget Tracking Apps',
                    'type': 'app',
                    'description': 'Popular apps for budget management',
                    'url': '#budget-apps'
                },
                {
                    'title': 'Spending Analysis Tools',
                    'type': 'tool',
                    'description': 'Analyze your spending patterns',
                    'url': '#spending-analysis'
                }
            ]
        }
        
        return resources.get(recommendation['type'], [])

    async def _generate_educational_content(self, recommendations: List[Dict]) -> List[Dict]:
        """Generate educational content based on recommendations."""
        content = []
        
        # Identify key topics from recommendations
        topics = list(set(rec['type'] for rec in recommendations))
        
        educational_modules = {
            'savings': {
                'title': 'Understanding Compound Interest',
                'content': 'Learn how compound interest can work for you to build wealth over time.',
                'reading_time': '5 minutes',
                'difficulty': 'beginner'
            },
            'debt': {
                'title': 'Debt Management Strategies',
                'content': 'Explore different approaches to managing and eliminating debt effectively.',
                'reading_time': '7 minutes',
                'difficulty': 'intermediate'
            },
            'budget': {
                'title': 'Creating a Budget That Works',
                'content': 'Step-by-step guide to creating a realistic budget you can stick with.',
                'reading_time': '10 minutes',
                'difficulty': 'beginner'
            },
            'emergency_fund': {
                'title': 'Building Your Emergency Fund',
                'content': 'Why you need an emergency fund and how to build one systematically.',
                'reading_time': '6 minutes',
                'difficulty': 'beginner'
            }
        }
        
        for topic in topics:
            if topic in educational_modules:
                content.append(educational_modules[topic])
        
        return content

    async def _get_relevant_success_stories(self, recommendations: List[Dict]) -> List[Dict]:
        """Get relevant success stories and case studies."""
        stories = [
            {
                'title': 'Sarah\'s Debt Freedom Journey',
                'category': 'debt',
                'summary': 'How Sarah paid off $25,000 in debt in 18 months',
                'key_takeaways': [
                    'Created a strict budget and tracked every expense',
                    'Used the debt snowball method for motivation',
                    'Increased income through freelance work'
                ],
                'timeframe': '18 months',
                'results': 'Debt-free with $5,000 emergency fund'
            },
            {
                'title': 'Mike\'s Savings Success',
                'category': 'savings',
                'summary': 'Building a 6-month emergency fund on a modest income',
                'key_takeaways': [
                    'Automated savings transfers',
                    'Cut discretionary spending by 20%',
                    'Used windfalls strategically'
                ],
                'timeframe': '12 months',
                'results': '$15,000 emergency fund saved'
            }
        ]
        
        # Filter stories relevant to recommendations
        relevant_categories = set(rec['type'] for rec in recommendations)
        return [story for story in stories if story['category'] in relevant_categories]

    async def _calculate_implementation_difficulty(self, recommendations: List[Dict]) -> List[Dict]:
        """Calculate implementation difficulty for each recommendation."""
        difficulty_scores = {
            'savings': 3,  # Medium difficulty
            'debt': 4,    # High difficulty
            'budget': 2,  # Low-medium difficulty
            'emergency_fund': 3,  # Medium difficulty
            'investment': 4  # High difficulty
        }
        
        for rec in recommendations:
            base_difficulty = difficulty_scores.get(rec['type'], 3)
            
            # Adjust based on priority
            if rec['priority'] == 'high':
                difficulty_modifier = 0.5  # High priority may increase difficulty
            elif rec['priority'] == 'low':
                difficulty_modifier = -0.5  # Low priority may be easier
            else:
                difficulty_modifier = 0
            
            final_difficulty = max(1, min(5, base_difficulty + difficulty_modifier))
            
            difficulty_labels = {
                1: 'Very Easy',
                2: 'Easy',
                3: 'Medium',
                4: 'Hard',
                5: 'Very Hard'
            }
            
            rec['implementation_difficulty'] = {
                'score': final_difficulty,
                'label': difficulty_labels[final_difficulty],
                'estimated_time': self._estimate_time_by_difficulty(final_difficulty)
            }
        
        return recommendations

    def _estimate_time_by_difficulty(self, difficulty: int) -> str:
        """Estimate implementation time based on difficulty."""
        time_estimates = {
            1: 'Less than 1 hour',
            2: '1-3 hours',
            3: '3-8 hours',
            4: '8-20 hours',
            5: '20+ hours'
        }
        return time_estimates.get(difficulty, '3-8 hours')

    async def _create_action_plan(self, recommendations: List[Dict], user_id: str) -> Dict:
        """Create a structured action plan for implementing recommendations."""
        # Sort by priority and difficulty
        sorted_recs = sorted(recommendations, key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x['priority']],
            -x['implementation_difficulty']['score']  # Easier first
        ), reverse=True)
        
        # Create phases
        phases = {
            'immediate': [],  # First 2 weeks
            'short_term': [],  # First month
            'medium_term': [],  # 2-3 months
            'long_term': []    # 3+ months
        }
        
        for rec in sorted_recs:
            if rec['priority'] == 'high' and rec['implementation_difficulty']['score'] <= 3:
                phases['immediate'].append(rec)
            elif rec['priority'] == 'high' or rec['implementation_difficulty']['score'] <= 2:
                phases['short_term'].append(rec)
            elif rec['implementation_difficulty']['score'] <= 3:
                phases['medium_term'].append(rec)
            else:
                phases['long_term'].append(rec)
        
        return {
            'phases': phases,
            'total_timeline': self._calculate_implementation_timeline(recommendations),
            'checkpoints': self._create_checkpoints(phases),
            'milestones': self._define_milestones(recommendations)
        }

    def _calculate_implementation_timeline(self, recommendations: List[Dict]) -> str:
        """Calculate overall implementation timeline."""
        if not recommendations:
            return 'No recommendations'
        
        max_difficulty = max(rec['implementation_difficulty']['score'] for rec in recommendations)
        high_priority_count = len([r for r in recommendations if r['priority'] == 'high'])
        
        if max_difficulty <= 2 and high_priority_count <= 2:
            return '2-4 weeks'
        elif max_difficulty <= 3 and high_priority_count <= 3:
            return '1-2 months'
        elif max_difficulty <= 4:
            return '2-4 months'
        else:
            return '4-6 months'

    def _create_checkpoints(self, phases: Dict) -> List[Dict]:
        """Create progress checkpoints for the action plan."""
        checkpoints = []
        
        if phases['immediate']:
            checkpoints.append({
                'title': 'Initial Progress Review',
                'timeline': '2 weeks',
                'goals': [f'Complete {len(phases["immediate"])} immediate actions'],
                'success_criteria': 'At least 50% of immediate actions completed'
            })
        
        if phases['short_term']:
            checkpoints.append({
                'title': 'Short-term Progress Check',
                'timeline': '1 month',
                'goals': [f'Complete {len(phases["short_term"])} short-term actions'],
                'success_criteria': 'All short-term actions initiated'
            })
        
        return checkpoints

    def _define_milestones(self, recommendations: List[Dict]) -> List[Dict]:
        """Define key milestones for the recommendation plan."""
        milestones = []
        
        # Savings milestones
        savings_recs = [r for r in recommendations if r['type'] == 'savings']
        if savings_recs:
            milestones.append({
                'title': 'Savings Rate Target',
                'description': 'Achieve recommended savings rate',
                'timeline': '3 months',
                'metrics': ['Savings rate >= 15%', 'Emergency fund growing']
            })
        
        # Debt milestones
        debt_recs = [r for r in recommendations if r['type'] == 'debt']
        if debt_recs:
            milestones.append({
                'title': 'Debt Reduction Progress',
                'description': 'Reduce debt-to-income ratio',
                'timeline': '6 months',
                'metrics': ['Debt-to-income < 30%', 'High-interest debt reduced']
            })
        
        return milestones

    def _generate_ethical_disclosure(self) -> Dict:
        """Generate ethical disclosure for transparency."""
        return {
            'title': 'Ethical Disclosure',
            'content': 'This recommendation system is designed to provide personalized financial advice based on your data. We are committed to transparency, user privacy, and ethical financial guidance. All recommendations are generated using rule-based logic and machine learning patterns, with your best interests as the primary consideration.',
            'principles': self.ethical_guidelines,
            'limitations': [
                'Recommendations are based on historical data and may not account for future changes',
                'Individual circumstances may vary, so professional advice may be beneficial',
                'Market conditions and personal situations can affect recommendation effectiveness'
            ],
            'user_rights': [
                'You have the right to accept or reject any recommendation',
                'Your data is used only for generating personalized advice',
                'You can request explanation for any recommendation',
                'You can opt out of data analysis at any time'
            ]
        }

# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
