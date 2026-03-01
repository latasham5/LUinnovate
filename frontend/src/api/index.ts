import api from "./client.ts";
import type {
  AnalysisResult,
  AuditEvent,
  UserRisk,
} from "../types/index.ts";
import { generateId } from "../utils/id.ts";

// ─── Auth ──────────────────────────────────────────

export interface LoginResponse {
  session_token: string;
  user_id: string;
  name: string;
  role: string;
  department: string;
  deployment_mode: string;
}

export async function login(employeeId: string): Promise<LoginResponse> {
  const { data } = await api.post("/auth/login", { sso_token: employeeId });
  return data;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } catch {
    // Ignore errors on logout
  }
  sessionStorage.removeItem("session_token");
  sessionStorage.removeItem("user");
}

// ─── Prompt Pipeline ───────────────────────────────

/**
 * Send prompt to backend for analysis and get full result
 */
export async function analyzePrompt(prompt: string): Promise<AnalysisResult> {
  const { data } = await api.post("/prompt/", {
    raw_prompt: prompt,
    policy_mode: "BALANCED",
  });

  // Use the new severity_color field from backend
  const riskLevel = data.severity_color === "RED"
    ? "high"
    : data.severity_color === "ORANGE"
    ? "medium"
    : "low";

  const safetyStatus = data.action === "BLOCKED"
    ? "blocked"
    : data.detected_categories?.length > 0
      ? "needs-review"
      : "safe";

  // Map ALL backend categories to frontend display names
  const categories = (data.detected_categories || []).map((cat: string) => {
    const mapping: Record<string, string> = {
      PII: "PII",
      CREDENTIALS: "Credentials",
      FINANCIAL: "Financial",
      HEALTH: "Health",
      INTERNAL: "Internal",
      CUSTOMER_INFO: "PII",
      INTERNAL_CODE_NAME: "Internal",
      REGULATED: "Health",
      PROPRIETARY: "Internal",
      GENERAL: "Internal",
    };
    return (mapping[cat] || cat) as any;
  });

  return {
    allowed: data.action !== "BLOCKED",
    categories: [...new Set(categories)],
    riskLevel,
    safetyStatus,
    explanation: data.explanation || `Risk score: ${data.risk_score}. Action: ${data.action}`,
    saferPrompt: data.rewritten_prompt || null,
    originalPrompt: prompt,
    aiResponse: data.response_content || null,
  };
}

export async function submitPrompt(
  prompt: string
): Promise<{ response: string }> {
  const { data } = await api.post("/prompt/", {
    raw_prompt: prompt,
    policy_mode: "BALANCED",
  });
  return {
    response: data.response_content || "Your prompt has been processed by CokeGPT.",
  };
}

// ─── Audit ─────────────────────────────────────────

export async function getAuditEvents(): Promise<AuditEvent[]> {
  try {
    const { data } = await api.get("/audit/events", {
      params: { limit: 100 },
    });

    const events = data.events || data || [];
    return events.map((e: any) => ({
      id: e.event_id || e.id || generateId(),
      timestamp: e.timestamp ? new Date(e.timestamp).getTime() : Date.now(),
      user: e.user_id || e.user || "unknown",
      severity: e.severity === "RED" ? "high" : e.severity === "ORANGE" ? "medium" : "low",
      categories: (e.detected_categories || e.categories || []).map((c: string) => {
        const mapping: Record<string, string> = {
          PII: "PII", CREDENTIALS: "Credentials", FINANCIAL: "Financial",
          HEALTH: "Health", INTERNAL: "Internal",
        };
        return mapping[c] || c;
      }),
      action: e.action_taken === "BLOCKED" ? "blocked"
        : e.action_taken === "REWRITTEN" ? "rewritten" : "allowed",
      policyVersion: e.policy_mode || "v1.0",
      redactedSnippet: e.rewritten_prompt || e.raw_prompt?.slice(0, 80) || "---",
      reason: e.explanation || `${e.action_taken} by PromptGuard`,
    }));
  } catch {
    return [];
  }
}

// ─── User Risk ─────────────────────────────────────

export async function getUserRisk(): Promise<UserRisk> {
  try {
    const user = JSON.parse(sessionStorage.getItem("user") || "{}");
    const { data } = await api.get(`/dashboard/user-scorecard/${user.user_id || "EMP001"}`);
    return {
      flaggedCount: data.total_flagged || 0,
      rewrittenCount: data.total_rewritten || 0,
      trainingRequired: data.training_required || false,
      trainingCompleted: data.training_completed || false,
    };
  } catch {
    return { flaggedCount: 0, rewrittenCount: 0, trainingRequired: false, trainingCompleted: false };
  }
}

// ─── Dashboard ─────────────────────────────────────

export async function getDashboardScorecard(): Promise<any> {
  try {
    const { data } = await api.get("/dashboard/scorecard");
    return data;
  } catch {
    return null;
  }
}

// ─── Training ──────────────────────────────────────

export async function completeTraining(): Promise<void> {
  try {
    const user = JSON.parse(sessionStorage.getItem("user") || "{}");
    await api.post("/training/complete", {
      user_id: user.user_id || "EMP001",
      module_id: "general_safety",
    });
  } catch {
    // Tracked locally
  }
}

// ─── Admin ─────────────────────────────────────────

export async function getDeploymentMode(): Promise<string> {
  try {
    const { data } = await api.get("/admin/deployment-mode");
    return data.mode || "SHADOW";
  } catch {
    return "SHADOW";
  }
}

// ─── Helpers (kept for compatibility) ──────────────

export function incrementRewrittenCount(): void {}
export function addAuditEvent(): void {}
export { generateId };
