import type { AuditEvent } from "../types/index.ts";

export function exportAuditCsv(events: AuditEvent[]): void {
  const headers = [
    "Time",
    "User",
    "Platform",
    "Severity",
    "Categories",
    "Action",
    "Policy Version",
    "Reason",
  ];

  const rows = events.map((e) => [
    new Date(e.timestamp).toISOString(),
    e.user,
    e.ai_platform || "",
    e.severity,
    e.categories.join("; "),
    e.action,
    e.policyVersion,
    `"${e.reason.replace(/"/g, '""')}"`,
  ]);

  const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `sip-audit-${Date.now()}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
