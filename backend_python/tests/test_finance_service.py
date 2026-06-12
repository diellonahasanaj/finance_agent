"""Tests for dashboard and analytics data builders."""
import pytest
from app.services.finance_service import build_dashboard_data, _category_breakdown


@pytest.mark.asyncio
async def test_build_dashboard_with_budget_alerts():
    user = {"_id": "test_id", "email": "test@example.com"}
    dashboard = await build_dashboard_data(user, month="2099-01")

    assert "total_income" in dashboard
    assert "alerts" in dashboard
    assert "recommendations" in dashboard
    assert "categoryBreakdown" in dashboard
    assert "savings_goal_progress" in dashboard


def test_category_breakdown():
    expenses = [
        {"category": "Food", "amount": 100},
        {"category": "Food", "amount": 50},
        {"category": "Transportation", "amount": 30},
    ]
    breakdown = _category_breakdown(expenses)
    assert breakdown["Food"] == 150
    assert breakdown["Transportation"] == 30
