# Backend Setup Guide

## Prerequisites

- Python 3.10+
- PostgreSQL database (Supabase recommended)
- Supabase account
- Lemon Squeezy account (for payments)

## Local Development Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# Database
DB_CONNECTION_STRING=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

### 3. Run Database Migration

In Supabase SQL Editor, run:

```sql
-- Copy contents of migrations/001_initial_schema.sql
```

### 4. Start Development Server

```bash
uvicorn main:app --reload
```

API available at: http://localhost:8000
Docs available at: http://localhost:8000/docs

## Testing Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Get Auth Config

```bash
curl http://localhost:8000/auth/config
```

## Environment Variables

See `.env.example` for all required variables.

## Next Steps

- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Architecture Overview](ARCHITECTURE.md)
