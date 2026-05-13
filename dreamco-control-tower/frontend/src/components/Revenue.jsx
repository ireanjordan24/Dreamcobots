import { useEffect, useState } from 'react';

const REV_STREAMS = [
  { name: 'Marketplace Subscriptions', amount: 82400, pct: 39 },
  { name: 'White-Label Licenses', amount: 54000, pct: 26 },
  { name: 'Enterprise Contracts', amount: 41200, pct: 20 },
  { name: 'Crypto Yields', amount: 18600, pct: 9 },
  { name: 'API Access Fees', amount: 12800, pct: 6 },
];

const MONTHLY = [
  { month: 'Nov', rev: 148000 },
  { month: 'Dec', rev: 162000 },
  { month: 'Jan', rev: 155000 },
  { month: 'Feb', rev: 178000 },
  { month: 'Mar', rev: 194000 },
  { month: 'Apr', rev: 209000 },
  { month: 'May', rev: 209000, current: true },
];

const COLORS = ['bg-dreamco-accent', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500', 'bg-cyan-500'];

export default function Revenue() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/revenue/stats')
      .then((r) => r.json())
      .then(setStats)
      .catch(() => setStats({ mrr: '$209,000', arr: '$2.5M', growth: '+31%', churn: '1.8%' }));
  }, []);

  const maxRev = Math.max(...MONTHLY.map((m) => m.rev));

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">💰</span>
        <div>
          <h2 className="text-xl font-bold text-white">Revenue</h2>
          <p className="text-xs text-slate-400">Revenue tracking, forecasting &amp; stream analysis</p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'MRR', value: stats?.mrr ?? '$209,000', sub: 'Monthly Recurring Revenue', color: 'text-green-400' },
          { label: 'ARR', value: stats?.arr ?? '$2.5M', sub: 'Annual Run Rate', color: 'text-white' },
          { label: 'Growth', value: stats?.growth ?? '+31%', sub: 'vs last month', color: 'text-dreamco-accent' },
          { label: 'Churn', value: stats?.churn ?? '1.8%', sub: 'monthly churn rate', color: 'text-red-400' },
        ].map((s) => (
          <div key={s.label} className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-sm text-slate-300 mt-1">{s.label}</div>
            <div className="text-xs text-slate-500 mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Bar chart */}
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">📈 Monthly Revenue (6mo)</h3>
          <div className="flex items-end gap-3 h-40">
            {MONTHLY.map((m) => (
              <div key={m.month} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-xs text-slate-400">${(m.rev / 1000).toFixed(0)}k</span>
                <div
                  className={`w-full rounded-t transition-all ${m.current ? 'bg-dreamco-accent' : 'bg-slate-600'}`}
                  style={{ height: `${(m.rev / maxRev) * 100}%` }}
                />
                <span className="text-xs text-slate-400">{m.month}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Revenue streams */}
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">🥧 Revenue Streams</h3>
          <div className="space-y-3">
            {REV_STREAMS.map((s, i) => (
              <div key={s.name}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">{s.name}</span>
                  <span className="text-white font-semibold">${s.amount.toLocaleString()}</span>
                </div>
                <div className="bg-slate-700 rounded-full h-2">
                  <div className={`h-2 rounded-full ${COLORS[i % COLORS.length]}`} style={{ width: `${s.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">⚡ Revenue Actions</h3>
        <div className="flex gap-2 flex-wrap">
          {['Export Revenue Report', 'Set Revenue Goal', 'Configure Alerts', 'View Invoice History', 'Forecast Next Quarter', 'Analyze Top Bots'].map((a) => (
            <button
              key={a}
              className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors"
            >
              {a}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
