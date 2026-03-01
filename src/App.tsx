import { useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  Navigate,
} from "react-router-dom";
import {
  MessageSquare,
  BarChart3,
  Users,
  Sparkles,
  Menu,
  X,
  Sun,
  Moon,
  LogOut,
  Shield,
  Clock,
  Plus,
  ChevronDown,
  Trash2,
  Accessibility,
  Type,
} from "lucide-react";
import { AppProvider, useApp } from "./state/AppContext.tsx";
import PolicySelector from "./components/PolicySelector.jsx";

/* ── Pages ─────────────────────────────────────────────────────── */
import LoginPage from "./pages/LoginPage.tsx";
import WorkspacePage from "./pages/WorkspacePage.tsx";
import AuditPage from "./pages/AuditPage.tsx";
import TrainingPage from "./pages/TrainingPage.tsx";
// @ts-ignore
import EmployeeView from "./pages/EmployeeView.jsx";
// @ts-ignore
import LogsDashboard from "./pages/LogsDashboard.jsx";
// @ts-ignore
import SupervisorDashboard from "./pages/SupervisorDashboard.jsx";

const ELEVATED_ROLES = ["manager", "director", "security_admin", "admin"];

const NAV_ITEMS = [
  { to: "/", label: "Workspace", icon: MessageSquare, end: true },
  { to: "/prompt", label: "Prompt Analyzer", icon: Sparkles, end: false },
  { to: "/audit", label: "Audit", icon: BarChart3, end: false, requiredRoles: ELEVATED_ROLES },
  { to: "/logs", label: "Risk Log", icon: BarChart3, end: false, requiredRoles: ELEVATED_ROLES },
  { to: "/supervisor", label: "Supervisor", icon: Users, end: false, requiredRoles: ELEVATED_ROLES },
];

