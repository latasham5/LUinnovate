import type {
  AnalysisResult,
  AuditEvent,
  UserRisk,
  DetectionCategory,
  RiskLevel,
  AuditAction,
} from "../types/index.ts";
import { detectSensitiveData } from "../utils/detection.ts";
import { generateId } from "../utils/id.ts";

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const MOCK_AUDIT_EVENTS: AuditEvent[] = [
  {
    id: "audit-1",
    timestamp: Date.now() - 3600000 * 5,
    user: "jsmith@company.com",
    severity: "high" as RiskLevel,
    categories: ["Credentials"] as DetectionCategory[],
    action: "blocked" as AuditAction,
    policyVersion: "v2.4",
    redactedSnippet: "Send the [API_KEY_REDACTED] to the vendor...",
    reason: "API key detected in outgoing prompt",
  },
  {
    id: "audit-2",
    timestamp: Date.now() - 3600000 * 4,
    user: "mjones@company.com",
    severity: "medium" as RiskLevel,
    categories: ["PII"] as DetectionCategory[],
    action: "rewritten" as AuditAction,
    policyVersion: "v2.4",
    redactedSnippet: "Contact [EMAIL_REDACTED] regarding the...",
    reason: "Email address detected in prompt",
  },
  {
    id: "audit-3",
    timestamp: Date.now() - 3600000 * 3,
    user: "klee@company.com",
    severity: "low" as RiskLevel,
    categories: ["Internal"] as DetectionCategory[],
    action: "allowed" as AuditAction,
    policyVersion: "v2.4",
    redactedSnippet: "Summarize the [INTERNAL_REDACTED] document...",
    reason: "Internal keyword detected, low severity under balanced policy",
  },
  {
    id: "audit-4",
    timestamp: Date.now() - 3600000 * 2,
    user: "dpark@company.com",
    severity: "high" as RiskLevel,
    categories: ["Financial", "PII"] as DetectionCategory[],
    action: "blocked" as AuditAction,
    policyVersion: "v2.4",
    redactedSnippet:
      "Process payment for [CARD_REDACTED] belonging to [EMAIL_REDACTED]...",
    reason: "Credit card number and email detected",
  },
  {
    id: "audit-5",
    timestamp: Date.now() - 3600000,
    user: "jsmith@company.com",
    severity: "medium" as RiskLevel,
    categories: ["Health"] as DetectionCategory[],
    action: "rewritten" as AuditAction,
    policyVersion: "v2.4",
    redactedSnippet: "The [HEALTH_INFO_REDACTED] for this case shows...",
    reason: "Health-related keyword detected in outgoing prompt",
  },
  {
    id: "audit-6",
    timestamp: Date.now() - 1800000,
    user: "awilson@company.com",
    severity: "high" as RiskLevel,
    categories: ["Credentials"] as DetectionCategory[],
    action: "blocked" as AuditAction,
    policyVersion: "v2.4",
    redactedSnippet: "Here is the [TOKEN_REDACTED] for the service...",
    reason: "Authentication token detected",
  },
  {
    id: "audit-7",
    timestamp: Date.now() - 900000,
    user: "bchen@company.com",
    severity: "medium" as RiskLevel,
    categories: ["PII"] as DetectionCategory[],
    action: "rewritten" as AuditAction,
    policyVersion: "v2.4",
    redactedSnippet: "Call [PHONE_REDACTED] and ask about...",
    reason: "Phone number detected in prompt",
  },
];

let userRisk: UserRisk = {
  flaggedCount: 0,
  rewrittenCount: 0,
  trainingRequired: false,
  trainingCompleted: false,
};

export async function analyzePrompt(
  prompt: string
): Promise<AnalysisResult> {
  await delay(600 + Math.random() * 400);

  const detection = detectSensitiveData(prompt);

  if (!detection.hasSensitiveData) {
    return {
      allowed: true,
      categories: [],
      riskLevel: "low",
      safetyStatus: "safe",
      explanation: "No sensitive data detected. Message is safe to send.",
      saferPrompt: null,
      originalPrompt: prompt,
    };
  }

  userRisk.flaggedCount += 1;

  const safetyStatus =
    detection.riskLevel === "high" ? "blocked" : "needs-review";
  const allowed = detection.riskLevel === "low";

  return {
    allowed,
    categories: detection.categories,
    riskLevel: detection.riskLevel,
    safetyStatus,
    explanation: detection.explanation,
    saferPrompt: detection.saferPrompt,
    originalPrompt: prompt,
  };
}

export async function submitPrompt(
  prompt: string
): Promise<{ response: string }> {
  await delay(800 + Math.random() * 400);

  return {
    response: `I've processed your request. Here's a summary based on your prompt: "${prompt.slice(0, 60)}${prompt.length > 60 ? "..." : ""}" — This is a simulated AI assistant response demonstrating how the integrated AI tool would respond after S.I.P verification.`,
  };
}

export async function getAuditEvents(): Promise<AuditEvent[]> {
  await delay(300);
  return [...MOCK_AUDIT_EVENTS];
}

export async function getUserRisk(): Promise<UserRisk> {
  await delay(200);
  if (userRisk.flaggedCount + userRisk.rewrittenCount >= 3) {
    userRisk.trainingRequired = true;
  }
  return { ...userRisk };
}

export function incrementRewrittenCount(): void {
  userRisk.rewrittenCount += 1;
}

export function completeTraining(): void {
  userRisk.trainingCompleted = true;
  userRisk.trainingRequired = false;
}

export function addAuditEvent(event: AuditEvent): void {
  MOCK_AUDIT_EVENTS.unshift(event);
}

export { generateId };
