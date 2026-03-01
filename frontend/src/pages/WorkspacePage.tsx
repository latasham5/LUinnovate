import { useState, useCallback } from "react";
import ChatArea from "../components/workspace/ChatArea.tsx";
import Composer from "../components/workspace/Composer.tsx";
import AgentPanel from "../components/workspace/AgentPanel.tsx";
import InterceptDialog from "../components/workspace/InterceptDialog.tsx";
import { useApp } from "../state/AppContext.tsx";

export default function WorkspacePage() {
  const [interceptOpen, setInterceptOpen] = useState(false);
  const { setLastAnalysis } = useApp();

  const { composerUI, handleUseSaferPrompt, textareaRef } = Composer({
    onInterceptOpen: () => setInterceptOpen(true),
  });

  const handleClose = useCallback(() => {
    setInterceptOpen(false);
    setTimeout(() => textareaRef.current?.focus(), 50);
  }, [textareaRef]);

  const handleUseSafer = useCallback(
    async (saferPrompt: string, originalPrompt: string) => {
      setInterceptOpen(false);
      await handleUseSaferPrompt(saferPrompt, originalPrompt);

      // Announce success
      const announcer = document.getElementById("safety-announcer");
      if (announcer) {
        announcer.textContent =
          "Safer prompt sent successfully. Sensitive data was removed.";
      }
    },
    [handleUseSaferPrompt]
  );

  const handleEditOriginal = useCallback(() => {
    setInterceptOpen(false);
    setLastAnalysis(null);
    setTimeout(() => textareaRef.current?.focus(), 50);
  }, [setLastAnalysis, textareaRef]);

  return (
    <div className="flex flex-1 overflow-hidden">
      <section className="flex flex-col flex-1 min-w-0">
        <ChatArea />
        {composerUI}
      </section>
      <AgentPanel />
      <InterceptDialog
        open={interceptOpen}
        onClose={handleClose}
        onUseSafer={handleUseSafer}
        onEditOriginal={handleEditOriginal}
      />
      <div aria-live="polite" className="sr-only" id="safety-announcer" />
    </div>
  );
}
