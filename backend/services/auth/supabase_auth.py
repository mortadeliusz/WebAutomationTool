"""
Supabase authentication provider implementation
"""
from supabase import create_client, Client
from .base import AuthProvider
from config import settings
from typing import Dict

class SupabaseAuthProvider(AuthProvider):
    def __init__(self):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_key)
    
    def get_auth_url(self) -> str:
        return f"{settings.supabase_url}/auth/v1/authorize"
    
    def get_client_id(self) -> str:
        return settings.supabase_anon_key
    
    async def exchange_code(self, code: str) -> Dict:
        try:
            response = self.client.auth.exchange_code_for_session({"auth_code": code})
            return {"access_token": response.session.access_token, "refresh_token": response.session.refresh_token}
        except Exception as e:
            raise Exception(f"Failed to exchange code: {str(e)}")
    
    async def validate_token(self, token: str) -> Dict:
        try:
            user = self.client.auth.get_user(token)
            return {"valid": True, "user_id": user.user.id, "email": user.user.email}
        except Exception:
            return {"valid": False}
    
    async def refresh_token(self, refresh_token: str) -> Dict:
        try:
            response = self.client.auth.refresh_session(refresh_token)
            return {"access_token": response.session.access_token, "refresh_token": response.session.refresh_token}
        except Exception as e:
            raise Exception(f"Failed to refresh token: {str(e)}")
