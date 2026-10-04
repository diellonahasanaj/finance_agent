from fastapi import APIRouter

router = APIRouter()

@router.get("/disclaimer")
async def disclaimer():
    return {"disclaimer": "This system provides educational financial suggestions and does not replace professional financial advice."}
