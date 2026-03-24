import { useState, useEffect, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

function useDashboard(refreshIntervalMs = 30_000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch_ = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch_();
    const id = setInterval(fetch_, refreshIntervalMs);
    return () => clearInterval(id);
  }, [fetch_, refreshIntervalMs]);

  return { data, loading, error, refresh: fetch_ };
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatusBadge({ status }) {
  const colors = {
    active: "bg-green-500",
    offline: "bg-red-500",
    updating: "bg-yellow-400",
    conflict: "bg-orange-500",
    unknown: "bg-gray-500",
  };
  const cls = colors[status] ?? colors.unknown;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold text-white ${cls}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-white opacity-80 inline-block" />
      {status}
    </span>
  );
}

function StatCard({ icon, label, value, sub }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-1">
      <div className="text-2xl">{icon}</div>
      <div className="text-3xl font-bold text-white">{value}</div>
      <div className="text-sm font-medium text-gray-300">{label}</div>
      {sub && <div className="text-xs text-gray-500">{sub}</div>}
    </div>
  );
}

function BotCard({ bot, onUpgrade, upgrading }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-white truncate">{bot.name}</span>
        <StatusBadge status={bot.status} />
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-400">
        <span>Tier</span>
        <span className="text-gray-200 font-medium capitalize">{bot.tier ?? "—"}</span>
        <span>Repo</span>
        <span className="text-gray-200 font-medium truncate">{bot.repoName ?? "—"}</span>
        {bot.branch && (
          <>
            <span>Branch</span>
            <span className="text-gray-200 font-medium">{bot.branch}</span>
          </>
        )}
        {bot.lastCommit && (
          <>
            <span>Last commit</span>
            <span className="text-gray-200 font-medium truncate">{bot.lastCommit}</span>
          </>
        )}
        {bot.latencyMs != null && (
          <>
            <span>Latency</span>
            <span className="text-gray-200 font-medium">{bot.latencyMs} ms</span>
          </>
        )}
        <span>Heartbeat</span>
        <span className="text-gray-200 font-medium">
          {bot.lastHeartbeat ? new Date(bot.lastHeartbeat).toLocaleTimeString() : "—"}
        </span>
      </div>

      <button
        onClick={() => onUpgrade(bot.name)}
        disabled={upgrading}
        className="mt-auto w-full bg-dreamco-600 hover:bg-dreamco-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-semibold py-1.5 rounded-lg transition-colors"
      >
        {upgrading ? "Upgrading…" : "⚙️  Upgrade"}
      </button>
    </div>
  );
}

