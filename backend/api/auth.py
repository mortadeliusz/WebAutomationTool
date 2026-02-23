"""
Authentication endpoints
"""
from fastapi import APIRouter, HTTPException
from models.schemas import AuthConfig, CodeExchangeRequest, TokenResponse, TokenValidationRequest, ValidationResponse
from services.auth import get_auth_provider
from services.subscription_service import SubscriptionService

router = APIRouter(prefix="/auth", tags=["auth"])
subscription_service = SubscriptionService()

@router.get("/config", response_model=AuthConfig)
async def get_auth_config():
    auth_provider = get_auth_provider()
    return AuthConfig(
        auth_url=auth_provider.get_auth_url(),
        client_id=auth_provider.get_client_id(),
        redirect_uri="http://localhost:8080/callback"
    )

@router.post("/exchange-code", response_model=TokenResponse)
async def exchange_code(request: CodeExchangeRequest):
    auth_provider = get_auth_provider()
    try:
        tokens = await auth_provider.exchange_code(request.code)
        user_info = await auth_provider.validate_token(tokens['access_token'])
        if not user_info['valid']:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await subscription_service.get_or_create_user(user_info['user_id'], user_info['email'])
        subscription_status = await subscription_service.check_subscription_status(user)
        return TokenResponse(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            subscription_status=subscription_status['subscription_status'],
            trial_ends_at=subscription_status.get('trial_ends_at'),
            subscription_expires_at=subscription_status.get('expires_at')
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidationResponse)
async def validate_token(request: TokenValidationRequest):
    auth_provider = get_auth_provider()
    try:
        user_info = await auth_provider.validate_token(request.access_token)
        if not user_info['valid']:
            return ValidationResponse(valid=False, subscription_active=False, subscription_status="invalid")
        user = await subscription_service.get_or_create_user(user_info['user_id'], user_info['email'])
        subscription_status = await subscription_service.check_subscription_status(user)
        return ValidationResponse(
            valid=True,
            subscription_active=subscription_status['subscription_active'],
            subscription_status=subscription_status['subscription_status'],
            subscription_tier=subscription_status.get('subscription_tier'),
            trial_ends_at=subscription_status.get('trial_ends_at'),
            expires_at=subscription_status.get('expires_at')
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
