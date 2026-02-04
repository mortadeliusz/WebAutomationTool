# Cross-Service Architecture: Desktop App & Backend

> **Modus Operandi Compliance:** This document follows the "Architecture-first approach" and "Separation of concerns" principles from [MODUS_OPERANDI.md](./MODUS_OPERANDI.md).

## Overview

This document describes the complete architecture for the Web Automation Tool ecosystem, including the desktop application, backend API, authentication system, subscription management, configuration strategy, and security model.

---

## System Architecture

### **Two Independent Services:**

```
┌─────────────────────────┐         HTTP API          ┌──────────────────────────┐
│   Desktop Application   │ ◄────────────────────────► │     Backend API          │
│                         │                            │                          │
│ - Python/CustomTkinter  │                            │ - FastAPI                │
│ - Browser Automation    │                            │ - JWT Verification       │
│ - Local Execution       │                            │ - Subscription Mgmt      │
│ - Workflow Management   │                            │ - Lemon Squeezy Sync     │
│                         │                            │ - Signature Generation   │
└─────────────────────────┘                            └──────────────────────────┘
         │                                                        │
         │                                                        │
         ▼                                                        ▼
  User's Computer                                         Your Infrastructure
  (Windows/Mac/Linux)                                     (Docker/Cloud)
```

### **Service Boundaries:**

**Desktop Application:**
- **Responsibility:** User interface, workflow execution, local file management
- **Deployment:** Distributed to users via installers
- **Runtime:** User's machine
- **Dependencies:** CustomTkinter, Playwright, keyring, OS libraries
- **Repository:** `WebAutomationTool/`

**Backend API:**
- **Responsibility:** Authentication, subscription management, configuration
- **Deployment:** Docker containers on your infrastructure
- **Runtime:** Your servers
- **Dependencies:** FastAPI, Supabase SDK, JWT libraries, cryptography
- **Repository:** `WebAutomationTool-Backend/`

**Connection:** HTTP API only (no shared code)

---

## Repository Strategy

### **Separate Repositories (Recommended):**

```
WebAutomationTool/              # Desktop app repo
├── main.py
├── ui/
├── src/
├── config/
│   └── app_config.yaml
├── docs/
├── tests/
├── pyproject.toml
└── README.md

WebAutomationTool-Backend/      # Backend repo
├── app/
│   ├── main.py
│   ├── routes/
│   ├── models/
│   └── config/
├── config/
│   └── config.yaml
├── keys/
├── tests/
├── .env.example
├── Dockerfile
├── pyproject.toml
└── README.md
```

### **Why Separate Repositories:**

**1. Different Products:**
- Desktop: Runs on user machines, distributed via installers
- Backend: Runs on servers, deployed via Docker
- Fundamentally different deployment targets

**2. Zero Shared Logic:**
- Desktop: UI rendering, browser automation, local file management
- Backend: HTTP API, JWT verification, database queries
- No code overlap, only API cooperation

**3. Independent Development:**
- Desktop: Monthly releases, users update manually
- Backend: Daily deployments, instant updates
- Different release cycles require separation

**4. Clean Dependencies:**
- Desktop: `customtkinter`, `playwright`, `keyring`
- Backend: `fastapi`, `uvicorn`, `supabase`, `pyjwt`
- Zero dependency overlap

**5. Future Scalability:**
- Frontend developer → Desktop repo only
- Backend developer → Backend repo only
- Clear separation prevents confusion

### **Modus Operandi Compliance:**

✅ **Separation of concerns** - Different repos for different products  
✅ **No mixed concerns** - Clean dependency management  
✅ **Future maintainability** - Independent evolution  
✅ **Clear boundaries** - API contract is the interface  

---

## Configuration Management

### **Desktop App Configuration:**

```yaml
# config/app_config.yaml (Desktop App)

# Backend connection (only hardcoded value)
backend:
  url: "https://api.yourapp.com"
  timeout_seconds: 30
  retry_attempts: 3

# App metadata
app:
  name: "Web Automation Tool"
  version: "1.0.0"

# Development settings (excluded from production builds)
dev:
  debug_mode: false
  log_level: "INFO"
```

