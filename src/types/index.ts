/* ── AI Platform tracking ──────────────────────────────────────── */

export type AiPlatform =
  | "ChatGPT"
  | "Microsoft Copilot"
  | "Google Gemini"
  | "GitHub Copilot"
  | "Claude"
  | "Custom/Other";

export const AI_PLATFORMS: AiPlatform[] = [
  "ChatGPT",
  "Microsoft Copilot",
  "Google Gemini",
  "GitHub Copilot",
  "Claude",
  "Custom/Other",
];

/* ── Frontend-only UI types ─────────────────────────────────────── */

export type TextSize = "sm" | "md" | "lg";

export interface AppSettings {
  policyMode: PolicyMode;
  textSize: TextSize;
  highContrast: boolean;
  darkMode: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  wasFlagged?: boolean;
  wasRewritten?: boolean;
  ai_platform?: AiPlatform;
}

/* ── Backend-aligned enums ─────────────────────────────────────── */

export enum RiskCategory {
  PII = "pii",
  CREDENTIALS = "credentials",
  FINANCIAL = "financial",
  HEALTH = "health",
  INTERNAL = "internal",
  BIAS = "bias",
  LEGAL = "legal",
}

export enum SeverityColor {
  GREEN = "green",
  YELLOW = "yellow",
  ORANGE = "orange",
  RED = "red",
}

export enum ActionType {
  ALLOWED = "allowed",
  WARNING = "warning",
  REWRITTEN = "rewritten",
  BLOCKED = "blocked",
}

export enum PolicyMode {
  STRICT = "strict",
  BALANCED = "balanced",
  PERMISSIVE = "permissive",
}

export enum DeploymentMode {
  SHADOW = "shadow",
  FULL = "full",
}

export enum ConfidenceLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export enum IntentType {
  DATA_EXTRACTION = "data_extraction",
  CODE_GENERATION = "code_generation",
  SUMMARIZATION = "summarization",
  ANALYSIS = "analysis",
  GENERAL = "general",
}

/* ── Auth types ────────────────────────────────────────────────── */

export interface LoginRequest {
  sso_token: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export interface UserProfile {
  employee_id: string;
  name: string;
  email: string;
  department: string;
  role: "employee" | "supervisor" | "admin";
  risk_score: number;
  training_completed: string[];
  training_required: string[];
}

/* ── Prompt types ──────────────────────────────────────────────── */

export interface PromptRequest {
  prompt_text: string;
  context?: string;
  policy_mode?: PolicyMode;
  ai_platform?: AiPlatform;
}

export interface RiskFlag {
  category: RiskCategory;
  severity: SeverityColor;
  confidence: number;
  description: string;
  matched_pattern?: string;
}

export interface PromptResponse {
  prompt_id: string;
  original_prompt: string;
  risk_score: number;
  action: ActionType;
  flags: RiskFlag[];
  rewritten_prompt?: string;
  explanation: string;
  policy_mode: PolicyMode;
  intent: IntentType;
  timestamp: string;
}

/* ── Policy types ──────────────────────────────────────────────── */

export interface PolicyRule {
  rule_id: string;
  category: RiskCategory;
  pattern: string;
  description: string;
  severity: SeverityColor;
  action: ActionType;
  enabled: boolean;
}

export interface PolicyConfig {
  mode: PolicyMode;
  deployment: DeploymentMode;
  rules: PolicyRule[];
  thresholds: {
    warning: number;
    rewrite: number;
    block: number;
  };
}

/* ── Dashboard types ───────────────────────────────────────────── */

export interface DashboardStats {
  total_prompts: number;
  blocked_count: number;
  rewritten_count: number;
  warning_count: number;
  allowed_count: number;
  top_categories: { category: RiskCategory; count: number }[];
  risk_trend: { date: string; score: number }[];
}

export interface DepartmentStats {
  department: string;
  total_prompts: number;
  flagged_count: number;
  avg_risk_score: number;
  top_offenders: {
    employee_id: string;
    name: string;
    flag_count: number;
  }[];
}

/* ── Training types ────────────────────────────────────────────── */

export interface TrainingModule {
  module_id: string;
  title: string;
  description: string;
  category: RiskCategory;
  difficulty: "beginner" | "intermediate" | "advanced";
  estimated_minutes: number;
  scenarios: TrainingScenario[];
}

export interface TrainingScenario {
  scenario_id: string;
  prompt_text: string;
  correct_action: ActionType;
  explanation: string;
  options: { text: string; correct: boolean }[];
}

export interface TrainingProgress {
  module_id: string;
  completed: boolean;
  score: number;
  completed_at?: string;
}

/* ── Audit types ───────────────────────────────────────────────── */

export interface AuditEntry {
  audit_id: string;
  timestamp: string;
  employee_id: string;
  employee_name: string;
  department: string;
  prompt_id: string;
  action: ActionType;
  risk_score: number;
  categories: RiskCategory[];
  policy_mode: PolicyMode;
  redacted_snippet: string;
  ai_platform?: AiPlatform;
}

export interface AuditFilters {
  start_date?: string;
  end_date?: string;
  department?: string;
  action?: ActionType;
  category?: RiskCategory;
  min_risk_score?: number;
}

export interface AuditSummary {
  total_entries: number;
  by_action: Record<ActionType, number>;
  by_category: Record<RiskCategory, number>;
  by_department: Record<string, number>;
  avg_risk_score: number;
}

/* ── Admin types ───────────────────────────────────────────────── */

export interface AdminUserEntry {
  employee_id: string;
  name: string;
  email: string;
  department: string;
  role: "employee" | "supervisor" | "admin";
  risk_score: number;
  total_flags: number;
  last_incident?: string;
  training_status: "complete" | "in_progress" | "required" | "none";
}

/* ── Legacy aliases for backward compatibility with existing pages ─ */

export type RiskLevel = "low" | "medium" | "high";
export type SafetyStatus = "safe" | "needs-review" | "blocked";
export type AuditAction = "allowed" | "rewritten" | "blocked";

export type DetectionCategory =
  | "PII"
  | "Credentials"
  | "Financial"
  | "Health"
  | "Internal";

export interface AnalysisResult {
  allowed: boolean;
  categories: DetectionCategory[];
  riskLevel: RiskLevel;
  safetyStatus: SafetyStatus;
  explanation: string;
  saferPrompt: string | null;
  originalPrompt: string;
}

export interface AuditEvent {
  id: string;
  timestamp: number;
  user: string;
  severity: RiskLevel;
  categories: DetectionCategory[];
  action: AuditAction;
  policyVersion: string;
  redactedSnippet: string;
  reason: string;
  ai_platform?: AiPlatform;
}

export interface UserRisk {
  flaggedCount: number;
  rewrittenCount: number;
  trainingRequired: boolean;
  trainingCompleted: boolean;
}

export interface FlaggedEvent {
  id: string;
  timestamp: number;
  categories: DetectionCategory[];
  riskLevel: RiskLevel;
  redactedSnippet: string;
  ai_platform?: AiPlatform;
}
