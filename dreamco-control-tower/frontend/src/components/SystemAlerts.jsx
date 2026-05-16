/**
 * SystemAlerts.jsx
 *
 * Displays active system alerts for the DreamCo Control Tower:
 *  - Stale bot heartbeats (no ping for >5 min)
 *  - Bots in error status
 *  - Deep-learning deadline warnings
 *
 * Data is fetched from /api/alerts on the Control Tower backend.
 * Auto-refreshes every 60 seconds.
 */

import { useEffect, useRef, useState } from 'react';

const REFRESH_MS = 60_000;

const SEVERITY_STYLE = {
  critical: {
    border: 'border-dreamco-red',
    bg: 'bg-red-900/20',
    badge: 'bg-red-900 text-red-300',
    icon: '🔴',
  },
  warning: {
    border: 'border-dreamco-yellow',
    bg: 'bg-yellow-900/20',
    badge: 'bg-yellow-900 text-yellow-300',
    icon: '🟡',
  },
  info: {
    border: 'border-slate-600',
    bg: 'bg-slate-700/20',
    badge: 'bg-slate-700 text-slate-300',
    icon: '🔵',
  },
};

function AlertCard({ alert }) {
  const style = SEVERITY_STYLE[alert.severity] ?? SEVERITY_STYLE.info;
  return (
    <div className={`rounded-xl p-4 border ${style.border} ${style.bg}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <span className="text-lg mt-0.5">{style.icon}</span>
          <div>
            <p className="text-sm text-white leading-snug">{alert.message}</p>
            {alert.bot && (
              <p className="text-xs text-slate-400 mt-1">
                Bot: <span className="font-mono text-slate-300">{alert.bot}</span>
              </p>
            )}
            {alert.since && (
              <p className="text-xs text-slate-500 mt-0.5">
                Since: {new Date(alert.since).toLocaleString()}
              </p>
            )}
          </div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full font-semibold shrink-0 ${style.badge}`}>
          {alert.severity}
        </span>
      </div>
    </div>
  );
}

export default function SystemAlerts() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const intervalRef = useRef(null);

  function fetchData() {
    fetch('/api/alerts')
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

  if (loading) return <p className="text-slate-400">Loading alerts…</p>;
  if (error) return <p className="text-dreamco-red">Error: {error}</p>;
  if (!data) return null;

  const { alerts = [], count, critical, warning } = data;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">🚨 System Alerts</h2>
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

      {/* Summary bar */}
      <div className="flex gap-4 mb-5 text-sm">
        <div className="bg-dreamco-card rounded-lg px-4 py-2 border border-slate-700 flex items-center gap-2">
          <span className="text-slate-400">Total</span>
          <span className="font-bold text-white">{count}</span>
        </div>
        <div
          className={`rounded-lg px-4 py-2 border flex items-center gap-2 ${
            critical > 0 ? 'border-dreamco-red bg-red-900/20' : 'border-slate-700 bg-dreamco-card'
          }`}
        >
          <span className="text-slate-400">Critical</span>
          <span className={`font-bold ${critical > 0 ? 'text-dreamco-red' : 'text-white'}`}>
            {critical}
          </span>
        </div>
        <div
          className={`rounded-lg px-4 py-2 border flex items-center gap-2 ${
            warning > 0
              ? 'border-dreamco-yellow bg-yellow-900/20'
              : 'border-slate-700 bg-dreamco-card'
          }`}
        >
          <span className="text-slate-400">Warning</span>
          <span className={`font-bold ${warning > 0 ? 'text-dreamco-yellow' : 'text-white'}`}>
            {warning}
          </span>
        </div>
      </div>

      {/* Alerts list */}
      {alerts.length === 0 ? (
        <div className="bg-dreamco-card rounded-xl p-8 border border-slate-700 text-center">
          <p className="text-2xl mb-2">✅</p>
          <p className="text-slate-300 font-medium">All systems healthy</p>
          <p className="text-slate-500 text-xs mt-1">No active alerts at this time.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Critical first */}
          {alerts
            .sort((a, b) => {
              const order = { critical: 0, warning: 1, info: 2 };
              return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
            })
            .map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
        </div>
      )}

      <p className="mt-6 text-xs text-slate-600">
        Alerts auto-refresh every 60 seconds. Stale threshold: 5 minutes without a bot heartbeat.
      </p>
    </div>
  );
}
