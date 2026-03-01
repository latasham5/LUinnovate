/**
 * Mock data and simulated risk detection logic for AI Safety Copilot.
 *
 * In production these would be replaced by real API calls to a backend
 * analysis service. For the hackathon demo everything runs client-side.
 */

// ─── Risk Detection Rules ────────────────────────────────────────────────────
// Each rule has a regex pattern, a risk category, and a confidence range.
// The analyzer checks the prompt against every rule and returns the highest
// confidence match (or marks the prompt as safe).

const RISK_RULES = [
  {
    pattern: /\b\d{3}-\d{2}-\d{4}\b/,
    category: 'PII',
    label: 'Social Security Number detected',
    explanation: 'The prompt contains what appears to be a Social Security Number. Sending SSNs to AI systems violates data handling policies.',
    confidence: 0.97,
    rewriteHint: 'Replace the SSN with a placeholder like XXX-XX-XXXX',
  },
  {
    pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
    category: 'PII',
    label: 'Email address detected',
    explanation: 'Personal email addresses should not be shared with AI tools. They can be used for phishing or social engineering.',
    confidence: 0.85,
    rewriteHint: 'Replace the email with a generic placeholder like user@example.com',
  },
  {
    pattern: /\b(password|passwd|secret|api[_-]?key|token|bearer)\s*[:=]\s*\S+/i,
    category: 'Credentials',
    label: 'Credential or secret detected',
    explanation: 'The prompt appears to contain a password, API key, or authentication token. These must never be sent to AI systems.',
    confidence: 0.95,
    rewriteHint: 'Remove the credential and describe what you need help with generically',
  },
  {
    pattern: /\b(credit\s*card|card\s*number|cvv|expir(y|ation))\b/i,
    category: 'Financial',
    label: 'Financial data reference detected',
    explanation: 'References to credit card details or financial account numbers violate PCI compliance policies.',
    confidence: 0.91,
    rewriteHint: 'Describe the financial structure without including real numbers',
  },
  {
    pattern: /\b(project\s*(phoenix|titan|omega|aurora|nexus)|codename\s*\w+)\b/i,
    category: 'Internal Code Name',
    label: 'Internal project code name detected',
    explanation: 'Internal project code names are confidential. Sharing them with AI tools risks information leakage.',
    confidence: 0.78,
    rewriteHint: 'Replace the code name with a generic description of the project type',
  },
  {
    pattern: /\b(hipaa|phi|protected\s*health|patient\s*(name|record|id|data))\b/i,
    category: 'Regulated',
    label: 'Regulated health data reference detected',
    explanation: 'Health-related data is protected under HIPAA. AI tools must not process identifiable patient information.',
    confidence: 0.88,
    rewriteHint: 'Remove patient identifiers and use de-identified example data',
  },
  {
    pattern: /\b(SELECT\s+.+FROM|INSERT\s+INTO|DROP\s+TABLE|DELETE\s+FROM)\b/i,
    category: 'Internal Code Name',
    label: 'Raw SQL query detected',
    explanation: 'Sending production SQL queries may expose database schema, table names, or sensitive data structures.',
    confidence: 0.82,
    rewriteHint: 'Describe what the query should do instead of pasting the raw SQL',
  },
];

/**
 * Analyze a prompt for risks. Returns a result object describing whether
 * the prompt is safe or flagged.
 *
 * @param {string} prompt - The raw user prompt text
 * @param {string} mode   - Policy mode: 'strict' | 'balanced' | 'fast'
 * @returns {{ safe: boolean, category?: string, label?: string, explanation?: string, confidence?: number, rewriteHint?: string }}
 */
export function analyzePrompt(prompt, mode = 'balanced') {
  // In "fast" mode we only flag very high-confidence matches (>0.90)
  const confidenceThreshold = mode === 'strict' ? 0.5 : mode === 'fast' ? 0.9 : 0.7;

  let bestMatch = null;

  for (const rule of RISK_RULES) {
    if (rule.pattern.test(prompt) && rule.confidence >= confidenceThreshold) {
      if (!bestMatch || rule.confidence > bestMatch.confidence) {
        bestMatch = rule;
      }
    }
  }

  if (!bestMatch) {
    return { safe: true };
  }

  return {
    safe: false,
    category: bestMatch.category,
    label: bestMatch.label,
    explanation: bestMatch.explanation,
    confidence: bestMatch.confidence,
    rewriteHint: bestMatch.rewriteHint,
  };
}

/**
 * Generate a "safer" rewrite of a flagged prompt.
 * In production this would call an LLM; here we do simple regex replacements.
 */
