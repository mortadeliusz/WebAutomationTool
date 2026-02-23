# Launcher Architecture - System Browser Authentication

## Overview

The launcher is a **lightweight authentication gateway** that runs before the main application. It opens the user's system browser for authentication via Firebase, validates access with the backend, passes user data to the main app, then exits cleanly.

---

## Architecture Principles

### **System Browser Authentication**
- Uses user's actual browser (Chrome, Edge, Firefox)
- User sees saved accounts and persistent login
- Familiar authentication environment
- No heavy dependencies (no Playwright bundle)

### **Backend-Driven Logic**
- Backend controls all authentication methods
- Backend validates tokens and checks subscriptions
- Backend can add new login providers without desktop app updates
- Desktop app is provider-agnostic

### **User Data Flow**
- Launcher receives user data from backend
- Passes to main app via command line args (base64 encoded)
- Main app has access to email, tier, features
- Enables feature gating and user info display

### **Minimal Launcher**
- ~100 lines of simple, synchronous code
- No token storage (no encryption complexity)
- No async complexity
- Clean separation of concerns

---

## File Structure

```
launcher/
├── __init__.py
├── launcher.py              # Entry point (system browser flow)
├── auth/
│   ├── __init__.py
│   ├── callback_server.py   # HTTP server for receiving auth callback
│   └── backend_client.py    # Token validation with backend

config.py                    # Shared config (BACKEND_URL)
main.py                      # Main application (receives user data)
```

---

## Authentication Flow

### **Step 1: Start Callback Server**
```python
callback_server = CallbackServer()  # OS assigns available port
callback_server.start()
```

**Purpose:** Listen for authentication callback from browser

**Details:**
- Starts HTTP server on `localhost` with OS-assigned port
- Port 0 = OS picks any available port (zero port conflicts)
- Handles GET requests to `/callback?token=...`
- Extracts token from query parameter
- Returns success HTML to browser

---

### **Step 2: Open System Browser**
```python
auth_url = f"{BACKEND_URL}/ui/auth/index.html?callback_port={callback_server.port}"
webbrowser.open(auth_url)
```

**Purpose:** Open auth page in user's default browser

**Details:**
- Uses Python's `webbrowser` module (standard library)
- Opens user's default browser (Chrome, Edge, Firefox, etc.)
- User sees saved Google accounts and persistent login
- Browser session cookies provide "remember me" functionality

---

### **Step 3: Auth Page Handles Authentication**

**Auth page (backend responsibility) does:**
1. Check if Firebase session exists (browser cookies)
2. If session valid → Get token → Send to callback → Redirect to welcome page
3. If no session → Show login buttons (Google, Email/Password, etc.)
4. User logs in → Get token → Send to callback → Redirect to welcome page

**Callback URL format:**
```
http://localhost:{PORT}/callback?token=firebase_id_token
```

**Desktop app just waits for callback.**

---

### **Step 4: Wait for Callback**
```python
token = callback_server.wait_for_callback(timeout=300)
```

**Purpose:** Block until token received or timeout

**Details:**
- Waits up to 5 minutes (300 seconds)
- Callback server extracts token from URL
- Returns token to launcher
- Daemon thread cleans up automatically (no explicit stop needed)

---

### **Step 5: Validate Token with Backend**
```python
backend_client = BackendClient(BACKEND_URL)
user_data = backend_client.validate_token(token)
```

**Purpose:** Verify token and get user access status

**Backend validates:**
- Token authenticity (Firebase verification)
- Token expiration
- User subscription status
- User access permissions

**Returns:**
```json
{
  "access": true/false,
  "user_id": "abc123",
  "email": "user@example.com",
  "tier": "premium",
  "features": ["basic_automation", "multi_browser"],
  "trial_days_left": null
}
```

---

### **Step 6: Pass User Data and Launch**

```python
if user_data.get('access'):
    launch_main_app(user_data)  # Pass entire user_data object
else:
    print("Access denied.")
    sys.exit(1)
```

**User data passing:**
```python
def launch_main_app(user_data):
    # Encode user data (base64 obfuscation)
    encoded = base64.b64encode(json.dumps(user_data).encode()).decode()
    
    # Launch with --session arg
    subprocess.Popen([
        sys.executable,
        str(main_app_path),
        '--session', encoded
    ])
```

**Main app receives:**
```python
# In main.py
def parse_user_data():
    if '--session' in sys.argv:
        idx = sys.argv.index('--session')
        decoded = base64.b64decode(sys.argv[idx + 1]).decode()
        return json.loads(decoded)
    return None

# In App.__init__
self.user_data = parse_user_data() or {}
```

---

## User Data Usage in Main App

**Available data:**
```python
self.user_data = {
    "email": "user@example.com",
    "tier": "premium",
    "user_id": "abc123",
    "features": ["basic_automation", "multi_browser"],
    "trial_days_left": null
}
```

**Usage examples:**
```python
# Display user email
email = self.user_data.get('email', 'User')

# Check tier
tier = self.user_data.get('tier', 'free')

# Feature gating
if 'multi_browser' in self.user_data.get('features', []):
    self.enable_multi_browser_feature()
```

---

## Production vs Development Output

**Development (running from source):**
- Shows all output and errors
- Useful for debugging

**Production (packaged executable):**
- Suppresses output for clean UX
- No confusing error messages for users

**Implementation:**
```python
if getattr(sys, 'frozen', False):
    # Production: suppress output
    subprocess.Popen([...], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
else:
    # Development: keep output
    subprocess.Popen([...])
```

---

## User Experience Flows

