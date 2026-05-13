import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
} from 'recharts';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4'];

const DEADLINE = new Date('2026-06-22');

function daysUntilDeadline() {
  const now = new Date();
  return Math.max(0, Math.ceil((DEADLINE - now) / (1000 * 60 * 60 * 24)));
}

function ProgressBar({ label, value, color = '#6366f1' }) {
  const pct = Math.min(100, Math.max(0, value));
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span>{pct.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div
          className="h-2 rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, accent }) {
  return (
    <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
      <div className={`text-2xl font-bold ${accent || 'text-white'}`}>{value}</div>
      <div className="text-sm text-slate-300 mt-1">{label}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

export default function LearningTracker() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(daysUntilDeadline());

  useEffect(() => {
    const tick = setInterval(() => setDays(daysUntilDeadline()), 60_000);
    return () => clearInterval(tick);
  }, []);

  useEffect(() => {
    fetch('/api/learning')
      .then((r) => r.json())
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400 animate-pulse">Loading learning data…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400">
        ⚠ Could not load learning data: {error}
      </div>
    );
  }

  const agg = data?.aggregate || {};
  const bots = data?.bots || [];

  // Radar data for aggregate scores
  const radarData = [
    { subject: 'API Mastery', A: agg.avg_api_mastery || 0 },
    { subject: 'Competitor Intel', A: agg.avg_competitor_intel || 0 },
    { subject: 'Sandbox Pass', A: agg.avg_sandbox_pass_rate || 0 },
  ];

  // Per-bot bar data
  const barData = bots.slice(0, 12).map((b) => ({
    name: (b.bot_id || '').replace(/_bot$/, '').replace(/_/g, ' '),
    api: b.api_mastery || 0,
    intel: b.competitor_intel_score || 0,
    sandbox: b.sandbox_pass_rate || 0,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">🧠 Bot Deep Learning Tracker</h2>
        <div className="flex items-center gap-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              data?.learning_active
                ? 'bg-green-900 text-green-300'
                : 'bg-slate-700 text-slate-400'
            }`}
          >
            {data?.learning_active ? '🟢 Learning Active' : '⚫ Learning Complete'}
          </span>
          <span className="text-sm text-slate-400">
            🗓 Go-Live: <span className="text-white font-semibold">June 22, 2026</span>
          </span>
        </div>
      </div>

      {/* Countdown + top stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Days Until Go-Live"
          value={days}
          sub="June 22, 2026"
          accent="text-yellow-400"
        />
        <StatCard
          label="Bots Learning"
          value={data?.registered_bots ?? bots.length}
          sub="registered for training"
        />
        <StatCard
          label="Total Cycles Run"
          value={data?.total_cycles_run ?? 0}
          sub="API + competitor + sandbox"
        />
        <StatCard
          label="Avg API Mastery"
          value={`${agg.avg_api_mastery ?? 0}%`}
          sub="across all bots"
          accent="text-indigo-400"
        />
      </div>

      {/* Aggregate progress bars */}
      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 space-y-4">
        <h3 className="text-sm font-semibold text-slate-300 mb-2">Aggregate Learning Progress</h3>
        <ProgressBar label="API Mastery (top-1000 APIs)" value={agg.avg_api_mastery || 0} color="#6366f1" />
        <ProgressBar label="Competitor Intelligence" value={agg.avg_competitor_intel || 0} color="#22c55e" />
        <ProgressBar label="Sandbox Pass Rate" value={agg.avg_sandbox_pass_rate || 0} color="#f59e0b" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar chart */}
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Learning Dimensions Radar</h3>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 9, fill: '#64748b' }} />
              <Radar
                name="Avg Score"
                dataKey="A"
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.3}
              />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Per-bot bar chart */}
        {barData.length > 0 && (
          <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Per-Bot Scores</h3>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={barData} layout="vertical" margin={{ left: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 9 }} width={60} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
                <Bar dataKey="api" name="API Mastery" fill="#6366f1" radius={[0, 3, 3, 0]} />
                <Bar dataKey="intel" name="Competitor Intel" fill="#22c55e" radius={[0, 3, 3, 0]} />
                <Bar dataKey="sandbox" name="Sandbox Pass" fill="#f59e0b" radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Bot table */}
      {bots.length > 0 && (
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Individual Bot Progress</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-slate-300">
              <thead>
                <tr className="border-b border-slate-700 text-xs text-slate-400">
                  <th className="text-left py-2 pr-4">Bot</th>
                  <th className="text-left py-2 pr-4">Category</th>
                  <th className="text-right py-2 pr-4">API Mastery</th>
                  <th className="text-right py-2 pr-4">Competitor Intel</th>
                  <th className="text-right py-2 pr-4">Sandbox Pass</th>
                  <th className="text-right py-2">Cycles</th>
                </tr>
              </thead>
              <tbody>
                {bots.map((b, i) => (
                  <tr key={b.bot_id || i} className="border-b border-slate-800 hover:bg-slate-800/40">
                    <td className="py-2 pr-4 font-medium text-white">
                      {(b.bot_id || '').replace(/_/g, ' ')}
                    </td>
                    <td className="py-2 pr-4 text-xs text-slate-400">{b.category}</td>
                    <td className="py-2 pr-4 text-right">
                      <span className="text-indigo-400">{(b.api_mastery || 0).toFixed(1)}%</span>
                    </td>
                    <td className="py-2 pr-4 text-right">
                      <span className="text-green-400">{(b.competitor_intel_score || 0).toFixed(1)}%</span>
                    </td>
                    <td className="py-2 pr-4 text-right">
                      <span className="text-yellow-400">{(b.sandbox_pass_rate || 0).toFixed(1)}%</span>
                    </td>
                    <td className="py-2 text-right text-slate-400">{b.cycles_completed || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
