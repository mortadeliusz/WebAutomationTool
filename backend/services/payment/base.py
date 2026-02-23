"""
Payment provider abstraction - Base interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional

class PaymentProvider(ABC):
    """Base interface for payment providers"""
    
    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        pass
    
    @abstractmethod
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        pass
    
    @abstractmethod
    def get_checkout_url(self, user_email: str) -> str:
        """Get checkout URL for user"""
        pass
