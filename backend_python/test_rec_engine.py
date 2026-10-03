import asyncio
from app.services.recommendation_engine_v2 import financial_recommendation_engine

async def test():
    recs = await financial_recommendation_engine.generate_recommendations(
        'test@example.com', 
        {'totalIncome': 5000, 'totalExpenses': 3000, 'categoryBreakdown': {'Food': 500}}, 
        {'Food': 600}
    )
    print("Recommendations:", recs)
    return recs

if __name__ == "__main__":
    asyncio.run(test())