export function rewritePrompt(prompt) {
  let safer = prompt;

  // Redact SSNs
  safer = safer.replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[SSN REDACTED]');

  // Redact emails
  safer = safer.replace(
    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    '[EMAIL REDACTED]'
  );

  // Redact credentials
  safer = safer.replace(
    /(password|passwd|secret|api[_-]?key|token|bearer)\s*[:=]\s*\S+/gi,
    '$1: [REDACTED]'
  );

  // Redact credit card-like numbers
  safer = safer.replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CARD REDACTED]');

  // Redact project code names
  safer = safer.replace(
    /\b(project\s*)(phoenix|titan|omega|aurora|nexus)/gi,
    '$1[CODE NAME REDACTED]'
  );

  return safer;
}

// ─── Mock Log Entries ────────────────────────────────────────────────────────
// Pre-populated log data shown on the Risk Log Dashboard.

export const MOCK_LOGS = [
  {
    id: 1,
    timestamp: '2026-02-28T09:14:22Z',
    user: 'Alice Chen',
    team: 'Engineering',
    category: 'PII',
    action: 'Rewritten',
    policyVersion: 'v2.4-strict',
    confidence: 0.97,
    snippet: 'Prompt contained SSN pattern',
  },
  {
    id: 2,
    timestamp: '2026-02-28T08:47:11Z',
    user: 'Bob Martinez',
    team: 'Sales',
    category: 'Credentials',
    action: 'Blocked',
    policyVersion: 'v2.4-strict',
    confidence: 0.95,
    snippet: 'API key included in prompt',
  },
  {
    id: 3,
    timestamp: '2026-02-27T16:33:05Z',
    user: 'Carol Johnson',
    team: 'Finance',
    category: 'Financial',
    action: 'Rewritten',
    policyVersion: 'v2.4-balanced',
    confidence: 0.91,
    snippet: 'Credit card number referenced',
  },
  {
    id: 4,
    timestamp: '2026-02-27T14:22:58Z',
    user: 'David Kim',
    team: 'Engineering',
    category: 'Internal Code Name',
    action: 'Allowed with Warning',
    policyVersion: 'v2.4-balanced',
    confidence: 0.78,
    snippet: 'Project code name mentioned',
  },
  {
    id: 5,
    timestamp: '2026-02-27T11:05:30Z',
    user: 'Eva Patel',
    team: 'Healthcare Ops',
    category: 'Regulated',
    action: 'Blocked',
    policyVersion: 'v2.4-strict',
    confidence: 0.88,
    snippet: 'Patient health identifier found',
  },
  {
    id: 6,
    timestamp: '2026-02-26T17:41:19Z',
    user: 'Frank Wu',
    team: 'Engineering',
    category: 'Internal Code Name',
    action: 'Rewritten',
    policyVersion: 'v2.4-balanced',
    confidence: 0.82,
    snippet: 'Production SQL query detected',
  },
  {
    id: 7,
    timestamp: '2026-02-26T13:28:44Z',
    user: 'Grace Lee',
    team: 'Marketing',
    category: 'PII',
    action: 'Rewritten',
    policyVersion: 'v2.4-fast',
    confidence: 0.85,
    snippet: 'Employee email address shared',
  },
  {
    id: 8,
    timestamp: '2026-02-26T10:15:02Z',
    user: 'Henry Zhao',
    team: 'Legal',
    category: 'Regulated',
    action: 'Blocked',
    policyVersion: 'v2.4-strict',
    confidence: 0.93,
    snippet: 'HIPAA-regulated data in prompt',
  },
  {
    id: 9,
    timestamp: '2026-02-25T15:52:37Z',
    user: 'Alice Chen',
    team: 'Engineering',
    category: 'Credentials',
    action: 'Blocked',
    policyVersion: 'v2.4-strict',
    confidence: 0.96,
    snippet: 'Bearer token pasted in prompt',
  },
  {
    id: 10,
    timestamp: '2026-02-25T09:30:15Z',
    user: 'Bob Martinez',
    team: 'Sales',
    category: 'PII',
    action: 'Allowed with Warning',
    policyVersion: 'v2.4-fast',
    confidence: 0.72,
    snippet: 'Customer contact info included',
  },
];

// ─── Mock Supervisor Data ────────────────────────────────────────────────────
// Aggregated per-employee data for the supervisor dashboard.

