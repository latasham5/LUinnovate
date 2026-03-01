import { useState, useCallback } from 'react';
import { Bot, CheckCircle2 } from 'lucide-react';
import PromptInput from '../components/PromptInput';
import SafetyWarning from '../components/SafetyWarning';
import SaferRewritePanel from '../components/SaferRewritePanel';
import { analyzePrompt as mockAnalyze, rewritePrompt } from '../data/mockData';
import { promptService } from '../api/index.ts';
import { AI_PLATFORMS } from '../types/index.ts';

/**
 * EmployeeView — Coca-Cola themed main prompt interface.
 * Calls the backend prompt API first, falls back to mock analysis.
 */
export default function EmployeeView({ mode }) {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [rewritten, setRewritten] = useState('');
  const [saferSent, setSaferSent] = useState(false);
  const [aiResponse, setAiResponse] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('ChatGPT');

  const handleAnalyze = useCallback(
    async (prompt) => {
      setResult(null);
      setRewritten('');
      setSaferSent(false);
      setAiResponse('');
      setOriginalPrompt(prompt);
      setAnalyzing(true);

      try {
        // Try backend API first
        const backendResult = await promptService.analyzePrompt({
          prompt_text: prompt,
          policy_mode: mode,
          ai_platform: selectedPlatform,
        });

        // Map backend response to the shape our components expect
        const isSafe = backendResult.action === 'allowed';
        const mapped = {
          safe: isSafe,
          category: backendResult.flags?.[0]?.category || null,
          label: backendResult.flags?.[0]?.description || null,
          explanation: backendResult.explanation,
          confidence: backendResult.flags?.[0]?.confidence || 0,
          rewriteHint: backendResult.explanation,
          riskScore: backendResult.risk_score,
          action: backendResult.action,
          promptId: backendResult.prompt_id,
        };

        setResult(mapped);

        if (!isSafe && backendResult.rewritten_prompt) {
          setRewritten(backendResult.rewritten_prompt);
        } else if (!isSafe) {
          setRewritten(rewritePrompt(prompt));
        }

        if (isSafe) {
          setAiResponse(
            'Thank you for your prompt! Here is a simulated AI response. In a production system, your prompt would be forwarded to the internal AI model and the real response would appear here.'
          );
        }
      } catch {
        // Fallback to client-side mock analysis
        const analysisResult = mockAnalyze(prompt, mode);
        setResult(analysisResult);

        if (!analysisResult.safe) {
          setRewritten(rewritePrompt(prompt));
        } else {
          setAiResponse(
            'Thank you for your prompt! Here is a simulated AI response. In a production system, your prompt would be forwarded to the internal AI model and the real response would appear here.'
          );
        }
      }

      setAnalyzing(false);
    },
    [mode, selectedPlatform]
  );

  const handleSendSafer = () => {
    setSaferSent(true);
    setAiResponse(
      'Safer prompt accepted. Here is the AI response based on your redacted prompt. Sensitive data was removed before processing.'
    );
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-black">AI Prompt Interface</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Type your prompt below. The safety layer will analyze it before sending to the AI.
        </p>
      </div>

      <div className="flex items-center gap-2 mb-2">
        <label htmlFor="ev-platform-select" className="text-xs font-medium text-neutral-500 whitespace-nowrap">
          Sending to:
        </label>
        <select
          id="ev-platform-select"
          value={selectedPlatform}
          onChange={(e) => setSelectedPlatform(e.target.value)}
          className="rounded-lg border border-neutral-200 px-2.5 py-1 text-xs font-medium text-neutral-700 focus:border-[#ea0000] focus:ring-0 focus:outline-none"
        >
          {AI_PLATFORMS.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      <PromptInput onAnalyze={handleAnalyze} analyzing={analyzing} />

      {result && !result.safe && <SafetyWarning result={result} />}

      {result && !result.safe && (
        <SaferRewritePanel
          original={originalPrompt}
          rewritten={rewritten}
          result={result}
          onSendSafer={handleSendSafer}
          sent={saferSent}
        />
      )}

      {aiResponse && (
        <div className="bg-white rounded-[16px] border border-neutral-200 shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-neutral-100 flex items-center gap-2">
            <Bot size={16} className="text-[#ea0000]" />
            <span className="text-sm font-semibold text-black">AI Response</span>
            {result?.safe && (
              <span className="ml-auto flex items-center gap-1 text-xs font-semibold text-[#1d6e17]">
                <CheckCircle2 size={12} />
                No risks detected
              </span>
            )}
          </div>
          <div className="px-5 py-4 text-sm text-neutral-700 leading-relaxed">{aiResponse}</div>
        </div>
      )}
    </div>
  );
}
