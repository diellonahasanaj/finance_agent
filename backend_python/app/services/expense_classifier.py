"""
Expense classification service using rule-based keyword matching.
Automatically categorizes expenses based on title/description.
"""
from typing import Tuple, Optional
import re

class ExpenseClassifier:
    """Classifies expenses into categories using keyword matching."""
    
    # Category keywords for classification
    CATEGORY_KEYWORDS = {
        'Food': [
            'restaurant', 'cafe', 'coffee', 'lunch', 'dinner', 'breakfast',
            'grocery', 'groceries', 'supermarket', 'market', 'bakery',
            'pizza', 'burger', 'fast food', 'food', 'eat', 'meal',
            'kitchen', 'dining', 'bar', 'pub', 'drink', 'alcohol',
            'wine', 'beer', 'juice', 'soda', 'snack', 'dessert',
            'catering', 'delivery', 'doordash', 'uber eats', 'grubhub'
        ],
        'Transportation': [
            'uber', 'lyft', 'taxi', 'gas', 'fuel', 'parking',
            'bus', 'train', 'metro', 'transit', 'toll', 'car',
            'maintenance', 'oil change', 'repair', 'mechanic',
            'insurance', 'registration', 'license', 'public transport',
            'bike', 'bicycle', 'scooter', 'motorcycle', 'airline',
            'flight', 'hotel', 'accommodation', 'travel', 'commute'
        ],
        'Housing': [
            'rent', 'mortgage', 'apartment', 'house', 'home',
            'landlord', 'lease', 'property', 'maintenance',
            'repair', 'paint', 'furniture', 'decor', 'household'
        ],
        'Utilities': [
            'electricity', 'water', 'gas', 'internet', 'phone',
            'mobile', 'wifi', 'power', 'utility', 'bill',
            'cable', 'streaming', 'subscription', 'service'
        ],
        'Entertainment': [
            'movie', 'cinema', 'theater', 'concert', 'music',
            'game', 'gaming', 'entertainment', 'netflix', 'spotify',
            'hulu', 'disney', 'youtube', 'gaming', 'playstation',
            'xbox', 'steam', 'ticket', 'event', 'show', 'comedy',
            'sports', 'entertainment park', 'theme park'
        ],
        'Health': [
            'doctor', 'dentist', 'hospital', 'medicine', 'pharmacy',
            'health', 'medical', 'healthcare', 'clinic', 'therapy',
            'mental', 'gym', 'fitness', 'yoga', 'exercise',
            'vitamins', 'supplement', 'prescription', 'surgery'
        ],
        'Education': [
            'school', 'university', 'college', 'course', 'education',
            'training', 'books', 'textbook', 'tuition', 'class',
            'learning', 'study', 'certification', 'workshop'
        ],
        'Shopping': [
            'amazon', 'mall', 'store', 'shop', 'clothing', 'clothes',
            'apparel', 'fashion', 'shoes', 'dress', 'department store',
            'retail', 'purchase', 'buy', 'shopping', 'target',
            'walmart', 'costco', 'ebay', 'online', 'electronics'
        ],
        'Other': []
    }
    
    def classify_expense(self, title: str, description: str = "") -> Tuple[str, float]:
        """
        Classify an expense into a category based on title and description.
        Returns (category, confidence_score)
        
        Priority:
        1. Rule-based keyword matching
        2. Default to "Other"
        
        Args:
            title: Expense title
            description: Optional expense description
            
        Returns:
            Tuple of (category, confidence_score) where confidence is 0-1
        """
        combined_text = f"{title} {description}".lower()
        
        # Try to find matching category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if category == 'Other':
                continue
                
            # Calculate matching score
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            
            if matches > 0:
                # Calculate confidence based on number of keyword matches
                confidence = min(matches / 2, 1.0)  # Max confidence at 2+ matches
                return category, confidence
        
        # Default to Other if no matches found
        return 'Other', 0.5
    
    def auto_classify(self, title: str, category: Optional[str] = None, description: str = "") -> str:
        """
        Auto-classify expense. If category provided but matches "Other", try to classify.
        
        Args:
            title: Expense title
            category: User-provided category (optional)
            description: Expense description (optional)
            
        Returns:
            Classified category
        """
        # If user provided a valid category, use it
        if category and category != 'Other' and category in self.CATEGORY_KEYWORDS:
            return category
        
        # Otherwise, try to classify
        classified_category, confidence = self.classify_expense(title, description)
        
        # If confidence is high or no category provided, use classified result
        if confidence > 0.3 or not category:
            return classified_category
        
        # Fall back to user-provided category if it exists
        return category if category else classified_category
    
    def get_all_categories(self) -> list:
        """Get list of all available categories."""
        return [cat for cat in self.CATEGORY_KEYWORDS.keys() if cat != 'Other'] + ['Other']


# Singleton instance
expense_classifier = ExpenseClassifier()
