import type { AuditEvent, AiPlatform } from "../../types/index.ts";
import { AI_PLATFORMS } from "../../types/index.ts";

interface PlatformChartProps {
  events: AuditEvent[];
}

const COLORS: Record<AiPlatform, string> = {
  ChatGPT: "bg-emerald-400",
  "Microsoft Copilot": "bg-blue-400",
  "Google Gemini": "bg-indigo-400",
  "GitHub Copilot": "bg-slate-400",
  Claude: "bg-orange-400",
  "Custom/Other": "bg-neutral-400",
};

export default function PlatformChart({ events }: PlatformChartProps) {
  const counts: Record<AiPlatform, number> = {} as Record<AiPlatform, number>;
  for (const p of AI_PLATFORMS) counts[p] = 0;

  for (const e of events) {
    if (e.ai_platform && counts[e.ai_platform] !== undefined) {
      counts[e.ai_platform] += 1;
    }
  }

  const max = Math.max(...Object.values(counts), 1);

  const summary = AI_PLATFORMS.filter((p) => counts[p] > 0)
    .map((p) => `${p}: ${counts[p]}`)
    .join(", ");

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm mb-6">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">
        Prompts by AI Platform
      </h3>
      <div
        className="space-y-3"
        role="img"
        aria-label="Bar chart showing prompts by AI platform"
      >
        {AI_PLATFORMS.map((plat) => (
          <div key={plat} className="flex items-center gap-3">
            <span className="w-32 text-xs text-gray-600 text-right truncate">
              {plat}
            </span>
            <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${COLORS[plat]} transition-all duration-500`}
                style={{ width: `${(counts[plat] / max) * 100}%` }}
              />
            </div>
            <span className="w-8 text-xs text-gray-500 font-medium">
              {counts[plat]}
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-3">
        {summary || "No events to display."}
      </p>
    </div>
  );
}
