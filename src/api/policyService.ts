import apiClient from "./client.ts";
import type { PolicyConfig, PolicyRule } from "../types/index.ts";
import { type PolicyMode } from "../types/index.ts";

export async function getPolicyConfig(): Promise<PolicyConfig> {
  const { data } = await apiClient.get<PolicyConfig>("/policy");
  return data;
}

export async function updatePolicyMode(mode: PolicyMode): Promise<PolicyConfig> {
  const { data } = await apiClient.put<PolicyConfig>("/policy/mode", { mode });
  return data;
}

export async function updatePolicyRule(rule: PolicyRule): Promise<PolicyRule> {
  const { data } = await apiClient.put<PolicyRule>(
    `/policy/rules/${rule.rule_id}`,
    rule,
  );
  return data;
}

export async function getPolicyRules(): Promise<PolicyRule[]> {
  const { data } = await apiClient.get<PolicyRule[]>("/policy/rules");
  return data;
}
