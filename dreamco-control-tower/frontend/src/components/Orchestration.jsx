import { useEffect, useState } from 'react';

const WORKFLOWS = [
  { id: 'wf1', name: 'Deep Learning Cycle', trigger: 'schedule (6h)', status: 'running', steps: 5, lastRun: '18m ago', nextRun: '5h 42m' },
  { id: 'wf2', name: 'Bot CI/CD Pipeline', trigger: 'push to main', status: 'success', steps: 4, lastRun: '2h ago', nextRun: 'on push' },
  { id: 'wf3', name: 'Revenue Sync', trigger: 'schedule (daily)', status: 'success', steps: 3, lastRun: '6h ago', nextRun: '18h' },
  { id: 'wf4', name: 'Deal Analyzer', trigger: 'webhook', status: 'idle', steps: 2, lastRun: '1d ago', nextRun: 'on trigger' },
  { id: 'wf5', name: 'AI Enablement Hub', trigger: 'schedule (weekly)', status: 'success', steps: 6, lastRun: '3d ago', nextRun: '4d' },
];

const STATUS_CONFIG = {
  running: { dot: 'bg-blue-400 animate-pulse', label: 'text-blue-400', badge: 'bg-blue-500/20 text-blue-400' },
  success: { dot: 'bg-green-400', label: 'text-green-400', badge: 'bg-green-500/20 text-green-400' },
  failure: { dot: 'bg-red-400', label: 'text-red-400', badge: 'bg-red-500/20 text-red-400' },
  idle: { dot: 'bg-slate-500', label: 'text-slate-400', badge: 'bg-slate-600 text-slate-400' },
};

export default function Orchestration() {
  const [workflows, setWorkflows] = useState(WORKFLOWS);
  const [dispatch, setDispatch] = useState('');
  const [dispatching, setDispatching] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetch('/api/actions')
      .then((r) => r.json())
      .then((d) => { if (d?.runs) setWorkflows(d.runs); })
      .catch(() => {});
  }, []);

  async function dispatchWorkflow() {
    if (!dispatch.trim()) return;
    setDispatching(true);
    try {
      const res = await fetch('/api/actions/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow: dispatch }),
      });
      const data = await res.json();
      setMsg(data.message ?? 'Workflow dispatched!');
    } catch {
      setMsg('Dispatch failed — check connection.');
    } finally {
      setDispatching(false);
      setTimeout(() => setMsg(''), 4000);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">⚙️</span>
        <div>
          <h2 className="text-xl font-bold text-white">Orchestration</h2>
          <p className="text-xs text-slate-400">GitHub Actions workflows, bot pipelines &amp; automation control</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-white">{workflows.length}</div>
          <div className="text-sm text-slate-300 mt-1">Total Workflows</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-blue-400">{workflows.filter((w) => w.status === 'running').length}</div>
          <div className="text-sm text-slate-300 mt-1">Running Now</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-green-400">{workflows.filter((w) => w.status === 'success').length}</div>
          <div className="text-sm text-slate-300 mt-1">Last Run: Success</div>
        </div>
      </div>

      {/* Dispatch */}
      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mb-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">⚡ Dispatch Workflow</h3>
        <div className="flex gap-3">
          <input
            value={dispatch}
            onChange={(e) => setDispatch(e.target.value)}
            placeholder="Workflow name (e.g. deep-learning.yml)"
            className="flex-1 bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent"
          />
          <button
            onClick={dispatchWorkflow}
            disabled={dispatching || !dispatch.trim()}
            className="px-5 py-2 bg-dreamco-accent hover:bg-indigo-500 disabled:opacity-40 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            {dispatching ? 'Dispatching…' : 'Dispatch'}
          </button>
        </div>
        {msg && <p className="mt-2 text-xs text-green-400">{msg}</p>}
      </div>

      {/* Workflow list */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">Active Workflows</h3>
        </div>
        <div className="divide-y divide-slate-700/30">
          {workflows.map((wf) => {
            const cfg = STATUS_CONFIG[wf.status] ?? STATUS_CONFIG.idle;
            return (
              <div key={wf.id} className="px-5 py-4 flex items-center gap-4">
                <span className={`w-2 h-2 rounded-full shrink-0 ${cfg.dot}`} />
                <div className="flex-1">
                  <div className="font-medium text-white text-sm">{wf.name}</div>
                  <div className="text-xs text-slate-400">Trigger: {wf.trigger} · {wf.steps} steps</div>
                </div>
                <div className="text-xs text-slate-400 text-right">
                  <div>Last: {wf.lastRun}</div>
                  <div>Next: {wf.nextRun}</div>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cfg.badge}`}>
                  {wf.status}
                </span>
                <div className="flex gap-1">
                  {['Run', 'Logs', 'Pause'].map((a) => (
                    <button
                      key={a}
                      className="px-2 py-1 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
                    >
                      {a}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
