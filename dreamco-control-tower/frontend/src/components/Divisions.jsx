import { useEffect, useState } from 'react';

const DIVISION_DATA = [
  { id: 'bot-eng', name: 'Bot Engineering', emoji: '⚙️', lead: 'BuddyOrchestrator', status: 'active', bots: 12, kpi: '99.1% uptime', color: 'border-blue-500/40' },
  { id: 'ai-research', name: 'AI Research', emoji: '🧠', lead: 'AILeaderBot', status: 'active', bots: 8, kpi: '7 models trained', color: 'border-purple-500/40' },
  { id: 'finance', name: 'Finance Ops', emoji: '💰', lead: 'RevenueEngineBot', status: 'active', bots: 6, kpi: '$91k this month', color: 'border-green-500/40' },
  { id: 'market', name: 'Market Intel', emoji: '📊', lead: 'DealAnalyzerBot', status: 'active', bots: 9, kpi: '12 deals tracked', color: 'border-yellow-500/40' },
  { id: 'infra', name: 'Infrastructure', emoji: '🏗️', lead: 'OrchestrationBot', status: 'idle', bots: 5, kpi: '3 pipelines live', color: 'border-slate-500/40' },
];

export default function Divisions() {
  const [selected, setSelected] = useState(null);
  const [divisions, setDivisions] = useState(DIVISION_DATA);

  useEffect(() => {
    fetch('/api/divisions')
      .then((r) => r.json())
      .then((d) => { if (d?.divisions) setDivisions(d.divisions); })
      .catch(() => {});
  }, []);

  const detail = divisions.find((d) => d.id === selected);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🏢</span>
        <div>
          <h2 className="text-xl font-bold text-white">Divisions</h2>
          <p className="text-xs text-slate-400">Manage and monitor all organizational divisions</p>
        </div>
        <button className="ml-auto px-4 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-sm rounded-lg transition-colors">
          + New Division
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {divisions.map((div) => (
          <button
            key={div.id}
            onClick={() => setSelected(selected === div.id ? null : div.id)}
            className={`text-left bg-dreamco-card rounded-xl p-5 border ${selected === div.id ? 'border-dreamco-accent' : div.color} transition-all hover:scale-[1.01]`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">{div.emoji}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${div.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-slate-600 text-slate-400'}`}>
                {div.status}
              </span>
            </div>
            <div className="font-semibold text-white mb-1">{div.name}</div>
            <div className="text-xs text-slate-400 mb-3">Lead: {div.lead}</div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300">🤖 {div.bots} bots</span>
              <span className="text-dreamco-accent font-medium">{div.kpi}</span>
            </div>
          </button>
        ))}
      </div>

      {detail && (
        <div className="bg-dreamco-card rounded-xl border border-dreamco-accent/30 p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-2xl">{detail.emoji}</span>
            <h3 className="text-lg font-bold text-white">{detail.name} — Detail View</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {[
              { label: 'AI Lead', val: detail.lead },
              { label: 'Bot Count', val: detail.bots },
              { label: 'KPI', val: detail.kpi },
            ].map((s) => (
              <div key={s.label} className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-xs text-slate-400 mb-1">{s.label}</div>
                <div className="font-semibold text-white">{s.val}</div>
              </div>
            ))}
          </div>
          <div className="flex gap-3 flex-wrap">
            {['View Bots', 'Edit Division', 'Generate Report', 'Archive'].map((a) => (
              <button
                key={a}
                className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors"
              >
                {a}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
