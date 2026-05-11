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
  const [chatHistory, setChatHistory] = useState([]);
  const [chatMessage, setChatMessage] = useState('');
  const [chatTargets, setChatTargets] = useState('buddy-bot');
  const [chatSender, setChatSender] = useState('user');
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState('');
  const [botName, setBotName] = useState('buddy-bot');
  const [botDepth, setBotDepth] = useState('standard');
  const [botPlan, setBotPlan] = useState(null);
  const [botPlanBusy, setBotPlanBusy] = useState(false);
  const [botPlanError, setBotPlanError] = useState('');
  const [chargeData, setChargeData] = useState(null);
  const [chargeError, setChargeError] = useState('');
  const [chargeBusy, setChargeBusy] = useState(false);
  const [chargeMessage, setChargeMessage] = useState('');
  const [approveBusyId, setApproveBusyId] = useState('');
  const [chargeDescription, setChargeDescription] = useState('OpenAI API test run');
  const [chargeUnits, setChargeUnits] = useState('1000');
  const [chargeUnitCost, setChargeUnitCost] = useState('0.002');
  const [commandTarget, setCommandTarget] = useState('buddy-bot');
  const [commandRunMode, setCommandRunMode] = useState('single');
  const [commandValidation, setCommandValidation] = useState('standard');
  const [commandBusy, setCommandBusy] = useState(false);
  const [commandError, setCommandError] = useState('');
  const [commandResult, setCommandResult] = useState(null);
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

  function fetchChatHistory() {
    fetch('/api/actions/chat')
      .then((r) => r.json())
      .then((json) => {
        setChatHistory(json.history || []);
      })
      .catch(() => {
        setChatHistory([]);
      });
  }

  async function sendBuddyMessage() {
    setChatError('');
    const trimmed = chatMessage.trim();
    if (!trimmed) return;
    setChatBusy(true);
    try {
      const response = await fetch('/api/actions/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          sender: chatSender,
          targetBots: chatTargets
            .split(',')
            .map((v) => v.trim())
            .filter(Boolean),
        }),
      });
      const json = await response.json();
      if (!response.ok) {
        throw new Error(json.error || 'Chat request failed');
      }
      setChatHistory(json.history || []);
      setChatMessage('');
    } catch (err) {
      setChatError(err.message);
    } finally {
      setChatBusy(false);
    }
  }

  async function generateBotPlan() {
    setBotPlanError('');
    setBotPlanBusy(true);
    try {
      const response = await fetch('/api/actions/test-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          botName,
          depth: botDepth,
        }),
      });
      const json = await response.json();
      if (!response.ok) {
        throw new Error(json.error || 'Failed to generate bot test plan');
      }
      setBotPlan(json);
    } catch (err) {
      setBotPlanError(err.message);
    } finally {
      setBotPlanBusy(false);
    }
  }

  function fetchChargeSummary() {
    fetch('/api/actions/charges')
      .then((r) => r.json())
      .then((json) => {
        setChargeData(json);
        setChargeError('');
      })
      .catch((err) => {
        setChargeError(err.message);
      });
  }

  async function previewCharge() {
    setChargeBusy(true);
    setChargeMessage('');
    setChargeError('');
    try {
      const response = await fetch('/api/actions/charges/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: chargeDescription,
          units: chargeUnits,
          unit_cost_usd: chargeUnitCost,
        }),
      });
      const json = await response.json();
      if (!response.ok) {
        throw new Error(json.error || 'Failed to create charge preview');
      }
      setChargeData((prev) => ({
        ...(prev || {}),
        summary: json.summary,
        pending_approvals: [...(prev?.pending_approvals || []), json.preview],
      }));
      setChargeMessage('Charge preview created. Approval is required before spend.');
      fetchChargeSummary();
    } catch (err) {
      setChargeError(err.message);
    } finally {
      setChargeBusy(false);
    }
  }

  async function approveCharge(previewId) {
    setApproveBusyId(previewId);
    setChargeMessage('');
    setChargeError('');
    try {
      const response = await fetch('/api/actions/charges/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          preview_id: previewId,
          approved_by: 'actions-page-user',
        }),
      });
      const json = await response.json();
      if (!response.ok) {
        throw new Error(json.error || 'Failed to approve preview');
      }
      setChargeMessage(json.message || 'Charge approved.');
      fetchChargeSummary();
    } catch (err) {
      setChargeError(err.message);
    } finally {
      setApproveBusyId('');
    }
  }

  async function runBuddyCommand() {
    setCommandBusy(true);
    setCommandError('');
    try {
      const response = await fetch('/api/actions/buddy-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: commandTarget,
          runMode: commandRunMode,
          validation: commandValidation,
        }),
      });
      const json = await response.json();
      if (!response.ok) {
        throw new Error(json.error || 'Buddy command failed');
      }
      setCommandResult(json);
    } catch (err) {
      setCommandError(err.message);
      setCommandResult(null);
    } finally {
      setCommandBusy(false);
    }
  }

  useEffect(() => {
    fetchActions();
    fetchChatHistory();
    fetchChargeSummary();
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
                          <span className="text-[11px] text-slate-500 uppercase">{key.replace(/_/g, ' ')}</span>
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

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-white mb-2">💬 Buddy Chat + Training</h3>
          <p className="text-xs text-slate-500 mb-3">
            Chat in plain language. No SQL required. You can also mark messages as bot-system training sync.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Sender</span>
              <select
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={chatSender}
                onChange={(e) => setChatSender(e.target.value)}
              >
                <option value="user">User</option>
                <option value="bot_system">Bot System</option>
              </select>
            </label>
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Target Bots (comma separated)</span>
              <input
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={chatTargets}
                onChange={(e) => setChatTargets(e.target.value)}
              />
            </label>
          </div>
          <label className="block mt-2">
            <span className="text-[11px] text-slate-500 uppercase">Message</span>
            <textarea
              className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white min-h-20"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder="Buddy, help me test company-lookup bot with easy steps."
            />
          </label>
          <button
            className="mt-2 px-3 py-2 rounded-lg text-xs font-semibold bg-dreamco-accent text-white hover:opacity-90 disabled:opacity-40"
            onClick={sendBuddyMessage}
            disabled={chatBusy}
          >
            {chatBusy ? 'Sending…' : 'Send to Buddy'}
          </button>
          {chatError && <p className="mt-2 text-xs text-dreamco-red">{chatError}</p>}
          <div className="mt-3 rounded-lg border border-slate-700 bg-slate-900/40 p-3 max-h-56 overflow-y-auto">
            {(chatHistory || []).length === 0 ? (
              <p className="text-xs text-slate-500">No chat yet.</p>
            ) : (
              chatHistory.map((entry, idx) => (
                <div key={`${entry.created_at}-${idx}`} className="mb-2">
                  <p className="text-[11px] text-slate-500 uppercase">{entry.role}</p>
                  <p className="text-xs text-slate-200">{entry.message}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-white mb-2">🧪 Buddy Bot Test Planner</h3>
          <p className="text-xs text-slate-500 mb-3">
            Type any bot name and get an easy no-SQL test plan you can run right from Actions.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Bot Name</span>
              <input
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={botName}
                onChange={(e) => setBotName(e.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Depth</span>
              <select
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={botDepth}
                onChange={(e) => setBotDepth(e.target.value)}
              >
                <option value="quick">Quick</option>
                <option value="standard">Standard</option>
                <option value="deep">Deep</option>
              </select>
            </label>
          </div>
          <button
            className="mt-2 px-3 py-2 rounded-lg text-xs font-semibold bg-dreamco-accent text-white hover:opacity-90 disabled:opacity-40"
            onClick={generateBotPlan}
            disabled={botPlanBusy}
          >
            {botPlanBusy ? 'Planning…' : 'Generate No-SQL Plan'}
          </button>
          {botPlanError && <p className="mt-2 text-xs text-dreamco-red">{botPlanError}</p>}
          {botPlan && (
            <div className="mt-3 rounded-lg border border-slate-700 bg-slate-900/40 p-3">
              <p className="text-xs text-white">
                Target: {botPlan.requested_bot}
                {botPlan.resolved_bot ? ` → ${botPlan.resolved_bot}` : ''}
              </p>
              <p className="text-xs text-slate-400 mt-1">Workflow: {botPlan.recommended_workflow}</p>
              <ul className="mt-2 list-disc list-inside text-xs text-slate-300 space-y-1">
                {(botPlan.no_sql_steps || []).map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-white mb-2">💳 API Charge Monitor + Approvals</h3>
          <p className="text-xs text-slate-500 mb-3">
            Preview costs first, inform users, and approve spending before any purchase or external API charge.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            <label className="block md:col-span-3">
              <span className="text-[11px] text-slate-500 uppercase">Description</span>
              <input
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={chargeDescription}
                onChange={(e) => setChargeDescription(e.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Units</span>
              <input
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={chargeUnits}
                onChange={(e) => setChargeUnits(e.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Unit Cost (USD)</span>
              <input
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={chargeUnitCost}
                onChange={(e) => setChargeUnitCost(e.target.value)}
              />
            </label>
            <button
              className="self-end px-3 py-2 rounded-lg text-xs font-semibold bg-dreamco-accent text-white hover:opacity-90 disabled:opacity-40"
              onClick={previewCharge}
              disabled={chargeBusy}
            >
              {chargeBusy ? 'Previewing…' : 'Preview Charge'}
            </button>
          </div>
          {chargeMessage && <p className="mt-2 text-xs text-green-300">{chargeMessage}</p>}
          {chargeError && <p className="mt-2 text-xs text-dreamco-red">{chargeError}</p>}
          <div className="mt-3 text-xs text-slate-300 space-y-1">
            <p>Budget: ${chargeData?.summary?.monthly_budget_usd ?? '—'}</p>
            <p>Approved: ${chargeData?.summary?.approved_total_usd ?? '—'}</p>
            <p>Pending: ${chargeData?.summary?.pending_total_usd ?? '—'}</p>
            <p>Projected: ${chargeData?.summary?.projected_total_usd ?? '—'}</p>
          </div>
          <div className="mt-3 rounded-lg border border-slate-700 bg-slate-900/40 p-3 max-h-44 overflow-y-auto">
            {(chargeData?.pending_approvals || []).length === 0 ? (
              <p className="text-xs text-slate-500">No pending charge approvals.</p>
            ) : (
              chargeData.pending_approvals.map((item) => (
                <div key={item.preview_id} className="mb-2 border-b border-slate-700 pb-2 last:border-b-0">
                  <p className="text-xs text-slate-200">{item.description}</p>
                  <p className="text-[11px] text-slate-400">
                    ${item.estimated_cost_usd} · {item.preview_id}
                  </p>
                  <button
                    className="mt-1 px-2 py-1 rounded text-[11px] bg-slate-700 text-slate-200 hover:text-white disabled:opacity-40"
                    onClick={() => approveCharge(item.preview_id)}
                    disabled={approveBusyId === item.preview_id}
                  >
                    {approveBusyId === item.preview_id ? 'Approving…' : 'Approve Charge'}
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-white mb-2">🛰️ Buddy Command Runner</h3>
          <p className="text-xs text-slate-500 mb-3">
            Call one bot or all bots, run validation depth checks, and view revenue signal guidance.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Run Mode</span>
              <select
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={commandRunMode}
                onChange={(e) => setCommandRunMode(e.target.value)}
              >
                <option value="single">Single Bot</option>
                <option value="all">All Bots</option>
              </select>
            </label>
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Target</span>
              <input
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={commandTarget}
                onChange={(e) => setCommandTarget(e.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-[11px] text-slate-500 uppercase">Validation</span>
              <select
                className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white"
                value={commandValidation}
                onChange={(e) => setCommandValidation(e.target.value)}
              >
                <option value="quick">Quick</option>
                <option value="standard">Standard</option>
                <option value="deep">Deep</option>
              </select>
            </label>
          </div>
          <button
            className="mt-2 px-3 py-2 rounded-lg text-xs font-semibold bg-dreamco-accent text-white hover:opacity-90 disabled:opacity-40"
            onClick={runBuddyCommand}
            disabled={commandBusy}
          >
            {commandBusy ? 'Running…' : 'Run Buddy Command'}
          </button>
          {commandError && <p className="mt-2 text-xs text-dreamco-red">{commandError}</p>}
          {commandResult && (
            <div className="mt-3 rounded-lg border border-slate-700 bg-slate-900/40 p-3 text-xs text-slate-300">
              <p className="text-white">{commandResult.buddy_message}</p>
              <p className="mt-1">Targets: {commandResult.target_count}</p>
              <p>Revenue signal: ${commandResult.total_revenue_signal_usd}</p>
              <ul className="mt-2 list-disc list-inside space-y-1">
                {(commandResult.results || []).map((item) => (
                  <li key={item.bot}>
                    {item.bot}: {item.validation_depth} · {item.status}
                  </li>
                ))}
              </ul>
            </div>
          )}
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