**What's Hardcoded:**
- ✅ Backend URL (you control this, rarely changes)
- ✅ App metadata (version, name)
- ✅ Network settings (timeouts, retries)

**What's NOT Hardcoded:**
- ❌ Supabase URL (comes from backend dynamically)
- ❌ Supabase anon key (comes from backend dynamically)
- ❌ Business rules (offline grace days, tier limits)
- ❌ Feature flags (comes from backend dynamically)

### **Backend Configuration:**

```bash
# backend/.env (Secrets - NEVER commit)

SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # SECRET
SUPABASE_JWT_SECRET=your-jwt-secret  # SECRET

LEMON_SQUEEZY_API_KEY=your-api-key  # SECRET
LEMON_SQUEEZY_WEBHOOK_SECRET=your-webhook-secret  # SECRET

DATABASE_URL=postgresql://...  # SECRET

SIGNATURE_PRIVATE_KEY_PATH=/path/to/private.pem  # SECRET
```

```yaml
# backend/config/config.yaml (Public settings - can commit)

app:
  subscription_sync_interval_days: 4
  offline_grace_days: 7

features:
  cloud_workflows: false
  ai_suggestions: false

signature:
  public_key: |
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
    -----END PUBLIC KEY-----
```

### **Dynamic Configuration Flow:**

```
Desktop App Launch
    ↓
Read: config/app_config.yaml → Get backend URL
    ↓
Call: GET /api/v1/public/config
    ↓
Backend Returns:
{
  "auth": {
    "provider": "supabase",
    "url": "https://xxx.supabase.co",
    "anon_key": "eyJhbGc..."
  },
  "app": {
    "offline_grace_days": 7
  },
  "features": {
    "cloud_workflows": false
  }
}
    ↓
Desktop App Uses Runtime Config
```

**Benefits:**
- ✅ Switch auth providers without app update
- ✅ Rotate anon keys instantly
- ✅ Change business rules (grace period) without app rebuild
- ✅ Toggle features dynamically

---

## Business Model

**Subscription-based SaaS:**
- Lower price point, shorter user commitment
- Easier to abandon project if needed (honest reasoning)
- Free tier for beta testing
- Free trial for new users

**Revenue Strategy:**
- Lemon Squeezy for payment processing
- Backend manages subscription state
- Client enforces feature limits based on tier

**Monetization Philosophy:**
- Focus on product quality over DRM
- Accept that determined pirates will crack it
- Signature verification stops 95% of casual tampering
- 5% who pirate wouldn't pay anyway

---

## Service Responsibilities

### **Desktop Application (Dumb Client):**

**What It Does:**
- ✅ Authenticate users via Supabase
- ✅ Store JWT + refresh token in OS keyring
- ✅ Send JWT to backend for subscription checks
- ✅ Cache signed subscription data
- ✅ Execute workflows locally
- ✅ Manage local files

**What It Does NOT Do:**
- ❌ Verify JWT signatures (backend does this)
- ❌ Manage subscriptions (backend does this)
- ❌ Store secrets (backend only)
- ❌ Business logic (backend decides)

### **Backend API (Smart Server):**

**What It Does:**
- ✅ Verify JWT signatures (local verification)
- ✅ Manage subscription state (database)
- ✅ Sync with Lemon Squeezy (webhooks + periodic)
- ✅ Sign subscription data (for client caching)
- ✅ Provide dynamic configuration
- ✅ Enforce business rules

**What It Does NOT Do:**
- ❌ Execute workflows (client does this locally)
- ❌ Manage user files (client does this locally)
- ❌ Browser automation (client does this locally)

---

## Authentication Flow

### **First-Time Login:**

```
User Opens App
    ↓
No Refresh Token in Keyring
    ↓
Show Login Screen
    ↓
User Enters Email/Password
    ↓
Desktop App → Supabase Auth
    ↓
Supabase Returns: JWT + Refresh Token
    ↓
Store in OS Keyring (encrypted by OS)
    ↓
Desktop App → Backend: GET /subscription/status (with JWT)
    ↓
Backend: Verify JWT → Check Subscription → Sign Data
    ↓
    ├─ Active? → Desktop App: Cache Signed Data → Launch Main App
    └─ Expired? → Desktop App: Show Subscription/Payment Screen
```

