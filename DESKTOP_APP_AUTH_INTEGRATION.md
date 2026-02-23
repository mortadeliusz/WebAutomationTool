# Desktop App Authentication Integration Specification

## Executive Summary

This document specifies the **complete authentication implementation** for the desktop application. The backend authentication system is **fully implemented and tested**. This specification follows modus operandi principles: proper separation of concerns, maintainability-first design, and provider-agnostic architecture.

---

## Architecture Overview

### Design Principles

**Provider Agnostic:**
- Desktop app NEVER knows about Firebase, Auth0, or any specific auth provider
- Only knows: backend URL, token storage, HTTP communication
- Switching auth providers = ZERO desktop app code changes

**Token-Based Sessions:**
- Token stored locally (encrypted)
- Persists across app restarts
- Validated on every launch
- Explicit logout deletes token

**Single Responsibility:**
- Backend: Authentication, validation, subscription logic
- Desktop app: Token storage, UI orchestration, user flow

---

## Backend API Contract

### Base URLs

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://yourapp.railway.app
```

### Endpoint: POST /auth/validate

**Purpose:** Validate token AND check subscription status (single call)

**Request:**
```http
POST /auth/validate
Content-Type: application/json

{
  "token": "firebase_id_token_string"
}
```

**Response - Valid Token with Access (200):**
```json
{
  "access": true,
  "user_id": "abc123xyz",
  "email": "user@example.com",
  "tier": "premium",
  "features": ["basic_automation", "single_browser"],
  "trial_days_left": null
}
```

**Response - Valid Token without Access (200):**
```json
{
  "access": false,
  "user_id": "abc123xyz",
  "email": "user@example.com",
  "tier": "free",
  "features": [],
  "trial_days_left": 0,
  "required_action": {
    "type": "subscription_required",
    "message": "Your trial has ended. Subscribe to continue using the application.",
    "action_url": "https://yourapp.com/subscribe?user_id=abc123xyz&email=user@example.com"
  }
}
```

**Response - Invalid Token (401):**
```json
{
  "detail": "Invalid token"
}
```

---

## Required File Structure

```
desktop-app/
├── auth/
│   ├── __init__.py
│   ├── manager.py          # Orchestrates auth flow
│   ├── token_storage.py    # Token persistence
│   ├── backend_client.py   # HTTP communication
│   └── callback_server.py  # Localhost callback handler
├── config.py               # Configuration
└── main.py                 # Entry point
```

**Rationale:**
- Separation of concerns (each file has single responsibility)
- Testable (each component can be unit tested)
- Maintainable (clear boundaries between components)
- Scalable (easy to add features without touching other components)

---

## Component 1: Token Storage

**File:** `auth/token_storage.py`

**Responsibility:** Persist token securely on disk

**Interface:**
```python
class TokenStorage:
    """Handles secure token persistence"""
    
    def save_token(self, token: str) -> None:
        """
        Save token to disk with encryption
        
        Args:
            token: Firebase ID token string
            
        Raises:
            StorageError: If save fails
        """
        
    def load_token(self) -> str | None:
        """
        Load token from disk
        
        Returns:
            Token string or None if not found/invalid
        """
        
    def delete_token(self) -> None:
        """
        Delete token from disk
        
        Raises:
            StorageError: If delete fails (non-critical)
        """
```

**Implementation Requirements:**

1. **Storage Location:**
   - Windows: `%APPDATA%/WebAutomationTool/token.enc`
   - macOS: `~/Library/Application Support/WebAutomationTool/token.enc`
   - Linux: `~/.config/WebAutomationTool/token.enc`

2. **Encryption:**
   - Use `cryptography.fernet` for symmetric encryption
   - Generate key from machine-specific data (e.g., MAC address hash)
   - Store encrypted token, not plaintext

3. **File Permissions:**
   - Unix: chmod 600 (user read/write only)
   - Windows: Set ACL to current user only

4. **Error Handling:**
   - Gracefully handle missing files (return None)
   - Gracefully handle corrupted files (delete and return None)
   - Log errors but don't crash

**Dependencies:**
```python
from cryptography.fernet import Fernet
import os
from pathlib import Path
```

---

## Component 2: Backend Client

**File:** `auth/backend_client.py`

**Responsibility:** HTTP communication with backend

**Interface:**
```python
class BackendClient:
    """Handles all backend HTTP communication"""
    
    def __init__(self, base_url: str):
        """
        Initialize client
        
        Args:
            base_url: Backend URL (e.g., http://localhost:8000)
        """
        self.base_url = base_url
    
    def validate_token(self, token: str) -> dict:
        """
        Validate token and get subscription status
        
        Args:
            token: Firebase ID token
            
        Returns:
            {
                "access": bool,
                "user_id": str,
                "email": str,
                "tier": str,
                "features": list[str],
                "trial_days_left": int | None
            }
        
        Raises:
            TokenInvalidError: Token is invalid/expired (401)
            BackendError: Network/server error
        """
