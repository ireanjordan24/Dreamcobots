import { useEffect, useState } from 'react';

const CATEGORIES = ['APIs', 'Competitors', 'Revenue Models', 'UX Patterns', 'Security', 'Performance', 'AI Ethics'];

const MOCK_PROGRESS = [
  { bot: 'BuddyOrchestrator', scores: [92, 88, 95, 79, 97, 91, 84] },
  { bot: 'DealAnalyzerBot', scores: [85, 94, 98, 72, 88, 76, 65] },
  { bot: 'RevenueEngineBot', scores: [78, 70, 99, 81, 84, 83, 71] },
  { bot: 'MarketplaceBot', scores: [88, 95, 91, 94, 79, 85, 77] },
  { bot: 'CryptoSentinelBot', scores: [91, 87, 82, 68, 96, 88, 83] },
];

function ScoreCell({ score }) {
  const bg = score >= 90 ? 'bg-green-500' : score >= 75 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <td className="px-3 py-3 text-center">
      <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold text-white ${bg}`}>{score}</span>
    </td>
  );
}

export default function LearningMatrix() {
  const [matrix, setMatrix] = useState(MOCK_PROGRESS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/learning')
      .then((r) => r.json())
      .then((d) => {
        if (d?.bots) setMatrix(d.bots);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading learning data…</p>;

  const avgByCategory = CATEGORIES.map((_, ci) => {
    const total = matrix.reduce((sum, b) => sum + (b.scores[ci] ?? 0), 0);
    return Math.round(total / matrix.length);
  });

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🧬</span>
        <div>
          <h2 className="text-xl font-bold text-white">Learning Matrix</h2>
          <p className="text-xs text-slate-400">Cross-bot deep learning progress across all knowledge domains</p>
        </div>
      </div>

      <div className="grid grid-cols-3 lg:grid-cols-7 gap-3 mb-6">
        {CATEGORIES.map((cat, i) => (
          <div key={cat} className="bg-dreamco-card rounded-xl p-3 border border-slate-700 text-center">
            <div className={`text-lg font-bold ${avgByCategory[i] >= 90 ? 'text-green-400' : avgByCategory[i] >= 75 ? 'text-yellow-400' : 'text-red-400'}`}>
              {avgByCategory[i]}
            </div>
            <div className="text-xs text-slate-400 mt-1 leading-tight">{cat}</div>
          </div>
        ))}
      </div>

      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-x-auto mb-6">
        <table className="w-full text-sm min-w-max">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left px-5 py-3 text-slate-400 font-medium text-xs">Bot</th>
              {CATEGORIES.map((c) => (
                <th key={c} className="px-3 py-3 text-xs text-slate-400 font-medium text-center">{c}</th>
              ))}
              <th className="px-3 py-3 text-xs text-slate-400 font-medium text-center">Avg</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/30">
            {matrix.map((row) => {
              const avg = Math.round(row.scores.reduce((a, b) => a + b, 0) / row.scores.length);
              return (
                <tr key={row.bot} className="hover:bg-slate-700/20 transition-colors">
                  <td className="px-5 py-3 font-medium text-white whitespace-nowrap">{row.bot}</td>
                  {row.scores.map((s, i) => <ScoreCell key={i} score={s} />)}
                  <td className="px-3 py-3 text-center font-bold text-white">{avg}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">🎓 Training Actions</h3>
          <div className="space-y-2">
            {['Start Training Cycle', 'Schedule Deep Learning', 'Export Learning Report', 'Reset Category Scores'].map((a) => (
              <button
                key={a}
                className="w-full text-left px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors"
              >
                {a}
              </button>
            ))}
          </div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">📅 Training Schedule</h3>
          <div className="space-y-2 text-sm">
            {[
              { time: 'Every 6h', job: 'API Scraper Training' },
              { time: 'Daily', job: 'Competitor Analysis' },
              { time: 'Weekly', job: 'Full Retrain Cycle' },
              { time: 'On Demand', job: 'Custom Domain Training' },
            ].map((s) => (
              <div key={s.job} className="flex items-center justify-between py-1 border-b border-slate-700/50">
                <span className="text-slate-300">{s.job}</span>
                <span className="text-xs text-dreamco-accent">{s.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
