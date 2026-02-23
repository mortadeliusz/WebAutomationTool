"""
Configuration management using environment variables
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")
    auth_provider: str = os.getenv("AUTH_PROVIDER", "supabase")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    db_provider: str = os.getenv("DB_PROVIDER", "supabase")
    db_connection_string: str = os.getenv("DB_CONNECTION_STRING", "")
    payment_provider: str = os.getenv("PAYMENT_PROVIDER", "lemon_squeezy")
    lemon_squeezy_api_key: str = os.getenv("LEMON_SQUEEZY_API_KEY", "")
    lemon_squeezy_webhook_secret: str = os.getenv("LEMON_SQUEEZY_WEBHOOK_SECRET", "")
    lemon_squeezy_store_id: str = os.getenv("LEMON_SQUEEZY_STORE_ID", "")
    trial_days: int = int(os.getenv("TRIAL_DAYS", "14"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    class Config:
        env_file = ".env"

settings = Settings()