```

**Implementation Requirements:**

1. **HTTP Library:**
   - Use `requests` library
   - Set timeout: 10 seconds
   - Set headers: `Content-Type: application/json`

2. **Retry Logic:**
   - Retry on network errors: 2 attempts
   - Exponential backoff: 1s, 2s
   - Don't retry on 401 (invalid token)

3. **Error Handling:**
   - 401 → Raise `TokenInvalidError`
   - Network errors → Raise `BackendError`
   - Timeout → Raise `BackendError`
   - Invalid JSON → Raise `BackendError`

4. **Logging:**
   - Log all requests (URL, method)
   - Log all responses (status, body)
   - Never log token values

**Dependencies:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
```

**Custom Exceptions:**
```python
class TokenInvalidError(Exception):
    """Token is invalid or expired"""
    pass

class BackendError(Exception):
    """Backend communication failed"""
    pass
```

---

## Component 3: Callback Server

**File:** `auth/callback_server.py`

**Responsibility:** Receive authentication callback from browser

**Interface:**
```python
class CallbackServer:
    """HTTP server for receiving auth callbacks"""
    
    def __init__(self, port: int = 8080):
        """
        Initialize callback server
        
        Args:
            port: Port to listen on (default 8080)
        """
        self.port = port
        self.received_data = None
    
    def start(self) -> None:
        """Start HTTP server on localhost"""
    
    def wait_for_callback(self, timeout: int = 300) -> str:
        """
        Wait for browser callback
        
        Args:
            timeout: Max seconds to wait (default 300)
            
        Returns:
            Token string from callback
        
        Raises:
            TimeoutError: No callback within timeout
            CallbackError: Invalid callback data (no token)
        """
    
    def stop(self) -> None:
        """Stop HTTP server"""
```

**Callback URL Format:**
```
http://localhost:8080/callback?token=firebase_id_token
```

**Implementation Notes:**
- Callback contains ONLY the token
- Desktop app extracts token and validates with backend
- Desktop app calls `/auth/validate` to get subscription data

**Implementation Requirements:**

1. **HTTP Server:**
   - Use `http.server.HTTPServer`
   - Listen only on 127.0.0.1 (localhost)
   - Handle GET requests to `/callback`

2. **Response to Browser:**
   ```html
   <html>
   <body style="font-family: sans-serif; text-align: center; padding: 40px;">
       <h1>✅ Authentication Complete!</h1>
       <p>You can close this window and return to the app.</p>
       <script>setTimeout(() => window.close(), 2000);</script>
   </body>
   </html>
   ```

3. **Port Conflict Handling:**
   - If port 8080 in use, try 8081, 8082, etc.
   - Max 10 attempts
   - Raise error if all ports in use

4. **Timeout:**
   - Default: 5 minutes (300 seconds)
   - Use threading.Event for clean timeout

5. **Security:**
   - Only accept connections from localhost
   - Validate callback has required parameters
   - Stop server immediately after receiving callback

**Dependencies:**
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
```

---

## Component 4: Auth Manager

**File:** `auth/manager.py`

**Responsibility:** Orchestrate entire authentication flow

**Interface:**
```python
class AuthManager:
    """Main authentication orchestrator"""
    
    def __init__(self, backend_url: str):
        """
        Initialize auth manager
        
        Args:
            backend_url: Backend URL
        """
        self.backend_client = BackendClient(backend_url)
        self.token_storage = TokenStorage()
    
    def authenticate(self) -> dict:
        """
        Main authentication flow
        
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
            AuthenticationError: Authentication failed
        """
    
    def logout(self) -> None:
        """Delete stored token"""
