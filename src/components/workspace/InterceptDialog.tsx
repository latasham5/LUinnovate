import { useState, useEffect, useRef } from "react";
import { ShieldX, ChevronDown, ChevronUp, X } from "lucide-react";
import { useApp } from "../../state/AppContext.tsx";
import { useFocusTrap } from "../../hooks/useFocusTrap.ts";
import { RiskBadge, CategoryChip } from "../common/StatusBadge.tsx";

interface InterceptDialogProps {
  open: boolean;
  onClose: () => void;
  onUseSafer: (saferPrompt: string, originalPrompt: string) => void;
  onEditOriginal: () => void;
}

export default function InterceptDialog({
  open,
  onClose,
  onUseSafer,
  onEditOriginal,
}: InterceptDialogProps) {
  const { lastAnalysis } = useApp();
  const [saferText, setSaferText] = useState("");
  const [showOriginal, setShowOriginal] = useState(false);
  const containerRef = useFocusTrap(open);
  const returnFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (open) {
      returnFocusRef.current = document.activeElement as HTMLElement;
      if (lastAnalysis?.saferPrompt) {
        setSaferText(lastAnalysis.saferPrompt);
      }
    }
  }, [open, lastAnalysis]);

  useEffect(() => {
    if (!open && returnFocusRef.current) {
      returnFocusRef.current.focus();
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function handleEsc(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [open, onClose]);

  if (!open || !lastAnalysis) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      aria-hidden={!open}
    >
      <div
        ref={containerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="intercept-title"
        aria-describedby="intercept-desc"
        className="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center">
                <ShieldX className="w-5 h-5 text-brand-red" aria-hidden="true" />
              </div>
              <div>
                <h2
                  id="intercept-title"
                  className="text-base font-semibold text-gray-900"
                >
                  PromptGuard stopped this message
                </h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  Sensitive data was detected in your prompt
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Close dialog"
            >
              <X className="w-4 h-4 text-gray-400" aria-hidden="true" />
            </button>
          </div>

          {/* Severity and categories */}
          <div id="intercept-desc" className="mb-4">
            <div className="flex items-center gap-2 flex-wrap mb-3">
              <RiskBadge level={lastAnalysis.riskLevel} />
              {lastAnalysis.categories.map((cat) => (
                <CategoryChip key={cat} category={cat} />
              ))}
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">
              {lastAnalysis.explanation}
            </p>
          </div>

          {/* Safer prompt */}
          {lastAnalysis.saferPrompt && (
            <div className="mb-4">
              <label
                htmlFor="safer-prompt"
                className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5"
              >
                Safer Prompt
              </label>
              <textarea
                id="safer-prompt"
                value={saferText}
                onChange={(e) => setSaferText(e.target.value)}
                rows={4}
                className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm focus:border-brand-red focus:ring-0 focus:outline-none resize-none"
              />
            </div>
          )}

          {/* Collapsible original */}
          <div className="mb-6">
            <button
              onClick={() => setShowOriginal(!showOriginal)}
              className="flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-700 transition-colors"
              aria-expanded={showOriginal}
            >
              {showOriginal ? (
                <ChevronUp className="w-3.5 h-3.5" aria-hidden="true" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" aria-hidden="true" />
              )}
              Original Prompt
            </button>
            {showOriginal && (
              <div className="mt-2 bg-gray-50 rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-600">
                {lastAnalysis.originalPrompt}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={() =>
                onUseSafer(saferText, lastAnalysis.originalPrompt)
              }
              className="flex-1 bg-brand-red text-white py-2.5 px-4 rounded-xl text-sm font-medium hover:bg-brand-red-hover transition-colors"
            >
              Use safer prompt
            </button>
            <button
              onClick={onEditOriginal}
              className="flex-1 bg-gray-100 text-gray-700 py-2.5 px-4 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
            >
              Edit original
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2.5 text-gray-500 text-sm font-medium hover:text-gray-700 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>

      {/* aria-live announcer */}
      <div aria-live="assertive" className="sr-only" id="intercept-announcer" />
    </div>
  );
}
