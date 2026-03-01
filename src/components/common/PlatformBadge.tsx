import type { AiPlatform } from "../../types/index.ts";

const PLATFORM_CONFIG: Record<AiPlatform, { bg: string; text: string }> = {
  ChatGPT: { bg: "bg-emerald-100", text: "text-emerald-700" },
  "Microsoft Copilot": { bg: "bg-blue-100", text: "text-blue-700" },
  "Google Gemini": { bg: "bg-indigo-100", text: "text-indigo-700" },
  "GitHub Copilot": { bg: "bg-slate-100", text: "text-slate-700" },
  Claude: { bg: "bg-orange-100", text: "text-orange-700" },
  "Custom/Other": { bg: "bg-neutral-100", text: "text-neutral-600" },
};

export default function PlatformBadge({ platform }: { platform: AiPlatform }) {
  const config = PLATFORM_CONFIG[platform] ?? PLATFORM_CONFIG["Custom/Other"];
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${config.bg} ${config.text}`}
    >
      {platform}
    </span>
  );
}
