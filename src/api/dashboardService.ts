import apiClient from "./client.ts";
import type { DashboardStats, DepartmentStats } from "../types/index.ts";

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await apiClient.get<DashboardStats>("/dashboard");
  return data;
}

export async function getDepartmentStats(
  department: string,
): Promise<DepartmentStats> {
  const { data } = await apiClient.get<DepartmentStats>(
    `/dashboard/department/${encodeURIComponent(department)}`,
  );
  return data;
}

export async function getAllDepartmentStats(): Promise<DepartmentStats[]> {
  const { data } = await apiClient.get<DepartmentStats[]>(
    "/dashboard/departments",
  );
  return data;
}
