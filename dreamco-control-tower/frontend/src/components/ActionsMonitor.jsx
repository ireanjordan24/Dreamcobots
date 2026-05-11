import { useEffect, useRef, useState } from 'react';

const REFRESH_INTERVAL_MS = 45_000;

const CONCLUSION_STYLE = {
  success: 'bg-green-900/60 text-green-300 border border-green-700/60',
  failure: 'bg-red-900/60 text-red-300 border border-red-700/60',
  cancelled: 'bg-slate-800 text-slate-300 border border-slate-600',
  skipped: 'bg-slate-800 text-slate-300 border border-slate-600',
  timed_out: 'bg-orange-900/60 text-orange-300 border border-orange-700/60',
  action_required: 'bg-yellow-900/60 text-yellow-300 border border-yellow-700/60',
};

const STATUS_STYLE = {
  completed: 'text-slate-300',
  in_progress: 'text-dreamco-yellow',
  queued: 'text-slate-400',
  waiting: 'text-slate-400',
};

function ConclusionBadge({ conclusion }) {
  const cls = CONCLUSION_STYLE[conclusion] ?? 'bg-slate-800 text-slate-400 border border-slate-700';
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${cls}`}>
      {conclusion ?? '—'}
    </span>
  );
}

function StatusText({ status }) {
  const cls = STATUS_STYLE[status] ?? 'text-slate-400';
  return <span className={`text-xs font-semibold ${cls}`}>{status ?? '—'}</span>;
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' });
}

export default function ActionsMonitor() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [dispatching, setDispatching] = useState({});
  const [dispatchMessage, setDispatchMessage] = useState('');
  const [controlInputs, setControlInputs] = useState({});
  const intervalRef = useRef(null);

  function bootstrapControlInputs(controls) {
    const initial = {};
    (controls || []).forEach((c) => {
      initial[c.workflow] = { ...(c.defaultInputs || {}) };
    });
    setControlInputs(initial);
  }

  function fetchActions() {
    fetch('/api/actions')
      .then((r) => r.json())
      .then((json) => {
        setData(json);
        setLastRefresh(new Date());
        setLoading(false);
        setError(null);
        bootstrapControlInputs(json.controls || []);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }

  function updateControlInput(workflow, key, value) {
    setControlInputs((prev) => ({
      ...prev,
      [workflow]: {
        ...(prev[workflow] || {}),
        [key]: value,
      },
    }));
  }

  async function triggerWorkflow(workflow) {
    setDispatchMessage('');
    setDispatching((prev) => ({ ...prev, [workflow]: true }));
    try {
      const response = await fetch('/api/actions/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow,
          inputs: controlInputs[workflow] || {},
        }),
      });
      const json = await response.json();
      if (!response.ok) {
        throw new Error(json.error || json.message || 'Dispatch failed');
      }
      setDispatchMessage(`✅ ${workflow} dispatched successfully.`);
      fetchActions();
    } catch (err) {
      setDispatchMessage(`❌ ${workflow}: ${err.message}`);
    } finally {
      setDispatching((prev) => ({ ...prev, [workflow]: false }));
    }
  }

  useEffect(() => {
    fetchActions();
    intervalRef.current = setInterval(fetchActions, REFRESH_INTERVAL_MS);
    return () => clearInterval(intervalRef.current);
  }, []);

  const runs = data?.runs ?? [];
  const pullRequests = data?.pull_requests ?? [];
  const controls = data?.controls ?? [];
  const source = data?.source ?? 'unknown';
  const controlsByCategory = controls.reduce((acc, control) => {
    const category = control.category || 'General';
    if (!acc[category]) acc[category] = [];
    acc[category].push(control);
    return acc;
  }, {});

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white">⚡ Actions Command Center</h2>
          <p className="text-xs text-slate-400 mt-1">
            Intelligent game-builder/simulation-builder/vibe-coder workflow controls, bot skill testing, SQL action labs, and pull request visibility.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {lastRefresh && (
            <span className="text-xs text-slate-500">Last refresh: {lastRefresh.toLocaleTimeString()}</span>
          )}
          <button
            onClick={fetchActions}
            className="text-xs px-3 py-1.5 bg-slate-700 text-slate-200 hover:text-white rounded-lg transition-colors"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <p className="text-xs text-slate-500 uppercase">Workflow Runs</p>
          <p className="text-2xl font-bold text-white mt-1">{runs.length}</p>
        </div>
        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <p className="text-xs text-slate-500 uppercase">In Progress</p>
          <p className="text-2xl font-bold text-dreamco-yellow mt-1">
            {runs.filter((r) => r.status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <p className="text-xs text-slate-500 uppercase">Pull Requests</p>
          <p className="text-2xl font-bold text-white mt-1">{pullRequests.length}</p>
        </div>
        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <p className="text-xs text-slate-500 uppercase">Data Source</p>
          <p className={`text-sm font-semibold mt-2 ${source === 'github_api' ? 'text-green-300' : 'text-slate-400'}`}>
            {source === 'github_api' ? 'Live GitHub API' : 'Unavailable'}
          </p>
        </div>
      </div>

      {dispatchMessage && (
        <div className="bg-dreamco-card border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-200">
          {dispatchMessage}
        </div>
      )}

      <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-white mb-3">🎛️ Workflow Controls</h3>
        <p className="text-xs text-slate-500 mb-4">
          Pick a card, keep defaults if you want, then tap Run. Builder Lab supports SQL create/read/update/delete and full bot skill checks.
        </p>
        <div className="space-y-4">
          {Object.entries(controlsByCategory).map(([category, categoryControls]) => (
            <div key={category}>
              <h4 className="text-xs uppercase tracking-wide text-slate-400 mb-2">{category}</h4>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {categoryControls.map((control) => (
                  <div key={control.id} className="rounded-xl border border-slate-700 bg-slate-900/30 p-4">
                    <div className="flex items-center justify-between gap-2">
                      <h5 className="text-sm font-semibold text-white">{control.label}</h5>
                      {control.isPermanent && (
                        <span className="text-[10px] uppercase tracking-wide px-2 py-1 rounded-full bg-dreamco-accent/20 text-dreamco-accent border border-dreamco-accent/40">
                          Permanent
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{control.description}</p>

                    <div className="mt-3 space-y-2">
                      {Object.keys(control.defaultInputs || {}).map((key) => (
                        <label key={key} className="block">
                          <span className="text-[11px] text-slate-500 uppercase">{key.replaceAll('_', ' ')}</span>
                          <input
                            className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                            value={controlInputs[control.workflow]?.[key] ?? ''}
                            onChange={(e) => updateControlInput(control.workflow, key, e.target.value)}
                          />
                        </label>
                      ))}
                    </div>

                    <button
                      className="mt-3 w-full px-3 py-2 rounded-lg text-xs font-semibold bg-dreamco-accent text-white hover:opacity-90 disabled:opacity-40"
                      onClick={() => triggerWorkflow(control.workflow)}
                      disabled={dispatching[control.workflow]}
                    >
                      {dispatching[control.workflow] ? 'Dispatching…' : `Run ${control.label}`}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {loading && <p className="text-slate-400">Loading workflow runs…</p>}
      {error && <p className="text-dreamco-red">Error: {error}</p>}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="overflow-x-auto rounded-xl border border-slate-700">
          <div className="px-4 py-3 bg-slate-800 border-b border-slate-700 text-xs uppercase text-slate-400">
            Recent Workflow Runs
          </div>
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-3 py-2">Workflow</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Conclusion</th>
                <th className="px-3 py-2">Started</th>
                <th className="px-3 py-2">Link</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} className="border-t border-slate-700 bg-dreamco-card hover:bg-slate-700/30">
                  <td className="px-3 py-2 text-white text-xs font-medium">{run.name ?? `Run #${run.id}`}</td>
                  <td className="px-3 py-2">
                    <StatusText status={run.status} />
                  </td>
                  <td className="px-3 py-2">
                    <ConclusionBadge conclusion={run.conclusion} />
                  </td>
                  <td className="px-3 py-2 text-slate-400 text-xs">{formatDate(run.run_started_at)}</td>
                  <td className="px-3 py-2 text-xs">
                    {run.url ? (
                      <a href={run.url} target="_blank" rel="noreferrer" className="text-dreamco-accent underline">
                        View
                      </a>
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-700">
          <div className="px-4 py-3 bg-slate-800 border-b border-slate-700 text-xs uppercase text-slate-400">
            Pull Requests
          </div>
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-3 py-2">#</th>
                <th className="px-3 py-2">Title</th>
                <th className="px-3 py-2">State</th>
                <th className="px-3 py-2">Author</th>
                <th className="px-3 py-2">Updated</th>
              </tr>
            </thead>
            <tbody>
              {pullRequests.map((pr) => (
                <tr key={pr.id} className="border-t border-slate-700 bg-dreamco-card hover:bg-slate-700/30">
                  <td className="px-3 py-2 text-slate-300 text-xs">#{pr.number}</td>
                  <td className="px-3 py-2 text-xs">
                    <a href={pr.url} target="_blank" rel="noreferrer" className="text-white hover:text-dreamco-accent">
                      {pr.title}
                    </a>
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-300">
                    {pr.merged_at ? 'merged' : pr.state}
                    {pr.draft ? ' · draft' : ''}
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-400">{pr.user}</td>
                  <td className="px-3 py-2 text-xs text-slate-400">{formatDate(pr.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
