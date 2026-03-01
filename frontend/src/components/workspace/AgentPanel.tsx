import { Shield, Copy, Check } from "lucide-react";
import { useState } from "react";
import { useApp } from "../../state/AppContext.tsx";
import {
  SafetyStatusBadge,
  RiskBadge,
  CategoryChip,
} from "../common/StatusBadge.tsx";

export default function AgentPanel() {
  const { lastAnalysis, flaggedEvents, userRisk } = useApp();
  const [copied, setCopied] = useState(false);

  const status = lastAnalysis?.safetyStatus ?? "safe";
  const riskLevel = lastAnalysis?.riskLevel ?? "low";

  const handleCopy = async () => {
    if (lastAnalysis?.saferPrompt) {
      await navigator.clipboard.writeText(lastAnalysis.saferPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <aside
      className="w-80 border-l border-gray-200 bg-gray-50 flex flex-col overflow-y-auto flex-shrink-0"
      aria-label="PromptGuard Agent panel"
    >
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4 h-4 text-brand-red" aria-hidden="true" />
          <h2 className="text-sm font-semibold text-gray-900">
            PromptGuard Agent
          </h2>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <SafetyStatusBadge status={status} />
          <RiskBadge level={riskLevel} />
        </div>
      </div>

      {lastAnalysis && lastAnalysis.categories.length > 0 && (
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Detected Categories
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {lastAnalysis.categories.map((cat) => (
              <CategoryChip key={cat} category={cat} />
            ))}
          </div>
        </div>
      )}

      {lastAnalysis && (
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Why Flagged
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed">
            {lastAnalysis.explanation}
          </p>
        </div>
      )}

      {lastAnalysis?.saferPrompt && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Safer Rewrite
            </h3>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
              aria-label="Copy safer prompt"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3" aria-hidden="true" /> Copied
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" aria-hidden="true" /> Copy
                </>
              )}
            </button>
          </div>
          <p className="text-sm text-gray-700 bg-white rounded-lg border border-gray-200 p-3 leading-relaxed">
            {lastAnalysis.saferPrompt}
          </p>
        </div>
      )}

      {userRisk.trainingRequired && !userRisk.trainingCompleted && (
        <div className="p-4 border-b border-gray-200">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-3">
            <p className="text-sm text-amber-800 font-medium">
              Training Required
            </p>
            <p className="text-xs text-amber-600 mt-1">
              You have had {userRisk.flaggedCount + userRisk.rewrittenCount}{" "}
              flagged events. Please complete the training module.
            </p>
          </div>
        </div>
      )}

      <div className="p-4 flex-1">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Recent Flagged Events
        </h3>
        {flaggedEvents.length === 0 ? (
          <p className="text-xs text-gray-400 italic">No flagged events yet.</p>
        ) : (
          <ul className="space-y-2">
            {flaggedEvents.map((ev) => (
              <li
                key={ev.id}
                className="bg-white rounded-lg border border-gray-200 p-2.5"
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <RiskBadge level={ev.riskLevel} />
                  <span className="text-xs text-gray-400">
                    {new Date(ev.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                <p className="text-xs text-gray-600 truncate">
                  {ev.redactedSnippet}
                </p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {ev.categories.map((c) => (
                    <span
                      key={c}
                      className="text-[10px] px-1.5 py-0.5 bg-gray-50 text-gray-500 rounded"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
