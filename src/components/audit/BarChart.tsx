import type { AuditEvent, DetectionCategory } from "../../types/index.ts";

interface BarChartProps {
  events: AuditEvent[];
}

const ALL_CATEGORIES: DetectionCategory[] = [
  "PII",
  "Credentials",
  "Financial",
  "Health",
  "Internal",
];

const COLORS: Record<DetectionCategory, string> = {
  PII: "bg-blue-400",
  Credentials: "bg-red-400",
  Financial: "bg-amber-400",
  Health: "bg-emerald-400",
  Internal: "bg-purple-400",
};

export default function BarChart({ events }: BarChartProps) {
  const counts: Record<DetectionCategory, number> = {
    PII: 0,
    Credentials: 0,
    Financial: 0,
    Health: 0,
    Internal: 0,
  };

  for (const e of events) {
    for (const cat of e.categories) {
      counts[cat] = (counts[cat] || 0) + 1;
    }
  }

  const max = Math.max(...Object.values(counts), 1);

  const summary = ALL_CATEGORIES.filter((c) => counts[c] > 0)
    .map((c) => `${c}: ${counts[c]}`)
    .join(", ");

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm mb-6">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">
        Flags by Category
      </h3>
      <div className="space-y-3" role="img" aria-label="Bar chart showing flags by category">
        {ALL_CATEGORIES.map((cat) => (
          <div key={cat} className="flex items-center gap-3">
            <span className="w-24 text-xs text-gray-600 text-right">
              {cat}
            </span>
            <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${COLORS[cat]} transition-all duration-500`}
                style={{ width: `${(counts[cat] / max) * 100}%` }}
              />
            </div>
            <span className="w-8 text-xs text-gray-500 font-medium">
              {counts[cat]}
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-3">
        {summary || "No flagged events to display."}
      </p>
    </div>
  );
}
