import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Loader2 } from "lucide-react";
import { useApp } from "../state/AppContext.tsx";

// Actual employee IDs from the backend's mock_users/users.json
const DEMO_USERS = [
  { name: "Sarah Johnson", role: "Analyst", dept: "Marketing", token: "EMP001" },
  { name: "Michael Chen", role: "Analyst", dept: "Finance", token: "EMP002" },
  { name: "Jessica Williams", role: "Senior Analyst", dept: "Supply Chain", token: "EMP003" },
  { name: "David Martinez", role: "Manager", dept: "Marketing", token: "MGR001" },
  { name: "Emily Davis", role: "Manager", dept: "Finance", token: "MGR002" },
  { name: "Robert Taylor", role: "Manager", dept: "Supply Chain", token: "MGR003" },
  { name: "Amanda Wilson", role: "Director", dept: "Operations", token: "DIR001" },
  { name: "James Anderson", role: "Security Admin", dept: "Cybersecurity", token: "SEC001" },
  { name: "System Administrator", role: "Admin", dept: "IT", token: "ADM001" },
];

const ROLE_STYLES: Record<string, string> = {
  Admin: "bg-red-50 text-red-700",
  "Security Admin": "bg-red-50 text-red-700",
  Director: "bg-purple-50 text-purple-700",
  Manager: "bg-amber-50 text-amber-700",
  "Senior Analyst": "bg-blue-50 text-blue-700",
  Analyst: "bg-gray-100 text-gray-600",
};

export default function LoginPage() {
  const { login, authLoading } = useApp();
  const navigate = useNavigate();
  const [ssoToken, setSsoToken] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!ssoToken.trim()) return;
    setError("");
    try {
      await login(ssoToken.trim());
      navigate("/");
    } catch {
      setError("Invalid employee ID. Try one of the demo users below.");
    }
  }

  async function handleDemoLogin(token: string) {
    setError("");
    setSsoToken(token);
    try {
      await login(token);
      navigate("/");
    } catch {
      setError("Backend not reachable. Make sure the server is running on port 8000.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        {/* Logo & title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-black mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <img
            src="/the-coca-cola-company-logo.svg"
            alt="The Coca-Cola Company"
            className="h-5 mx-auto mb-3"
          />
          <h1 className="text-2xl font-bold text-gray-900">PromptGuard Agent</h1>
          <p className="text-sm text-gray-500 mt-1">AI Safety Layer — Sign in to continue</p>
        </div>

        {/* Login card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="sso-token" className="block text-sm font-medium text-gray-700 mb-1">
                Employee ID
              </label>
              <input
                id="sso-token"
                type="text"
                value={ssoToken}
                onChange={(e) => setSsoToken(e.target.value)}
                placeholder="e.g. EMP001, MGR001, ADM001"
                className="w-full px-3 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ea0000]/30 focus:border-[#ea0000]"
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>
            )}

            <button
              type="submit"
              disabled={authLoading || !ssoToken.trim()}
              className="w-full py-2.5 rounded-lg bg-[#ea0000] text-white text-sm font-semibold hover:bg-[#c50000] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {authLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 border-t border-gray-200" />
            <span className="text-xs text-gray-400 uppercase tracking-wide">Demo Users</span>
            <div className="flex-1 border-t border-gray-200" />
          </div>

          {/* Demo user quick-login buttons */}
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {DEMO_USERS.map((u) => (
              <button
                key={u.token}
                onClick={() => handleDemoLogin(u.token)}
                disabled={authLoading}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-left disabled:opacity-50 cursor-pointer"
              >
                <div>
                  <span className="text-sm font-medium text-gray-800">{u.name}</span>
                  <span className="text-xs text-gray-400 ml-2">{u.dept}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ROLE_STYLES[u.role] || "bg-gray-100 text-gray-600"}`}>
                  {u.role}
                </span>
              </button>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-4">
          Policy engine v2.4 &middot; Phantom App Backend
        </p>
      </div>
    </div>
  );
}