### **Subsequent Launches (Silent Auth):**

```
User Opens App
    ↓
Refresh Token Found in Keyring
    ↓
Show Loading ("Signing in...")
    ↓
Desktop App → Supabase: Exchange Refresh Token
    ↓
Supabase Returns: New JWT
    ↓
Update JWT in Keyring
    ↓
Desktop App → Backend: GET /subscription/status (with JWT)
    ↓
Backend: Verify JWT → Check Subscription → Sign Data
    ↓
Desktop App: Cache Signed Data → Launch App
```

### **No "Remember Me" Checkbox:**
- Always store refresh token (industry standard)
- User stays logged in until explicit logout
- Matches Slack, Discord, VS Code behavior
- Explicit "Logout" button in settings

---

## JWT Verification

### **How JWT Works:**

```
JWT Structure:
eyJhbGc...  .  eyJ1c2Vy...  .  SflKxwRJ...
   ↑              ↑              ↑
 Header        Payload       Signature

Signature = HMACSHA256(header + payload, SUPABASE_JWT_SECRET)
```

### **Attack Prevention:**

```
User tries to tamper:
1. Decode JWT
2. Change payload: {"sub": "victim-user-id"}
3. Re-encode JWT
4. Send to backend

Result:
- Signature doesn't match modified payload
- Backend verification FAILS
- User needs SUPABASE_JWT_SECRET (only on backend)
- Attack impossible
```

### **Backend Verification (Local):**

```python
# backend/app/routes/auth.py

import jwt

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def verify_jwt(token: str) -> str:
    """Verify JWT locally and return user_id"""
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return payload["sub"]  # user_id
    
    except jwt.InvalidSignatureError:
        raise HTTPException(401, "Invalid signature")
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
```

**Why Local Verification:**
- ✅ Fast (no network call to Supabase)
- ✅ Reliable (works if Supabase has issues)
- ✅ Industry standard
- ✅ Lower latency

---

## Subscription Management

### **Subscription Check Flow:**

```
App Launch
    ↓
Try: GET /api/v1/public/config (backend)
    ↓
    ├─ Success? → Backend is UP
    │                ↓
    │            Authenticate via Supabase
    │                ↓
    │            GET /subscription/status (with JWT)
    │                ↓
    │            Cache Signed Subscription
    │                ↓
    │            Launch App
    │
    └─ Failed? → Backend is DOWN
                    ↓
                Check Cached Subscription
                    ↓
                    ├─ Valid Signature + Not Expired? → Launch Offline Mode
                    └─ Invalid/Missing? → Show Error
```

### **Backend Subscription Sync:**

```
Client: GET /api/v1/subscription/status
    ↓
Backend: Check DB
    ↓
    ├─ Fresh (< 4 days)? → Return DB data
    │
    └─ Stale (≥ 4 days)? → Ping Lemon Squeezy API
                              ↓
                          Update DB
                              ↓
                          Return fresh data
```

**Sync Mechanisms:**
1. **Webhooks** - Real-time updates (subscription created/canceled/updated)
2. **Periodic Sync** - Backend checks Lemon Squeezy every 4 days (backup)
3. **Manual Refresh** - User-triggered sync (edge cases)

---

## Signed Configuration Cache

### **Universal Pattern for Secure Client-Side Caching:**

**Backend Signs Everything:**
```python
# backend/app/routes/config.py

@app.get("/api/v1/config/user")
async def get_user_config(authorization: str = Header(...)):
    """Return ALL user config, signed"""
    
    user_id = verify_jwt(authorization)
    subscription = await db.get_subscription(user_id)
    
    # Everything user needs
    data = {
        "subscription": {
            "status": subscription.status,
            "tier": subscription.tier,
            "expires_at": subscription.expires_at.isoformat()
        },
        "user": {
            "id": user_id,
            "email": subscription.email
        },
        "settings": {
            "offline_grace_days": public_config["app"]["offline_grace_days"],
            "max_workflows": get_tier_limits(subscription.tier)["max_workflows"]
        },
        "auth": {
            "provider": "supabase",
            "url": settings.supabase_url,
            "anon_key": settings.supabase_anon_key
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Sign everything with private key
    signature = sign_data(data)
    
    return {"data": data, "signature": signature}
```

