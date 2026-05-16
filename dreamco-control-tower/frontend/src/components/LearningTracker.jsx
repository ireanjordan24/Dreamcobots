/**
 * LearningTracker.jsx
 *
 * Displays the DreamCo AI deep-learning progress toward the June 22 2026
 * deadline.  Data is fetched from /api/learning on the Control Tower backend.
 *
 * Features:
 *  - Deadline countdown (days remaining)
 *  - Overall progress bar
 *  - Per-category progress grid
 *  - Top-scoring bots table
 *  - Auto-refresh every 5 minutes
 */

import { useEffect, useRef, useState } from 'react';

const REFRESH_MS = 5 * 60 * 1000;

function ProgressBar({ pct, color = 'bg-dreamco-accent' }) {
  return (
    <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${Math.min(100, pct)}%` }}
      />
    </div>
  );
}

function DeadlineCountdown({ daysRemaining, scrapingActive }) {
  const urgent = daysRemaining <= 7;
  return (
    <div
      className={`rounded-xl p-5 border ${urgent ? 'border-dreamco-yellow bg-yellow-900/20' : 'border-slate-700 bg-dreamco-card'}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className={`text-3xl font-bold ${urgent ? 'text-dreamco-yellow' : 'text-white'}`}>
            {daysRemaining}
          </div>
          <div className="text-sm text-slate-400 mt-1">days until deadline</div>
          <div className="text-xs text-slate-500 mt-0.5">June 22, 2026</div>
        </div>
        <div className="text-right">
          <span
            className={`text-xs px-2 py-1 rounded-full font-semibold ${
              scrapingActive ? 'bg-green-900 text-green-300' : 'bg-slate-700 text-slate-400'
            }`}
          >
            {scrapingActive ? '🟢 Scraping Active' : '⚫ Scraping Ended'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function LearningTracker() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const intervalRef = useRef(null);

  function fetchData() {
    fetch('/api/learning')
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

  if (loading) return <p className="text-slate-400">Loading learning tracker…</p>;
  if (error) return <p className="text-dreamco-red">Error: {error}</p>;
  if (!data) return null;

  const { deadline, days_remaining, scraping_active, overall_progress, categories, top_bots } =
    data;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">🧠 Learning Tracker</h2>
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

      {/* Deadline countdown + overall progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <DeadlineCountdown daysRemaining={days_remaining} scrapingActive={scraping_active} />

        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-slate-300">Overall Progress</span>
            <span className="text-xl font-bold text-white">{overall_progress}%</span>
          </div>
          <ProgressBar pct={overall_progress} color="bg-dreamco-accent" />
          <div className="mt-2 text-xs text-slate-500">Deadline: {deadline}</div>
        </div>
      </div>

      {/* Per-category progress */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">Category Progress</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {(categories ?? []).map((cat) => (
            <div
              key={cat.category}
              className="bg-dreamco-card rounded-xl p-4 border border-slate-700"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-white">{cat.category}</span>
                <span className="text-xs text-slate-400">{cat.progress}%</span>
              </div>
              <ProgressBar
                pct={cat.progress}
                color={cat.bots_active > 0 ? 'bg-dreamco-green' : 'bg-slate-600'}
              />
              <div className="mt-2 text-xs text-slate-500">
                {cat.bots_active} / {cat.bots_total} bots active
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top learning bots */}
      {top_bots && top_bots.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Top Learning Bots</h3>
          <div className="overflow-x-auto rounded-xl border border-slate-700">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3">Bot</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Tier</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Learning Score</th>
                </tr>
              </thead>
              <tbody>
                {top_bots.map((bot) => (
                  <tr
                    key={bot.name}
                    className="border-t border-slate-700 bg-dreamco-card hover:bg-slate-700/30 transition-colors"
                  >
                    <td className="px-4 py-3 font-medium text-white">{bot.name}</td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{bot.category}</td>
                    <td className="px-4 py-3">
                      <span className="text-xs px-2 py-0.5 bg-dreamco-accent/20 text-dreamco-accent rounded-full font-medium">
                        {bot.tier}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-medium ${
                          bot.status === 'active' ? 'text-dreamco-green' : 'text-slate-400'
                        }`}
                      >
                        {bot.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-semibold">{bot.learning_score}</span>
                        <div className="flex-1 max-w-[80px]">
                          <ProgressBar
                            pct={bot.learning_score}
                            color="bg-dreamco-yellow"
                          />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
