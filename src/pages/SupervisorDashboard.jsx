import { useState, useEffect } from 'react';
import {
  Users,
  AlertTriangle,
  Eye,
  GraduationCap,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import TrainingModal from '../components/TrainingModal';
import { MOCK_EMPLOYEES, TRAINING_MODULES } from '../data/mockData';
import { adminService } from '../api/index.ts';

const FLAG_THRESHOLD = 3;

const CATEGORY_BADGE = {
  PII: 'bg-orange-100 text-orange-700',
  pii: 'bg-orange-100 text-orange-700',
  Credentials: 'bg-red-100 text-[#ea0000]',
  credentials: 'bg-red-100 text-[#ea0000]',
  Financial: 'bg-amber-100 text-amber-700',
  financial: 'bg-amber-100 text-amber-700',
  'Internal Code Name': 'bg-purple-100 text-purple-700',
  internal: 'bg-purple-100 text-purple-700',
  Regulated: 'bg-rose-100 text-rose-700',
  health: 'bg-rose-100 text-rose-700',
  bias: 'bg-blue-100 text-blue-700',
  legal: 'bg-indigo-100 text-indigo-700',
};

export default function SupervisorDashboard() {
  const [employees, setEmployees] = useState(MOCK_EMPLOYEES);
  const [trainingOpen, setTrainingOpen] = useState(false);
  const [trainingModuleId, setTrainingModuleId] = useState(null);
  const [detailsRequested, setDetailsRequested] = useState(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    adminService
      .getUsers()
      .then((users) => {
        if (!mounted) return;
        // Map backend users to the shape our component expects
        const mapped = users.map((u, i) => ({
          id: i + 1,
          name: u.name,
          team: u.department,
          flags: u.total_flags,
          categories: [], // Backend doesn't provide per-user categories in list
          recommendedTraining:
            u.training_status === 'required' ? 'Secure AI Prompt Practices' : null,
          lastIncident: u.last_incident || null,
        }));
        setEmployees(mapped);
      })
      .catch(() => {
        // Keep mock data
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, []);

  const handleRequestDetails = (id) => {
    setDetailsRequested((prev) => new Set(prev).add(id));
  };

  const handleOpenTraining = (moduleId) => {
    setTrainingModuleId(moduleId || TRAINING_MODULES[0].id);
    setTrainingOpen(true);
  };

  const totalFlags = employees.reduce((s, e) => s + e.flags, 0);
  const needsTraining = employees.filter((e) => e.flags >= FLAG_THRESHOLD).length;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-black">Supervisor Dashboard</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Aggregated safety metrics per employee. Raw prompts are hidden by default.
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Users size={18} />}
          value={employees.length}
          label="Team Members"
          color="text-[#ea0000] bg-[#ea0000]/10"
        />
        <StatCard
          icon={<AlertTriangle size={18} />}
          value={totalFlags}
          label="Total Flags"
          color="text-red-700 bg-red-50"
        />
        <StatCard
          icon={<ShieldAlert size={18} />}
          value={needsTraining}
          label="Need Training"
          color="text-amber-700 bg-amber-50"
        />
        <StatCard
          icon={<GraduationCap size={18} />}
          value={TRAINING_MODULES.length}
          label="Training Modules"
          color="text-[#1d6e17] bg-emerald-50"
        />
      </div>

      {/* Employee cards */}
      {loading ? (
        <div className="text-center py-8 text-neutral-400 text-sm">Loading employees...</div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {employees.map((emp) => (
            <div
              key={emp.id}
              className={`bg-white rounded-[16px] border shadow-sm overflow-hidden ${
                emp.flags >= FLAG_THRESHOLD ? 'border-[#ea0000]/30' : 'border-neutral-200'
              }`}
            >
              <div className="px-5 py-4 flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-black">{emp.name}</h3>
                    {emp.flags >= FLAG_THRESHOLD && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#ea0000]/10 text-[#ea0000]">
                        Action needed
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-neutral-500 mt-0.5">{emp.team}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-black">{emp.flags}</p>
                  <p className="text-[10px] text-neutral-400 uppercase tracking-wider">flags</p>
                </div>
              </div>

              {/* Category tags */}
              {emp.categories && emp.categories.length > 0 && (
                <div className="px-5 pb-3 flex flex-wrap gap-1.5">
                  {emp.categories.map((cat) => (
                    <span
                      key={cat}
                      className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                        CATEGORY_BADGE[cat] || 'bg-neutral-100 text-neutral-600'
                      }`}
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              )}

              {/* Training recommendation */}
              {emp.recommendedTraining && (
                <div className="px-5 pb-3">
                  <p className="text-xs text-neutral-500">
                    <GraduationCap size={12} className="inline mr-1 -mt-0.5" />
                    Recommended:{' '}
                    <span className="font-semibold text-black">
                      {emp.recommendedTraining}
                    </span>
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="px-5 py-3 border-t border-neutral-100 flex items-center gap-2">
                {detailsRequested.has(emp.id) ? (
                  <span className="text-xs text-[#1d6e17] font-semibold flex items-center gap-1">
                    <Eye size={12} /> Detail request submitted
                  </span>
                ) : (
                  <button
                    onClick={() => handleRequestDetails(emp.id)}
                    className="text-xs text-[#ea0000] hover:text-[#c50000] font-semibold flex items-center gap-1 cursor-pointer"
                  >
                    <Eye size={12} /> Request More Details
                    <ChevronRight size={12} />
                  </button>
                )}

                {emp.recommendedTraining && (
                  <button
                    onClick={() =>
                      handleOpenTraining(
                        TRAINING_MODULES.find((m) => m.title === emp.recommendedTraining)?.id
                      )
                    }
                    className="ml-auto text-xs px-3 py-1.5 rounded-full bg-[#ea0000] text-white font-semibold hover:bg-[#c50000] transition-colors cursor-pointer flex items-center gap-1"
                  >
                    <GraduationCap size={12} />
                    Preview Training
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <TrainingModal
        open={trainingOpen}
        onClose={() => setTrainingOpen(false)}
        moduleId={trainingModuleId}
      />
    </div>
  );
}

function StatCard({ icon, value, label, color }) {
  return (
    <div className="bg-white rounded-[16px] border border-neutral-200 shadow-sm p-4 flex items-center gap-3">
      <div className={`p-2.5 rounded-[10px] ${color}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-black">{value}</p>
        <p className="text-xs text-neutral-500">{label}</p>
      </div>
    </div>
  );
}
