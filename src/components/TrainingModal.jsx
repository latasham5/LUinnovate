import { useState } from 'react';
import { X, GraduationCap, CheckCircle2, XCircle } from 'lucide-react';
import { TRAINING_MODULES } from '../data/mockData';

/**
 * TrainingModal — Coca-Cola themed micro-training popup.
 * Red header bar, pill-shaped submit button, 20px card radius.
 */
export default function TrainingModal({ open, onClose, moduleId }) {
  const [selected, setSelected] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const mod = TRAINING_MODULES.find((m) => m.id === moduleId) || TRAINING_MODULES[0];

  const handleSubmit = () => {
    if (selected === null) return;
    setSubmitted(true);
  };

  const handleClose = () => {
    setSelected(null);
    setSubmitted(false);
    onClose();
  };

  if (!open) return null;

  const isCorrect = submitted && mod.options[selected]?.correct;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={handleClose} />

      <div className="relative bg-white rounded-[20px] shadow-2xl max-w-lg w-full overflow-hidden">
        {/* Header — Coca-Cola red */}
        <div className="bg-[#ea0000] px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-white">
            <GraduationCap size={20} />
            <span className="font-bold">Quick AI Safety Training</span>
          </div>
          <button onClick={handleClose} className="text-white/80 hover:text-white cursor-pointer">
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4">
          <h3 className="text-base font-bold text-black">{mod.title}</h3>
          <p className="text-sm text-neutral-600 leading-relaxed">{mod.scenario}</p>

          <div className="space-y-2">
            {mod.options.map((opt, idx) => {
              let ringClass = 'border-neutral-200 hover:border-[#ea0000]/40';
              if (submitted && idx === selected) {
                ringClass = opt.correct
                  ? 'border-[#1d6e17] bg-emerald-50'
                  : 'border-[#ea0000] bg-red-50';
              } else if (submitted && opt.correct) {
                ringClass = 'border-[#1d6e17] bg-emerald-50';
              }

              return (
                <button
                  key={idx}
                  onClick={() => !submitted && setSelected(idx)}
                  disabled={submitted}
                  className={`w-full text-left px-4 py-3 rounded-[12px] border text-sm transition-colors cursor-pointer flex items-start gap-3 ${ringClass} ${
                    !submitted && selected === idx ? 'border-[#ea0000] bg-[#ea0000]/5' : ''
                  }`}
                >
                  <span className={`mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                    !submitted && selected === idx ? 'border-[#ea0000]' : 'border-neutral-300'
                  }`}>
                    {!submitted && selected === idx && (
                      <span className="w-2.5 h-2.5 rounded-full bg-[#ea0000]" />
                    )}
                    {submitted && opt.correct && <CheckCircle2 size={16} className="text-[#1d6e17]" />}
                    {submitted && idx === selected && !opt.correct && <XCircle size={16} className="text-[#ea0000]" />}
                  </span>
                  <span className="text-black">{opt.text}</span>
                </button>
              );
            })}
          </div>

          {submitted && (
            <div className={`p-3 rounded-[12px] text-sm ${isCorrect ? 'bg-emerald-50 text-[#1d6e17]' : 'bg-amber-50 text-amber-700'}`}>
              {isCorrect
                ? 'Correct! Always redact or remove sensitive data before sending prompts to AI systems.'
                : 'Not quite. The safest approach is to remove or replace sensitive data with placeholders before sending.'}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-neutral-100 flex justify-end gap-3">
          {!submitted ? (
            <button
              onClick={handleSubmit}
              disabled={selected === null}
              className="px-5 py-2 rounded-full bg-[#ea0000] text-white text-sm font-semibold hover:bg-[#c50000] disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
            >
              Submit Answer
            </button>
          ) : (
            <button
              onClick={handleClose}
              className="px-5 py-2 rounded-full bg-[#ea0000] text-white text-sm font-semibold hover:bg-[#c50000] transition-colors cursor-pointer"
            >
              {isCorrect ? 'Complete Training' : 'Close & Review'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
