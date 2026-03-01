import { useState, useRef, useCallback } from "react";
import { Send, Loader2 } from "lucide-react";
import { useApp } from "../../state/AppContext.tsx";
import {
  analyzePrompt,
  submitPrompt,
  getUserRisk,
  generateId,
} from "../../api/index.ts";
import type { ChatMessage } from "../../types/index.ts";

interface ComposerProps {
  onInterceptOpen: () => void;
}

export default function Composer({ onInterceptOpen }: ComposerProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const {
    addMessage,
    setLastAnalysis,
    addFlaggedEvent,
    setUserRisk,
    setIsAnalyzing,
    setIsSubmitting,
    isAnalyzing,
    isSubmitting,
  } = useApp();

  const handleSend = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed || isAnalyzing || isSubmitting) return;

    setIsAnalyzing(true);

    try {
      const result = await analyzePrompt(trimmed);
      setLastAnalysis(result);

      if (!result.allowed) {
        addFlaggedEvent({
          id: generateId(),
          timestamp: Date.now(),
          categories: result.categories,
          riskLevel: result.riskLevel,
          redactedSnippet:
            result.saferPrompt?.slice(0, 80) ?? trimmed.slice(0, 80),
        });
        onInterceptOpen();
        setIsAnalyzing(false);
        return;
      }

      // Safe — send directly using the response we already got
      setIsAnalyzing(false);
      setIsSubmitting(true);

      const userMsg: ChatMessage = {
        id: generateId(),
        role: "user",
        content: trimmed,
        timestamp: Date.now(),
      };
      addMessage(userMsg);
      setText("");

      // Use the AI response from the analysis (backend already processed it)
      const aiResponse = result.aiResponse || "Your prompt has been processed by CokeGPT.";
      const assistantMsg: ChatMessage = {
        id: generateId(),
        role: "assistant",
        content: aiResponse,
        timestamp: Date.now(),
      };
      addMessage(assistantMsg);

      const systemMsg: ChatMessage = {
        id: generateId(),
        role: "system",
        content: "S.I.P verified — no sensitive data detected",
        timestamp: Date.now(),
      };
      addMessage(systemMsg);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: generateId(),
        role: "system",
        content: err.response?.data?.detail || "Error: Could not reach the backend server.",
        timestamp: Date.now(),
      };
      addMessage(errorMsg);
    } finally {
      setIsAnalyzing(false);
      setIsSubmitting(false);
    }
  }, [
    text,
    isAnalyzing,
    isSubmitting,
    setIsAnalyzing,
    setIsSubmitting,
    setLastAnalysis,
    addFlaggedEvent,
    addMessage,
    onInterceptOpen,
  ]);

  const handleUseSaferPrompt = useCallback(
    async (saferPrompt: string, originalPrompt: string) => {
      setIsSubmitting(true);

      const userMsg: ChatMessage = {
        id: generateId(),
        role: "user",
        content: saferPrompt,
        timestamp: Date.now(),
        wasRewritten: true,
      };
      addMessage(userMsg);
      setText("");

      try {
        const risk = await getUserRisk();
        setUserRisk(risk);
      } catch {}

      try {
        const { response } = await submitPrompt(saferPrompt);
        const assistantMsg: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content: response,
          timestamp: Date.now(),
        };
        addMessage(assistantMsg);

        const systemMsg: ChatMessage = {
          id: generateId(),
          role: "system",
          content: "S.I.P rewrote this message to remove sensitive data",
          timestamp: Date.now(),
        };
        addMessage(systemMsg);
      } catch {
        // Swallow
      } finally {
        setIsSubmitting(false);
        setLastAnalysis(null);
        textareaRef.current?.focus();
      }
    },
    [addMessage, setUserRisk, setIsSubmitting, setLastAnalysis]
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const disabled = isAnalyzing || isSubmitting;

  return {
    composerUI: (
      <div className="border-t border-gray-200 bg-white p-4">
        <label htmlFor="composer-input" className="sr-only">
          Message to AI tool
        </label>
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              id="composer-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message to AI tool"
              disabled={disabled}
              rows={2}
              className="w-full resize-none rounded-xl border border-gray-200 px-4 py-3 text-sm focus:border-brand-red focus:ring-0 focus:outline-none disabled:bg-gray-50 disabled:text-gray-400"
              aria-describedby="composer-help"
            />
            <p id="composer-help" className="text-xs text-gray-400 mt-1 px-1">
              S.I.P checks for sensitive data before sending.
            </p>
          </div>
          <button
            onClick={handleSend}
            disabled={disabled || !text.trim()}
            className="flex items-center justify-center w-10 h-10 rounded-xl bg-brand-red text-white hover:bg-brand-red-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors mb-5"
            aria-label="Send message"
          >
            {isAnalyzing ? (
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
            ) : (
              <Send className="w-4 h-4" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>
    ),
    handleUseSaferPrompt,
    textareaRef,
  };
}
