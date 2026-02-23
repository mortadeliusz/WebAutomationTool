# API Documentation

Base URL: `http://localhost:8000` (local) or `https://your-api.railway.app` (production)

## Authentication Endpoints

### GET /auth/config

Get authentication configuration for desktop app.

**Response:**
```json
{
  "auth_url": "https://xxx.supabase.co/auth/v1/authorize",
  "client_id": "your_client_id",
  "redirect_uri": "http://localhost:8080/callback"
}
```

### POST /auth/exchange-code

Exchange authorization code for tokens.

**Request:**
```json
{
  "code": "authorization_code_from_callback"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "subscription_status": "trial",
  "trial_ends_at": "2025-02-01T00:00:00Z",
  "subscription_expires_at": null
}
```

### POST /auth/validate

Validate access token and check subscription.

**Request:**
```json
{
  "access_token": "eyJ..."
}
```

**Response:**
```json
{
  "valid": true,
  "subscription_active": true,
  "subscription_status": "trial",
  "subscription_tier": "pro",
  "trial_ends_at": "2025-02-01T00:00:00Z",
  "expires_at": null
}
```

## Subscription Endpoints

### POST /subscription/check

Force subscription check with Lemon Squeezy (future).

**Status:** Not implemented yet

### POST /subscription/webhook

Receive Lemon Squeezy webhook events (future).

**Status:** Not implemented yet

## Health Endpoints

### GET /

Root endpoint with API info.

### GET /health

Health check for monitoring.

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error message"
}
```

Status codes:
- 400: Bad request
- 401: Unauthorized
- 404: Not found
- 500: Internal server error
- 501: Not implemented