function RepoCard({ repo }) {
  // openPRs may be an array (from /api/repos/:owner/:repo) or a number (from config/repos.json).
  const openPRsArray = Array.isArray(repo.openPRs) ? repo.openPRs : [];
  const openPRCount = Array.isArray(repo.openPRs) ? repo.openPRs.length : (repo.openPRs ?? 0);
  const openIssueCount = Array.isArray(repo.openIssues) ? repo.openIssues.length : (repo.openIssues ?? 0);
  const hasConflicts = openPRsArray.some((pr) =>
    pr.title?.toLowerCase().includes("conflict")
  );

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-white">{repo.name}</span>
        {hasConflicts && (
          <span className="text-xs bg-orange-500 text-white px-2 py-0.5 rounded-full">
            ⚠️ Conflict
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-400">
        <span>Owner</span>
        <span className="text-gray-200">{repo.owner}</span>
        <span>Bots</span>
        <span className="text-gray-200">{(repo.bots ?? []).length}</span>
        <span>Open PRs</span>
        <span className="text-gray-200">{openPRCount}</span>
        <span>Open issues</span>
        <span className="text-gray-200">{openIssueCount}</span>
        <span>Auto-upgrade</span>
        <span className={repo.autoUpgrade ? "text-green-400" : "text-gray-500"}>
          {repo.autoUpgrade ? "enabled" : "disabled"}
        </span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main App
// ---------------------------------------------------------------------------

export default function App() {
  const { data, loading, error, refresh } = useDashboard();
  const [upgradingBot, setUpgradingBot] = useState(null);
  const [upgradeResults, setUpgradeResults] = useState({});

  const handleUpgrade = async (botName) => {
    setUpgradingBot(botName);
    try {
      const res = await fetch(`${API_BASE}/bots/${botName}/upgrade`, { method: "POST" });
      const result = await res.json();
      setUpgradeResults((prev) => ({ ...prev, [botName]: result }));
      await refresh();
    } catch (err) {
      setUpgradeResults((prev) => ({ ...prev, [botName]: { error: err.message } }));
    } finally {
      setUpgradingBot(null);
    }
  };

  const summary = data?.summary ?? {};
  const bots = data?.bots ?? [];
  const repos = data?.repos ?? [];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏰</span>
            <div>
              <h1 className="text-lg font-bold text-white leading-none">
                DreamCo Control Tower
              </h1>
              <p className="text-xs text-gray-400">Autonomous Bot Empire Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {data?.timestamp && (
              <span className="text-xs text-gray-500 hidden sm:block">
                Updated {new Date(data.timestamp).toLocaleTimeString()}
              </span>
            )}
            <button
              onClick={refresh}
              className="bg-gray-800 hover:bg-gray-700 text-sm text-white px-3 py-1.5 rounded-lg transition-colors"
            >
              ↻ Refresh
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Error banner */}
        {error && (
          <div className="bg-red-900/50 border border-red-700 rounded-xl p-4 text-red-200 text-sm">
            ⚠️ Could not reach Control Tower backend: <strong>{error}</strong>
            <span className="ml-2 text-red-400 text-xs">(showing cached / mock data)</span>
          </div>
        )}

        {/* Stats */}
        {loading && !data ? (
          <div className="text-center text-gray-500 py-16">Loading dashboard…</div>
        ) : (
          <>
            <section>
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Overview
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <StatCard icon="🤖" label="Total Bots" value={summary.totalBots ?? bots.length} />
                <StatCard
                  icon="✅"
                  label="Active Bots"
                  value={summary.activeBots ?? bots.filter((b) => b.status === "active").length}
                  sub="live & reporting"
                />
                <StatCard
                  icon="❌"
                  label="Offline Bots"
                  value={summary.offlineBots ?? bots.filter((b) => b.status !== "active").length}
                  sub="need attention"
                />
                <StatCard icon="📦" label="Repos" value={summary.totalRepos ?? repos.length} />
              </div>
            </section>

            {/* Bots */}
            <section>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                  Bot Registry
                </h2>
                <span className="text-xs text-gray-500">{bots.length} registered</span>
              </div>
              {bots.length === 0 ? (
                <p className="text-gray-500 text-sm">No bots registered yet.</p>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {bots.map((bot) => (
                    <BotCard
                      key={bot.name}
                      bot={bot}
                      onUpgrade={handleUpgrade}
                      upgrading={upgradingBot === bot.name}
                    />
                  ))}
                </div>
              )}
            </section>

            {/* Repos */}
            {repos.length > 0 && (
              <section>
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Repository Monitor
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {repos.map((repo) => (
                    <RepoCard key={repo.name} repo={repo} />
                  ))}
                </div>
              </section>
            )}

            {/* Upgrade Results */}
            {Object.keys(upgradeResults).length > 0 && (
              <section>
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Recent Upgrade Results
                </h2>
                <div className="space-y-2">
                  {Object.entries(upgradeResults).map(([name, result]) => (
                    <div
                      key={name}
                      className="bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 text-xs text-gray-300 flex items-start gap-3"
                    >
                      <span className="font-semibold text-white whitespace-nowrap">{name}</span>
                      <pre className="overflow-auto text-gray-400 flex-1">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>

      <footer className="border-t border-gray-800 mt-12 py-4 text-center text-xs text-gray-600">
        DreamCo Control Tower © {new Date().getFullYear()} — Autonomous Bot Empire
      </footer>
    </div>
  );
}
