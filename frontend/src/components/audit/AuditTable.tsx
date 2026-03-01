import { useState } from "react";
import { Eye, X } from "lucide-react";
import type { AuditEvent } from "../../types/index.ts";
import { RiskBadge, CategoryChip } from "../common/StatusBadge.tsx";

interface AuditTableProps {
  events: AuditEvent[];
}

export default function AuditTable({ events }: AuditTableProps) {
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);

  return (
    <>
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th
                  scope="col"
                  className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  Time
                </th>
                <th
                  scope="col"
                  className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  User
                </th>
                <th
                  scope="col"
                  className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  Severity
                </th>
                <th
                  scope="col"
                  className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  Categories
                </th>
                <th
                  scope="col"
                  className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  Action
                </th>
                <th
                  scope="col"
                  className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  Policy
                </th>
                <th
                  scope="col"
                  className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  Details
                </th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr
                  key={event.id}
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                    {new Date(event.timestamp).toLocaleString([], {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </td>
                  <td className="px-4 py-3 text-gray-700 font-medium">
                    {event.user}
                  </td>
                  <td className="px-4 py-3">
                    <RiskBadge level={event.severity} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {event.categories.map((cat) => (
                        <CategoryChip key={cat} category={cat} />
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`capitalize text-xs font-medium px-2 py-0.5 rounded-full ${
                        event.action === "blocked"
                          ? "bg-red-100 text-red-700"
                          : event.action === "rewritten"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-emerald-100 text-emerald-700"
                      }`}
                    >
                      {event.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {event.policyVersion}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setSelectedEvent(event)}
                      className="flex items-center gap-1 text-xs text-brand-red hover:text-brand-red-hover font-medium transition-colors"
                      aria-label={`View details for event from ${event.user}`}
                    >
                      <Eye className="w-3.5 h-3.5" aria-hidden="true" />
                      View
                    </button>
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-8 text-center text-gray-400"
                  >
                    No audit events match the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail drawer */}
      {selectedEvent && (
        <div
          className="fixed inset-0 z-50 flex justify-end bg-black/30"
          onClick={() => setSelectedEvent(null)}
        >
          <aside
            className="bg-white w-full max-w-md shadow-xl p-6 overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Audit event details"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-base font-semibold text-gray-900">
                Event Details
              </h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Close details"
              >
                <X className="w-4 h-4 text-gray-400" aria-hidden="true" />
              </button>
            </div>

            <dl className="space-y-4">
              <div>
                <dt className="text-xs font-medium text-gray-500">Time</dt>
                <dd className="text-sm text-gray-900 mt-0.5">
                  {new Date(selectedEvent.timestamp).toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">User</dt>
                <dd className="text-sm text-gray-900 mt-0.5">
                  {selectedEvent.user}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">Severity</dt>
                <dd className="mt-0.5">
                  <RiskBadge level={selectedEvent.severity} />
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">
                  Categories
                </dt>
                <dd className="flex flex-wrap gap-1 mt-0.5">
                  {selectedEvent.categories.map((c) => (
                    <CategoryChip key={c} category={c} />
                  ))}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">
                  Redacted Snippet
                </dt>
                <dd className="text-sm text-gray-700 bg-gray-50 rounded-xl p-3 mt-0.5 border border-gray-200">
                  {selectedEvent.redactedSnippet}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">Reason</dt>
                <dd className="text-sm text-gray-700 mt-0.5">
                  {selectedEvent.reason}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">
                  Action Taken
                </dt>
                <dd className="text-sm text-gray-900 capitalize mt-0.5">
                  {selectedEvent.action}
                </dd>
              </div>
            </dl>
          </aside>
        </div>
      )}
    </>
  );
}
