import React, { useEffect, useState, useCallback } from 'react';

const STATUS_COLORS = {
  active: 'bg-green-500',
  idle: 'bg-yellow-500',
  error: 'bg-red-500',
};

function BotCard({ bot }) {
  const statusColor = STATUS_COLORS[bot.status] || 'bg-gray-500';
  return (
    <div className="bg-gray-800 rounded-xl p-5 shadow-lg border border-gray-700 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold text-lg">{bot.name}</h3>
        <span className={`text-xs px-2 py-1 rounded-full text-white font-medium ${statusColor}`}>
          {bot.status}
        </span>
      </div>
      <p className="text-gray-400 text-sm">{bot.description}</p>
      <div className="grid grid-cols-2 gap-1 text-xs text-gray-300 mt-1">
        <span>Tier: <strong>{bot.tier}</strong></span>
        <span>Pending PRs: <strong>{bot.pendingPRs ?? 0}</strong></span>
        <span>
          Last Heartbeat:{' '}
          <strong>{bot.lastHeartbeat ? new Date(bot.lastHeartbeat).toLocaleString() : '—'}</strong>
        </span>
        <span>
          Last Update:{' '}
          <strong>{bot.lastUpdate ? new Date(bot.lastUpdate).toLocaleString() : '—'}</strong>
        </span>
      </div>
    </div>
  );
}

export default function BotOverview() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const fetchBots = useCallback(() => {
    setLoading(true);
    setError(null);
    fetch('/api/get-bots')
      .then(res => {
        if (!res.ok) {
          return res.json().then(body => {
            throw new Error(body.error || `Server responded with ${res.status}`);
          });
        }
        return res.json();
      })
      .then(data => {
        setBots(data.bots || []);
        setLastRefresh(data.timestamp ? new Date(data.timestamp).toLocaleString() : new Date().toLocaleString());
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchBots();
  }, [fetchBots]);

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-white text-2xl font-bold">🤖 Bot Overview</h1>
          {lastRefresh && (
            <p className="text-gray-400 text-sm mt-1">Last refreshed: {lastRefresh}</p>
          )}
        </div>
        <button
          onClick={fetchBots}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
        >
          {loading ? 'Refreshing…' : '⟳ Refresh'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900 border border-red-600 text-red-200 px-4 py-3 rounded-lg mb-4">
          ⚠️ {error}
        </div>
      )}

      {loading && bots.length === 0 ? (
        <p className="text-gray-400">Loading bots…</p>
      ) : bots.length === 0 ? (
        <p className="text-gray-400">No bots registered yet.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {bots.map(bot => (
            <BotCard key={bot.name} bot={bot} />
          ))}
        </div>
      )}
    </div>
  );
}
