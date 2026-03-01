import { NavLink } from "react-router-dom";
import {
  Shield,
  ChevronDown,
  Type,
  Eye,
  Sun,
  Moon,
} from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useApp } from "../../state/AppContext.tsx";
import type { PolicyMode, TextSize } from "../../types/index.ts";

const POLICY_OPTIONS: { value: PolicyMode; label: string }[] = [
  { value: "strict", label: "Strict" },
  { value: "balanced", label: "Balanced" },
  { value: "fast", label: "Fast" },
];

const TEXT_SIZE_OPTIONS: { value: TextSize; label: string }[] = [
  { value: "sm", label: "S" },
  { value: "md", label: "M" },
  { value: "lg", label: "L" },
];

function navLinkClass({ isActive }: { isActive: boolean }) {
  return `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
    isActive
      ? "bg-gray-100 text-gray-900"
      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
  }`;
}

export default function Header() {
  const {
    settings,
    setPolicyMode,
    setTextSize,
    toggleHighContrast,
    toggleDarkMode,
  } = useApp();

  const [policyOpen, setPolicyOpen] = useState(false);
  const [a11yOpen, setA11yOpen] = useState(false);
  const policyRef = useRef<HTMLDivElement>(null);
  const a11yRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (policyRef.current && !policyRef.current.contains(e.target as Node)) {
        setPolicyOpen(false);
      }
      if (a11yRef.current && !a11yRef.current.contains(e.target as Node)) {
        setA11yOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <header className="border-b border-gray-200 bg-white px-6 py-3 flex items-center justify-between flex-shrink-0">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4">
          <img
            src="/the-coca-cola-company-logo.svg"
            alt="The Coca-Cola Company"
            className="h-5 w-auto text-gray-900"
            style={{ filter: "var(--logo-filter, none)" }}
          />
          <span className="text-gray-300 text-xl font-extralight select-none" aria-hidden="true">|</span>
          <div className="flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-brand-red" aria-hidden="true" />
            <span className="font-semibold text-gray-900 text-sm">
              S.I.P
            </span>
          </div>
        </div>

        <nav aria-label="Main navigation" className="flex items-center gap-1">
          <NavLink to="/" className={navLinkClass} end>
            Workspace
          </NavLink>
          <NavLink to="/audit" className={navLinkClass}>
            Audit
          </NavLink>
          <NavLink to="/training" className={navLinkClass}>
            Training
          </NavLink>
        </nav>
      </div>

      <div className="flex items-center gap-3">
        {/* Dark mode toggle */}
        <button
          onClick={toggleDarkMode}
          className="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          aria-label={settings.darkMode ? "Switch to light mode" : "Switch to dark mode"}
          aria-pressed={settings.darkMode}
        >
          {settings.darkMode ? (
            <Sun className="w-4 h-4 text-amber-500" aria-hidden="true" />
          ) : (
            <Moon className="w-4 h-4 text-gray-500" aria-hidden="true" />
          )}
        </button>

        {/* Policy mode dropdown */}
        <div className="relative" ref={policyRef}>
          <button
            onClick={() => setPolicyOpen(!policyOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            aria-haspopup="listbox"
            aria-expanded={policyOpen}
          >
            <span className="text-gray-500 text-xs">Policy:</span>
            <span className="font-medium capitalize">
              {settings.policyMode}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-gray-400" aria-hidden="true" />
          </button>
          {policyOpen && (
            <div
              role="listbox"
              className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg py-1 z-50 min-w-[140px]"
            >
              {POLICY_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  role="option"
                  aria-selected={settings.policyMode === opt.value}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${
                    settings.policyMode === opt.value
                      ? "font-semibold text-brand-red"
                      : "text-gray-700"
                  }`}
                  onClick={() => {
                    setPolicyMode(opt.value);
                    setPolicyOpen(false);
                  }}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Accessibility dropdown */}
        <div className="relative" ref={a11yRef}>
          <button
            onClick={() => setA11yOpen(!a11yOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            aria-haspopup="true"
            aria-expanded={a11yOpen}
            aria-label="Accessibility settings"
          >
            <Eye className="w-4 h-4 text-gray-500" aria-hidden="true" />
            <ChevronDown className="w-3.5 h-3.5 text-gray-400" aria-hidden="true" />
          </button>
          {a11yOpen && (
            <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg p-4 z-50 min-w-[200px]">
              <div className="mb-3">
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Type className="w-3.5 h-3.5" aria-hidden="true" />
                  Text Size
                </label>
                <div className="flex gap-1 mt-1">
                  {TEXT_SIZE_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setTextSize(opt.value)}
                      className={`flex-1 py-1.5 text-sm rounded-lg border transition-colors ${
                        settings.textSize === opt.value
                          ? "border-brand-red bg-brand-red-light text-brand-red font-semibold"
                          : "border-gray-200 text-gray-600 hover:bg-gray-50"
                      }`}
                      aria-pressed={settings.textSize === opt.value}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <button
                  onClick={toggleHighContrast}
                  className="w-full flex items-center justify-between py-2 text-sm"
                  aria-pressed={settings.highContrast}
                >
                  <span className="text-gray-700">High contrast</span>
                  <span
                    className={`w-9 h-5 rounded-full relative transition-colors ${
                      settings.highContrast ? "bg-brand-red" : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                        settings.highContrast
                          ? "translate-x-4"
                          : "translate-x-0.5"
                      }`}
                    />
                  </span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
