import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import type {
  AppSettings,
  PolicyMode,
  TextSize,
  ChatMessage,
  AnalysisResult,
  FlaggedEvent,
  UserRisk,
  User,
} from "../types/index.ts";

interface AppState {
  settings: AppSettings;
  messages: ChatMessage[];
  lastAnalysis: AnalysisResult | null;
  flaggedEvents: FlaggedEvent[];
  userRisk: UserRisk;
  isAnalyzing: boolean;
  isSubmitting: boolean;
  user: User | null;
}

interface AppContextValue extends AppState {
  setPolicyMode: (mode: PolicyMode) => void;
  setTextSize: (size: TextSize) => void;
  toggleHighContrast: () => void;
  toggleDarkMode: () => void;
  addMessage: (msg: ChatMessage) => void;
  setLastAnalysis: (result: AnalysisResult | null) => void;
  addFlaggedEvent: (event: FlaggedEvent) => void;
  setUserRisk: (risk: UserRisk) => void;
  setIsAnalyzing: (v: boolean) => void;
  setIsSubmitting: (v: boolean) => void;
  setUser: (user: User | null) => void;
}

function loadUser(): User | null {
  try {
    const raw = sessionStorage.getItem("user");
    const token = sessionStorage.getItem("session_token");
    if (raw && token) {
      const parsed = JSON.parse(raw);
      return { ...parsed, session_token: token };
    }
  } catch {}
  return null;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<AppSettings>({
    policyMode: "balanced",
    textSize: "md",
    highContrast: false,
    darkMode: false,
  });
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg-welcome",
      role: "assistant",
      content:
        "Hello! I'm CokeGPT, your AI assistant. S.I.P is actively monitoring this conversation to protect sensitive data. Feel free to ask me anything.",
      timestamp: Date.now(),
    },
  ]);
  const [lastAnalysis, setLastAnalysis] = useState<AnalysisResult | null>(null);
  const [flaggedEvents, setFlaggedEvents] = useState<FlaggedEvent[]>([]);
  const [userRisk, setUserRisk] = useState<UserRisk>({
    flaggedCount: 0,
    rewrittenCount: 0,
    trainingRequired: false,
    trainingCompleted: false,
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [user, setUser] = useState<User | null>(loadUser);

  const setPolicyMode = useCallback((mode: PolicyMode) => {
    setSettings((s) => ({ ...s, policyMode: mode }));
  }, []);

  const setTextSize = useCallback((size: TextSize) => {
    setSettings((s) => ({ ...s, textSize: size }));
  }, []);

  const toggleHighContrast = useCallback(() => {
    setSettings((s) => ({ ...s, highContrast: !s.highContrast }));
  }, []);

  const toggleDarkMode = useCallback(() => {
    setSettings((s) => ({ ...s, darkMode: !s.darkMode }));
  }, []);

  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const addFlaggedEvent = useCallback((event: FlaggedEvent) => {
    setFlaggedEvents((prev) => [event, ...prev].slice(0, 5));
  }, []);

  return (
    <AppContext.Provider
      value={{
        settings,
        messages,
        lastAnalysis,
        flaggedEvents,
        userRisk,
        isAnalyzing,
        isSubmitting,
        user,
        setPolicyMode,
        setTextSize,
        toggleHighContrast,
        toggleDarkMode,
        addMessage,
        setLastAnalysis,
        addFlaggedEvent,
        setUserRisk,
        setIsAnalyzing,
        setIsSubmitting,
        setUser,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
