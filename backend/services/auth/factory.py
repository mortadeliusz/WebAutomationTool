"""
Auth provider factory
"""
from .base import AuthProvider
from .supabase_auth import SupabaseAuthProvider
from config import settings

def get_auth_provider() -> AuthProvider:
    provider = settings.auth_provider.lower()
    if provider == "supabase":
        return SupabaseAuthProvider()
    else:
        raise ValueError(f"Unknown auth provider: {provider}")