export const MOCK_EMPLOYEES = [
  {
    id: 1,
    name: 'Alice Chen',
    team: 'Engineering',
    flags: 5,
    categories: ['PII', 'Credentials'],
    recommendedTraining: 'Handling Sensitive Identifiers',
    lastIncident: '2026-02-28',
  },
  {
    id: 2,
    name: 'Bob Martinez',
    team: 'Sales',
    flags: 3,
    categories: ['PII', 'Credentials'],
    recommendedTraining: 'Secure AI Prompt Practices',
    lastIncident: '2026-02-28',
  },
  {
    id: 3,
    name: 'Carol Johnson',
    team: 'Finance',
    flags: 2,
    categories: ['Financial'],
    recommendedTraining: 'PCI Compliance Basics',
    lastIncident: '2026-02-27',
  },
  {
    id: 4,
    name: 'David Kim',
    team: 'Engineering',
    flags: 1,
    categories: ['Internal Code Name'],
    recommendedTraining: null,
    lastIncident: '2026-02-27',
  },
  {
    id: 5,
    name: 'Eva Patel',
    team: 'Healthcare Ops',
    flags: 4,
    categories: ['Regulated', 'PII'],
    recommendedTraining: 'HIPAA & AI Data Handling',
    lastIncident: '2026-02-27',
  },
  {
    id: 6,
    name: 'Frank Wu',
    team: 'Engineering',
    flags: 2,
    categories: ['Internal Code Name'],
    recommendedTraining: null,
    lastIncident: '2026-02-26',
  },
  {
    id: 7,
    name: 'Grace Lee',
    team: 'Marketing',
    flags: 1,
    categories: ['PII'],
    recommendedTraining: null,
    lastIncident: '2026-02-26',
  },
  {
    id: 8,
    name: 'Henry Zhao',
    team: 'Legal',
    flags: 3,
    categories: ['Regulated'],
    recommendedTraining: 'Regulated Data & AI Systems',
    lastIncident: '2026-02-26',
  },
];

// ─── Training Module Content ─────────────────────────────────────────────────

export const TRAINING_MODULES = [
  {
    id: 'sensitive-ids',
    title: 'Handling Sensitive Identifiers',
    scenario: 'You need to ask the AI assistant to help format a customer report. The report contains customer Social Security Numbers. What should you do?',
    options: [
      { text: 'Paste the full report including SSNs into the AI prompt', correct: false },
      { text: 'Replace all SSNs with placeholder values before sending', correct: true },
      { text: 'Ask the AI to promise not to store the data, then send it', correct: false },
      { text: 'Send only the SSNs without any other context', correct: false },
    ],
  },
  {
    id: 'secure-prompts',
    title: 'Secure AI Prompt Practices',
    scenario: 'Your manager asks you to use the AI tool to debug a production API issue. You have the API key and error logs. What is the safest approach?',
    options: [
      { text: 'Include the API key so the AI can reproduce the issue', correct: false },
      { text: 'Share the error logs with the API key redacted', correct: true },
      { text: 'Describe the error from memory without any logs', correct: false },
      { text: 'Ask IT to temporarily disable the API key before sharing', correct: false },
    ],
  },
  {
    id: 'pci-basics',
    title: 'PCI Compliance Basics',
    scenario: 'A customer calls with a billing issue and reads you their credit card number. You want the AI to help calculate a refund. What should you do?',
    options: [
      { text: 'Type the full card number into the AI prompt', correct: false },
      { text: 'Use only the last four digits and describe the refund scenario', correct: true },
      { text: 'Encrypt the card number before sending it to the AI', correct: false },
      { text: 'Ask the AI to delete the card number after processing', correct: false },
    ],
  },
];

// ─── Example Prompts for Demo ────────────────────────────────────────────────
// Pre-loaded example prompts users can click to see the system in action.

export const EXAMPLE_PROMPTS = [
  {
    label: 'SSN in prompt',
    text: 'Can you help me format this employee record? Name: John Smith, SSN: 451-23-7890, Department: Engineering',
  },
  {
    label: 'API key leak',
    text: 'I\'m getting errors with this API call. My api_key: sk-proj-abc123def456 and the endpoint returns a 403.',
  },
  {
    label: 'Credit card ref',
    text: 'Help me write a script to validate credit card numbers. The customer\'s card number is 4532-1234-5678-9012 and the CVV is 321.',
  },
  {
    label: 'Project code name',
    text: 'Summarize the latest status update for Project Phoenix. The launch date is confidential — Q3 2026.',
  },
  {
    label: 'Safe prompt',
    text: 'Can you help me write a Python function that sorts a list of dictionaries by a given key?',
  },
];
