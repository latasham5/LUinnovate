# Phantom App — Frontend Developer Handoff Document

## Context
The Phantom App is a **prompt security middleware** for Coca-Cola's internal AI tool (CokeGPT). The backend (FastAPI, Python 3.12) is fully scaffolded with 87 files. The frontend team will build a separate **Vite + React + TypeScript** project that consumes all API endpoints below. The backend runs at `http://localhost:8000`.

---

## 1. SERVER & CONNECTION INFO

| Property | Value |
|---|---|
| Base URL | `http://localhost:8000/api/v1` |
| Root health | `GET http://localhost:8000/` |
| Health check | `GET http://localhost:8000/health` |
| Swagger docs | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| CORS | All origins allowed (dev) |
| Auth | Bearer token in `Authorization` header |

---

## 2. AUTHENTICATION FLOW

**Every request** (except `/`, `/health`, `/docs`, `/openapi.json`, `/redoc`) requires:
```
Authorization: Bearer <session_token>
```
If missing, the backend returns:
```json
{ "detail": "Authorization header required", "code": "AUTH_ERROR" }
```

### Login flow:
1. Frontend sends SSO token to `POST /api/v1/auth/login`
2. Backend returns `session_token` + user info
3. Frontend stores `session_token` and sends it as `Bearer <token>` on all subsequent requests
4. `POST /api/v1/auth/logout` revokes the session

### Admin routes:
Routes under `/api/v1/admin` and `PUT /api/v1/policy/update` require admin role. The backend `require_admin` dependency checks this.

---

## 3. ALL ENUMS (TypeScript Types)

Your frontend should define these as TypeScript enums or union types:

### RiskCategory
```typescript
type RiskCategory =
  | "FINANCIAL"
  | "CREDENTIALS"
  | "PII"
  | "CUSTOMER_INFO"
  | "PROPRIETARY"
  | "INTERNAL_CODE_NAME"
  | "REGULATED"
  | "GENERAL";
```

### SeverityColor
```typescript
type SeverityColor = "YELLOW" | "ORANGE" | "RED";
// YELLOW = Low risk (score 1-39) — log only, weekly digest
// ORANGE = Medium risk (score 40-69) — real-time manager notification
// RED = High risk (score 70-100) — immediate manager + cybersecurity alert
```

### ActionType
```typescript
type ActionType =
  | "ALLOWED"              // Clean prompt, no issues
  | "ALLOWED_WITH_WARNING" // Low risk, user sees a warning
  | "REWRITTEN"            // Prompt was sanitized and resubmitted
  | "BLOCKED"              // Prompt rejected entirely
  | "SHADOW_LOGGED";       // Logged only (shadow mode), user sees nothing
```

### PolicyMode
```typescript
type PolicyMode = "STRICT" | "BALANCED" | "FAST";
// STRICT  = multiplier 0.7 (lower thresholds, more sensitive)
// BALANCED = multiplier 1.0 (default)
// FAST     = multiplier 1.3 (higher thresholds, less sensitive)
```

### DeploymentMode
```typescript
type DeploymentMode = "SHADOW" | "FULL_ENFORCEMENT";
// SHADOW = log everything, only block credentials, user doesn't see enforcement
// FULL_ENFORCEMENT = full policy applied, prompts can be blocked/rewritten
```

### ConfidenceLevel
```typescript
type ConfidenceLevel = "LOW" | "MEDIUM" | "HIGH";
// LOW:    0.0 - 0.39
// MEDIUM: 0.4 - 0.69
// HIGH:   0.7 - 1.0
```

### IntentType
```typescript
type IntentType =
  | "QUESTION"
  | "DATA_PASTE"
  | "CONTENT_GENERATION"
  | "DATA_EXTRACTION"
  | "SUMMARIZATION"
  | "UNKNOWN";
```

---

## 4. ALL API ENDPOINTS (Complete Reference)

### 4.1 PROMPT — `/api/v1/prompt`

#### `POST /api/v1/prompt`
**The main entry point.** User types a prompt, frontend sends it here, backend analyzes and returns the result.

