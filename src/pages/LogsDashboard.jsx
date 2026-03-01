import { BarChart3, TrendingDown, ShieldCheck, AlertTriangle } from 'lucide-react';
import LogTable from '../components/LogTable';
import { MOCK_LOGS } from '../data/mockData';

/**
 * LogsDashboard — Coca-Cola themed risk log with stat cards.
 * Uses brand red for primary stat, 16px card radius.
 */
export default function LogsDashboard() {
  const totalEvents = MOCK_LOGS.length;
  const blockedCount = MOCK_LOGS.filter((l) => l.action === 'Blocked').length;
  const rewrittenCount = MOCK_LOGS.filter((l) => l.action === 'Rewritten').length;
  const avgConfidence = Math.round(
    (MOCK_LOGS.reduce((sum, l) => sum + l.confidence, 0) / totalEvents) * 100
  );

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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-[16px] border border-neutral-200 shadow-sm p-4 flex items-center gap-3">
            <div className={`p-2.5 rounded-[10px] ${s.color}`}>{s.icon}</div>
            <div>
              <p className="text-2xl font-bold text-black">{s.value}</p>
              <p className="text-xs text-neutral-500">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      <LogTable logs={MOCK_LOGS} />
    </div>
  );
}
