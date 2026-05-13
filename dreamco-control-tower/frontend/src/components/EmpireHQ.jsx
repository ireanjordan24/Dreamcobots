import { useEffect, useState } from 'react';

function StatCard({ label, value, sub, color }) {
  return (
    <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
      <div className={`text-2xl font-bold ${color ?? 'text-white'}`}>{value}</div>
      <div className="text-sm text-slate-300 mt-1">{label}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

const DIVISIONS = [
  { name: 'Bot Engineering', lead: 'BuddyOrchestrator', status: 'active', bots: 12, revenue: '$48k' },
  { name: 'AI Research', lead: 'AILeaderBot', status: 'active', bots: 8, revenue: '$32k' },
  { name: 'Finance Ops', lead: 'RevenueEngineBot', status: 'active', bots: 6, revenue: '$91k' },
  { name: 'Market Intel', lead: 'DealAnalyzerBot', status: 'active', bots: 9, revenue: '$27k' },
  { name: 'Infrastructure', lead: 'OrchestrationBot', status: 'idle', bots: 5, revenue: '$14k' },
];

export default function EmpireHQ() {
  const [hq, setHq] = useState(null);

  useEffect(() => {
    fetch('/api/empire/hq')
      .then((r) => r.json())
      .then(setHq)
      .catch(() => setHq({ divisions: 5, totalBots: 40, monthlyRevenue: '$212k', growth: '+31%' }));
  }, []);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🏛️</span>
        <div>
          <h2 className="text-xl font-bold text-white">Empire HQ</h2>
          <p className="text-xs text-slate-400">Central command — all divisions, all systems</p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Divisions" value={hq?.divisions ?? 5} sub="active divisions" />
        <StatCard label="Total Bots" value={hq?.totalBots ?? 40} sub="across all divisions" />
        <StatCard label="Monthly Revenue" value={hq?.monthlyRevenue ?? '$212k'} color="text-green-400" />
        <StatCard label="Empire Growth" value={hq?.growth ?? '+31%'} sub="vs last month" color="text-dreamco-accent" />
      </div>

      {/* Org chart / division table */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden mb-6">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">🏢 Division Overview</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-slate-500 border-b border-slate-700/50">
              <th className="text-left px-5 py-3">Division</th>
              <th className="text-left px-5 py-3">AI Lead</th>
              <th className="text-center px-5 py-3">Bots</th>
              <th className="text-right px-5 py-3">Revenue</th>
              <th className="text-center px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/30">
            {DIVISIONS.map((d) => (
              <tr key={d.name} className="hover:bg-slate-700/20 transition-colors">
                <td className="px-5 py-3 font-medium text-white">{d.name}</td>
                <td className="px-5 py-3 text-slate-300">{d.lead}</td>
                <td className="px-5 py-3 text-center text-slate-300">{d.bots}</td>
                <td className="px-5 py-3 text-right text-green-400 font-semibold">{d.revenue}</td>
                <td className="px-5 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${d.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-slate-600 text-slate-400'}`}>
                    {d.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">📡 HQ Broadcasts</h3>
          <div className="space-y-2 text-sm">
            {[
              { time: '2m ago', msg: 'Finance Ops exceeded monthly target ✅' },
              { time: '15m ago', msg: 'Bot Engineering deployed 3 new bots 🚀' },
              { time: '1h ago', msg: 'AI Research completed training cycle 🧠' },
              { time: '3h ago', msg: 'Market Intel captured 12 new deals 💼' },
            ].map((b, i) => (
              <div key={i} className="flex gap-3">
                <span className="text-xs text-slate-500 shrink-0 w-14">{b.time}</span>
                <span className="text-slate-300">{b.msg}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">⚡ HQ Actions</h3>
          <div className="space-y-2">
            {['Issue Empire-Wide Alert', 'Schedule Division Meeting', 'Generate Empire Report', 'Sync All Divisions', 'Archive Quarter Data'].map((a) => (
              <button
                key={a}
                className="w-full text-left px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors"
              >
                {a}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
