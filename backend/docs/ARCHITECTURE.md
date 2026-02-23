# Backend Architecture

## Overview

FastAPI backend providing authentication and subscription management for WebAutomationTool desktop app.

## Architecture Principles

- **Provider Abstraction** - Easy to swap auth/database/payment providers
- **Environment Configuration** - All config via .env
- **OAuth 2.0 Standard** - Loopback redirect for desktop apps
- **Trial Outside Payment** - 14-day trial managed in database
- **PostgreSQL + JSONB** - Structured columns + flexible metadata

## System Components

### API Layer (api/)

HTTP endpoints for desktop app communication.

- `auth.py` - Authentication endpoints
- `subscription.py` - Subscription management

### Services Layer (services/)

Business logic and provider abstractions.

- `auth/` - Auth provider abstraction (Supabase, Auth0, etc.)
- `database/` - Database provider abstraction
- `payment/` - Payment provider abstraction (Lemon Squeezy, Stripe, etc.)
- `subscription_service.py` - Trial and subscription logic

### Models Layer (models/)

Data validation and schemas.

- `schemas.py` - Pydantic models for requests/responses

### Database Layer

PostgreSQL with structured + JSONB hybrid approach.

## Authentication Flow

```
Desktop App → GET /auth/config → Returns Supabase auth URL
Desktop App → Opens browser → User authenticates
Supabase → Redirects to http://localhost:8080/callback?code=xxx
Desktop App → POST /auth/exchange-code → Returns tokens + subscription status
Desktop App → Stores tokens in keyring
```

## Subscription States

- `trial` - 14-day trial active
- `active` - Paid subscription active
- `expired` - Trial ended, no subscription
- `cancelled` - Subscription cancelled

## Provider Abstraction

### Auth Provider

```python
class AuthProvider(ABC):
    def get_auth_url() -> str
    def get_client_id() -> str
    async def exchange_code(code: str) -> Dict
    async def validate_token(token: str) -> Dict
    async def refresh_token(refresh_token: str) -> Dict
```

**Current:** Supabase
**Future:** Auth0, Firebase, Custom

### Database Provider

**Current:** Supabase PostgreSQL
**Future:** AWS RDS, Neon, Custom

### Payment Provider

**Current:** Lemon Squeezy
**Future:** Stripe, Paddle, Custom

## Database Schema

```sql
users (
    id UUID PRIMARY KEY,
    email TEXT,
    trial_started_at TIMESTAMP,
    trial_ends_at TIMESTAMP,
    subscription_status TEXT,
    subscription_tier TEXT,
    subscription_expires_at TIMESTAMP,
    lemon_customer_id TEXT,
    lemon_subscription_id TEXT,
    registered_devices JSONB,
    max_devices INTEGER,
    metadata JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

## Scalability

- **Stateless backend** - Horizontal scaling
- **PostgreSQL** - Scales to millions of rows
- **Async FastAPI** - High concurrency
- **Provider abstraction** - Easy to swap services

## Security

- **Secrets in .env** - Never committed
- **Token validation** - Server-side only
- **HTTPS only** - Production requirement
- **Webhook signatures** - Lemon Squeezy verification

## Future Enhancements

- Device limiting (3 devices per user)
- Lemon Squeezy webhook implementation
- Force subscription refresh
- Analytics and usage tracking
