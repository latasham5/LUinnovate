import { useState } from 'react';
import { Filter, Clock, ShieldCheck, ShieldX, ShieldAlert } from 'lucide-react';

/**
 * LogTable — Coca-Cola themed filterable log table.
 * Pill-shaped filter buttons with red active state, 16px card radius.
 */

const ACTION_BADGE = {
  Blocked: 'bg-red-100 text-[#ea0000]',
  Rewritten: 'bg-amber-100 text-amber-700',
  'Allowed with Warning': 'bg-blue-100 text-blue-700',
};

const ACTION_ICON = {
  Blocked: <ShieldX size={12} />,
  Rewritten: <ShieldAlert size={12} />,
  'Allowed with Warning': <ShieldCheck size={12} />,
};

const CATEGORY_BADGE = {
  PII: 'bg-orange-100 text-orange-700',
  Credentials: 'bg-red-100 text-[#ea0000]',
  Financial: 'bg-amber-100 text-amber-700',
  'Internal Code Name': 'bg-purple-100 text-purple-700',
  Regulated: 'bg-rose-100 text-rose-700',
};

const ALL_CATEGORIES = ['All', 'PII', 'Credentials', 'Financial', 'Internal Code Name', 'Regulated'];

export default function LogTable({ logs }) {
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = logs.filter((log) => {
    const matchesCategory = categoryFilter === 'All' || log.category === categoryFilter;
    const matchesSearch =
      !searchTerm ||
      log.snippet.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const formatTime = (iso) => {
    const d = new Date(iso);
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-[16px] border border-neutral-200 shadow-sm overflow-hidden">
      {/* Toolbar */}
      <div className="px-5 py-3 border-b border-neutral-100 flex flex-col sm:flex-row items-start sm:items-center gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-black">
          <Filter size={14} className="text-neutral-400" />
          Filters
        </div>

        {/* Category pills */}
        <div className="flex flex-wrap gap-1.5">
          {ALL_CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`text-xs px-2.5 py-1 rounded-full border transition-colors cursor-pointer ${
                categoryFilter === cat
                  ? 'bg-[#ea0000] text-white border-[#ea0000]'
                  : 'bg-white text-neutral-600 border-neutral-200 hover:border-[#ea0000]/40'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search logs…"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="ml-auto text-sm px-3 py-1.5 rounded-full border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-[#ea0000]/20 focus:border-[#ea0000]/40 w-full sm:w-48"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-neutral-50 text-left text-xs font-bold text-neutral-500 uppercase tracking-wider">
              <th className="px-5 py-3">Timestamp</th>
              <th className="px-5 py-3">User</th>
              <th className="px-5 py-3">Category</th>
              <th className="px-5 py-3">Action</th>
              <th className="px-5 py-3">Policy</th>
              <th className="px-5 py-3">Confidence</th>
              <th className="px-5 py-3">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {filtered.map((log) => (
              <tr key={log.id} className="hover:bg-neutral-50 transition-colors">
                <td className="px-5 py-3 text-neutral-500 whitespace-nowrap">
                  <Clock size={12} className="inline mr-1 -mt-0.5" />
                  {formatTime(log.timestamp)}
                </td>
                <td className="px-5 py-3 font-semibold text-black">{log.user}</td>
                <td className="px-5 py-3">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${CATEGORY_BADGE[log.category] || 'bg-neutral-100 text-neutral-600'}`}>
                    {log.category}
                  </span>
                </td>
                <td className="px-5 py-3">
                  <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${ACTION_BADGE[log.action] || 'bg-neutral-100'}`}>
                    {ACTION_ICON[log.action]}
                    {log.action}
                  </span>
                </td>
                <td className="px-5 py-3 text-neutral-500 font-mono text-xs">{log.policyVersion}</td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          log.confidence >= 0.9 ? 'bg-[#ea0000]' : log.confidence >= 0.75 ? 'bg-amber-500' : 'bg-yellow-400'
                        }`}
                        style={{ width: `${log.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-neutral-500">{Math.round(log.confidence * 100)}%</span>
                  </div>
                </td>
                <td className="px-5 py-3 text-neutral-500 text-xs">{log.snippet}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-neutral-400">
                  No matching log entries found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-neutral-100 text-xs text-neutral-400">
        Showing {filtered.length} of {logs.length} entries
      </div>
    </div>
  );
}
