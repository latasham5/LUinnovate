import { useState } from 'react';
import { Shield, ChevronDown, Info } from 'lucide-react';

/**
 * PolicySelector — Coca-Cola themed dropdown for Strict / Balanced / Fast modes.
 * Uses pill-shaped trigger and 16px-radius dropdown card.
 */

const MODES = [
  {
    value: 'strict',
    label: 'Strict',
    color: 'text-[#ea0000] bg-red-50 border-red-200',
    dot: 'bg-[#ea0000]',
    description: 'Maximum protection — flags low-confidence matches. Best for finance, health, and legal teams.',
  },
  {
    value: 'balanced',
    label: 'Balanced',
    color: 'text-amber-700 bg-amber-50 border-amber-200',
    dot: 'bg-amber-500',
    description: 'Default mode — balances safety and usability for most teams.',
  },
  {
    value: 'fast',
    label: 'Fast',
    color: 'text-[#1d6e17] bg-emerald-50 border-emerald-200',
    dot: 'bg-[#1d6e17]',
    description: 'Minimal friction — only blocks high-confidence risks. Best for engineering workflows.',
  },
];

export default function PolicySelector({ mode, onModeChange }) {
  const [open, setOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const current = MODES.find((m) => m.value === mode);

  return (
    <div className="relative">
      {/* Trigger button — pill shaped */}
      <button
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-colors cursor-pointer ${current.color}`}
      >
        <Shield size={14} />
        {current.label}
        <ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {/* Info icon with tooltip */}
      <div
        className="absolute -right-7 top-1/2 -translate-y-1/2"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <Info size={14} className="text-neutral-400 cursor-help" />
        {showTooltip && (
          <div className="absolute right-0 top-full mt-2 w-64 p-3 bg-black text-white text-xs rounded-[12px] shadow-lg z-50">
            <p className="font-semibold mb-1">Policy Modes</p>
            {MODES.map((m) => (
              <p key={m.value} className="mb-1">
                <span className="font-medium">{m.label}:</span> {m.description}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* Dropdown menu */}
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-2 w-72 bg-white rounded-[16px] shadow-lg border border-neutral-200 z-50 overflow-hidden">
            {MODES.map((m) => (
              <button
                key={m.value}
                onClick={() => {
                  onModeChange(m.value);
                  setOpen(false);
                }}
                className={`w-full text-left px-4 py-3 flex items-start gap-3 hover:bg-neutral-50 transition-colors cursor-pointer ${
                  m.value === mode ? 'bg-neutral-50' : ''
                }`}
              >
                <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${m.dot}`} />
                <div>
                  <p className="text-sm font-medium text-black">{m.label}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{m.description}</p>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