**Request Body:**
```typescript
interface PromptRequest {
  raw_prompt: string;            // The user's prompt text
  policy_mode?: string;          // "STRICT" | "BALANCED" | "FAST" (default: "BALANCED")
}
```

**Response (200):**
```typescript
interface PromptResponse {
  action: ActionType;                   // What happened to the prompt
  response_content: string | null;      // CokeGPT's response (null if blocked)
  rewritten_prompt: string | null;      // Sanitized version (if action=REWRITTEN)
  rewrite_explanation: string[] | null; // List of what was changed and why
  severity_color: string | null;        // "YELLOW" | "ORANGE" | "RED"
  warning_message: string | null;       // Warning text (if action=ALLOWED_WITH_WARNING)
  disclaimers: string[];                // General disclaimers to display
}
```

**Frontend behavior by `action`:**
| Action | What to show the user |
|---|---|
| `ALLOWED` | Show `response_content` normally |
| `ALLOWED_WITH_WARNING` | Show `response_content` + yellow warning banner with `warning_message` |
| `REWRITTEN` | Show `response_content` + orange notice: "Your prompt was sanitized" + collapsible `rewrite_explanation` list + show `rewritten_prompt` as "what was sent" |
| `BLOCKED` | Show red block screen: "Prompt blocked" + `warning_message` reason. No `response_content`. |
| `SHADOW_LOGGED` | Show `response_content` normally (user doesn't know it was logged) |

---

### 4.2 AUTHENTICATION — `/api/v1/auth`

#### `POST /api/v1/auth/login`
**No auth header required.**

**Request Body:**
```typescript
interface LoginRequest {
  sso_token: string;   // SSO token from Coca-Cola identity provider
}
```

**Response (200):**
```typescript
interface LoginResponse {
  session_token: string;    // Store this, send as Bearer token
  user_id: string;          // e.g., "EMP001"
  name: string;             // e.g., "Sarah Johnson"
  role: string;             // "analyst" | "senior_analyst" | "manager" | "director" | "security_admin" | "admin"
  department: string;       // e.g., "Marketing"
  deployment_mode: string;  // "SHADOW" | "FULL_ENFORCEMENT"
}
```

#### `GET /api/v1/auth/profile/{employee_id}`
**Path param:** `employee_id` (string)

**Response (200):**
```typescript
interface UserProfileResponse {
  employee_id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  department_id: string;     // e.g., "DEPT_MKT"
  clearance_level: string;   // "standard" | "elevated" | "executive" | "top_secret"
  manager_id: string | null;
}
```

#### `POST /api/v1/auth/logout`
**Response (200):**
```json
{ "message": "Session revoked" }
```

---

### 4.3 POLICY — `/api/v1/policy`

#### `GET /api/v1/policy/active`
Returns all currently enforced policy rules.

**Response (200):**
```typescript
interface ActivePoliciesResponse {
  policies: PolicyRule[];
  version: string;           // e.g., "1.0.0"
}

interface PolicyRule {
  rule_id: string;           // e.g., "RULE_001"
  category: RiskCategory;
  description: string;
  threshold: number;         // 0.0 - 100.0
  action: ActionType;
  enabled: boolean;
}
```

#### `GET /api/v1/policy/category/{category}`
**Path param:** `category` (RiskCategory string)

**Response (200):**
```typescript
{ category: string; rules: PolicyRule[] }
```

#### `GET /api/v1/policy/version`
**Response (200):**
```typescript
{ version: string }
```

#### `PUT /api/v1/policy/update` *(Admin only)*
**Request Body:**
```typescript
interface PolicyUpdateRequest {
  admin_id: string;
  new_rules: PolicyRule[];    // Array of rule objects
  effective_date: string;     // ISO date string
}
```
**Response (200):**
```typescript
{ message: string; effective_date: string }
```

#### `GET /api/v1/policy/templates/{role}/{department}`
Returns pre-approved safe prompt templates.

**Path params:** `role` (string), `department` (string)

**Response (200):**
```typescript
interface TemplatesResponse {
  templates: PromptTemplate[];
}

interface PromptTemplate {
  id: string;            // e.g., "TPL_001"
  title: string;         // e.g., "General Summary Request"
  template: string;      // Template text with [PLACEHOLDERS]
  role: string;          // "all" or specific role
  department: string;    // "all" or specific department
  category: string;      // "summarization" | "content_generation" | "data_extraction" | "question"
}
```

#### `GET /api/v1/policy/thresholds/{policy_mode}`
**Path param:** `policy_mode` ("STRICT" | "BALANCED" | "FAST")

**Response (200):**
```typescript
interface ThresholdsResponse {
  policy_mode: string;
  thresholds: PolicyThresholds;
}

interface PolicyThresholds {
  yellow_min: number;    // default 1.0
  yellow_max: number;    // default 39.0
  orange_min: number;    // default 40.0
  orange_max: number;    // default 69.0
  red_min: number;       // default 70.0
  red_max: number;       // default 100.0
}
```

---

### 4.4 ADMIN — `/api/v1/admin` *(All routes require admin role)*

#### `GET /api/v1/admin/deployment-mode`
**Response (200):**
```typescript
{ mode: "SHADOW" | "FULL_ENFORCEMENT" }
```

#### `PUT /api/v1/admin/deployment-mode`
**Request Body:**
```typescript
interface DeploymentModeRequest {
  admin_id: string;
  mode: "SHADOW" | "FULL_ENFORCEMENT";
  effective_date: string;     // ISO date
}
```
**Response (200):**
```typescript
{ message: string; effective_date: string }
```

#### `GET /api/v1/admin/shadow-config`
Returns what is logged-only vs hard-blocked in shadow mode.

**Response (200):**
```typescript
{ config: Record<string, any> }
```

#### `PUT /api/v1/admin/shadow-config`
**Request Body:**
```typescript
interface ShadowModeConfigRequest {
  admin_id: string;
  config: Record<string, any>;
}
```
**Response (200):**
```typescript
{ message: "Shadow mode config updated" }
```

#### `GET /api/v1/admin/readiness-report`
Shadow-to-enforcement readiness assessment.

**Response (200):**
```typescript
interface ReadinessReport {
  ready: boolean;
  recommendation: string;
}
```

#### `GET /api/v1/admin/shadow-vs-enforcement`
**Query params:** `date_from` (string), `date_to` (string)

**Response (200):**
```typescript
interface ShadowComparison {
  date_range: { from: string; to: string };
  comparison: Record<string, any>;  // Blocked-vs-logged breakdown
}
```

---

### 4.5 DASHBOARD — `/api/v1/dashboard`

All dashboard endpoints support optional query params: `date_from` (string), `date_to` (string) for date filtering.

#### `GET /api/v1/dashboard/scorecard/company`
Company-wide scorecard — all departments in one view.

**Response (200):**
```typescript
interface CompanyScorecard {
  departments: DepartmentScore[];
}

interface DepartmentScore {
  department_id: string;
  department_name: string;
  score: number;            // 0-100
  color: SeverityColor;     // Based on score
  total_prompts: number;
  flagged_prompts: number;
  breakdown: ActionBreakdown;
}

interface ActionBreakdown {
  allowed: number;
  allowed_with_warning: number;
  rewritten: number;
  blocked: number;
  shadow_logged: number;
}
```

#### `GET /api/v1/dashboard/scorecard/department/{department_id}`
**Path param:** `department_id` (e.g., "DEPT_MKT")

**Response (200):**
```typescript
{
  department_id: string;
  score: number;
  color: SeverityColor;
  breakdown: ActionBreakdown;
}
```

#### `GET /api/v1/dashboard/department/{department_id}/breakdown`
Counts by action type for a department.

**Response (200):**
```typescript
{ department_id: string; breakdown: ActionBreakdown }
```

#### `GET /api/v1/dashboard/department/{department_id}/top-offenders`
Highest flag counts in a department.

**Response (200):**
```typescript
interface TopOffenders {
  department_id: string;
  offenders: Offender[];
}

interface Offender {
  user_id: string;
  name: string;
  flag_count: number;
  most_common_category: RiskCategory;
  risk_trend: "IMPROVING" | "STABLE" | "WORSENING";
}
```

#### `GET /api/v1/dashboard/department/{department_id}/trends`
Behavioral trends over time.

**Response (200):**
```typescript
interface TrendAnalysis {
  department_id: string;
  trends: TrendPoint[];
}

interface TrendPoint {
  date: string;              // ISO date
  total_prompts: number;
  flagged_prompts: number;
  risk_score_avg: number;
  dominant_action: ActionType;
}
```

#### `GET /api/v1/dashboard/department/{department_id}/risk-distribution`
Which risk categories triggered most flags.

**Response (200):**
```typescript
interface RiskDistribution {
  department_id: string;
  distribution: Record<RiskCategory, number>;
  // e.g., { "PII": 45, "CREDENTIALS": 12, "FINANCIAL": 8, ... }
}
```

#### `GET /api/v1/dashboard/compare`
Side-by-side department comparison.

**Query params:** `department_ids` (comma-separated string, e.g., "DEPT_MKT,DEPT_FIN")

**Response (200):**
```typescript
interface DepartmentComparison {
  departments: string[];
  comparison: Record<string, DepartmentScore>;
}
```

#### `GET /api/v1/dashboard/shadow-impact`
Projected impact if shadow mode switches to full enforcement.

**Response (200):**
```typescript
interface ShadowImpact {
  impact: {
    total_would_block: number;
    total_would_rewrite: number;
    total_would_warn: number;
    affected_departments: string[];
    affected_users_count: number;
  }
}
```

#### `GET /api/v1/dashboard/training-correlation/{department_id}`
Training completion vs flag reduction correlation.

**Response (200):**
```typescript
interface TrainingCorrelation {
  department_id: string;
  correlation: {
    training_completion_rate: number;   // 0-100%
    flag_reduction_rate: number;        // 0-100%
    before_training_avg_flags: number;
    after_training_avg_flags: number;
  }
}
```

#### `GET /api/v1/dashboard/executive-briefing`
One-page leadership summary.

**Response (200):**
```typescript
interface ExecutiveBriefing {
  briefing: {
    date_range: { from: string; to: string };
    total_prompts: number;
    total_flagged: number;
    flag_rate_percent: number;
    deployment_mode: DeploymentMode;
    top_risk_category: RiskCategory;
    worst_department: string;
    best_department: string;
    training_compliance_rate: number;
    recommendation: string;
  }
}
```

---

### 4.6 TRAINING — `/api/v1/training`

#### `GET /api/v1/training/modules/{module_id}`
Retrieve scenario-based training content.

**Path param:** `module_id` ("pii_training" | "credentials_training" | "financial_training")

**Response (200):**
```typescript
interface TrainingModule {
  module_id: string;
  title: string;
  description: string;
  estimated_minutes: number;
  scenarios: Scenario[];
  quiz: QuizQuestion[];
}

interface Scenario {
  id: string;                // e.g., "PII_S1"
  title: string;
  description: string;
  unsafe_example: string;    // Show in red/danger styling
  safe_example: string;      // Show in green/safe styling
  explanation: string;
}

interface QuizQuestion {
  question_id: string;       // e.g., "PII_Q1"
  question: string;
  options: string[];          // 4 multiple choice options
  correct_answer: string;    // One of the options
  explanation: string;       // Show after answering
}
```

#### `GET /api/v1/training/user/{user_id}/history`
**Response (200):**
```typescript
interface TrainingHistory {
  user_id: string;
  completed: CompletedModule[];
  pending: PendingModule[];
}

interface CompletedModule {
  module_id: string;
  completed_at: string;
  score: number;
  badge_earned: boolean;
}

interface PendingModule {
  module_id: string;
  assigned_at: string;
  reason: string;       // Why it was assigned
  status: "pending" | "in_progress" | "overdue";
}
```

#### `POST /api/v1/training/quiz/submit`
**Request Body:**
```typescript
interface QuizResponseRequest {
  user_id: string;
  module_id: string;
  question_id: string;
  selected_answer: string;
}
```
**Response (200):**
```typescript
{ recorded: boolean }
```

#### `GET /api/v1/training/quiz/evaluate/{user_id}/{module_id}`
**Response (200):**
```typescript
interface QuizEvaluation {
  user_id: string;
  module_id: string;
  passed: boolean;
  score: number;       // 0-100
}
```

#### `GET /api/v1/training/effectiveness/{module_id}`
**Query params:** `date_from`, `date_to` (optional)

**Response (200):**
```typescript
interface TrainingEffectiveness {
  module_id: string;
  effectiveness: {
    total_assigned: number;
    total_completed: number;
    average_score: number;
    flag_reduction_after: number;
  }
}
```

---

### 4.7 AUDIT — `/api/v1/audit`

#### `GET /api/v1/audit/user/{user_id}`
**Query params:** `date_from`, `date_to` (optional)

**Response (200):**
```typescript
interface AuditTrail {
  user_id: string;
  events: AuditEvent[];
}

interface AuditEvent {
  incident_id: string;          // UUID
  created_at: string;           // ISO timestamp
  user_id: string;
  department: string;
  department_id: string;
  risk_category: RiskCategory;
  risk_score: number;
  severity_color: SeverityColor;
  confidence_score: ConfidenceLevel;
  action_taken: ActionType;
  policy_version: string;
  policy_mode: PolicyMode;
  deployment_mode: DeploymentMode;
  detected_elements_summary: string[];
  rewrite_explanation: string[] | null;
  // NOTE: raw_prompt is NOT included in audit trails (privacy)
}
```

#### `GET /api/v1/audit/department/{department_id}`
Same response shape as user audit trail but for an entire department.

#### `GET /api/v1/audit/category/{category}`
**Path param:** `category` (RiskCategory string)
Filters all events by risk category.

#### `GET /api/v1/audit/action/{action_type}`
**Path param:** `action_type` (ActionType string)
Filters all events by action taken.

#### `GET /api/v1/audit/incident/{incident_id}`
Single incident detail for investigation.

**Response (200):**
```typescript
interface IncidentDetail {
  incident_id: string;
  record: AuditEvent;          // Full event record
}
```

#### `GET /api/v1/audit/summary`
Executive-level stats.

**Response (200):**
```typescript
interface AuditSummary {
  summary: {
    total_prompts: number;
    flagged_prompts: number;
    flag_rate: number;
    by_category: Record<RiskCategory, number>;
    by_action: Record<ActionType, number>;
    by_severity: Record<SeverityColor, number>;
  }
}
```

#### `GET /api/v1/audit/export`
Compliance report download.

**Query params:**
- `format`: "json" | "csv" | "pdf" (default: "json")
- `date_from`, `date_to` (optional)
- `category` (optional RiskCategory filter)

**Response (200):**
```typescript
{ format: string; download_url: string }
```

#### `GET /api/v1/audit/supervisor/request-detail`
Manager requests to see more detail on an incident (logged in audit trail).

**Query params:**
- `manager_id` (string)
- `incident_id` (string)
- `justification` (string)

**Response (200):**
```typescript
{ status: "pending_review" | "approved" | "denied" }
```

---

## 5. ERROR RESPONSE FORMAT

All errors follow this structure:
```typescript
interface ErrorResponse {
  detail: string;
  code: string;
}
```

### Error codes the frontend should handle:
| Code | HTTP Status | Meaning |
|---|---|---|
| `AUTH_ERROR` | 401 | Missing or invalid token |
| `AUTHORIZATION_ERROR` | 403 | Not an admin for admin routes |
| `DETECTION_ERROR` | 500 | NLP analysis failed |
| `REWRITE_ERROR` | 500 | Rewrite engine failed |
| `RISK_CLASSIFICATION_ERROR` | 500 | Scoring failed |
| `POLICY_ERROR` | 500 | Policy lookup failed |
| `COKEGPT_ERROR` | 502 | CokeGPT API unreachable |
| `PROMPT_BLOCKED` | 403 | Prompt blocked by policy |
| `LOGGING_ERROR` | 500 | Database logging failed |
| `ALERTING_ERROR` | 500 | Notification dispatch failed |
| `TRAINING_ERROR` | 500 | Training service failed |

---

## 6. RISK SCORE THRESHOLDS & ACTION LOGIC

The pipeline determines what happens to each prompt based on the risk score:

```
Score = 0         -> ALLOWED (green)
Score = 1-39      -> ALLOWED_WITH_WARNING (yellow)
Score = 40-69     -> REWRITTEN (orange)
Score = 70-100    -> BLOCKED (red)
```

**In SHADOW mode:** Everything returns `SHADOW_LOGGED` (user sees normal response), except credentials which are ALWAYS blocked.

**Policy mode multipliers** adjust the thresholds:
- STRICT (0.7x) — thresholds are lower, more things get caught
- BALANCED (1.0x) — default
- FAST (1.3x) — thresholds are higher, less sensitive

---

## 7. MOCK USER DATA (For Development)

9 test users across 6 departments:

| ID | Name | Role | Department | Dept ID | Clearance | Manager |
|---|---|---|---|---|---|---|
| EMP001 | Sarah Johnson | analyst | Marketing | DEPT_MKT | standard | MGR001 |
| EMP002 | Michael Chen | analyst | Finance | DEPT_FIN | standard | MGR002 |
| EMP003 | Jessica Williams | senior_analyst | Supply Chain | DEPT_SCH | elevated | MGR003 |
| MGR001 | David Martinez | manager | Marketing | DEPT_MKT | elevated | DIR001 |
| MGR002 | Emily Davis | manager | Finance | DEPT_FIN | elevated | DIR001 |
| MGR003 | Robert Taylor | manager | Supply Chain | DEPT_SCH | elevated | DIR001 |
| DIR001 | Amanda Wilson | director | Operations | DEPT_OPS | executive | null |
| SEC001 | James Anderson | security_admin | Cybersecurity | DEPT_SEC | top_secret | DIR001 |
| ADM001 | System Administrator | admin | IT | DEPT_IT | top_secret | null |

**Roles:** `analyst`, `senior_analyst`, `manager`, `director`, `security_admin`, `admin`
**Clearance levels:** `standard`, `elevated`, `executive`, `top_secret`
**Department IDs:** `DEPT_MKT`, `DEPT_FIN`, `DEPT_SCH`, `DEPT_OPS`, `DEPT_SEC`, `DEPT_IT`

---

## 8. POLICY RULES (8 Default Rules)

| Rule ID | Category | Action | Threshold | Description |
|---|---|---|---|---|
| RULE_001 | CREDENTIALS | BLOCKED | 0.0 | API keys, passwords, tokens, internal URLs — always blocked |
| RULE_002 | PII | REWRITTEN | 40.0 | Personally identifiable information |
| RULE_003 | FINANCIAL | REWRITTEN | 40.0 | Sensitive financial data |
| RULE_004 | CUSTOMER_INFO | REWRITTEN | 40.0 | Customer-specific information |
| RULE_005 | PROPRIETARY | ALLOWED_WITH_WARNING | 30.0 | Proprietary business information |
| RULE_006 | INTERNAL_CODE_NAME | REWRITTEN | 30.0 | Internal project code names |
| RULE_007 | REGULATED | BLOCKED | 50.0 | HIPAA, SOX, legally privileged content |
| RULE_008 | GENERAL | ALLOWED | 0.0 | General prompts, no sensitive content |

---

## 9. TRAINING MODULES (3 Available)

| Module ID | Title | Duration | Scenarios | Quiz Questions |
|---|---|---|---|---|
| `pii_training` | Protecting Personally Identifiable Information | 10 min | 2 | 2 |
| `credentials_training` | Credential and Secret Protection | 8 min | 1 | 1 |
| `financial_training` | Financial Data Security | 10 min | 1 | 1 |

Each module has:
- **Scenarios**: Side-by-side `unsafe_example` (red) vs `safe_example` (green) with `explanation`
- **Quiz**: Multiple choice questions (4 options) with `correct_answer` and `explanation` for after they answer

Training is **auto-assigned** when a user reaches 5 flags (configurable via `DEFAULT_FLAG_THRESHOLD`).

---

## 10. DATABASE TABLES (Supabase PostgreSQL)

These tables back all the API data. Useful for understanding what data exists:

| Table | Purpose | Key Columns |
|---|---|---|
| `prompt_events` | Core logging table for every prompt | id (UUID), user_id, department_id, raw_prompt, rewritten_prompt, risk_category, risk_score, severity_color, action_taken, policy_mode, deployment_mode, created_at |
| `shadow_mode_events` | What would have happened in enforcement | id, user_id, raw_prompt, what_would_have_happened, risk_score, risk_category, severity_color |
| `user_sessions` | Session tracking | id, user_id, session_start, session_end, total_prompts, flagged_prompts |
| `flag_events` | User flag history | id, user_id, risk_category, severity, incident_id (FK to prompt_events) |
| `training_assignments` | Training module assignments | id, user_id, module_id, reason, status, assigned_at, completed_at, score |
| `quiz_responses` | Individual quiz answers | id, user_id, module_id, question_id, selected_answer, is_correct |
| `badges` | Completion badges | id, user_id, module_id, badge_type |
| `detail_access_log` | Supervisor audit trail | id, manager_id, incident_id (FK), accessed_fields |

---

## 11. PROMPT TEMPLATES (5 Pre-approved)

| ID | Title | For Department | For Role | Category |
|---|---|---|---|---|
| TPL_001 | General Summary Request | all | all | summarization |
| TPL_002 | Marketing Copy Draft | Marketing | all | content_generation |
| TPL_003 | Data Analysis Template | all | analyst | data_extraction |
| TPL_004 | Report Structure Request | all | all | content_generation |
| TPL_005 | Supply Chain Query | Supply Chain | all | question |

Templates contain `[PLACEHOLDER]` tokens the user fills in before sending.

---

## 12. RECOMMENDED FRONTEND PAGES & COMPONENTS

### Page 1: Login
- SSO token input field
- Calls `POST /api/v1/auth/login`
- Stores `session_token`, `user_id`, `role`, `department`, `deployment_mode` in app state
- Redirects based on role: admin -> Admin Dashboard, others -> Prompt Interface

### Page 2: Prompt Interface (Main Chat)
- Text area for prompt input
- Policy mode selector dropdown: STRICT / BALANCED / FAST
- "Send" button -> `POST /api/v1/prompt`
- Template sidebar: `GET /api/v1/policy/templates/{role}/{department}` — clickable templates that pre-fill the text area
- Response display area with conditional rendering based on `action`:
  - **ALLOWED**: Green check + response text
  - **ALLOWED_WITH_WARNING**: Yellow banner with `warning_message` + response text
  - **REWRITTEN**: Orange banner "Your prompt was sanitized" + expandable `rewrite_explanation` list + "Original sent as:" `rewritten_prompt` + response text
  - **BLOCKED**: Red full-screen overlay "Prompt Blocked" + `warning_message` reason
  - **SHADOW_LOGGED**: Show response normally (invisible to user)
- Disclaimer footer showing `disclaimers[]`

### Page 3: Company Dashboard (Recharts)
- Company-wide scorecard: `GET /api/v1/dashboard/scorecard/company`
  - Grid of department cards, each colored by severity (YELLOW/ORANGE/RED)
  - Click a card -> department drilldown
- Executive briefing panel: `GET /api/v1/dashboard/executive-briefing`
- Department comparison chart: `GET /api/v1/dashboard/compare?department_ids=DEPT_MKT,DEPT_FIN,...`

### Page 4: Department Drilldown
- Department score + color: `GET /api/v1/dashboard/scorecard/department/{id}`
- Action breakdown pie/bar chart: `GET /api/v1/dashboard/department/{id}/breakdown`
- Risk category distribution chart: `GET /api/v1/dashboard/department/{id}/risk-distribution`
- Trend line chart over time: `GET /api/v1/dashboard/department/{id}/trends`
- Top offenders table: `GET /api/v1/dashboard/department/{id}/top-offenders`
- Training correlation: `GET /api/v1/dashboard/training-correlation/{id}`

### Page 5: Admin Panel (Admin role only)
- **Deployment mode toggle**: `GET /api/v1/admin/deployment-mode` + `PUT` to switch
  - Big toggle switch: SHADOW <-> FULL_ENFORCEMENT
  - Confirmation modal before switching
- **Shadow config editor**: `GET /api/v1/admin/shadow-config` + `PUT` to update
- **Readiness report**: `GET /api/v1/admin/readiness-report`
  - Shows `ready: true/false` + `recommendation` text
- **Shadow vs Enforcement comparison**: `GET /api/v1/admin/shadow-vs-enforcement?date_from=...&date_to=...`
  - Date range picker + comparison table/chart
- **Shadow impact projection**: `GET /api/v1/dashboard/shadow-impact`
- **Policy management**: `GET /api/v1/policy/active` + `PUT /api/v1/policy/update`
  - Table of all 8 policy rules
  - Edit rule threshold, action, enabled toggle
  - Save changes button

### Page 6: Training Center
- **Module list**: Show all 3 modules (pii_training, credentials_training, financial_training)
  - `GET /api/v1/training/modules/{module_id}` for each
- **Module viewer**: Display scenarios with unsafe (red) vs safe (green) examples
- **Quiz interface**:
  - Show questions one at a time
  - Submit each answer: `POST /api/v1/training/quiz/submit`
  - After all questions: `GET /api/v1/training/quiz/evaluate/{user_id}/{module_id}`
  - Show pass/fail + score
- **User history**: `GET /api/v1/training/user/{user_id}/history`
  - Completed modules (with scores and badges)
  - Pending/overdue modules
- **Training effectiveness** (admin view): `GET /api/v1/training/effectiveness/{module_id}`

### Page 7: Audit Trail
- **Filterable log table** with columns: Date, User, Department, Category, Severity, Action, Confidence
  - Filter by user: `GET /api/v1/audit/user/{user_id}`
  - Filter by department: `GET /api/v1/audit/department/{department_id}`
  - Filter by category: `GET /api/v1/audit/category/{category}`
  - Filter by action: `GET /api/v1/audit/action/{action_type}`
  - Date range picker for `date_from` / `date_to` query params
- **Incident detail modal**: Click a row -> `GET /api/v1/audit/incident/{incident_id}`
- **Summary stats panel**: `GET /api/v1/audit/summary`
- **Export button**: `GET /api/v1/audit/export?format=json|csv|pdf`
  - Download file from returned `download_url`
- **Supervisor access**: `GET /api/v1/audit/supervisor/request-detail?manager_id=...&incident_id=...&justification=...`
  - Button for managers to request full detail on an incident
  - Requires justification text input

---

## 13. SEVERITY COLOR UI MAPPING

Use these consistently across all components:

| Color | Hex Suggestion | Meaning | Score Range |
|---|---|---|---|
| YELLOW | `#F59E0B` (amber-500) | Low risk | 1-39 |
| ORANGE | `#F97316` (orange-500) | Medium risk | 40-69 |
| RED | `#EF4444` (red-500) | High risk | 70-100 |
| GREEN | `#22C55E` (green-500) | No risk (ALLOWED) | 0 |

---

## 14. AXIOS API CLIENT SETUP

```typescript
// src/api/client.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Add auth token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('session_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('session_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 15. SUGGESTED TECH STACK

| Library | Purpose |
|---|---|
| Vite | Build tool |
| React 18+ | UI framework |
| TypeScript | Type safety |
| React Router v6 | Page routing |
| Axios | API calls |
| Recharts | Dashboard charts (bar, line, pie, area) |
| TailwindCSS | Styling |
| Zustand or React Context | State management (user session, deployment mode) |
| React Hook Form | Form handling (policy editor, quiz) |
| date-fns | Date formatting for audit trails |

---

## Verification
To test the frontend against the backend:
1. Start backend: `cd C:\Users\Selam\Desktop\Phantom_App && C:\Users\Selam\AppData\Local\Programs\Python\Python312\python.exe -m uvicorn main:app --reload --port 8000`
2. Open Swagger: `http://localhost:8000/docs` — test any endpoint directly
3. Start frontend dev server: `npm run dev` (from your Vite project)
4. Test login -> prompt -> dashboard -> audit flow end-to-end
