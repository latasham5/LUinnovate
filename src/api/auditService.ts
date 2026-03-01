import apiClient from "./client.ts";
import type {
  AuditEntry,
  AuditFilters,
  AuditSummary,
} from "../types/index.ts";

export async function getAuditEntries(
  filters?: AuditFilters,
): Promise<AuditEntry[]> {
  const { data } = await apiClient.get<AuditEntry[]>("/audit", {
    params: filters,
  });
  return data;
}

export async function getAuditSummary(
  filters?: AuditFilters,
): Promise<AuditSummary> {
  const { data } = await apiClient.get<AuditSummary>("/audit/summary", {
    params: filters,
  });
  return data;
}

export async function getAuditEntry(auditId: string): Promise<AuditEntry> {
  const { data } = await apiClient.get<AuditEntry>(`/audit/${auditId}`);
  return data;
}

export async function exportAuditCSV(
  filters?: AuditFilters,
): Promise<Blob> {
  const { data } = await apiClient.get("/audit/export", {
    params: filters,
    responseType: "blob",
  });
  return data as Blob;
}