**Desktop App Caches and Verifies:**
```python
# src/config/user_config.py

class UserConfig:
    PUBLIC_KEY_PEM = """..."""  # Hardcoded
    
    @classmethod
    def verify_signature(cls, data: dict, signature: str) -> bool:
        """Verify with public key"""
        # RSA signature verification
        # Returns True if valid, False if tampered
    
    @classmethod
    def get_cached(cls) -> Optional[dict]:
        """Get cached config with verification"""
        cache = json.loads(cls.CACHE_FILE.read_text())
        
        # Verify signature
        if not cls.verify_signature(cache["data"], cache["signature"]):
            cls.CACHE_FILE.unlink()  # Tampered!
            return None
        
        # Check age (grace period from signed data)
        grace_days = cache["data"]["settings"]["offline_grace_days"]
        age = datetime.now() - datetime.fromisoformat(cache["data"]["timestamp"])
        
        if age.days >= grace_days:
            return None  # Too old
        
        return cache["data"]
```

**Cached File:**
```json
// user_data/user_config_cache.json
{
  "data": {
    "subscription": {...},
    "user": {...},
    "settings": {
      "offline_grace_days": 7,
      "max_workflows": null
    },
    "auth": {...},
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "signature": "MEUCIQDx7mK..."
}
```

### **Why Asymmetric Signatures (RSA):**

**Backend:**
- Has: Private key (secret, never leaves backend)
- Does: Sign data with private key

**Desktop App:**
- Has: Public key (hardcoded, safe to commit)
- Does: Verify signature with public key

**User:**
- Can: Extract public key from app
- Cannot: Sign data (needs private key)
- Cannot: Forge signature (impossible without private key)

### **What's Protected:**

**User CANNOT:**
- ❌ Change subscription status
- ❌ Change tier
- ❌ Extend offline grace period
- ❌ Modify any cached value
- ❌ Fake timestamp

**User CAN:**
- ⚠️ Block backend via firewall (works for grace period only)
- ⚠️ Delete cache (app shows error)
- ⚠️ Decompile app and patch checks (accepted risk - 5% of users)

### **Security Philosophy:**

**Signature Verification:**
- ✅ Stops 95% of casual tampering
- ✅ Industry-standard approach
- ✅ Minimal complexity (~50 lines)

**Accepted Limitations:**
- ❌ Doesn't stop app decompilation/patching
- ❌ Doesn't stop determined pirates
- ✅ But those 5% wouldn't pay anyway

**Focus:**
- Product quality over DRM
- Customer service over piracy prevention
- 95% of honest users over 5% of pirates

---

## Offline Mode

### **What "Offline" Means:**

**NOT "No Internet":**
- App requires internet (browser automation needs websites)
- Offline mode = "Backend down, internet up"

**Use Cases:**
- Backend maintenance/outage
- Network hiccups during startup
- Temporary connectivity issues

### **Offline Behavior:**

**Scenario 1: Backend Down, Valid Cache (< 7 days)**
```
App Launch → Backend Unreachable → Check Cache → Valid Signature
    ↓
Launch App in Offline Mode
    ↓
Status Bar: "⚠️ Offline Mode - Last verified 2 days ago"
    ↓
✅ Create/edit/execute workflows (browser automation works)
❌ Sync to cloud (backend down)
❌ Verify subscription (using cache)
```

**Scenario 2: Backend Down, No Cache**
```
App Launch → Backend Unreachable → No Cache
    ↓
Error: "Cannot connect to service. Please check your connection."
    ↓
[Retry] [Exit]
```

