import { useEffect, useState } from 'react';

const MEDALS = ['🥇', '🥈', '🥉'];
const LEADERS_MOCK = [
  { name: 'BuddyOrchestrator', role: 'Command AI', score: 98, tasks: 4820, revenue: '$42.8k', model: 'GPT-4o', trend: '+3%' },
  { name: 'DealAnalyzerBot', role: 'Finance AI', score: 95, tasks: 3210, revenue: '$38.2k', model: 'Claude-3', trend: '+7%' },
  { name: 'RevenueEngineBot', role: 'Revenue AI', score: 93, tasks: 2980, revenue: '$35.6k', model: 'GPT-4o', trend: '+2%' },
  { name: 'MarketplaceBot', role: 'Commerce AI', score: 91, tasks: 2540, revenue: '$31.4k', model: 'Gemini Pro', trend: '+5%' },
  { name: 'CryptoSentinelBot', role: 'Crypto AI', score: 89, tasks: 1890, revenue: '$28.9k', model: 'Claude-3', trend: '+9%' },
  { name: 'AILeaderBot', role: 'Strategy AI', score: 87, tasks: 1650, revenue: '$24.1k', model: 'GPT-4o', trend: '+1%' },
  { name: 'OrchestrationBot', role: 'Ops AI', score: 85, tasks: 1420, revenue: '$19.3k', model: 'Llama-3', trend: '+4%' },
];

export default function AILeaders() {
  const [leaders, setLeaders] = useState(LEADERS_MOCK);
  const [period, setPeriod] = useState('month');

  useEffect(() => {
    fetch(`/api/ai-leaders?period=${period}`)
      .then((r) => r.json())
      .then((d) => { if (d?.leaders) setLeaders(d.leaders); })
      .catch(() => {});
  }, [period]);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🏆</span>
        <div>
          <h2 className="text-xl font-bold text-white">AI Leaders</h2>
          <p className="text-xs text-slate-400">Top performing AI bots ranked by score, tasks, and revenue</p>
        </div>
        <div className="ml-auto flex gap-2">
          {['week', 'month', 'quarter'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors capitalize ${period === p ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Top 3 podium */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {leaders.slice(0, 3).map((l, i) => (
          <div
            key={l.name}
            className={`bg-dreamco-card rounded-xl p-5 border text-center ${i === 0 ? 'border-yellow-400/50 ring-1 ring-yellow-400/30' : 'border-slate-700'}`}
          >
            <div className="text-3xl mb-2">{MEDALS[i]}</div>
            <div className="font-bold text-white mb-1">{l.name}</div>
            <div className="text-xs text-slate-400 mb-3">{l.role}</div>
            <div className="text-2xl font-bold text-dreamco-accent mb-1">{l.score}</div>
            <div className="text-xs text-slate-400">score</div>
            <div className="mt-3 text-green-400 font-semibold text-sm">{l.revenue}</div>
            <div className="text-xs text-slate-500 mt-1">{l.trend} vs last {period}</div>
          </div>
        ))}
      </div>

      {/* Full leaderboard */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">Full Leaderboard</h3>
        </div>
        <div className="divide-y divide-slate-700/30">
          {leaders.map((l, i) => (
            <div key={l.name} className="px-5 py-4 flex items-center gap-4">
              <span className="text-sm font-bold text-slate-500 w-6">{i < 3 ? MEDALS[i] : `#${i + 1}`}</span>
              <div className="flex-1">
                <div className="font-medium text-white text-sm">{l.name}</div>
                <div className="text-xs text-slate-400">{l.role} · {l.model}</div>
              </div>
              <div className="text-xs text-slate-400 w-20 text-right">{l.tasks.toLocaleString()} tasks</div>
              <div className="text-green-400 font-semibold text-sm w-16 text-right">{l.revenue}</div>
              <div className="text-dreamco-accent text-xs w-8 text-right">{l.trend}</div>
              <div className="flex items-center gap-1 w-24">
                <div className="flex-1 bg-slate-700 rounded-full h-1.5">
                  <div className="h-1.5 rounded-full bg-dreamco-accent" style={{ width: `${l.score}%` }} />
                </div>
                <span className="text-xs font-bold text-white">{l.score}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
