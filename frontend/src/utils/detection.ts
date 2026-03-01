import type { DetectionCategory, RiskLevel } from "../types/index.ts";

interface DetectionRule {
  pattern: RegExp;
  category: DetectionCategory;
  placeholder: string;
}

const RULES: DetectionRule[] = [
  {
    pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    category: "PII",
    placeholder: "[EMAIL_REDACTED]",
  },
  {
    pattern: /\b\d{3}[-.]?\d{2}[-.]?\d{4}\b/g,
    category: "PII",
    placeholder: "[SSN_REDACTED]",
  },
  {
    pattern: /\b(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g,
    category: "PII",
    placeholder: "[PHONE_REDACTED]",
  },
  {
    pattern: /\b(?:password|passwd|pwd)\s*[:=]\s*\S+/gi,
    category: "Credentials",
    placeholder: "[PASSWORD_REDACTED]",
  },
  {
    pattern: /\b(?:api[_-]?key|apikey)\s*[:=]\s*\S+/gi,
    category: "Credentials",
    placeholder: "[API_KEY_REDACTED]",
  },
  {
    pattern: /\b(?:token|access_token|auth_token)\s*[:=]\s*\S+/gi,
    category: "Credentials",
    placeholder: "[TOKEN_REDACTED]",
  },
  {
    pattern: /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b/g,
    category: "Financial",
    placeholder: "[CARD_REDACTED]",
  },
  {
    pattern: /\b(?:diagnosis|prescription|patient|medical\s+record|HIPAA)\b/gi,
    category: "Health",
    placeholder: "[HEALTH_INFO_REDACTED]",
  },
  {
    pattern: /\b(?:internal|confidential|proprietary|do\s+not\s+share|restricted)\b/gi,
    category: "Internal",
    placeholder: "[INTERNAL_REDACTED]",
  },
];

export interface DetectionResult {
  hasSensitiveData: boolean;
  categories: DetectionCategory[];
  riskLevel: RiskLevel;
  saferPrompt: string;
  explanation: string;
}

export function detectSensitiveData(text: string): DetectionResult {
  const foundCategories = new Set<DetectionCategory>();
  let saferPrompt = text;
  const explanations: string[] = [];

  for (const rule of RULES) {
    const regex = new RegExp(rule.pattern.source, rule.pattern.flags);
    if (regex.test(text)) {
      foundCategories.add(rule.category);
      const replaceRegex = new RegExp(rule.pattern.source, rule.pattern.flags);
      saferPrompt = saferPrompt.replace(replaceRegex, rule.placeholder);
      explanations.push(
        `Detected ${rule.category} content matching "${rule.placeholder.replace(/[\[\]]/g, "")}".`
      );
    }
  }

  const categories = Array.from(foundCategories);
  const hasSensitiveData = categories.length > 0;

  let riskLevel: RiskLevel = "low";
  if (categories.includes("Credentials") || categories.includes("Financial")) {
    riskLevel = "high";
  } else if (categories.length >= 2) {
    riskLevel = "high";
  } else if (categories.length === 1) {
    riskLevel = "medium";
  }

  const explanation = hasSensitiveData
    ? `This message contains sensitive data: ${explanations.join(" ")}`
    : "No sensitive data detected.";

  return { hasSensitiveData, categories, riskLevel, saferPrompt, explanation };
}
