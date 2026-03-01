import { useEffect, useState, useMemo } from "react";
import { Download } from "lucide-react";
import { getAuditEvents } from "../api/mock.ts";
import { auditService } from "../api/index.ts";
import { exportAuditCsv } from "../utils/csv.ts";
import type {
  AuditEvent,
  RiskLevel,
  DetectionCategory,
  AiPlatform,
} from "../types/index.ts";
import KpiCards from "../components/audit/KpiCards.tsx";
import AuditFilters from "../components/audit/AuditFilters.tsx";
import BarChart from "../components/audit/BarChart.tsx";
import PlatformChart from "../components/audit/PlatformChart.tsx";
import AuditTable from "../components/audit/AuditTable.tsx";

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [severity, setSeverity] = useState<RiskLevel | "all">("all");
  const [category, setCategory] = useState<DetectionCategory | "all">("all");
  const [platform, setPlatform] = useState<AiPlatform | "all">("all");

  useEffect(() => {
    let mounted = true;

    // Try backend first, fall back to mock
    auditService
      .getAuditEntries()
      .then((entries) => {
        if (!mounted) return;
        // Map backend AuditEntry to legacy AuditEvent shape
        const mapped: AuditEvent[] = entries.map((e) => ({
          id: e.audit_id,
          timestamp: new Date(e.timestamp).getTime(),
          user: e.employee_name,
          severity: (e.risk_score >= 70
            ? "high"
            : e.risk_score >= 40
              ? "medium"
              : "low") as RiskLevel,
          categories: e.categories.map((c) => {
            const catMap: Record<string, DetectionCategory> = {
              pii: "PII",
              credentials: "Credentials",
              financial: "Financial",
              health: "Health",
              internal: "Internal",
            };
            return catMap[c] || ("Internal" as DetectionCategory);
          }),
          action: (e.action === "blocked"
            ? "blocked"
            : e.action === "rewritten"
              ? "rewritten"
              : "allowed") as AuditEvent["action"],
          policyVersion: e.policy_mode,
          redactedSnippet: e.redacted_snippet,
          reason: `Risk score: ${e.risk_score}`,
          ai_platform: (e as any).ai_platform || undefined,
        }));
        setEvents(mapped);
      })
      .catch(() => {
        // Fall back to mock data
        if (mounted) {
          getAuditEvents().then(setEvents);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(() => {
    return events.filter((e) => {
      if (severity !== "all" && e.severity !== severity) return false;
      if (category !== "all" && !e.categories.includes(category)) return false;
      if (platform !== "all" && e.ai_platform !== platform) return false;
      return true;
    });
  }, [events, severity, category, platform]);

  return (
    <main className="flex-1 overflow-y-auto p-6" id="main-content">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Audit Log</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Review flagged prompts, policy violations, and actions taken by
              S.I.P.
            </p>
          </div>
          <button
            onClick={() => exportAuditCsv(filtered)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
          >
            <Download className="w-4 h-4" aria-hidden="true" />
            Export CSV
          </button>
        </div>

        <KpiCards events={events} />

        <AuditFilters
          severity={severity}
          category={category}
          platform={platform}
          onSeverityChange={setSeverity}
          onCategoryChange={setCategory}
          onPlatformChange={setPlatform}
        />

        <BarChart events={filtered} />

        <PlatformChart events={filtered} />

        <AuditTable events={filtered} />
      </div>
    </main>
  );
}