```

**Authentication Flow Logic:**

```python
def authenticate(self) -> dict:
    # Step 1: Try to load stored token
    token = self.token_storage.load_token()
    
    if token:
        # Step 2: Validate with backend
        try:
            user_data = self.backend_client.validate_token(token)
            # Token valid, return user data
            return user_data
        except TokenInvalidError:
            # Token expired/invalid, delete and continue to browser auth
            self.token_storage.delete_token()
    
    # Step 3: No token or invalid token -> browser authentication
    return self._browser_auth()

def _browser_auth(self) -> dict:
    # Step 1: Start callback server
    callback_server = CallbackServer(port=8080)
    callback_server.start()
    
    # Step 2: Open browser to auth page
    auth_url = f"{self.backend_client.base_url}/ui/auth/index.html?callback_port={callback_server.port}"
    webbrowser.open(auth_url)
    
    # Step 3: Wait for callback with token
    try:
        token = callback_server.wait_for_callback(timeout=300)
    finally:
        callback_server.stop()
    
    # Step 4: Validate token with backend to get subscription data
    user_data = self.backend_client.validate_token(token)
    
    # Step 5: Store token for future use
    self.token_storage.save_token(token)
    
    return user_data
```

**Dependencies:**
```python
import webbrowser
from .backend_client import BackendClient, TokenInvalidError
from .token_storage import TokenStorage
from .callback_server import CallbackServer
```

---

## Component 5: Configuration

**File:** `config.py`

**Responsibility:** Centralized configuration

**Content:**
```python
import os

# Backend URL
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"  # Development default
)

# Callback server port
CALLBACK_PORT = int(os.getenv("CALLBACK_PORT", "8080"))

# Token storage directory
TOKEN_STORAGE_DIR = os.getenv(
    "TOKEN_STORAGE_DIR",
    None  # None = use platform default
)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

**Production Configuration:**
```bash
# Set environment variables
export BACKEND_URL=https://yourapp.railway.app
export LOG_LEVEL=WARNING
```

---

## Component 6: Main Entry Point

**File:** `main.py`

**Responsibility:** Application entry point

**Implementation:**
```python
import sys
import logging
from auth.manager import AuthManager
from config import BACKEND_URL, LOG_LEVEL

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def show_subscription_prompt(user_data: dict) -> None:
    """Show subscription required message"""
    # Desktop app decides implementation:
    # - Dialog, full screen, or notification?
    # - Handle required_action if present?
    # - Open browser automatically or show button?
    
    print(f"\n{'='*60}")
    print("SUBSCRIPTION REQUIRED")
    print(f"{'='*60}")
    print(f"Email: {user_data['email']}")
    print(f"Current Tier: {user_data['tier']}")
    if user_data.get('trial_days_left'):
        print(f"Trial Days Remaining: {user_data['trial_days_left']}")
    print("\nPlease subscribe to continue using the application.")
    print(f"{'='*60}\n")

def run_app(user_data: dict) -> None:
    """Main application logic"""
    logger.info(f"Starting app for user: {user_data['email']}")
    
    print(f"\n{'='*60}")
    print("WEBAUTOMATIONTOOL")
    print(f"{'='*60}")
    print(f"User: {user_data['email']}")
    print(f"Tier: {user_data['tier']}")
    print(f"Features: {', '.join(user_data['features'])}")
    print(f"{'='*60}\n")
    
    # Your application logic here
    # ...

def main() -> None:
    """Application entry point"""
    logger.info("Application starting")
    
    # Initialize auth manager
    auth_manager = AuthManager(BACKEND_URL)
    
    # Authenticate
    try:
        logger.info("Authenticating user...")
        user_data = auth_manager.authenticate()
        logger.info(f"Authentication successful: {user_data['email']}")
    except Exception as e:
        logger.error(f"Authentication failed: {e}", exc_info=True)
        print(f"\nAuthentication failed: {e}")
        print("Please check your internet connection and try again.\n")
        sys.exit(1)
    
    # Check access and handle required actions
    # Desktop app decides: check required_action first or access first?
    # See "Response Field: required_action" section for guidelines
    if not user_data['access']:
        logger.warning(f"User {user_data['email']} has no access")
        show_subscription_prompt(user_data)
        sys.exit(0)
    
    # Run application
    try:
        run_app(user_data)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nApplication closed.")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nApplication error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Error Handling Strategy

### Token Invalid/Expired
```python
try:
    user_data = backend_client.validate_token(token)
