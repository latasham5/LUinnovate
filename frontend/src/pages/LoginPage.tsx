import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Loader2 } from "lucide-react";
import { login } from "../api/index.ts";

const MOCK_EMPLOYEES = [
  { id: "EMP001", name: "Sarah Johnson", role: "analyst", dept: "Marketing" },
  { id: "EMP002", name: "Michael Chen", role: "analyst", dept: "Finance" },
  { id: "EMP003", name: "Jessica Williams", role: "senior_analyst", dept: "Supply Chain" },
  { id: "MGR001", name: "David Martinez", role: "manager", dept: "Marketing" },
  { id: "MGR002", name: "Emily Davis", role: "manager", dept: "Finance" },
  { id: "MGR003", name: "Robert Taylor", role: "manager", dept: "Supply Chain" },
  { id: "DIR001", name: "Amanda Wilson", role: "director", dept: "Operations" },
  { id: "SEC001", name: "James Anderson", role: "security_admin", dept: "Cybersecurity" },
  { id: "ADM001", name: "System Admin", role: "admin", dept: "IT" },
];

export default function LoginPage() {
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!selectedId) return;
    setLoading(true);
    setError("");

    try {
      const data = await login(selectedId);
      sessionStorage.setItem("session_token", data.session_token);
      sessionStorage.setItem(
        "user",
        JSON.stringify({
          user_id: data.user_id,
          name: data.name,
          role: data.role,
          department: data.department,
          deployment_mode: data.deployment_mode,
        })
      );
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Shield className="w-8 h-8 text-brand-red" />
            <span className="text-2xl font-bold text-gray-900">PromptGuard</span>
          </div>
          <p className="text-sm text-gray-500">
            Coca-Cola AI Security Middleware
          </p>
        </div>

        {/* Login card */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <h1 className="text-lg font-semibold text-gray-900 mb-1">Sign In</h1>
          <p className="text-sm text-gray-500 mb-6">
            Select an employee to log in with mock SSO
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              {error}
            </div>
          )}

          <label htmlFor="employee-select" className="block text-sm font-medium text-gray-700 mb-2">
            Employee
          </label>
          <select
            id="employee-select"
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm focus:border-brand-red focus:ring-0 focus:outline-none mb-4 bg-white"
          >
            <option value="">Choose an employee...</option>
            {MOCK_EMPLOYEES.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.name} ({emp.id}) - {emp.role}, {emp.dept}
              </option>
            ))}
          </select>

          <button
            onClick={handleLogin}
            disabled={!selectedId || loading}
            className="w-full py-3 bg-brand-red text-white rounded-xl text-sm font-medium hover:bg-brand-red-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>

          {/* Quick login buttons */}
          <div className="mt-6 pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-400 mb-3 text-center">Quick login as:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {[
                { id: "EMP001", label: "Analyst" },
                { id: "MGR001", label: "Manager" },
                { id: "SEC001", label: "Security" },
                { id: "ADM001", label: "Admin" },
              ].map((quick) => (
                <button
                  key={quick.id}
                  onClick={() => { setSelectedId(quick.id); }}
                  className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors"
                >
                  {quick.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-xs text-gray-400 text-center mt-4">
          Phantom App v1.0 &middot; Internal Use Only
        </p>
      </div>
    </div>
  );
}
