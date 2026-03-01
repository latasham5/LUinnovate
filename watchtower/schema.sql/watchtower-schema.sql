-- ═══════════════════════════════════════════════════════════════════════
-- The Watchtower — Supabase PostgreSQL Schema
-- Run in Supabase SQL Editor or as a migration.
-- ═══════════════════════════════════════════════════════════════════════

-- Enums
CREATE TYPE severity_color AS ENUM ('yellow', 'orange', 'red');
CREATE TYPE deployment_mode AS ENUM ('live', 'shadow');
CREATE TYPE policy_mode     AS ENUM ('block', 'warn', 'log_only');
CREATE TYPE action_taken    AS ENUM ('allowed', 'warned', 'blocked', 'redacted');

-- 1. Flag Events (core audit table)
CREATE TABLE flag_events (
    incident_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp        TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id          TEXT NOT NULL,
    department_id    TEXT NOT NULL,
    risk_category    TEXT NOT NULL,
    action_taken     action_taken NOT NULL,
    policy_version   TEXT NOT NULL,
    confidence_score DOUBLE PRECISION CHECK (confidence_score BETWEEN 0 AND 1),
    severity_color   severity_color NOT NULL,
    deployment_mode  deployment_mode NOT NULL,
    policy_mode      policy_mode NOT NULL,
    raw_prompt       TEXT,
    summary          TEXT,
    reset            BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_flags_user      ON flag_events (user_id, timestamp);
CREATE INDEX idx_flags_dept      ON flag_events (department_id, timestamp);
CREATE INDEX idx_flags_category  ON flag_events (risk_category, timestamp);
CREATE INDEX idx_flags_action    ON flag_events (action_taken, timestamp);
CREATE INDEX idx_flags_severity  ON flag_events (severity_color, timestamp);

-- 2. User Sessions
CREATE TABLE user_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         TEXT NOT NULL,
    session_start   TIMESTAMPTZ NOT NULL,
    session_end     TIMESTAMPTZ NOT NULL,
    total_prompts   INTEGER NOT NULL DEFAULT 0,
    flagged_prompts INTEGER NOT NULL DEFAULT 0
);

-- 3. Shadow Mode Events
CREATE TABLE shadow_mode_events (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                   TEXT NOT NULL,
    raw_prompt                TEXT NOT NULL,
    what_would_have_happened  TEXT NOT NULL,
    timestamp                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Incident Reports
CREATE TABLE incident_reports (
    incident_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          TEXT NOT NULL,
    prompt_summary   TEXT,
    risk_category    TEXT NOT NULL,
    action_taken     action_taken NOT NULL,
    policy_version   TEXT NOT NULL,
    confidence_score DOUBLE PRECISION,
    timestamp        TIMESTAMPTZ NOT NULL DEFAULT now(),
    severity_color   severity_color NOT NULL
);

-- 5. Incident Tickets
CREATE TABLE incident_tickets (
    ticket_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incident_reports(incident_id),
    system      TEXT DEFAULT 'internal',
    created_at  TIMESTAMPTZ DEFAULT now(),
    status      TEXT DEFAULT 'open',
    severity    severity_color
);

-- 6. Escalation Rules
CREATE TABLE escalation_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_id   TEXT NOT NULL,
    incident_type   TEXT NOT NULL,
    notify_manager  BOOLEAN DEFAULT TRUE,
    notify_security BOOLEAN DEFAULT FALSE,
    auto_ticket     BOOLEAN DEFAULT FALSE,
    UNIQUE (department_id, incident_type)
);

-- 7. User Flag History
CREATE TABLE user_flag_history (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    severity      severity_color NOT NULL,
    timestamp     TIMESTAMPTZ NOT NULL DEFAULT now(),
    reset         BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_ufh_user ON user_flag_history (user_id, timestamp);

-- 8. Flag Count Resets
CREATE TABLE flag_count_resets (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  TEXT NOT NULL,
    reason   TEXT NOT NULL,
    admin_id TEXT NOT NULL,
    reset_at TIMESTAMPTZ DEFAULT now()
);

-- 9. Training Assignments
CREATE TABLE training_assignments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             TEXT NOT NULL,
    module_id           TEXT NOT NULL,
    reason              TEXT,
    assigned_timestamp  TIMESTAMPTZ DEFAULT now(),
    status              TEXT DEFAULT 'pending'
);

CREATE INDEX idx_ta_user ON training_assignments (user_id, status);

-- 10. Quiz Responses
CREATE TABLE quiz_responses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         TEXT NOT NULL,
    module_id       TEXT NOT NULL,
    question_id     TEXT NOT NULL,
    selected_answer TEXT NOT NULL,
    is_correct      BOOLEAN NOT NULL
);

-- 11. Training Completions
CREATE TABLE training_completions (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               TEXT NOT NULL,
    module_id             TEXT NOT NULL,
    score                 DOUBLE PRECISION,
    completion_timestamp  TIMESTAMPTZ DEFAULT now()
);

-- 12. Training Badges
CREATE TABLE training_badges (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    TEXT NOT NULL,
    module_id  TEXT NOT NULL,
    badge_type TEXT DEFAULT 'completion',
    issued_at  TIMESTAMPTZ DEFAULT now()
);

-- 13. Detail Access Policies (supervisor)
CREATE TABLE detail_access_policies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manager_id      TEXT NOT NULL UNIQUE,
    approved_fields TEXT[] DEFAULT ARRAY[
        'incident_id','risk_category','severity_color',
        'action_taken','timestamp','prompt_summary','confidence_score'
    ]
);

-- 14. Detail Access Log
CREATE TABLE detail_access_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manager_id      TEXT NOT NULL,
    incident_id     UUID NOT NULL,
    approved_fields TEXT[],
    timestamp       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_dal_manager ON detail_access_log (manager_id, timestamp);

-- 15. Enable Row Level Security (adjust policies per your auth setup)
ALTER TABLE flag_events          ENABLE ROW LEVEL SECURITY;
ALTER TABLE incident_reports     ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_flag_history    ENABLE ROW LEVEL SECURITY;
ALTER TABLE detail_access_log   ENABLE ROW LEVEL SECURITY;