except TokenInvalidError:
    # Delete invalid token
    token_storage.delete_token()
    # Re-authenticate via browser
    user_data = auth_manager.authenticate()
```

### Backend Unreachable
```python
try:
    user_data = backend_client.validate_token(token)
except BackendError as e:
    logger.error(f"Backend unreachable: {e}")
    print("Cannot connect to server. Please check your internet connection.")
    sys.exit(1)
```

### Callback Timeout
```python
try:
    callback_data = callback_server.wait_for_callback(timeout=300)
except TimeoutError:
    logger.warning("Authentication timeout")
    print("Authentication timed out. Please try again.")
    sys.exit(1)
```

### No Subscription Access
```python
user_data = auth_manager.authenticate()

if not user_data['access']:
    show_subscription_prompt(user_data)
    sys.exit(0)
```

---

## Response Field: required_action

### Overview

When `access=false`, backend MAY include a `required_action` field indicating user must complete an action before using the app.

### Structure

```json
{
  "type": "subscription_required",
  "message": "Your trial has ended. Subscribe to continue using the application.",
  "action_url": "https://yourapp.com/subscribe?user_id=123&email=user@example.com"
}
```

### Fields

- **type** (string): Action type identifier
  - `subscription_required` - Trial ended or subscription expired
  - `payment_failed` - Payment method needs updating
  - `account_suspended` - Account suspended by admin
  - Future types can be added without breaking changes

- **message** (string): User-facing message to display
  - Clear explanation of the issue
  - Actionable language

- **action_url** (string): URL to open in browser to resolve issue
  - Pre-filled with user context (user_id, email)
  - Leads to checkout, payment update, or support page

### Recommended Behavior

**When `required_action` is present:**

1. **Display the message** to user (dialog, full screen, notification - your choice)
2. **Open action_url** in system browser
3. **Block app execution** until issue is resolved
4. **Exit or wait** for user to restart app after completing action

**Priority handling:**
```python
# Check required_action first (highest priority)
if user_data.get('required_action'):
    # Handle blocking action
    # Desktop app decides: dialog? full screen? notification?
    pass

# Then check access (fallback)
if not user_data['access']:
    # Handle generic no-access case
    pass
```

### Implementation Freedom

Desktop app team decides:
- UI presentation (dialog, full screen, banner)
- User flow (block immediately, show countdown, allow limited access)
- Error handling (retry logic, offline mode)
- Message formatting (plain text, rich text, localization)

### Example Handling

```python
# Example only - not prescriptive
user_data = auth_manager.authenticate()

if user_data.get('required_action'):
    action = user_data['required_action']
    
    # Show message (your UI choice)
    show_message(action['message'])
    
    # Open browser (standard)
    import webbrowser
    webbrowser.open(action['action_url'])
    
    # Block app (your choice: exit, wait, limited mode)
    sys.exit(0)
```

---

## Logout Implementation

### Desktop App UI
```python
# Add logout button/menu item
def on_logout_clicked():
    """Handle logout button click"""
    auth_manager.logout()
    print("Logged out successfully. Please restart the application.")
    sys.exit(0)

# AuthManager.logout()
def logout(self) -> None:
    """Logout user by deleting stored token"""
    self.token_storage.delete_token()
    logger.info("User logged out")
```

**No backend call needed** - logout is purely local (delete token).

---

## Periodic Subscription Checks

**Requirement:** Check subscription status every hour while app is running

**Implementation:**
```python
import threading
import time

