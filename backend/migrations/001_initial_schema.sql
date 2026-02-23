-- Initial database schema for WebAutomationTool backend

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    
    -- Trial tracking
    trial_started_at TIMESTAMP,
    trial_ends_at TIMESTAMP,
    
    -- Subscription
    subscription_status TEXT NOT NULL DEFAULT 'trial',
    subscription_tier TEXT DEFAULT 'pro',
    subscription_expires_at TIMESTAMP,
    
    -- Lemon Squeezy
    lemon_customer_id TEXT,
    lemon_subscription_id TEXT,
    last_subscription_check TIMESTAMP,
    
    -- Device limiting
    registered_devices JSONB DEFAULT '[]',
    max_devices INTEGER DEFAULT 3,
    
    -- Flexible metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status);
CREATE INDEX IF NOT EXISTS idx_users_trial_ends_at ON users(trial_ends_at);
CREATE INDEX IF NOT EXISTS idx_users_registered_devices ON users USING GIN (registered_devices);
