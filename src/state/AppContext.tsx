import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";
import type {
  AppSettings,
  TextSize,
  ChatMessage,
  AnalysisResult,
  FlaggedEvent,
  UserRisk,
  UserProfile,
} from "../types/index.ts";
import { PolicyMode } from "../types/index.ts";
import {
  getStoredUser,
  getStoredToken,
  login as apiLogin,
  logout as apiLogout,
  getProfile,
} from "../api/authService.ts";

/* ── State shape ───────────────────────────────────────────────── */

interface AppState {
  settings: AppSettings;
  messages: ChatMessage[];
  lastAnalysis: AnalysisResult | null;
  flaggedEvents: FlaggedEvent[];
  userRisk: UserRisk;
  isAnalyzing: boolean;
  isSubmitting: boolean;
  // Auth
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  authLoading: boolean;
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
  // Auth actions
  login: (ssoToken: string) => Promise<void>;
  logout: () => void;
}

/* ── Seed messages ─────────────────────────────────────────────── */

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "msg-1",
    role: "assistant",
    content:
      "Hello! I'm your AI assistant. PromptGuard is actively monitoring this conversation to protect sensitive data. Feel free to ask me anything.",
    timestamp: Date.now() - 60000,
  },
  {
    id: "msg-2",
    role: "user",
    content: "Can you help me draft a summary of our Q4 sales performance?",
    timestamp: Date.now() - 50000,
  },
  {
    id: "msg-3",
    role: "assistant",
    content:
      "Of course! I'd be happy to help you draft a Q4 sales performance summary. Could you share the key metrics or data points you'd like included?",
    timestamp: Date.now() - 40000,
  },
];

/* ── Context ───────────────────────────────────────────────────── */

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  /* ── Settings ───────────────────────────────────────────────── */
  const [settings, setSettings] = useState<AppSettings>({
    policyMode: PolicyMode.BALANCED,
    textSize: "md",
    highContrast: false,
    darkMode: false,
  });

  /* ── Chat / analysis state ──────────────────────────────────── */
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
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

  /* ── Auth state ─────────────────────────────────────────────── */
  const [user, setUser] = useState<UserProfile | null>(getStoredUser());
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [authLoading, setAuthLoading] = useState(false);

  // Hydrate user profile on mount if we have a token
  useEffect(() => {
    if (token && !user) {
      setAuthLoading(true);
      getProfile()
        .then(setUser)
        .catch(() => {
          // Token is stale — clear it
          apiLogout();
          setToken(null);
          setUser(null);
        })
        .finally(() => setAuthLoading(false));
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  /* ── Settings callbacks ─────────────────────────────────────── */
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

  /* ── Chat callbacks ─────────────────────────────────────────── */
  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const addFlaggedEvent = useCallback((event: FlaggedEvent) => {
    setFlaggedEvents((prev) => [event, ...prev].slice(0, 5));
  }, []);

  /* ── Auth callbacks ─────────────────────────────────────────── */
  const login = useCallback(async (ssoToken: string) => {
    setAuthLoading(true);
    try {
      const response = await apiLogin(ssoToken);
      setToken(response.access_token);
      setUser(response.user);
    } finally {
      setAuthLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setToken(null);
    setUser(null);
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
        token,
        isAuthenticated: !!token,
        authLoading,
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
        login,
        logout,
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
