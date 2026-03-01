import { useState, useEffect } from 'react';
import { BarChart3, TrendingDown, ShieldCheck, AlertTriangle, Monitor } from 'lucide-react';
import LogTable from '../components/LogTable';
import { MOCK_LOGS } from '../data/mockData';
import { auditService } from '../api/index.ts';

/**
 * LogsDashboard — Coca-Cola themed risk log with stat cards.
 * Tries backend audit API first, falls back to mock data.
 */
export default function LogsDashboard() {
  const [logs, setLogs] = useState(MOCK_LOGS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    auditService
      .getAuditEntries()
      .then((entries) => {
        if (!mounted) return;
        // Map backend audit entries to the shape LogTable expects
        const mapped = entries.map((e, i) => ({
          id: i + 1,
          timestamp: e.timestamp,
          user: e.employee_name,
          team: e.department,
          category: e.categories?.[0] || 'Unknown',
          action:
            e.action === 'allowed'
              ? 'Allowed'
              : e.action === 'warning'
                ? 'Allowed with Warning'
                : e.action === 'rewritten'
                  ? 'Rewritten'
                  : 'Blocked',
          policyVersion: e.policy_mode,
          confidence: e.risk_score / 100,
          snippet: e.redacted_snippet,
          aiPlatform: e.ai_platform || 'ChatGPT',
        }));
        setLogs(mapped);
      })
      .catch(() => {
        // Keep mock data as fallback
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, []);

  const totalEvents = logs.length;
  const blockedCount = logs.filter((l) => l.action === 'Blocked').length;
  const rewrittenCount = logs.filter((l) => l.action === 'Rewritten').length;
  const avgConfidence =
    totalEvents > 0
      ? Math.round(
          (logs.reduce((sum, l) => sum + l.confidence, 0) / totalEvents) * 100
        )
      : 0;

  // Find top platform
  const platformCounts = {};
  logs.forEach((l) => {
    if (l.aiPlatform) {
      platformCounts[l.aiPlatform] = (platformCounts[l.aiPlatform] || 0) + 1;
    }
  });
  const topPlatform = Object.entries(platformCounts).sort((a, b) => b[1] - a[1])[0];

  const stats = [
    {
      label: 'Total Events',
      value: totalEvents,
      icon: <BarChart3 size={18} />,
      color: 'text-[#ea0000] bg-[#ea0000]/10',
    },
    {
      label: 'Blocked',
      value: blockedCount,
      icon: <AlertTriangle size={18} />,
      color: 'text-red-700 bg-red-50',
    },
    {
      label: 'Rewritten',
      value: rewrittenCount,
      icon: <ShieldCheck size={18} />,
      color: 'text-amber-700 bg-amber-50',
    },
    {
      label: 'Avg Confidence',
      value: `${avgConfidence}%`,
      icon: <TrendingDown size={18} />,
      color: 'text-[#1d6e17] bg-emerald-50',
    },
    {
      label: 'Top Platform',
      value: topPlatform ? topPlatform[0] : '—',
      icon: <Monitor size={18} />,
      color: 'text-blue-700 bg-blue-50',
    },
  ];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-black">Risk Event Log</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Audit trail of all flagged prompts. Filter by category to drill down.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {stats.map((s) => (
          <div
            key={s.label}
            className="bg-white rounded-[16px] border border-neutral-200 shadow-sm p-4 flex items-center gap-3"
          >
            <div className={`p-2.5 rounded-[10px] ${s.color}`}>{s.icon}</div>
            <div>
              <p className="text-2xl font-bold text-black">{s.value}</p>
              <p className="text-xs text-neutral-500">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-8 text-neutral-400 text-sm">Loading logs...</div>
      ) : (
        <LogTable logs={logs} />
      )}
    </div>
  );
}
