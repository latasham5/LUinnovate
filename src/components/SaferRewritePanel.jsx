import { ArrowRight, CheckCircle2, FileEdit, Send, Diff } from 'lucide-react';

/**
 * SaferRewritePanel — Coca-Cola themed side-by-side prompt comparison.
 * 16px card radius, red/green comparison, pill-shaped send button.
 */
export default function SaferRewritePanel({ original, rewritten, result, onSendSafer, sent }) {
  if (!result || result.safe) return null;

  const bullets = [];
  if (/\[SSN REDACTED\]/.test(rewritten)) bullets.push('Sensitive identifiers (SSN) removed');
  if (/\[EMAIL REDACTED\]/.test(rewritten)) bullets.push('Email addresses replaced with placeholders');
  if (/\[REDACTED\]/.test(rewritten) && !/SSN|EMAIL/.test(rewritten.replace(/\[.*?REDACTED\]/g, '')))
    bullets.push('Credentials and secrets removed');
  if (/\[CARD REDACTED\]/.test(rewritten)) bullets.push('Financial card numbers removed');
  if (/\[CODE NAME REDACTED\]/.test(rewritten)) bullets.push('Internal project code names generalized');
  if (bullets.length === 0) bullets.push('Prompt reframed to describe structure instead of raw data');
  bullets.push('Data generalized to prevent information leakage');

  return (
    <div className="bg-white rounded-[16px] border border-neutral-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 border-b border-neutral-100 flex items-center gap-2">
        <Diff size={16} className="text-[#ea0000]" />
        <span className="text-sm font-semibold text-black">Safer Prompt Rewrite</span>
      </div>

      <div className="p-5 space-y-4">
        {/* Side-by-side comparison */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-bold text-[#ea0000] uppercase tracking-wider mb-2 flex items-center gap-1">
              <FileEdit size={12} />
              Original Prompt
            </p>
            <div className="p-3 rounded-[12px] bg-red-50 border border-red-100 text-sm text-black leading-relaxed">
              {original}
            </div>
          </div>

          <div>
            <p className="text-xs font-bold text-[#1d6e17] uppercase tracking-wider mb-2 flex items-center gap-1">
              <CheckCircle2 size={12} />
              Safer Rewrite
            </p>
            <div className="p-3 rounded-[12px] bg-emerald-50 border border-emerald-100 text-sm text-black leading-relaxed">
              {rewritten}
            </div>
          </div>
        </div>

        {/* Explanation bullets */}
        <div className="bg-neutral-50 rounded-[12px] p-4">
          <p className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-2">
            What changed
          </p>
          <ul className="space-y-1.5">
            {bullets.map((b, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-neutral-600">
                <ArrowRight size={14} className="text-[#ea0000] mt-0.5 shrink-0" />
                {b}
              </li>
            ))}
          </ul>
        </div>

        {/* Send button — pill shaped, green */}
        {sent ? (
          <div className="flex items-center gap-2 text-[#1d6e17] text-sm font-semibold">
            <CheckCircle2 size={16} />
            Safer prompt sent successfully
          </div>
        ) : (
          <button
            onClick={onSendSafer}
            className="flex items-center gap-2 px-5 py-2 rounded-full bg-[#1d6e17] text-white text-sm font-semibold hover:bg-[#165a12] transition-colors cursor-pointer"
          >
            <Send size={14} />
            Send Safer Prompt
          </button>
        )}
      </div>
    </div>
  );
}