def start_periodic_subscription_check(auth_manager: AuthManager, interval: int = 3600):
    """
    Start background thread to check subscription periodically
    
    Args:
        auth_manager: AuthManager instance
        interval: Check interval in seconds (default 3600 = 1 hour)
    """
    def check_subscription():
        while True:
            time.sleep(interval)
            
            token = auth_manager.token_storage.load_token()
            if not token:
                continue
            
            try:
                user_data = auth_manager.backend_client.validate_token(token)
                
                if not user_data['access']:
                    logger.warning("Subscription expired during session")
                    print("\n⚠️  Your subscription has expired.")
                    print("Please renew to continue using the application.\n")
                    # Optionally: pause app functionality or exit
                    
            except Exception as e:
                logger.error(f"Periodic subscription check failed: {e}")
                # Don't crash app on check failure
    
    # Start daemon thread
    thread = threading.Thread(target=check_subscription, daemon=True)
    thread.start()
    logger.info(f"Started periodic subscription check (interval: {interval}s)")

# In main.py, after successful authentication:
start_periodic_subscription_check(auth_manager, interval=3600)
```

---

## Testing Strategy

### Unit Tests

**test_token_storage.py:**
```python
import pytest
from auth.token_storage import TokenStorage

def test_save_and_load_token(tmp_path):
    storage = TokenStorage(storage_dir=tmp_path)
    storage.save_token("test_token_123")
    assert storage.load_token() == "test_token_123"

def test_delete_token(tmp_path):
    storage = TokenStorage(storage_dir=tmp_path)
    storage.save_token("test_token_123")
    storage.delete_token()
    assert storage.load_token() is None

def test_load_nonexistent_token(tmp_path):
    storage = TokenStorage(storage_dir=tmp_path)
    assert storage.load_token() is None
```

**test_backend_client.py:**
```python
import pytest
from unittest.mock import Mock, patch
from auth.backend_client import BackendClient, TokenInvalidError, BackendError

def test_validate_token_success():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access": True,
            "user_id": "123",
            "email": "test@example.com",
            "tier": "premium",
            "features": ["feature1"],
            "trial_days_left": None
        }
        
        client = BackendClient("http://localhost:8000")
        result = client.validate_token("valid_token")
        
        assert result["access"] is True
        assert result["tier"] == "premium"

def test_validate_token_invalid():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 401
        
        client = BackendClient("http://localhost:8000")
        
        with pytest.raises(TokenInvalidError):
            client.validate_token("invalid_token")

def test_validate_token_network_error():
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        client = BackendClient("http://localhost:8000")
        
        with pytest.raises(BackendError):
            client.validate_token("token")
```

### Integration Tests

**test_auth_flow.py:**
```python
import pytest
from auth.manager import AuthManager

@pytest.mark.integration
def test_full_auth_flow_with_valid_token(tmp_path):
    """Test auth flow when valid token exists"""
    # Setup
    storage = TokenStorage(storage_dir=tmp_path)
    storage.save_token("valid_token")
    
    # Mock backend to return success
    with patch('auth.backend_client.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access": True,
            "user_id": "123",
            "email": "test@example.com",
            "tier": "premium",
            "features": ["feature1"],
            "trial_days_left": None
        }
        
        # Execute
        auth_manager = AuthManager("http://localhost:8000")
        user_data = auth_manager.authenticate()
        
        # Verify
        assert user_data["access"] is True
        assert user_data["email"] == "test@example.com"

@pytest.mark.integration
@pytest.mark.manual
def test_full_auth_flow_browser():
    """Manual test: Full browser authentication flow"""
    # This test requires manual interaction
    # 1. Ensure backend is running
    # 2. Run test
    # 3. Complete authentication in browser
    # 4. Verify token is stored
    
    auth_manager = AuthManager("http://localhost:8000")
    user_data = auth_manager.authenticate()
    
    assert user_data["access"] is True
    assert "user_id" in user_data
    assert "email" in user_data
