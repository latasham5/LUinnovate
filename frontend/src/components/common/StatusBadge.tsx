import { ShieldCheck, ShieldAlert, ShieldX } from "lucide-react";
import type { SafetyStatus, RiskLevel } from "../../types/index.ts";

const STATUS_CONFIG: Record<
  SafetyStatus,
  { label: string; bg: string; text: string; icon: typeof ShieldCheck }
> = {
  safe: {
    label: "Safe",
    bg: "bg-emerald-50 border-emerald-200",
    text: "text-emerald-700",
    icon: ShieldCheck,
  },
  "needs-review": {
    label: "Needs Review",
    bg: "bg-amber-50 border-amber-200",
    text: "text-amber-700",
    icon: ShieldAlert,
  },
  blocked: {
    label: "Blocked",
    bg: "bg-red-50 border-red-200",
    text: "text-red-700",
    icon: ShieldX,
  },
};

const RISK_CONFIG: Record<RiskLevel, { label: string; bg: string; text: string }> = {
  low: { label: "Low Risk", bg: "bg-emerald-100", text: "text-emerald-800" },
  medium: { label: "Medium Risk", bg: "bg-amber-100", text: "text-amber-800" },
  high: { label: "High Risk", bg: "bg-red-100", text: "text-red-800" },
};

export function SafetyStatusBadge({ status }: { status: SafetyStatus }) {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;
  return (
    <div
      className={`flex items-center gap-2 px-3 py-2 rounded-xl border ${config.bg}`}
    >
      <Icon className={`w-4 h-4 ${config.text}`} aria-hidden="true" />
      <span className={`text-sm font-semibold ${config.text}`}>
        {config.label}
      </span>
    </div>
  );
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  const config = RISK_CONFIG[level];
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${config.bg} ${config.text}`}
    >
      {config.label}
    </span>
  );
}

export function CategoryChip({ category }: { category: string }) {
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200">
      {category}
    </span>
  );
}
