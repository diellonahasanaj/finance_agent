"""Tests for rule-based expense classification."""
from app.services.expense_classifier import expense_classifier


def test_classify_food_expense():
    category, confidence = expense_classifier.classify_expense("Grocery shopping at supermarket")
    assert category == "Food"
    assert confidence > 0


def test_classify_transportation_expense():
    category, confidence = expense_classifier.classify_expense("Uber ride to airport")
    assert category == "Transportation"
    assert confidence > 0


def test_classify_unknown_expense():
    category, confidence = expense_classifier.classify_expense("Miscellaneous payment")
    assert category == "Other"
    assert confidence == 0.5


def test_get_all_categories():
    categories = expense_classifier.get_all_categories()
    assert "Food" in categories
    assert "Transportation" in categories
    assert "Other" in categories
