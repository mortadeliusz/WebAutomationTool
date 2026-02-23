# Deployment Guide

## Railway Deployment (Recommended)

### 1. Create Railway Account

Sign up at https://railway.app

### 2. Create New Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init
```

### 3. Configure Environment Variables

In Railway dashboard, add all variables from `.env.example`:

```
ENVIRONMENT=production
AUTH_PROVIDER=supabase
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
DB_CONNECTION_STRING=...
TRIAL_DAYS=14
```

### 4. Deploy

```bash
railway up
```

### 5. Get Deployment URL

```bash
railway domain
```

Your API will be available at: `https://your-app.railway.app`

## Render Deployment (Alternative)

### 1. Create Render Account

Sign up at https://render.com

### 2. Create Web Service

- Connect GitHub repo
- Select `backend` folder as root
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Configure Environment Variables

Add all variables from `.env.example` in Render dashboard.

### 4. Deploy

Render auto-deploys on git push.

## Post-Deployment

### 1. Test Health Endpoint

```bash
curl https://your-api.railway.app/health
```

### 2. Update Desktop App

Update backend URL in desktop app:

```python
BACKEND_URL = "https://your-api.railway.app"
```

### 3. Configure Lemon Squeezy Webhook

In Lemon Squeezy dashboard:
- Webhook URL: `https://your-api.railway.app/subscription/webhook`
- Events: subscription_created, subscription_updated, subscription_cancelled

## Monitoring

### Railway

- View logs: `railway logs`
- View metrics: Railway dashboard

### Render

- View logs: Render dashboard
- View metrics: Render dashboard

## Scaling

Both Railway and Render auto-scale based on traffic.

## Costs

- Railway: Free tier available, pay-as-you-grow
- Render: Free tier available, $7/month for production
