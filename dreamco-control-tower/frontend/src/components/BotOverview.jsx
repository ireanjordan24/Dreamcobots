import { useEffect, useState } from 'react';

const STATUS_COLOR = {
  active: 'text-dreamco-green',
  idle: 'text-slate-400',
  error: 'text-dreamco-red',
  updating: 'text-dreamco-yellow',
};

const STATUS_DOT = {
  active: 'bg-dreamco-green',
  idle: 'bg-slate-500',
  error: 'bg-dreamco-red',
  updating: 'bg-dreamco-yellow',
};

function formatHeartbeat(ts) {
  if (!ts) return 'Never';
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}

export default function BotOverview() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/bots')
      .then((r) => r.json())
      .then((data) => {
        setBots(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="text-slate-400">Loading bots…</p>;
  if (error) return <p className="text-dreamco-red">Error: {error}</p>;

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-4">🤖 Bot Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {bots.map((bot) => (
          <div key={bot.name} className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            {/* Bot name + status dot */}
            <div className="flex items-center justify-between mb-3">
              <span className="font-semibold text-white">{bot.name}</span>
              <span
                className={`inline-flex items-center gap-1.5 text-xs font-medium ${STATUS_COLOR[bot.status] ?? 'text-slate-400'}`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${STATUS_DOT[bot.status] ?? 'bg-slate-500'}`}
                />
                {bot.status ?? 'unknown'}
              </span>
            </div>

            {/* Heartbeat */}
            <div className="text-xs text-slate-400 space-y-1">
              <div>
                💓 Last heartbeat:{' '}
                <span className="text-slate-300">{formatHeartbeat(bot.lastHeartbeat)}</span>
              </div>

              {/* Workflow status */}
              <div>
                ⚙️ Workflow:{' '}
                <span
                  className={
                    bot.workflowStatus === 'success'
                      ? 'text-dreamco-green'
                      : bot.workflowStatus === 'failure'
                        ? 'text-dreamco-red'
                        : 'text-slate-400'
                  }
                >
                  {bot.workflowStatus ?? 'unknown'}
                </span>
              </div>

              {/* Last PR */}
              {bot.lastPR && (
                <div>
                  🔀 Last PR:{' '}
                  <a
                    href={bot.lastPR}
                    target="_blank"
                    rel="noreferrer"
                    className="text-dreamco-accent underline"
                  >
                    view
                  </a>
                </div>
              )}
            </div>
          </div>
        ))}

        {bots.length === 0 && <p className="text-slate-500 col-span-3">No bots registered yet.</p>}
      </div>
    </div>
  );
}