/* ── Route guards ──────────────────────────────────────────────── */
function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, authLoading } = useApp();
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Shield className="w-8 h-8 text-[#ea0000] animate-pulse" />
      </div>
    );
  }
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function RequireRole({ roles, children }: { roles: string[]; children: React.ReactNode }) {
  const { user } = useApp();
  if (!user || !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

/* ── App shell (sidebar + top bar + pages) ─────────────────────── */
function formatRelativeTime(timestamp: number): string {
  const diff = Date.now() - timestamp;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function AppShell() {
  const { settings, toggleDarkMode, setTextSize, toggleHighContrast, user, logout, chatHistory, startNewChat, loadChat, deleteChat } = useApp();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(true);
  const [mode, setMode] = useState("balanced");
  const [a11yOpen, setA11yOpen] = useState(false);

  const initials = user
    ? user.name
        .split(" ")
        .map((w) => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??";

  const rootClasses = [
    "min-h-screen flex",
    settings.highContrast ? "high-contrast" : "",
    settings.darkMode ? "dark" : "",
    `text-size-${settings.textSize}`,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={rootClasses}>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* ── Mobile overlay ──────────────────────────────────────── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-60 bg-black text-white flex flex-col transition-transform lg:translate-x-0 flex-shrink-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand — Coca-Cola logo */}
        <div className="px-4 py-5 flex items-center gap-3 border-b border-neutral-800">
          <img
            src="/the-coca-cola-company-logo.svg"
            alt="The Coca-Cola Company"
            className="h-4 shrink-0 invert"
          />
          <span className="text-[10px] text-neutral-500 uppercase tracking-widest ml-auto">
            Safety
          </span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="ml-auto lg:hidden text-neutral-400 hover:text-white cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.filter(
            (item) => !item.requiredRoles || (user && item.requiredRoles.includes(user.role))
          ).map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-full text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[#ea0000]/15 text-red-400"
                    : "text-neutral-400 hover:text-white hover:bg-neutral-900"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Previous Chats */}
        <div className="px-3 pb-2 border-t border-neutral-800">
          <button
            onClick={() => setHistoryOpen((o) => !o)}
            className="flex items-center justify-between w-full px-3 py-2.5 text-xs font-medium text-neutral-400 hover:text-white transition-colors cursor-pointer"
          >
            <span className="flex items-center gap-2">
              <Clock size={13} />
              Previous Chats
            </span>
            <ChevronDown
              size={13}
              className={`transition-transform ${historyOpen ? "" : "-rotate-90"}`}
            />
          </button>

          {historyOpen && (
            <div className="space-y-0.5">
              <button
                onClick={() => { startNewChat(); setSidebarOpen(false); }}
                className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-xs font-medium text-green-400 hover:bg-neutral-900 transition-colors cursor-pointer"
              >
                <Plus size={13} />
                New Chat
              </button>

              {chatHistory.length === 0 ? (
                <p className="px-3 py-2 text-[10px] text-neutral-600">
                  No previous chats
                </p>
              ) : (
                <div className="max-h-40 overflow-y-auto space-y-0.5">
                  {chatHistory.slice(0, 5).map((session) => (
                    <div
                      key={session.id}
                      className="flex items-center w-full rounded-lg hover:bg-neutral-900 transition-colors group"
                    >
                      <button
                        onClick={() => { loadChat(session.id); setSidebarOpen(false); }}
                        className="flex-1 flex items-center justify-between px-3 py-2 text-left cursor-pointer min-w-0"
                      >
                        <span className="text-xs text-neutral-400 group-hover:text-white truncate max-w-[100px]">
                          {session.title}
                        </span>
                        <span className="text-[10px] text-neutral-600 shrink-0 ml-2">
                          {formatRelativeTime(session.timestamp)}
                        </span>
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteChat(session.id); }}
                        className="p-1.5 mr-1 text-neutral-700 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all cursor-pointer"
                        aria-label="Delete chat"
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* User + logout */}
        {user && (
          <div className="px-4 py-3 border-t border-neutral-800">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-full bg-[#ea0000]/20 flex items-center justify-center text-[10px] font-bold text-red-400">
                {initials}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white truncate">{user.name}</p>
                <p className="text-[10px] text-neutral-500 truncate">{user.department}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 text-neutral-500 hover:text-white text-xs transition-colors cursor-pointer"
            >
              <LogOut size={12} />
              Sign out
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="px-5 py-3 border-t border-neutral-800 text-[10px] text-neutral-600">
          Policy engine v2.4 &middot; {user?.role ?? "Demo"}
        </div>
      </aside>

      {/* ── Main content ────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-14 bg-white border-b border-neutral-200 flex items-center px-5 gap-4 flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-neutral-600 hover:text-black cursor-pointer"
          >
            <Menu size={20} />
          </button>

          <span className="text-sm font-semibold text-black hidden sm:block">
            S.I.P Agent
          </span>

          <div className="ml-auto flex items-center gap-3">
            {/* Dark mode toggle */}
            <button
              onClick={toggleDarkMode}
              className="flex items-center justify-center w-8 h-8 rounded-full border border-neutral-200 hover:bg-neutral-50 transition-colors cursor-pointer"
              aria-label={
                settings.darkMode ? "Switch to light mode" : "Switch to dark mode"
              }
            >
              {settings.darkMode ? (
                <Sun className="w-4 h-4 text-amber-500" />
              ) : (
                <Moon className="w-4 h-4 text-neutral-500" />
              )}
            </button>

            {/* Accessibility dropdown */}
            <div className="relative">
              <button
                onClick={() => setA11yOpen(!a11yOpen)}
                className="flex items-center justify-center w-8 h-8 rounded-full border border-neutral-200 hover:bg-neutral-50 transition-colors cursor-pointer"
                aria-label="Accessibility settings"
                aria-haspopup="true"
                aria-expanded={a11yOpen}
              >
                <Accessibility className="w-4 h-4 text-neutral-500" />
              </button>
              {a11yOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setA11yOpen(false)} />
                  <div className="absolute right-0 top-full mt-1 bg-white border border-neutral-200 rounded-xl shadow-lg p-4 z-50 min-w-[200px]">
                    <div className="mb-3">
                      <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <Type className="w-3.5 h-3.5" aria-hidden="true" />
                        Text Size
                      </label>
                      <div className="flex gap-1 mt-1">
                        {(["sm", "md", "lg"] as const).map((size) => (
                          <button
                            key={size}
                            onClick={() => setTextSize(size)}
                            className={`flex-1 py-1.5 text-sm rounded-lg border transition-colors cursor-pointer ${
                              settings.textSize === size
                                ? "border-[#ea0000] bg-[#ea0000]/5 text-[#ea0000] font-semibold"
                                : "border-neutral-200 text-neutral-600 hover:bg-neutral-50"
                            }`}
                            aria-pressed={settings.textSize === size}
                          >
                            {size.toUpperCase()}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <button
                        onClick={toggleHighContrast}
                        className="w-full flex items-center justify-between py-2 text-sm cursor-pointer"
                        aria-pressed={settings.highContrast}
                      >
                        <span className="text-neutral-700">High contrast</span>
                        <span
                          className={`w-9 h-5 rounded-full relative transition-colors ${
                            settings.highContrast ? "bg-[#ea0000]" : "bg-neutral-300"
                          }`}
                        >
                          <span
                            className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                              settings.highContrast ? "translate-x-4" : "translate-x-0.5"
                            }`}
                          />
                        </span>
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>

            <PolicySelector mode={mode} onModeChange={setMode} />

            <div className="w-8 h-8 rounded-full bg-[#ea0000]/10 flex items-center justify-center text-xs font-bold text-[#ea0000]">
              {initials}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto" id="main-content">
          <Routes>
            <Route path="/" element={<WorkspacePage />} />
            <Route
              path="/prompt"
              element={
                <div className="p-5 lg:p-8 max-w-6xl w-full mx-auto">
                  <EmployeeView mode={mode} />
                </div>
              }
            />
            <Route path="/audit" element={<RequireRole roles={ELEVATED_ROLES}><AuditPage /></RequireRole>} />
            <Route
              path="/logs"
              element={
                <RequireRole roles={ELEVATED_ROLES}>
                  <div className="p-5 lg:p-8 max-w-6xl w-full mx-auto">
                    <LogsDashboard />
                  </div>
                </RequireRole>
              }
            />
            <Route path="/training" element={<TrainingPage />} />
            <Route
              path="/supervisor"
              element={
                <RequireRole roles={ELEVATED_ROLES}>
                  <div className="p-5 lg:p-8 max-w-6xl w-full mx-auto">
                    <SupervisorDashboard />
                  </div>
                </RequireRole>
              }
            />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <RequireAuth>
                <AppShell />
              </RequireAuth>
            }
          />
        </Routes>
      </AppProvider>
    </BrowserRouter>
  );
}
