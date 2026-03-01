import apiClient from "./client.ts";
import type { AdminUserEntry, UserProfile } from "../types/index.ts";

export async function getUsers(): Promise<AdminUserEntry[]> {
  const { data } = await apiClient.get<AdminUserEntry[]>("/admin/users");
  return data;
}

export async function getUserById(
  employeeId: string,
): Promise<AdminUserEntry> {
  const { data } = await apiClient.get<AdminUserEntry>(
    `/admin/users/${employeeId}`,
  );
  return data;
}

export async function updateUserRole(
  employeeId: string,
  role: UserProfile["role"],
): Promise<AdminUserEntry> {
  const { data } = await apiClient.put<AdminUserEntry>(
    `/admin/users/${employeeId}/role`,
    { role },
  );
  return data;
}

export async function assignTraining(
  employeeId: string,
  moduleId: string,
): Promise<void> {
  await apiClient.post(`/admin/users/${employeeId}/training`, {
    module_id: moduleId,
  });
}
