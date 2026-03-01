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
  GraduationCap,
  Menu,
  X,
  Sun,
  Moon,
  LogOut,
  Shield,
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

const NAV_ITEMS = [
  { to: "/", label: "Workspace", icon: MessageSquare, end: true },
  { to: "/prompt", label: "Prompt Analyzer", icon: Sparkles, end: false },
  { to: "/audit", label: "Audit", icon: BarChart3, end: false },
  { to: "/logs", label: "Risk Log", icon: BarChart3, end: false },
  { to: "/training", label: "Training", icon: GraduationCap, end: false },
  { to: "/supervisor", label: "Supervisor", icon: Users, end: false },
];

/* ── Route guard ───────────────────────────────────────────────── */
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

/* ── App shell (sidebar + top bar + pages) ─────────────────────── */
function AppShell() {
  const { settings, toggleDarkMode, user, logout } = useApp();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mode, setMode] = useState("balanced");

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
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
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
            PromptGuard Agent
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
            <Route path="/audit" element={<AuditPage />} />
            <Route
              path="/logs"
              element={
                <div className="p-5 lg:p-8 max-w-6xl w-full mx-auto">
                  <LogsDashboard />
                </div>
              }
            />
            <Route path="/training" element={<TrainingPage />} />
            <Route
              path="/supervisor"
              element={
                <div className="p-5 lg:p-8 max-w-6xl w-full mx-auto">
                  <SupervisorDashboard />
                </div>
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
