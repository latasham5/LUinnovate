import { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import {
  MessageSquare,
  BarChart3,
  Users,
  Menu,
  X,
} from 'lucide-react';
import PolicySelector from './components/PolicySelector';
import EmployeeView from './pages/EmployeeView';
import LogsDashboard from './pages/LogsDashboard';
import SupervisorDashboard from './pages/SupervisorDashboard';

/**
 * App — root layout themed to Coca-Cola brand guidelines.
 * Black sidebar, Coca-Cola red (#ea0000) accents, Poppins font, pill buttons.
 */

const NAV_ITEMS = [
  { to: '/', label: 'Prompt Interface', icon: MessageSquare },
  { to: '/logs', label: 'Risk Log', icon: BarChart3 },
  { to: '/supervisor', label: 'Supervisor', icon: Users },
];

export default function App() {
  const [mode, setMode] = useState('balanced');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen flex">
        {/* ── Sidebar ─────────────────────────────────────────────── */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/40 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <aside
          className={`fixed lg:static inset-y-0 left-0 z-50 w-60 bg-black text-white flex flex-col transition-transform lg:translate-x-0 ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          {/* Brand — Coca-Cola logo */}
          <div className="px-4 py-5 flex items-center gap-3 border-b border-neutral-800">
            <img
              src="/coca-cola-logo.svg"
              alt="The Coca-Cola Company"
              className="h-5 shrink-0"
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
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-full text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-[#ea0000]/15 text-red-400'
                      : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
                  }`
                }
              >
                <Icon size={16} />
                {label}
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          <div className="px-5 py-4 border-t border-neutral-800 text-[10px] text-neutral-600">
            Policy engine v2.4 &middot; Demo mode
          </div>
        </aside>

        {/* ── Main content ────────────────────────────────────────── */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Top bar */}
          <header className="sticky top-0 z-30 h-14 bg-white/90 backdrop-blur border-b border-neutral-200 flex items-center px-5 gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-neutral-600 hover:text-black cursor-pointer"
            >
              <Menu size={20} />
            </button>

            <span className="text-sm font-semibold text-black hidden sm:block">
              AI Safety Copilot
            </span>

            <div className="ml-auto flex items-center gap-4">
              <PolicySelector mode={mode} onModeChange={setMode} />
              <div className="w-8 h-8 rounded-full bg-[#ea0000]/10 flex items-center justify-center text-xs font-bold text-[#ea0000]">
                JD
              </div>
            </div>
          </header>

          {/* Page content */}
          <main className="flex-1 p-5 lg:p-8 max-w-6xl w-full mx-auto">
            <Routes>
              <Route path="/" element={<EmployeeView mode={mode} />} />
              <Route path="/logs" element={<LogsDashboard />} />
              <Route path="/supervisor" element={<SupervisorDashboard />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
