import {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  type ReactNode,
} from "react";
import type {
  AppSettings,
  TextSize,
  ChatMessage,
  AnalysisResult,
  FlaggedEvent,
  UserRisk,
  AiPlatform,
} from "../types/index.ts";
import { PolicyMode } from "../types/index.ts";
import {
  getStoredUser,
  getStoredToken,
  login as apiLogin,
  logout as apiLogout,
  type BackendLoginResponse,
} from "../api/authService.ts";

/* ── Chat session type ─────────────────────────────────────────── */

export interface ChatSession {
  id: string;
  title: string;
  timestamp: number;
  messages: ChatMessage[];
}

/* ── Per-user state snapshot (saved/restored on account switch) ── */

interface UserSnapshot {
  messages: ChatMessage[];
  chatHistory: ChatSession[];
  activeChatId: string | null;
  flaggedEvents: FlaggedEvent[];
  userRisk: UserRisk;
  lastAnalysis: AnalysisResult | null;
  selectedPlatform: AiPlatform;
}

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
  user: BackendLoginResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  authLoading: boolean;
  // Chat sessions
  chatHistory: ChatSession[];
  activeChatId: string | null;
  isViewingHistory: boolean;
  // AI platform
  selectedPlatform: AiPlatform;
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
  // Chat session actions
  startNewChat: () => void;
  loadChat: (sessionId: string) => void;
  deleteChat: (sessionId: string) => void;
  // AI platform
  setSelectedPlatform: (platform: AiPlatform) => void;
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

  /* ── AI platform state ──────────────────────────────────────── */
  const [selectedPlatform, setSelectedPlatform] = useState<AiPlatform>("ChatGPT");

  /* ── Chat session state ─────────────────────────────────────── */
  // Per-user snapshot map: userId -> full state snapshot
  const userSnapshotsRef = useRef<Record<string, UserSnapshot>>({});
  const [activeChatId, setActiveChatId] = useState<string | null>(
    () => `chat-${Date.now()}`
  );
  const [isViewingHistory, setIsViewingHistory] = useState(false);
  // Bump this to force re-render when we mutate the ref (e.g. deleteChat)
  const [, setSnapshotVersion] = useState(0);

  /* ── Auth state ─────────────────────────────────────────────── */
  const [user, setUser] = useState<BackendLoginResponse | null>(getStoredUser());
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [authLoading, setAuthLoading] = useState(false);

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

  /* ── Session helpers ────────────────────────────────────────── */

  const DEFAULT_RISK: UserRisk = {
    flaggedCount: 0,
    rewrittenCount: 0,
    trainingRequired: false,
    trainingCompleted: false,
  };

  /** Save a full snapshot of the current user's state */
  const saveUserSnapshot = useCallback(
    (userId: string, currentMessages: ChatMessage[], chatId: string | null) => {
      // Build updated chat history: archive active chat if it has user messages
      const existing = userSnapshotsRef.current[userId];
      let history = existing?.chatHistory ?? [];

      const hasUserMessages = currentMessages.some((m) => m.role === "user");
      if (hasUserMessages && chatId && !history.some((s) => s.id === chatId)) {
        const firstUserMsg = currentMessages.find((m) => m.role === "user");
        const title = firstUserMsg?.content.slice(0, 50) || "Untitled chat";
        history = [
          { id: chatId, title, timestamp: Date.now(), messages: [...currentMessages] },
          ...history,
        ];
      }

      userSnapshotsRef.current[userId] = {
        messages: [...currentMessages],
        chatHistory: history,
        activeChatId: chatId,
        flaggedEvents: [...flaggedEvents],
        userRisk: { ...userRisk },
        lastAnalysis,
        selectedPlatform,
      };
    },
    [flaggedEvents, userRisk, lastAnalysis, selectedPlatform]
  );

  /** Restore a user's full snapshot (or return fresh defaults) */
  const restoreUserSnapshot = useCallback((userId: string) => {
    const snap = userSnapshotsRef.current[userId];
    if (snap) {
      setMessages([...snap.messages]);
      setActiveChatId(snap.activeChatId);
      setFlaggedEvents([...snap.flaggedEvents]);
      setUserRisk({ ...snap.userRisk });
      setLastAnalysis(snap.lastAnalysis);
      setSelectedPlatform(snap.selectedPlatform ?? "ChatGPT");
    } else {
      setMessages([...INITIAL_MESSAGES]);
      setActiveChatId(`chat-${Date.now()}`);
      setFlaggedEvents([]);
      setUserRisk({ ...DEFAULT_RISK });
      setLastAnalysis(null);
      setSelectedPlatform("ChatGPT");
    }
    setIsViewingHistory(false);
  }, []);

  /** Get chat history for the current user */
  const chatHistory = user
    ? userSnapshotsRef.current[user.user_id]?.chatHistory ?? []
    : [];

  const startNewChat = useCallback(() => {
    if (user) {
      saveUserSnapshot(user.user_id, messages, activeChatId);
    }
    setMessages([...INITIAL_MESSAGES]);
    setActiveChatId(`chat-${Date.now()}`);
    setIsViewingHistory(false);
    setLastAnalysis(null);
  }, [user, messages, activeChatId, saveUserSnapshot]);

  const loadChat = useCallback(
    (sessionId: string) => {
      const userId = user?.user_id;
      if (!userId) return;
      const snap = userSnapshotsRef.current[userId];
      const session = snap?.chatHistory.find((s) => s.id === sessionId);
      if (session) {
        setMessages([...session.messages]);
        setActiveChatId(session.id);
        setIsViewingHistory(true);
        setLastAnalysis(null);
      }
    },
    [user]
  );

  const deleteChat = useCallback(
    (sessionId: string) => {
      const userId = user?.user_id;
      if (!userId) return;
      const snap = userSnapshotsRef.current[userId];
      if (snap) {
        snap.chatHistory = snap.chatHistory.filter((s) => s.id !== sessionId);
      }
      // If we're currently viewing the deleted session, go back to a new chat
      if (activeChatId === sessionId) {
        setMessages([...INITIAL_MESSAGES]);
        setActiveChatId(`chat-${Date.now()}`);
        setIsViewingHistory(false);
        setLastAnalysis(null);
      }
      // Force re-render since we mutated the ref
      setSnapshotVersion((v) => v + 1);
    },
    [user, activeChatId]
  );

  /* ── Auth callbacks ─────────────────────────────────────────── */
  const login = useCallback(
    async (ssoToken: string) => {
      setAuthLoading(true);
      try {
        // Save outgoing user's full state
        if (user) {
          saveUserSnapshot(user.user_id, messages, activeChatId);
        }
        const response = await apiLogin(ssoToken);
        setToken(response.session_token);
        setUser(response);
        // Restore incoming user's state (or fresh defaults)
        restoreUserSnapshot(response.user_id);
      } finally {
        setAuthLoading(false);
      }
    },
    [user, messages, activeChatId, saveUserSnapshot, restoreUserSnapshot]
  );

  const logout = useCallback(() => {
    if (user) {
      saveUserSnapshot(user.user_id, messages, activeChatId);
    }
    apiLogout();
    setToken(null);
    setUser(null);
    setMessages([...INITIAL_MESSAGES]);
    setActiveChatId(null);
    setFlaggedEvents([]);
    setUserRisk({ ...DEFAULT_RISK });
    setIsViewingHistory(false);
    setLastAnalysis(null);
  }, [user, messages, activeChatId, saveUserSnapshot]);

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
        chatHistory,
        activeChatId,
        isViewingHistory,
        selectedPlatform,
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
        startNewChat,
        loadChat,
        deleteChat,
        setSelectedPlatform,
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
