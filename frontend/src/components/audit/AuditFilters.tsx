import type { RiskLevel, DetectionCategory } from "../../types/index.ts";

interface AuditFiltersProps {
  severity: RiskLevel | "all";
  category: DetectionCategory | "all";
  onSeverityChange: (v: RiskLevel | "all") => void;
  onCategoryChange: (v: DetectionCategory | "all") => void;
}

const SEVERITIES: (RiskLevel | "all")[] = ["all", "low", "medium", "high"];
const CATEGORIES: (DetectionCategory | "all")[] = [
  "all",
  "PII",
  "Credentials",
  "Financial",
  "Health",
  "Internal",
];

export default function AuditFilters({
  severity,
  category,
  onSeverityChange,
  onCategoryChange,
}: AuditFiltersProps) {
  return (
    <fieldset className="flex flex-wrap items-center gap-4 mb-6">
      <legend className="sr-only">Audit log filters</legend>

      <div className="flex items-center gap-2">
        <label
          htmlFor="filter-severity"
          className="text-xs font-medium text-gray-500"
        >
          Severity
        </label>
        <select
          id="filter-severity"
          value={severity}
          onChange={(e) =>
            onSeverityChange(e.target.value as RiskLevel | "all")
          }
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-brand-red focus:ring-0 focus:outline-none"
        >
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s === "all" ? "All Severities" : s.charAt(0).toUpperCase() + s.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label
          htmlFor="filter-category"
          className="text-xs font-medium text-gray-500"
        >
          Category
        </label>
        <select
          id="filter-category"
          value={category}
          onChange={(e) =>
            onCategoryChange(e.target.value as DetectionCategory | "all")
          }
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-brand-red focus:ring-0 focus:outline-none"
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c === "all" ? "All Categories" : c}
            </option>
          ))}
        </select>
      </div>
    </fieldset>
  );
}
