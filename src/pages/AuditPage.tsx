import { useEffect, useState, useMemo } from "react";
import { Download } from "lucide-react";
import { getAuditEvents } from "../api/index.ts";
import { exportAuditCsv } from "../utils/csv.ts";
import type {
  AuditEvent,
  RiskLevel,
  DetectionCategory,
} from "../types/index.ts";
import KpiCards from "../components/audit/KpiCards.tsx";
import AuditFilters from "../components/audit/AuditFilters.tsx";
import BarChart from "../components/audit/BarChart.tsx";
import AuditTable from "../components/audit/AuditTable.tsx";

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [severity, setSeverity] = useState<RiskLevel | "all">("all");
  const [category, setCategory] = useState<DetectionCategory | "all">("all");

  useEffect(() => {
    getAuditEvents().then(setEvents);
  }, []);

  const filtered = useMemo(() => {
    return events.filter((e) => {
      if (severity !== "all" && e.severity !== severity) return false;
      if (category !== "all" && !e.categories.includes(category)) return false;
      return true;
    });
  }, [events, severity, category]);

  return (
    <main className="flex-1 overflow-y-auto p-6" id="main-content">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Audit Log</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Review flagged prompts, policy violations, and actions taken by
              PromptGuard.
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
          onSeverityChange={setSeverity}
          onCategoryChange={setCategory}
        />

        <BarChart events={filtered} />

        <AuditTable events={filtered} />
      </div>
    </main>
  );
}
