"""
Data handling service for importing and processing financial datasets.
Supports CSV, JSON, and manual data entry.
"""
import csv
import json
import pandas as pd
from typing import List, Dict, Optional, Union
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.finance import IncomeModel, ExpenseModel, BudgetModel, DebtModel, FinancialGoalModel
from bson import ObjectId

class DataHandler:
    """Handles data import, processing, and validation for financial datasets."""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.get_default_database()
        
        # Expense categories for classification
        self.expense_categories = {
            'Housing': ['rent', 'mortgage', 'property tax', 'home insurance', 'maintenance'],
            'Food': ['groceries', 'restaurant', 'dining', 'food delivery', 'coffee'],
            'Transportation': ['gas', 'car payment', 'car insurance', 'public transport', 'uber', 'taxi'],
            'Utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'cable'],
            'Healthcare': ['doctor', 'hospital', 'pharmacy', 'insurance', 'dental'],
            'Entertainment': ['movies', 'concerts', 'games', 'subscriptions', 'hobbies'],
            'Shopping': ['clothing', 'electronics', 'home goods', 'personal care'],
            'Education': ['tuition', 'books', 'courses', 'supplies'],
            'Debt Payments': ['loan payment', 'credit card', 'student loan'],
            'Savings': ['emergency fund', 'retirement', 'investment'],
            'Other': []
        }
        
        # Income sources classification
        self.income_sources = {
            'Salary': ['salary', 'wages', 'paycheck'],
            'Freelance': ['freelance', 'contract', 'consulting'],
            'Investment': ['dividends', 'interest', 'capital gains', 'rental income'],
            'Business': ['business income', 'self-employment'],
            'Other': []
        }

    async def import_csv_data(self, user_id: str, file_content: str, data_type: str) -> Dict:
        """
        Import financial data from CSV file.
        
        Args:
            user_id: User ID for data ownership
            file_content: CSV file content as string
            data_type: Type of data ('expenses', 'income', 'budgets', 'debts')
        
        Returns:
            Dict with import results and statistics
        """
        try:
            # Parse CSV content
            df = pd.read_csv(pd.StringIO(file_content))
            
            # Validate required columns
            required_columns = self._get_required_columns(data_type)
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    'success': False,
                    'error': f'Missing required columns: {missing_columns}',
                    'available_columns': list(df.columns)
                }
            
            # Process and validate data
            processed_data = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    processed_item = await self._process_row(data_type, row, user_id)
                    if processed_item:
                        processed_data.append(processed_item)
                except Exception as e:
                    errors.append(f'Row {index + 1}: {str(e)}')
            
            # Save to database
            collection_name = f"{data_type[:-1]}s"  # expenses, income, etc.
            collection = self.db[collection_name]
            
            if processed_data:
                result = await collection.insert_many(processed_data)
                
                return {
                    'success': True,
                    'imported_count': len(result.inserted_ids),
                    'total_rows': len(df),
                    'errors': errors,
                    'statistics': await self._generate_import_statistics(user_id, data_type)
                }
            else:
                return {
                    'success': False,
                    'error': 'No valid data to import',
                    'errors': errors
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process CSV: {str(e)}'
            }

    async def import_json_data(self, user_id: str, json_content: str, data_type: str) -> Dict:
        """
        Import financial data from JSON file.
        """
        try:
            data = json.loads(json_content)
            
            if not isinstance(data, list):
                data = [data]
            
            processed_data = []
            errors = []
            
            for index, item in enumerate(data):
                try:
                    processed_item = await self._process_dict_item(data_type, item, user_id)
                    if processed_item:
                        processed_data.append(processed_item)
                except Exception as e:
                    errors.append(f'Item {index + 1}: {str(e)}')
            
            # Save to database
            collection_name = f"{data_type[:-1]}s"
            collection = self.db[collection_name]
            
            if processed_data:
                result = await collection.insert_many(processed_data)
                
                return {
                    'success': True,
                    'imported_count': len(result.inserted_ids),
                    'total_items': len(data),
                    'errors': errors,
                    'statistics': await self._generate_import_statistics(user_id, data_type)
                }
            else:
                return {
                    'success': False,
                    'error': 'No valid data to import',
                    'errors': errors
                }
                
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON format: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process JSON: {str(e)}'
            }

    async def classify_expense(self, description: str, amount: float) -> str:
        """
        Automatically classify expense based on description and amount patterns.
        """
        description_lower = description.lower()
        
        # Check keywords in description
        for category, keywords in self.expense_categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        # Amount-based heuristics
        if amount > 1000:
            return 'Housing'  # Likely rent/mortgage
        elif amount > 200:
            return 'Shopping'  # Likely large purchase
        elif amount < 5:
            return 'Entertainment'  # Likely small discretionary spending
        
        return 'Other'

    async def generate_sample_data(self, user_id: str, months: int = 6) -> Dict:
        """
        Generate realistic sample financial data for testing and demonstration.
        """
        from datetime import datetime, timedelta
        import random
        
        sample_data = {
            'expenses': [],
            'income': [],
            'budgets': [],
            'debts': []
        }
        
        # Generate sample expenses
        expense_templates = [
            {'category': 'Housing', 'description': 'Monthly Rent', 'amount': 1500, 'frequency': 'monthly'},
            {'category': 'Food', 'description': 'Grocery Shopping', 'amount': 200, 'frequency': 'weekly'},
            {'category': 'Transportation', 'description': 'Gas Station', 'amount': 50, 'frequency': 'weekly'},
            {'category': 'Utilities', 'description': 'Electricity Bill', 'amount': 120, 'frequency': 'monthly'},
            {'category': 'Entertainment', 'description': 'Netflix Subscription', 'amount': 15, 'frequency': 'monthly'},
            {'category': 'Food', 'description': 'Restaurant Dinner', 'amount': 45, 'frequency': 'bi-weekly'},
            {'category': 'Shopping', 'description': 'Clothing Purchase', 'amount': 80, 'frequency': 'monthly'},
            {'category': 'Healthcare', 'description': 'Pharmacy', 'amount': 25, 'frequency': 'monthly'},
        ]
        
        base_date = datetime.now() - timedelta(days=30 * months)
        
        for month_offset in range(months):
            current_month = base_date + timedelta(days=30 * month_offset)
            month_str = current_month.strftime('%Y-%m')
            
            for template in expense_templates:
                if template['frequency'] == 'monthly':
                    expense_date = current_month.replace(day=1)
                    sample_data['expenses'].append({
                        'user_id': user_id,
                        'amount': template['amount'] * random.uniform(0.9, 1.1),
                        'category': template['category'],
                        'description': template['description'],
                        'date': expense_date.strftime('%Y-%m-%d'),
                        'is_essential': template['category'] in ['Housing', 'Utilities', 'Healthcare']
                    })
                elif template['frequency'] == 'weekly':
                    for week in range(4):
                        expense_date = current_month + timedelta(days=week * 7)
                        sample_data['expenses'].append({
                            'user_id': user_id,
                            'amount': template['amount'] * random.uniform(0.8, 1.2),
                            'category': template['category'],
                            'description': template['description'],
                            'date': expense_date.strftime('%Y-%m-%d'),
                            'is_essential': template['category'] in ['Housing', 'Utilities', 'Healthcare']
                        })
                elif template['frequency'] == 'bi-weekly':
                    for week in range(0, 4, 2):
                        expense_date = current_month + timedelta(days=week * 7)
                        sample_data['expenses'].append({
                            'user_id': user_id,
                            'amount': template['amount'] * random.uniform(0.8, 1.2),
                            'category': template['category'],
                            'description': template['description'],
                            'date': expense_date.strftime('%Y-%m-%d'),
                            'is_essential': False
                        })
        
        # Generate sample income
        sample_data['income'].append({
            'user_id': user_id,
            'amount': 4500,
            'source': 'Monthly Salary',
            'date': base_date.strftime('%Y-%m-01'),
            'frequency': 'monthly',
            'is_recurring': True
        })
        
        # Generate sample budgets
        categories = ['Housing', 'Food', 'Transportation', 'Utilities', 'Entertainment', 'Shopping', 'Healthcare']
        for category in categories:
            # Calculate 80% of average monthly spending as budget
            category_expenses = [e for e in sample_data['expenses'] if e['category'] == category]
            if category_expenses:
                avg_spending = sum(e['amount'] for e in category_expenses) / months
                budget_limit = avg_spending * 0.8
                
                sample_data['budgets'].append({
                    'user_id': user_id,
                    'category': category,
                    'limit': budget_limit,
                    'month': month_str,
                    'warning_threshold': 0.8
                })
        
        # Generate sample debt
        sample_data['debts'].append({
            'user_id': user_id,
            'amount': 5000,
            'creditor': 'Credit Card Company',
            'date': base_date.strftime('%Y-%m-01'),
            'interest_rate': 18.9,
            'minimum_payment': 150,
            'due_date': '15',
            'debt_type': 'credit_card'
        })
        
        # Save sample data to database
        results = {}
        for data_type, items in sample_data.items():
            if items:
                collection = self.db[data_type]
                result = await collection.insert_many(items)
                results[data_type] = len(result.inserted_ids)
        
        return {
            'success': True,
            'generated_data': results,
            'message': f'Sample data generated for {months} months'
        }

    def _get_required_columns(self, data_type: str) -> List[str]:
        """Get required columns for different data types."""
        column_requirements = {
            'expenses': ['amount', 'description', 'date'],
            'income': ['amount', 'source', 'date'],
            'budgets': ['category', 'limit', 'month'],
            'debts': ['amount', 'creditor', 'date']
        }
        return column_requirements.get(data_type, [])

    async def _process_row(self, data_type: str, row, user_id: str) -> Optional[Dict]:
        """Process a single row from CSV data."""
        if data_type == 'expenses':
            category = row.get('category', '')
            if not category:
                category = await self.classify_expense(str(row.get('description', '')), float(row.get('amount', 0)))
            
            return {
                'user_id': user_id,
                'amount': float(row.get('amount', 0)),
                'category': category,
                'description': str(row.get('description', '')),
                'date': str(row.get('date', '')),
                'is_essential': str(row.get('is_essential', '')).lower() == 'true'
            }
        
        elif data_type == 'income':
            return {
                'user_id': user_id,
                'amount': float(row.get('amount', 0)),
                'source': str(row.get('source', '')),
                'date': str(row.get('date', '')),
                'frequency': str(row.get('frequency', 'one-time')),
                'is_recurring': str(row.get('is_recurring', '')).lower() == 'true'
            }
        
        elif data_type == 'budgets':
            return {
                'user_id': user_id,
                'category': str(row.get('category', '')),
                'limit': float(row.get('limit', 0)),
                'month': str(row.get('month', '')),
                'warning_threshold': float(row.get('warning_threshold', 0.8))
            }
        
        elif data_type == 'debts':
            return {
                'user_id': user_id,
                'amount': float(row.get('amount', 0)),
                'creditor': str(row.get('creditor', '')),
                'date': str(row.get('date', '')),
                'interest_rate': float(row.get('interest_rate', 0)),
                'minimum_payment': float(row.get('minimum_payment', 0)),
                'debt_type': str(row.get('debt_type', 'other'))
            }
        
        return None

    async def _process_dict_item(self, data_type: str, item: Dict, user_id: str) -> Optional[Dict]:
        """Process a single item from JSON data."""
        # Similar to _process_row but for dict items
        item['user_id'] = user_id
        
        if data_type == 'expenses' and 'category' not in item:
            item['category'] = await self.classify_expense(
                item.get('description', ''), 
                float(item.get('amount', 0))
            )
        
        return item

    async def _generate_import_statistics(self, user_id: str, data_type: str) -> Dict:
        """Generate statistics for imported data."""
        collection = self.db[f"{data_type[:-1]}s"]
        
        total_count = await collection.count_documents({'user_id': user_id})
        
        if data_type == 'expenses':
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {
                    '_id': '$category',
                    'count': {'$sum': 1},
                    'total': {'$sum': '$amount'}
                }}
            ]
            category_stats = await collection.aggregate(pipeline).to_list(length=None)
            
            return {
                'total_expenses': total_count,
                'category_breakdown': category_stats
            }
        
        elif data_type == 'income':
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {
                    '_id': '$source',
                    'count': {'$sum': 1},
                    'total': {'$sum': '$amount'}
                }}
            ]
            source_stats = await collection.aggregate(pipeline).to_list(length=None)
            
            return {
                'total_income_entries': total_count,
                'source_breakdown': source_stats
            }
        
        return {'total_items': total_count}

# Global data handler instance
data_handler = DataHandler()