**Scenario 3: Backend Down, Expired Cache (> 7 days)**
```
App Launch → Backend Unreachable → Cache Too Old
    ↓
Error: "Subscription data outdated. Please connect to verify."
    ↓
[Retry] [Exit]
```

### **Offline Grace Period:**

**7 Days Maximum:**
- Signed in cache (user can't extend)
- Prevents indefinite offline abuse
- Covers weekend outages, short vacations
- Industry standard (most SaaS apps use 7-14 days)

**Why 7 Days:**
- ✅ Covers backend maintenance windows
- ✅ Reasonable for temporary outages
- ✅ Limits abuse (canceled users get 1 week max)
- ❌ Not too short (1-2 days = poor UX)
- ❌ Not too long (30+ days = abuse potential)

---

## Backend API Specification

### **Endpoints:**

#### **1. Public Config (No Auth)**
```
GET /api/v1/public/config

Response:
{
  "auth": {
    "provider": "supabase",
    "url": "https://xxx.supabase.co",
    "anon_key": "eyJhbGc..."
  },
  "features": {
    "cloud_workflows": false
  },
  "version": "1.0.0"
}
```

#### **2. User Config (Auth Required)**
```
GET /api/v1/config/user
Headers: Authorization: Bearer <jwt>

Response:
{
  "data": {
    "subscription": {...},
    "user": {...},
    "settings": {...},
    "auth": {...},
    "timestamp": "..."
  },
  "signature": "..."
}
```

#### **3. Subscription Status (Auth Required)**
```
GET /api/v1/subscription/status
Headers: Authorization: Bearer <jwt>

Response:
{
  "data": {
    "user_id": "...",
    "status": "active",
    "tier": "standard",
    "expires_at": "...",
    "offline_grace_days": 7
  },
  "signature": "..."
}
```

#### **4. Force Sync (Auth Required)**
```
POST /api/v1/subscription/force-sync
Headers: Authorization: Bearer <jwt>

Action: Bypass staleness, always ping Lemon Squeezy
Response: Updated subscription
```

#### **5. Lemon Squeezy Webhook**
```
POST /api/v1/webhooks/lemon-squeezy
Headers: X-Signature: <webhook_signature>

Body: <lemon squeezy payload>
Action: Update subscription in DB
```

#### **6. Health Check**
```
GET /api/health

Response: {"status": "ok"}
```

### **FastAPI Auto-Generated Documentation:**

**Swagger UI (Interactive):**
```
http://localhost:8000/docs

- Auto-generated from code
- "Try it out" buttons
- Request/response examples
- Authentication testing
```

**ReDoc (Alternative):**
```
http://localhost:8000/redoc

- Same info, different UI
- Better for reading/printing
```

**OpenAPI JSON:**
```
http://localhost:8000/openapi.json

- Machine-readable spec
- Generate client SDKs
- Import to Postman
```

**No Manual Documentation Needed:**
- ✅ FastAPI generates Swagger automatically
- ✅ Just write good docstrings
- ✅ Pydantic models = automatic schemas

---

## Database Schema

```sql
-- Supabase: subscriptions table

CREATE TABLE subscriptions (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    
    -- Lemon Squeezy IDs
    lemon_squeezy_customer_id TEXT,
    lemon_squeezy_subscription_id TEXT,
    
    -- Subscription state
    subscription_status TEXT,  -- active, trialing, expired, canceled
    tier TEXT,                 -- free_trial, standard, pro
    
    -- Dates
    trial_ends_at TIMESTAMP,
    current_period_ends_at TIMESTAMP,
    canceled_at TIMESTAMP,
    
    -- Sync tracking
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_id ON subscriptions(user_id);
CREATE INDEX idx_lemon_customer ON subscriptions(lemon_squeezy_customer_id);
```

---

## Security Considerations

### **Supabase Anon Key (Public by Design):**

**Safe to Expose:**
- ✅ Designed for client-side apps
- ✅ Protected by Row Level Security (RLS)
- ✅ Can only do what RLS policies allow

**Real Security:**
- RLS policies (server-side)
- Backend JWT verification (server-side)
- Lemon Squeezy webhook signatures (server-side)

**Not Security:**
- ❌ Hiding anon key (impossible in client apps)
- ❌ Obfuscating URLs (easily discovered)

### **Quota Abuse Protection:**

**Supabase Built-in:**
- Rate limiting: 30 auth requests/hour per IP
- Email verification required
- SMTP limits: 3 emails/hour per user

**Attack Scenario:**
```
Attacker extracts anon key → Spams signups
    ↓
Rate limited to 30/hour per IP
    ↓
Needs 100+ IPs for impact
    ↓
Email verification blocks automation
    ↓
Not worth attacker's effort
```

### **Token Storage:**

**OS Keyring:**
- Windows: Credential Manager
- macOS: Keychain
- Linux: Secret Service API

**Why:**
- ✅ Encrypted by OS
- ✅ Industry standard
- ✅ No custom encryption needed

---

## Technology Stack

### **Desktop Application:**
- **UI:** CustomTkinter 5.2.2+
- **Async:** async-tkinter-loop 0.10.3+
- **Browser:** Playwright 1.57.0+
- **Data:** Pandas 2.3.3+
- **Auth:** Supabase SDK
- **Storage:** keyring library
- **HTTP:** httpx
- **Crypto:** cryptography library

### **Backend API:**
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Auth:** Supabase SDK, PyJWT
- **Database:** Supabase (PostgreSQL)
- **Payments:** Lemon Squeezy SDK
- **Crypto:** cryptography library

### **Infrastructure:**
- **Deployment:** Docker containers
- **Hosting:** Railway/Render/DigitalOcean (free tier initially)
- **CI/CD:** GitHub Actions

---

## Implementation Phases

### **Phase 1: Backend Setup (Week 1)**
1. Create `WebAutomationTool-Backend` repository
2. Setup FastAPI project structure
3. Implement JWT verification
4. Create Supabase database schema
5. Implement config endpoints
6. Deploy to free tier

### **Phase 2: Auth Integration (Week 2)**
1. Desktop: Add Supabase SDK
2. Desktop: Add keyring library
3. Desktop: Implement AuthManager
4. Desktop: Implement TokenStorage
5. Desktop: Create LoginPage UI
6. Test end-to-end auth flow

### **Phase 3: Subscription System (Week 3)**
1. Backend: Setup Lemon Squeezy
2. Backend: Implement webhook handler
3. Backend: Implement subscription sync
4. Backend: Generate RSA keys
5. Backend: Implement signature generation
6. Test subscription flow

### **Phase 4: Client Integration (Week 4)**
1. Desktop: Implement SubscriptionChecker
2. Desktop: Add signature verification
3. Desktop: Implement offline mode
4. Desktop: Add user config cache
5. Desktop: Update SubscriptionPage UI
6. Test all scenarios

**Total: ~4 weeks for complete system**

---

## Modus Operandi Compliance

### **✅ Architecture-First Approach:**
- Complete design before implementation
- All decisions documented with rationale
- Security model clearly defined

### **✅ Separation of Concerns:**
- Desktop: Dumb client (no business logic)
- Backend: Smart server (all verification)
- Clear boundaries via API contract

### **✅ Best Practices:**
- JWT verification (industry standard)
- Asymmetric signatures (proper crypto)
- OS keyring (secure storage)
- Separate repositories (clean separation)

### **✅ Technical Debt Awareness:**
- Signature verification doesn't stop app patching (acknowledged)
- Offline grace period prevents indefinite abuse
- No false sense of security

### **✅ Honest Assessment:**
- Risks clearly identified
- Limitations acknowledged
- Trade-offs documented
- Focus on 95% of users, not 5% of pirates

---

## References

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Lemon Squeezy API](https://docs.lemonsqueezy.com/)
- [Python Keyring Library](https://pypi.org/project/keyring/)
- [Cryptography Library](https://cryptography.io/)

---

*This architecture provides a secure, scalable foundation for subscription-based SaaS while maintaining clean separation of concerns and following industry best practices. All implementation follows principles established in [MODUS_OPERANDI.md](./MODUS_OPERANDI.md).*
