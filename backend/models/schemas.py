"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthConfig(BaseModel):
    auth_url: str
    client_id: str
    redirect_uri: str = "http://localhost:8080/callback"

class CodeExchangeRequest(BaseModel):
    code: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    subscription_status: str
    trial_ends_at: Optional[datetime] = None
    subscription_expires_at: Optional[datetime] = None

class TokenValidationRequest(BaseModel):
    access_token: str

class ValidationResponse(BaseModel):
    valid: bool
    subscription_active: bool
    subscription_status: str
    subscription_tier: Optional[str] = None
    trial_ends_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
