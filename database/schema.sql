-- Phantom App Database Schema for Supabase (PostgreSQL)
-- Run this in the Supabase SQL Editor to create all tables

-- ============================================
-- PROMPT EVENTS — Core logging table
-- ============================================
CREATE TABLE IF NOT EXISTS prompt_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT NOT NULL,
    department TEXT NOT NULL,
    department_id TEXT NOT NULL,
    raw_prompt TEXT NOT NULL,
    rewritten_prompt TEXT,
    risk_category TEXT NOT NULL,
    risk_score FLOAT NOT NULL DEFAULT 0,
    severity_color TEXT NOT NULL DEFAULT 'YELLOW',
    confidence_score TEXT NOT NULL DEFAULT 'LOW',
    action_taken TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    policy_mode TEXT NOT NULL DEFAULT 'BALANCED',
    deployment_mode TEXT NOT NULL DEFAULT 'SHADOW',
    detected_elements_summary TEXT[] DEFAULT '{}',
    rewrite_explanation TEXT[]
);

-- ============================================
-- SHADOW MODE EVENTS — What would have happened
-- ============================================
CREATE TABLE IF NOT EXISTS shadow_mode_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT NOT NULL,
    raw_prompt TEXT NOT NULL,
    what_would_have_happened TEXT NOT NULL,
    risk_score FLOAT DEFAULT 0,
    risk_category TEXT,
    severity_color TEXT
);

-- ============================================
-- USER SESSIONS — Session-level tracking
-- ============================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_start TIMESTAMPTZ NOT NULL,
    session_end TIMESTAMPTZ,
    total_prompts INT DEFAULT 0,
    flagged_prompts INT DEFAULT 0
);

-- ============================================
-- FLAG EVENTS — User flag history
-- ============================================
CREATE TABLE IF NOT EXISTS flag_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    severity TEXT NOT NULL,
    incident_id UUID REFERENCES prompt_events(id)
);

-- ============================================
-- TRAINING ASSIGNMENTS — Micro-training tracking
-- ============================================
CREATE TABLE IF NOT EXISTS training_assignments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'pending',
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    score FLOAT
);

-- ============================================
-- QUIZ RESPONSES — Individual quiz answers
-- ============================================
CREATE TABLE IF NOT EXISTS quiz_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    selected_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL
);

-- ============================================
-- BADGES — Completion badges
-- ============================================
CREATE TABLE IF NOT EXISTS badges (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    badge_type TEXT DEFAULT 'completion'
);

-- ============================================
-- DETAIL ACCESS LOG — Supervisor audit trail
-- ============================================
CREATE TABLE IF NOT EXISTS detail_access_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    manager_id TEXT NOT NULL,
    incident_id UUID REFERENCES prompt_events(id),
    accessed_fields TEXT[]
);

-- ============================================
-- INDEXES for common queries
-- ============================================
CREATE INDEX IF NOT EXISTS idx_prompt_events_user ON prompt_events(user_id);
CREATE INDEX IF NOT EXISTS idx_prompt_events_dept ON prompt_events(department_id);
CREATE INDEX IF NOT EXISTS idx_prompt_events_category ON prompt_events(risk_category);
CREATE INDEX IF NOT EXISTS idx_prompt_events_action ON prompt_events(action_taken);
CREATE INDEX IF NOT EXISTS idx_prompt_events_created ON prompt_events(created_at);
CREATE INDEX IF NOT EXISTS idx_flag_events_user ON flag_events(user_id);
CREATE INDEX IF NOT EXISTS idx_flag_events_created ON flag_events(created_at);
CREATE INDEX IF NOT EXISTS idx_training_assignments_user ON training_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_shadow_events_user ON shadow_mode_events(user_id);
