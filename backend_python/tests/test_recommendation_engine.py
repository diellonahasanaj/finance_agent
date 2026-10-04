"""Tests for rule-based financial recommendation engine."""
import pytest
from app.services.recommendation_engine_v2 import financial_recommendation_engine


@pytest.mark.asyncio
async def test_budget_exceeded_recommendation():
    financial_data = {
        "totalIncome": 3000,
        "totalExpenses": 2500,
        "categoryBreakdown": {"Food": 600},
    }
    budget_data = {"Food": 500}

    recommendations = await financial_recommendation_engine.generate_recommendations(
        "test_user", financial_data, budget_data
    )

    budget_recs = [r for r in recommendations if "Budget" in r["title"]]
    assert len(budget_recs) >= 1
    assert budget_recs[0]["explanation"]
    assert budget_recs[0]["action_steps"]


@pytest.mark.asyncio
async def test_deficit_warning():
    financial_data = {
        "totalIncome": 2000,
        "totalExpenses": 2500,
        "categoryBreakdown": {"Food": 800},
    }
    budget_data = {}

    recommendations = await financial_recommendation_engine.generate_recommendations(
        "test_user", financial_data, budget_data
    )

    deficit_recs = [r for r in recommendations if "Exceed Income" in r["title"]]
    assert len(deficit_recs) == 1
    assert deficit_recs[0]["priority"] == "high"


@pytest.mark.asyncio
async def test_savings_recommendation():
    financial_data = {
        "totalIncome": 4000,
        "totalExpenses": 3800,
        "categoryBreakdown": {"Food": 500},
    }
    budget_data = {}

    recommendations = await financial_recommendation_engine.generate_recommendations(
        "test_user", financial_data, budget_data
    )

    savings_recs = [r for r in recommendations if r["type"] == "Savings"]
    assert len(savings_recs) >= 1
