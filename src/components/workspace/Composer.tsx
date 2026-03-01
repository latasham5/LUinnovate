import { useState, useRef, useCallback } from "react";
import { Send, Loader2, ArrowLeft } from "lucide-react";
import { useApp } from "../../state/AppContext.tsx";
import {
  analyzePromptMock as analyzePrompt,
  submitPrompt,
  addAuditEvent,
  incrementRewrittenCount,
  getUserRisk,
  generateId,
} from "../../api/index.ts";
import type { ChatMessage, AuditEvent } from "../../types/index.ts";
import PlatformSelector from "./PlatformSelector.tsx";

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
    isViewingHistory,
    startNewChat,
    lastAnalysis,
    user,
    selectedPlatform,
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
          ai_platform: selectedPlatform,
        });
        onInterceptOpen();
        setIsAnalyzing(false);
        return;
      }

      // Safe — send directly
      setIsAnalyzing(false);
      setIsSubmitting(true);

      const userMsg: ChatMessage = {
        id: generateId(),
        role: "user",
        content: trimmed,
        timestamp: Date.now(),
        ai_platform: selectedPlatform,
      };
      addMessage(userMsg);
      setText("");

      const { response } = await submitPrompt(trimmed);
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
        content: "S.I.P verified — no sensitive data detected",
        timestamp: Date.now(),
      };
      addMessage(systemMsg);
    } catch {
      // Swallow mock errors
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
    selectedPlatform,
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
        ai_platform: selectedPlatform,
      };
      addMessage(userMsg);
      setText("");

      incrementRewrittenCount();
      const risk = await getUserRisk();
      setUserRisk(risk);

      const auditEvent: AuditEvent = {
        id: generateId(),
        timestamp: Date.now(),
        user: user?.name ?? "unknown",
        severity: lastAnalysis?.riskLevel ?? "medium",
        categories: lastAnalysis?.categories ?? [],
        action: "rewritten",
        policyVersion: "v2.4",
        redactedSnippet: saferPrompt.slice(0, 80),
        reason: `Original prompt was rewritten. Original: "${originalPrompt.slice(0, 40)}..."`,
        ai_platform: selectedPlatform,
      };
      addAuditEvent(auditEvent);

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
    [addMessage, setUserRisk, setIsSubmitting, setLastAnalysis, lastAnalysis, user, selectedPlatform]
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const disabled = isAnalyzing || isSubmitting || isViewingHistory;

  return {
    composerUI: (
      <div className="border-t border-gray-200 bg-white p-4">
        {isViewingHistory && (
          <div className="flex items-center justify-between bg-amber-50 border border-amber-200 rounded-lg px-4 py-2.5 mb-3">
            <span className="text-sm text-amber-800 font-medium">
              Viewing previous chat
            </span>
            <button
              onClick={startNewChat}
              className="flex items-center gap-1.5 text-xs font-medium text-amber-700 hover:text-amber-900 transition-colors cursor-pointer"
            >
              <ArrowLeft size={13} />
              Back to current chat
            </button>
          </div>
        )}
        <PlatformSelector />
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
              placeholder={isViewingHistory ? "Switch to a new chat to send messages" : "Message to AI tool"}
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
