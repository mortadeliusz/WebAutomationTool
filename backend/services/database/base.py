"""
Database provider abstraction - Base interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional

class DatabaseProvider(ABC):
    """Base interface for database providers"""
    
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def create_user(self, user_data: Dict) -> Dict:
        """Create new user"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, user_data: Dict) -> bool:
        """Update user data"""
        pass
