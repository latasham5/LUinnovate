import { FileText, AlertTriangle, ShieldX, Monitor } from "lucide-react";
import type { AuditEvent } from "../../types/index.ts";

interface KpiCardsProps {
  events: AuditEvent[];
}

export default function KpiCards({ events }: KpiCardsProps) {
  const total = events.length;
  const flagged = events.filter((e) => e.action !== "allowed").length;
  const highRisk = events.filter((e) => e.severity === "high").length;

  // Find top platform
  const platformCounts: Record<string, number> = {};
  for (const e of events) {
    if (e.ai_platform) {
      platformCounts[e.ai_platform] = (platformCounts[e.ai_platform] || 0) + 1;
    }
  }
  const topEntry = Object.entries(platformCounts).sort((a, b) => b[1] - a[1])[0];
  const topPlatformLabel = topEntry ? `${topEntry[0]} (${topEntry[1]})` : "—";

  const cards = [
    {
      label: "Total Prompts Scanned",
      value: total,
      icon: FileText,
      color: "text-gray-700",
      bg: "bg-gray-50",
    },
    {
      label: "Flagged",
      value: flagged,
      icon: AlertTriangle,
      color: "text-amber-700",
      bg: "bg-amber-50",
    },
    {
      label: "High Risk",
      value: highRisk,
      icon: ShieldX,
      color: "text-red-700",
      bg: "bg-red-50",
    },
    {
      label: "Top Platform",
      value: topPlatformLabel,
      icon: Monitor,
      color: "text-blue-700",
      bg: "bg-blue-50",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.label}
            className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-xl ${card.bg} flex items-center justify-center`}
              >
                <Icon className={`w-5 h-5 ${card.color}`} aria-hidden="true" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                <p className="text-xs text-gray-500">{card.label}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
