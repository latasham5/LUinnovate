export type PolicyMode = "strict" | "balanced" | "fast";
export type TextSize = "sm" | "md" | "lg";
export type RiskLevel = "low" | "medium" | "high";
export type SafetyStatus = "safe" | "needs-review" | "blocked";
export type AuditAction = "allowed" | "rewritten" | "blocked";

export type DetectionCategory =
  | "PII"
  | "Credentials"
  | "Financial"
  | "Health"
  | "Internal";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  wasFlagged?: boolean;
  wasRewritten?: boolean;
}

export interface AnalysisResult {
  allowed: boolean;
  categories: DetectionCategory[];
  riskLevel: RiskLevel;
  safetyStatus: SafetyStatus;
  explanation: string;
  saferPrompt: string | null;
  originalPrompt: string;
  aiResponse?: string | null;
}

export interface User {
  user_id: string;
  name: string;
  role: string;
  department: string;
  session_token: string;
  deployment_mode: string;
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
}

export interface AppSettings {
  policyMode: PolicyMode;
  textSize: TextSize;
  highContrast: boolean;
  darkMode: boolean;
}
