/**
 * RevenueMetrics.jsx
 *
 * Displays DreamCo revenue dashboard — MRR, ARR, top-earning bots, and
 * revenue breakdowns by tier and category.
 *
 * Data is fetched from /api/revenue on the Control Tower backend.
 * Auto-refreshes every 5 minutes.
 */

import { useEffect, useRef, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

const REFRESH_MS = 5 * 60 * 1000;

const TIER_COLORS = {
  FREE: '#94a3b8',
  PRO: '#6366f1',
  ENTERPRISE: '#f59e0b',
  ELITE: '#a855f7',
};

const CAT_COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4', '#a855f7', '#f97316'];

function MetricCard({ label, value, sub, highlight }) {
  return (
    <div
      className={`rounded-xl p-5 border ${highlight ? 'border-dreamco-accent bg-dreamco-accent/10' : 'border-slate-700 bg-dreamco-card'}`}
    >
      <div className={`text-2xl font-bold ${highlight ? 'text-dreamco-accent' : 'text-white'}`}>
        {value}
      </div>
      <div className="text-sm text-slate-300 mt-1">{label}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

function formatUSD(n) {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}k`;
  return `$${n.toLocaleString()}`;
}

export default function RevenueMetrics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const intervalRef = useRef(null);

  function fetchData() {
    fetch('/api/revenue')
      .then((r) => r.json())
      .then((json) => {
        setData(json);
        setLastRefresh(new Date());
        setLoading(false);
        setError(null);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData();
    intervalRef.current = setInterval(fetchData, REFRESH_MS);
    return () => clearInterval(intervalRef.current);
  }, []);

  if (loading) return <p className="text-slate-400">Loading revenue metrics…</p>;
  if (error) return <p className="text-dreamco-red">Error: {error}</p>;
  if (!data) return null;

  const { mrr, arr, total_catalog_value, active_revenue_bots, by_tier, by_category, top_earners } =
    data;

  // Chart data
  const tierData = Object.entries(by_tier ?? {}).map(([tier, revenue]) => ({ tier, revenue }));
  const categoryData = Object.entries(by_category ?? {})
    .sort((a, b) => b[1] - a[1])
    .map(([category, revenue]) => ({ category, revenue }));

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">💰 Revenue Metrics</h2>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-xs text-slate-500">
              Updated: {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchData}
            className="text-xs px-3 py-1.5 bg-slate-700 text-slate-300 hover:text-white rounded-lg transition-colors"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Monthly MRR" value={formatUSD(mrr)} sub="active subscriptions" highlight />
        <MetricCard label="Annual ARR" value={formatUSD(arr)} sub="projected" />
        <MetricCard
          label="Catalog Value"
          value={formatUSD(total_catalog_value)}
          sub="total across all bots"
        />
        <MetricCard
          label="Revenue Bots"
          value={active_revenue_bots}
          sub="active paid bots"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Revenue by tier */}
        {tierData.length > 0 && (
          <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Revenue by Tier</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={tierData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="tier" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: 'none' }}
                  formatter={(v) => [`$${v}/mo`, 'Revenue']}
                />
                <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
                  {tierData.map((entry) => (
                    <Cell
                      key={entry.tier}
                      fill={TIER_COLORS[entry.tier] ?? '#6366f1'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Revenue by category — pie */}
        {categoryData.length > 0 && (
          <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Revenue by Category</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={categoryData}
                  dataKey="revenue"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  label={({ category, percent }) =>
                    percent > 0.05 ? `${category} ${(percent * 100).toFixed(0)}%` : ''
                  }
                  labelLine={false}
                >
                  {categoryData.map((_, idx) => (
                    <Cell key={idx} fill={CAT_COLORS[idx % CAT_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: 'none' }}
                  formatter={(v) => [`$${v}/mo`, 'Revenue']}
                />
                <Legend wrapperStyle={{ fontSize: 10, color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Top earners table */}
      {top_earners && top_earners.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Top Earning Bots</h3>
          <div className="overflow-x-auto rounded-xl border border-slate-700">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3">Bot</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Tier</th>
                  <th className="px-4 py-3">Price / mo</th>
                </tr>
              </thead>
              <tbody>
                {top_earners.map((bot) => (
                  <tr
                    key={bot.name}
                    className="border-t border-slate-700 bg-dreamco-card hover:bg-slate-700/30 transition-colors"
                  >
                    <td className="px-4 py-3 font-medium text-white">{bot.name}</td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{bot.category || '—'}</td>
                    <td className="px-4 py-3">
                      <span
                        className="text-xs px-2 py-0.5 rounded-full font-semibold"
                        style={{
                          background: `${TIER_COLORS[bot.tier] ?? '#6366f1'}22`,
                          color: TIER_COLORS[bot.tier] ?? '#6366f1',
                        }}
                      >
                        {bot.tier}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-semibold text-dreamco-green">
                      ${bot.price_usd}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {mrr === 0 && (
        <div className="bg-dreamco-card rounded-xl p-6 border border-slate-700 text-center mt-4">
          <p className="text-slate-400 text-sm">No active revenue bots detected.</p>
          <p className="text-slate-500 text-xs mt-1">
            Deploy paid-tier bots and send heartbeats to start tracking revenue.
          </p>
        </div>
      )}
    </div>
  );
}
