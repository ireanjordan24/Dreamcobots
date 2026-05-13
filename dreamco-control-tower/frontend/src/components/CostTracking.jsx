import { useEffect, useState } from 'react';

const COST_CATEGORIES = [
  { name: 'AI APIs', budget: 500, spent: 342, icon: '🤖', items: ['OpenAI: $184', 'Anthropic: $98', 'Gemini: $60'] },
  { name: 'Infrastructure', budget: 800, spent: 621, icon: '☁️', items: ['AWS: $421', 'GitHub Actions: $120', 'DNS/CDN: $80'] },
  { name: 'Tools & SaaS', budget: 300, spent: 218, icon: '🛠️', items: ['Replit: $80', 'Stripe fees: $92', 'Monitoring: $46'] },
  { name: 'Marketing', budget: 400, spent: 180, icon: '📣', items: ['Ads: $140', 'Content: $40'] },
  { name: 'Labor/Contractors', budget: 2000, spent: 1640, icon: '👥', items: ['Dev contractors: $1,200', 'AI training: $440'] },
];

const ALERTS = [
  { msg: 'AWS cost spike +34% this week', severity: 'warning' },
  { msg: 'OpenAI usage trending toward limit', severity: 'warning' },
  { msg: 'All other categories within budget', severity: 'ok' },
];

export default function CostTracking() {
  const [categories, setCategories] = useState(COST_CATEGORIES);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/cost-tracking/summary')
      .then((r) => r.json())
      .then((d) => { if (d?.categories) setCategories(d.categories); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading cost data…</p>;

  const totalBudget = categories.reduce((s, c) => s + c.budget, 0);
  const totalSpent = categories.reduce((s, c) => s + c.spent, 0);
  const totalRemaining = totalBudget - totalSpent;
  const pct = Math.round((totalSpent / totalBudget) * 100);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">📉</span>
        <div>
          <h2 className="text-xl font-bold text-white">Cost Tracking</h2>
          <p className="text-xs text-slate-400">Monitor budget usage, burn rate &amp; cost optimization</p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-white">${totalBudget.toLocaleString()}</div>
          <div className="text-sm text-slate-300 mt-1">Monthly Budget</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-red-500/20">
          <div className="text-2xl font-bold text-red-400">${totalSpent.toLocaleString()}</div>
          <div className="text-sm text-slate-300 mt-1">Spent This Month</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-green-500/20">
          <div className="text-2xl font-bold text-green-400">${totalRemaining.toLocaleString()}</div>
          <div className="text-sm text-slate-300 mt-1">Remaining</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className={`text-2xl font-bold ${pct >= 90 ? 'text-red-400' : pct >= 75 ? 'text-yellow-400' : 'text-green-400'}`}>{pct}%</div>
          <div className="text-sm text-slate-300 mt-1">Budget Used</div>
        </div>
      </div>

      {/* Alerts */}
      <div className="space-y-2 mb-6">
        {ALERTS.map((a, i) => (
          <div key={i} className={`px-4 py-2.5 rounded-lg text-sm flex items-center gap-2 ${a.severity === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/20 text-yellow-300' : 'bg-green-500/10 border border-green-500/20 text-green-300'}`}>
            <span>{a.severity === 'warning' ? '⚠️' : '✅'}</span> {a.msg}
          </div>
        ))}
      </div>

      {/* Category breakdown */}
      <div className="space-y-4 mb-6">
        {categories.map((cat) => {
          const catPct = Math.round((cat.spent / cat.budget) * 100);
          const barColor = catPct >= 90 ? 'bg-red-500' : catPct >= 75 ? 'bg-yellow-500' : 'bg-green-500';
          return (
            <div key={cat.name} className="bg-dreamco-card rounded-xl border border-slate-700 p-5">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xl">{cat.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-white">{cat.name}</span>
                    <span className="text-sm text-slate-300">${cat.spent} / ${cat.budget}</span>
                  </div>
                  <div className="bg-slate-700 rounded-full h-2">
                    <div className={`h-2 rounded-full transition-all ${barColor}`} style={{ width: `${Math.min(catPct, 100)}%` }} />
                  </div>
                </div>
                <span className={`text-xs font-bold w-10 text-right ${catPct >= 90 ? 'text-red-400' : catPct >= 75 ? 'text-yellow-400' : 'text-green-400'}`}>{catPct}%</span>
              </div>
              <div className="flex gap-3 flex-wrap">
                {cat.items.map((item) => (
                  <span key={item} className="text-xs text-slate-400 px-2 py-0.5 bg-slate-800 rounded">{item}</span>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">💡 Cost Optimization Actions</h3>
        <div className="flex gap-2 flex-wrap">
          {['Set Budget Alert', 'Optimize API Usage', 'Export Cost Report', 'View Cost History', 'AI Cost Advisor', 'Upgrade/Downgrade Plan'].map((a) => (
            <button key={a} className="px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors">{a}</button>
          ))}
        </div>
      </div>
    </div>
  );
}
