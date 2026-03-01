import { AlertTriangle, ShieldAlert, TrendingUp } from 'lucide-react';

/**
 * SafetyWarning — Coca-Cola themed risk alert panel.
 * Uses brand-consistent 16px radius, confidence bar with red accent.
 */

const CATEGORY_STYLES = {
  PII: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', badge: 'bg-orange-100 text-orange-700' },
  Credentials: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-[#ea0000]', badge: 'bg-red-100 text-[#ea0000]' },
  Financial: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-700' },
  'Internal Code Name': { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', badge: 'bg-purple-100 text-purple-700' },
  Regulated: { bg: 'bg-rose-50', border: 'border-rose-200', text: 'text-rose-700', badge: 'bg-rose-100 text-rose-700' },
};

const fallbackStyle = { bg: 'bg-neutral-50', border: 'border-neutral-200', text: 'text-neutral-700', badge: 'bg-neutral-100 text-neutral-700' };

export default function SafetyWarning({ result }) {
  if (!result || result.safe) return null;

  const style = CATEGORY_STYLES[result.category] || fallbackStyle;
  const confidencePct = Math.round(result.confidence * 100);

  return (
    <div className={`rounded-[16px] border ${style.border} ${style.bg} p-5`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-[10px] ${style.badge}`}>
          <ShieldAlert size={20} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h3 className={`text-sm font-bold ${style.text}`}>
              <AlertTriangle size={14} className="inline mr-1 -mt-0.5" />
              Risk Detected
            </h3>
            <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${style.badge}`}>
              {result.category}
            </span>
          </div>

          <p className={`text-sm font-semibold ${style.text} mb-1`}>{result.label}</p>
          <p className="text-sm text-neutral-600">{result.explanation}</p>

          {/* Confidence bar */}
          <div className="mt-3 flex items-center gap-3">
            <TrendingUp size={14} className="text-neutral-400" />
            <span className="text-xs text-neutral-500 w-24">Confidence</span>
            <div className="flex-1 h-2 bg-white rounded-full overflow-hidden border border-neutral-200">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  confidencePct >= 90 ? 'bg-[#ea0000]' : confidencePct >= 75 ? 'bg-amber-500' : 'bg-yellow-400'
                }`}
                style={{ width: `${confidencePct}%` }}
              />
            </div>
            <span className="text-xs font-mono font-semibold text-black w-10 text-right">
              {confidencePct}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
