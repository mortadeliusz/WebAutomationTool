"""
Backend HTTP client
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TokenInvalidError(Exception):
    """Token is invalid or expired"""
    pass


class BackendError(Exception):
    """Backend communication failed"""
    pass


class BackendClient:
    """Handles all backend HTTP communication"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry logic"""
        session = requests.Session()
        
        # Retry on network errors (not on 401)
        retry = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def validate_token(self, token: str) -> dict:
        """
        Validate token and get subscription status
        
        Returns:
            {
                "access": bool,
                "user_id": str,
                "email": str,
                "tier": str,
                "features": list[str],
                "trial_days_left": int | None,
                "required_action": dict | None
            }
        
        Raises:
            TokenInvalidError: Token is invalid/expired (401)
            BackendError: Network/server error
        """
        try:
            response = self.session.post(
                f"{self.base_url}/auth/validate",
                json={"token": token},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 401:
                raise TokenInvalidError("Token is invalid or expired")
            
            if response.status_code != 200:
                raise BackendError(f"Backend returned {response.status_code}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise BackendError(f"Network error: {e}")
