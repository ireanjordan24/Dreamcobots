import { useEffect, useState } from 'react';

function PRBadge({ count, label }) {
  return (
    <div className="bg-slate-700 rounded-lg px-3 py-2 text-center">
      <div className="text-xl font-bold text-white">{count}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  );
}

export default function RepoActivity() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/bots')
      .then((r) => r.json())
      .then((data) => {
        setBots(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-slate-400">Loading activity…</p>;
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-4">📦 Repository Activity</h2>

      <div className="space-y-4">
        {bots.map((bot) => (
          <div key={bot.name} className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white">{bot.name}</h3>
              <span className="text-xs text-slate-400">{bot.repoName}</span>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-4">
              <PRBadge count="—" label="Open PRs" />
              <PRBadge count="—" label="Merged PRs" />
              <PRBadge count="—" label="Issues" />
            </div>

            {/* Workflow status pill */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400">Latest workflow:</span>
              <span
                className={`px-2 py-0.5 rounded-full font-medium ${
                  bot.workflowStatus === 'success'
                    ? 'bg-green-900 text-green-300'
                    : bot.workflowStatus === 'failure'
                      ? 'bg-red-900 text-red-300'
                      : 'bg-slate-700 text-slate-400'
                }`}
              >
                {bot.workflowStatus ?? 'unknown'}
              </span>
            </div>
          </div>
        ))}

        {bots.length === 0 && <p className="text-slate-500">No bots registered yet.</p>}
      </div>

      <p className="mt-4 text-xs text-slate-500">
        ℹ️ Live PR counts and commit history require a valid GITHUB_TOKEN in the backend.
      </p>
    </div>
  );
}
