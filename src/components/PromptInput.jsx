import { useState } from 'react';
import { Send, Sparkles, Loader2 } from 'lucide-react';
import { EXAMPLE_PROMPTS } from '../data/mockData';

/**
 * PromptInput — Coca-Cola themed prompt text area.
 * Pill-shaped example buttons, red primary action button, 16px card radius.
 */
export default function PromptInput({ onAnalyze, analyzing }) {
  const [text, setText] = useState('');

  const handleSubmit = () => {
    if (!text.trim() || analyzing) return;
    onAnalyze(text.trim());
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-white rounded-[16px] border border-neutral-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 border-b border-neutral-100 flex items-center gap-2">
        <Sparkles size={16} className="text-[#ea0000]" />
        <span className="text-sm font-semibold text-black">Prompt to Internal AI</span>
      </div>

      {/* Text area */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your prompt here… The system will analyze it for sensitive data before sending."
        rows={5}
        className="w-full px-5 py-4 text-sm text-black placeholder:text-neutral-400 resize-none focus:outline-none"
      />

      {/* Footer with examples + submit */}
      <div className="px-5 py-3 border-t border-neutral-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {/* Quick-fill example prompts — pill shaped */}
        <div className="flex flex-wrap gap-1.5">
          <span className="text-xs text-neutral-400 mr-1 self-center">Try:</span>
          {EXAMPLE_PROMPTS.map((ex) => (
            <button
              key={ex.label}
              onClick={() => setText(ex.text)}
              className="text-xs px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-600 hover:bg-[#ea0000]/10 hover:text-[#ea0000] transition-colors cursor-pointer"
            >
              {ex.label}
            </button>
          ))}
        </div>

        {/* Analyze button — Coca-Cola red, pill shaped */}
        <button
          onClick={handleSubmit}
          disabled={!text.trim() || analyzing}
          className="flex items-center gap-2 px-5 py-2 rounded-full bg-[#ea0000] text-white text-sm font-semibold hover:bg-[#c50000] disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer shrink-0"
        >
          {analyzing ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Send size={14} />
              Analyze Prompt
            </>
          )}
        </button>
      </div>
    </div>
  );
}
