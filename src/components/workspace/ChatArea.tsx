import { useEffect, useRef } from "react";
import { Shield } from "lucide-react";
import { useApp } from "../../state/AppContext.tsx";

export default function ChatArea() {
  const { messages } = useApp();
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
    >
      {messages.map((msg) => {
        const isUser = msg.role === "user";
        const isSystem = msg.role === "system";

        if (isSystem) {
          return (
            <div
              key={msg.id}
              className="flex justify-center"
            >
              <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium">
                <Shield className="w-3 h-3" aria-hidden="true" />
                {msg.content}
              </div>
            </div>
          );
        }

        return (
          <div
            key={msg.id}
            className={`flex ${isUser ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[70%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                isUser
                  ? "bg-gray-900 text-white rounded-br-md"
                  : "bg-gray-100 text-gray-800 rounded-bl-md"
              } ${msg.wasRewritten ? "border-2 border-emerald-300" : ""}`}
            >
              {msg.wasRewritten && (
                <div className="flex items-center gap-1 mb-1.5 text-xs text-emerald-600 font-medium">
                  <Shield className="w-3 h-3" aria-hidden="true" />
                  Rewritten by PromptGuard
                </div>
              )}
              {msg.content}
              <div
                className={`text-xs mt-1.5 ${
                  isUser ? "text-gray-400" : "text-gray-400"
                }`}
              >
                {new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </div>
            </div>
          </div>
        );
      })}
      <div ref={endRef} />
    </div>
  );
}
