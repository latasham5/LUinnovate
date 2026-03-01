export { default as apiClient } from "./client.ts";
export * as authService from "./authService.ts";
export * as promptService from "./promptService.ts";
export * as policyService from "./policyService.ts";
export * as dashboardService from "./dashboardService.ts";
export * as trainingService from "./trainingService.ts";
export * as auditService from "./auditService.ts";
export * as adminService from "./adminService.ts";

// Re-export legacy mock functions for pages that haven't migrated yet
export {
  analyzePrompt as analyzePromptMock,
  submitPrompt,
  getAuditEvents,
  getUserRisk,
  incrementRewrittenCount,
  completeTraining,
  addAuditEvent,
  generateId,
} from "./mock.ts";