```

---

## Security Considerations

### Token Storage
- ✅ Encrypt token on disk using `cryptography.fernet`
- ✅ File permissions: user-only (chmod 600 on Unix)
- ✅ Never log token values
- ✅ Clear token from memory after use
- ✅ Use machine-specific encryption key

### Network Communication
- ✅ Use HTTPS in production
- ✅ Validate SSL certificates (don't disable verification)
- ✅ Timeout all requests (10 seconds)
- ✅ No sensitive data in URLs (token in POST body only)
- ✅ Log requests but never log tokens

### Callback Server
- ✅ Listen only on localhost (127.0.0.1)
- ✅ Timeout after 5 minutes
- ✅ Stop server immediately after callback
- ✅ Validate callback has required parameters
- ✅ Return simple HTML (no XSS vulnerabilities)

---

## Dependencies

### Required Packages
```bash
pip install requests cryptography
```

### Optional (Recommended)
```bash
pip install pytest pytest-mock  # For testing
```

### Full requirements.txt
```
requests>=2.31.0
cryptography>=41.0.0
pytest>=7.4.0
pytest-mock>=3.11.0
```

---

## Production Deployment Checklist

- [ ] Backend URL configured via environment variable
- [ ] Token storage uses encryption
- [ ] File permissions set correctly (chmod 600)
- [ ] HTTPS enforced in production
- [ ] SSL certificate validation enabled
- [ ] Error messages user-friendly (no stack traces to user)
- [ ] Logging configured (file + console)
- [ ] Log rotation configured
- [ ] Retry logic implemented for network calls
- [ ] Timeout values appropriate for production
- [ ] Callback server handles port conflicts
- [ ] Logout functionality tested
- [ ] Periodic subscription check implemented
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Manual browser auth flow tested

---

## Critical Implementation Notes

### 1. Callback Server Returns Token Only

**Callback contains only the token:**
```
http://localhost:8080/callback?token=firebase_id_token
```

**Desktop app extracts token and validates with backend.**

No other data in callback URL - keeps it simple and secure.

---

### 2. Provider-Agnostic Design Validation

**Test:** Can you switch from Firebase to Auth0 without changing desktop app code?

**Checklist:**
- [ ] No "firebase" mentioned in desktop app code
- [ ] No hardcoded auth provider URLs
- [ ] Token treated as opaque string (no parsing)
- [ ] Only backend URL configured
- [ ] Only `/auth/validate` endpoint used for validation

**If all checked:** ✅ Provider-agnostic design achieved

---

### 3. Error Messages

**User-Facing Errors (Simple):**
- "Cannot connect to server. Please check your internet connection."
- "Authentication timed out. Please try again."
- "Your subscription has expired. Please renew to continue."

**Developer Logs (Detailed):**
- "Backend validation failed: 401 Unauthorized"
- "Token storage error: Permission denied on /path/to/token.enc"
- "Callback server failed to start: Port 8080 already in use"

**Never show stack traces to users** - log them for debugging.

---

## Reference Implementation

**See:** `WebAutomationTool-API/mock_desktop_app.py`

This file demonstrates:
- HTTP server for callback
- Browser opening
- Callback handling
- Parameter parsing

**Use as reference** for callback server implementation.

---

## Success Criteria

Desktop app implementation is complete when:

- [ ] User can authenticate via browser (email/password + Google)
- [ ] Token persists across app restarts
- [ ] Token validated on every app launch
- [ ] Subscription status checked correctly
- [ ] Access denied when subscription expired
- [ ] Logout deletes token and requires re-authentication
- [ ] No auth provider mentioned in code (provider-agnostic)
- [ ] All error cases handled gracefully
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual browser flow tested
- [ ] Works in both development and production
- [ ] Periodic subscription checks working
- [ ] Logging configured properly
- [ ] Security checklist complete

---

## Architecture Validation

### Separation of Concerns ✅
- Token storage: Isolated in `token_storage.py`
- HTTP communication: Isolated in `backend_client.py`
- Callback handling: Isolated in `callback_server.py`
- Orchestration: Isolated in `manager.py`
- Configuration: Isolated in `config.py`

### Maintainability ✅
- Each component has single responsibility
- Clear interfaces between components
- Comprehensive error handling
- Extensive logging
- Well-documented

### Scalability ✅
- Easy to add new auth providers (backend change only)
- Easy to add new features (extend components)
- Easy to add new storage backends (implement TokenStorage interface)
- Easy to add new validation logic (backend change only)

### Best Practices ✅
- No hardcoded credentials
- No mixed concerns
- Proper error handling
- Security-first design
- Testable architecture

---

**END OF SPECIFICATION**

This document contains everything needed to implement desktop app authentication following modus operandi principles. No assumptions, no shortcuts, no technical debt.
