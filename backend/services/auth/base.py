"""
Auth provider abstraction - Base interface
"""
from abc import ABC, abstractmethod
from typing import Dict

class AuthProvider(ABC):
    @abstractmethod
    def get_auth_url(self) -> str:
        pass
    
    @abstractmethod
    def get_client_id(self) -> str:
        pass
    
    @abstractmethod
    async def exchange_code(self, code: str) -> Dict:
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Dict:
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict:
        pass