### **Flow 1: First Time User**
```
Launch app
    ↓
Browser opens to auth page
    ↓
User sees login options (Google, Email/Password)
    ↓
User clicks "Sign in with Google"
    ↓
User selects account from saved accounts
    ↓
Browser shows "Authentication complete, you can close this tab"
    ↓
User closes browser tab
    ↓
Main app launches with user data
```

**Time:** ~30-60 seconds (user-dependent)

---

### **Flow 2: Returning User (Session Exists)**
```
Launch app
    ↓
Browser opens to auth page
    ↓
Auth page detects valid session (instant)
    ↓
Auto-redirect to callback
    ↓
Browser shows "Authentication complete, you can close this tab"
    ↓
User closes browser tab
    ↓
Main app launches with user data
```

**Time:** ~5-10 seconds (mostly user closing tab)

---

### **Flow 3: No Access**
```
Launch app
    ↓
Browser opens → Auth completes
    ↓
Desktop: "Access denied."
    ↓
Launcher exits
    ↓
User must subscribe via web, then relaunch app
```

---

## Security Considerations

### **User Data Obfuscation**
- Base64 encoded (not encryption, just obfuscation)
- Not visible in plain text in process list
- Casual users can't easily manipulate
- Determined users can decode (acceptable for desktop app)

**What we're passing:**
- Email (not secret)
- Tier (not secret)
- User ID (not secret)
- Features list (not secret)

**What we're NOT passing:**
- Tokens (never!)
- Passwords (never!)
- Payment info (never!)

**Security model:**
- Desktop app is untrusted (user owns the machine)
- Backend enforces actual limits
- Feature gating is UX, not security

### **Callback Server**
- ✅ Listens only on localhost (127.0.0.1)
- ✅ Daemon thread (auto-cleanup)
- ✅ Timeout after 5 minutes
- ✅ Validates callback has token parameter

### **Token Handling**
- ✅ Token never logged
- ✅ Token transmitted via localhost only
- ✅ Token validated with backend immediately
- ✅ Token not stored (ephemeral)

### **Browser Session**
- ✅ User's browser manages session (Firebase standard)
- ✅ Refresh tokens in browser localStorage (Firebase handles)
- ✅ Desktop app never sees refresh tokens

---

## Logout Implementation

**Desktop side (main app):**
```python
def logout():
    """Logout user and exit application"""
    import webbrowser
    from config import BACKEND_URL
    
    webbrowser.open(f"{BACKEND_URL}/logout")
    sys.exit(0)
```

**Backend side:**
- `/logout` endpoint clears Firebase session
- Redirects to landing page
- User closes browser tab

**Next launch:** User must log in again (session cleared)

---

## Component Details

### **launcher.py**

**Responsibility:** Orchestrate authentication flow

**Key Features:**
- Simple synchronous flow (no async)
- System browser integration
- Callback server lifecycle
- Token validation
- User data passing (base64 encoded)
- Production vs development output handling
- Comprehensive logging

**Dependencies:**
- `webbrowser` - Open system browser (standard library)
- `subprocess` - Launch main app (standard library)
- `logging` - Structured logging (standard library)
- `base64` - User data encoding (standard library)

**Code:** ~100 lines

---

### **auth/callback_server.py**

**Responsibility:** Receive authentication callback from browser

**Key Features:**
- HTTP server on localhost with OS-assigned port
- Handles `/callback?token=...` requests
- Extracts token from query parameter
- Returns success HTML to browser
- Zero port conflicts (OS assigns available port)
- Timeout support (5 minutes default)
- Daemon thread (auto-cleanup)

**Code:** ~110 lines

---

### **auth/backend_client.py**

**Responsibility:** Validate token with backend

**Key Features:**
- HTTP POST to `/auth/validate`
- Retry logic (2 attempts, exponential backoff)
- Error handling (401 = invalid token, network errors)
- Timeout (10 seconds)

**Exceptions:**
- `TokenInvalidError` - Token invalid/expired (401)
- `BackendError` - Network/server error

**Code:** ~70 lines

---

## Design Decisions

### **Why System Browser?**
- ✅ No Playwright bundle (~300MB saved)
- ✅ User's actual browser with saved accounts
- ✅ Persistent login via browser cookies
- ✅ Simpler code (no async)

### **Why OS-Assigned Port?**
- ✅ Zero risk of port conflicts
- ✅ OS guarantees available port
- ✅ Simpler code (no retry loop)

### **Why Base64 Encoding?**
- ✅ Not visible in plain text
- ✅ Simple (no dependencies)
- ✅ Good enough for non-sensitive data
- ✅ Minimal complexity

### **Why Pass Entire user_data?**
- ✅ Future-proof (backend can add fields)
- ✅ Simple (one parameter)
- ✅ Flexible (main app decides what to use)

---

## Modus Operandi Compliance

### **✅ Architecture-First Approach**
- System browser = authentication (industry standard)
- No token storage (YAGNI principle)
- Backend-driven logic (flexible)

### **✅ Best Practices**
- Standard library where possible
- Minimal dependencies
- Provider-agnostic design
- Clean error handling
- Comprehensive logging

### **✅ Maintainability**
- Simple, linear flow
- Each component single responsibility
- Easy to understand and modify
- Well-documented
- ~280 lines total

### **✅ No Technical Debt**
- No async complexity
- No threading complexity (daemon thread only)
- No token storage complexity
- No browser automation hacks

---

**Will we be proud of this code in 6 months?** ✅ **YES**

---

*This launcher architecture provides a clean, maintainable authentication gateway using industry-standard patterns while maintaining simplicity and provider-agnostic design.*
