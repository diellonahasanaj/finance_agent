from fastapi import APIRouter, Depends, Query
from app.services.analysis_service import get_monthly_summary
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/monthly-summary")
async def monthly_summary(month: str = Query(..., examples={"2026-02": {"value": "2026-02", "description": "Example month"}}), user=Depends(get_current_user)):
    return await get_monthly_summary(user, month)
