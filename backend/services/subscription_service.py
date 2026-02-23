"""
Subscription service - Business logic for trials and subscriptions
"""
from datetime import datetime, timedelta
from typing import Dict
from database import get_db_connection, get_db_cursor
from config import settings

class SubscriptionService:
    async def get_or_create_user(self, user_id: str, email: str) -> Dict:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return dict(user)
            now = datetime.utcnow()
            trial_ends_at = now + timedelta(days=settings.trial_days)
            cursor.execute("""
                INSERT INTO users (id, email, subscription_status, trial_started_at, trial_ends_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *
            """, (user_id, email, 'trial', now, trial_ends_at, now, now))
            return dict(cursor.fetchone())
    
    async def check_subscription_status(self, user: Dict) -> Dict:
        now = datetime.utcnow()
        if user['trial_ends_at'] and now < user['trial_ends_at']:
            return {
                "subscription_active": True,
                "subscription_status": "trial",
                "trial_ends_at": user['trial_ends_at'],
                "days_remaining": (user['trial_ends_at'] - now).days
            }
        if user['subscription_status'] == 'active':
            if user['subscription_expires_at'] and now < user['subscription_expires_at']:
                return {
                    "subscription_active": True,
                    "subscription_status": "active",
                    "subscription_tier": user.get('subscription_tier', 'pro'),
                    "expires_at": user['subscription_expires_at']
                }
        return {"subscription_active": False, "subscription_status": "expired"}
