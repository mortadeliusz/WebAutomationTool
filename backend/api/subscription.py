"""
Subscription endpoints
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.post("/check")
async def force_subscription_check():
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/webhook")
async def lemon_squeezy_webhook():
    raise HTTPException(status_code=501, detail="Not implemented yet")
