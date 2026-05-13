import { useEffect, useState } from 'react';

const ELITE_BOTS = [
  { name: 'BuddyOrchestrator', score: 98, tier: 'ELITE', uptime: '99.9%', revenue: '$42,800' },
  { name: 'DealAnalyzerBot', score: 95, tier: 'ELITE', uptime: '99.5%', revenue: '$38,200' },
  { name: 'RevenueEngineBot', score: 93, tier: 'ELITE', uptime: '99.1%', revenue: '$35,600' },
  { name: 'MarketplaceBot', score: 91, tier: 'ELITE', uptime: '98.7%', revenue: '$31,400' },
  { name: 'CryptoSentinelBot', score: 89, tier: 'ELITE', uptime: '98.3%', revenue: '$28,900' },
];

function StatCard({ label, value, sub, accent }) {
  return (
    <div className={`bg-dreamco-card rounded-xl p-5 border ${accent ? 'border-yellow-500/40' : 'border-slate-700'}`}>
      <div className={`text-2xl font-bold ${accent ? 'text-yellow-400' : 'text-white'}`}>{value}</div>
      <div className="text-sm text-slate-300 mt-1">{label}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

export default function Elite() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetch('/api/elite/status')
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({ tier: 'ELITE', members: 5, totalRevenue: '$176,900', growth: '+24%' }));
  }, []);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">👑</span>
        <div>
          <h2 className="text-xl font-bold text-yellow-400">ELITE Command Center</h2>
          <p className="text-xs text-slate-400">Top-tier autonomous bot performance dashboard</p>
        </div>
        <span className="ml-auto px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-bold border border-yellow-500/30">
          ELITE TIER
        </span>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Elite Bots" value={status?.members ?? 5} sub="top performers" accent />
        <StatCard label="Total Revenue" value={status?.totalRevenue ?? '$176,900'} sub="this month" accent />
        <StatCard label="Growth" value={status?.growth ?? '+24%'} sub="month over month" accent />
        <StatCard label="Avg Uptime" value="99.3%" sub="across elite fleet" accent />
      </div>

      <div className="bg-dreamco-card rounded-xl border border-yellow-500/30 overflow-hidden mb-6">
        <div className="px-5 py-3 border-b border-slate-700 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-yellow-400">⚡ Elite Bot Leaderboard</h3>
          <span className="text-xs text-slate-500">Ranked by performance score</span>
        </div>
        <div className="divide-y divide-slate-700/50">
          {ELITE_BOTS.map((bot, i) => (
            <div key={bot.name} className="px-5 py-4 flex items-center gap-4">
              <span className="text-lg font-bold text-yellow-400/60 w-6">#{i + 1}</span>
              <div className="flex-1">
                <div className="font-semibold text-white text-sm">{bot.name}</div>
                <div className="text-xs text-slate-400">Uptime: {bot.uptime}</div>
              </div>
              <div className="text-right">
                <div className="text-green-400 text-sm font-bold">{bot.revenue}</div>
                <div className="text-xs text-slate-400">revenue</div>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-16 bg-slate-700 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-yellow-400"
                    style={{ width: `${bot.score}%` }}
                  />
                </div>
                <span className="text-xs text-yellow-400 font-bold">{bot.score}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">🎯 Elite Privileges</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            {['Priority API access', 'Dedicated orchestration lane', 'White-label export', 'Revenue share program', 'Zero-downtime deploys'].map((p) => (
              <li key={p} className="flex items-center gap-2">
                <span className="text-yellow-400">✦</span> {p}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">🚀 Quick Actions</h3>
          <div className="space-y-2">
            {['Promote Bot to Elite', 'Generate Elite Report', 'Configure Elite Alerts', 'Export Elite Data'].map((a) => (
              <button
                key={a}
                className="w-full text-left px-4 py-2 rounded-lg bg-yellow-500/10 hover:bg-yellow-500/20 border border-yellow-500/20 text-yellow-300 text-sm transition-colors"
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
