import { useEffect, useState } from 'react';

const STATUS_COLOR = { active: 'text-green-400', idle: 'text-slate-400', error: 'text-red-400', deploying: 'text-yellow-400' };
const STATUS_DOT = { active: 'bg-green-400', idle: 'bg-slate-500', error: 'bg-red-400', deploying: 'bg-yellow-400' };

export default function BotFleet() {
  const [bots, setBots] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(new Set());

  useEffect(() => {
    fetch('/api/bots')
      .then((r) => r.json())
      .then((data) => { setBots(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const visible = filter === 'all' ? bots : bots.filter((b) => b.status === filter);

  function toggleSelect(name) {
    setSelected((prev) => {
      const n = new Set(prev);
      n.has(name) ? n.delete(name) : n.add(name);
      return n;
    });
  }

  function selectAll() {
    setSelected(selected.size === visible.length ? new Set() : new Set(visible.map((b) => b.name)));
  }

  if (loading) return <p className="text-slate-400">Loading fleet…</p>;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🚀</span>
        <div>
          <h2 className="text-xl font-bold text-white">Bot Fleet</h2>
          <p className="text-xs text-slate-400">Manage, deploy, and monitor your entire bot fleet</p>
        </div>
        <div className="ml-auto flex gap-2">
          <span className="text-xs text-slate-400 self-center">{bots.length} total bots</span>
        </div>
      </div>

      {/* Fleet summary */}
      <div className="grid grid-cols-4 gap-3 mb-5">
        {['active', 'idle', 'error', 'deploying'].map((s) => {
          const count = bots.filter((b) => b.status === s).length;
          return (
            <button
              key={s}
              onClick={() => setFilter(filter === s ? 'all' : s)}
              className={`bg-dreamco-card rounded-xl p-4 border transition-all ${filter === s ? 'border-dreamco-accent' : 'border-slate-700'}`}
            >
              <div className={`text-xl font-bold ${STATUS_COLOR[s]}`}>{count}</div>
              <div className="text-xs text-slate-400 capitalize">{s}</div>
            </button>
          );
        })}
      </div>

      {/* Bulk actions */}
      {selected.size > 0 && (
        <div className="bg-dreamco-accent/10 border border-dreamco-accent/30 rounded-xl px-5 py-3 mb-4 flex items-center gap-4">
          <span className="text-sm text-white">{selected.size} bot(s) selected</span>
          {['Restart', 'Pause', 'Update', 'Remove'].map((a) => (
            <button
              key={a}
              className="px-3 py-1.5 rounded-lg bg-dreamco-accent hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
            >
              {a}
            </button>
          ))}
        </div>
      )}

      {/* Fleet table */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700 flex items-center gap-3">
          <input type="checkbox" checked={selected.size === visible.length && visible.length > 0} onChange={selectAll} className="rounded" />
          <h3 className="text-sm font-semibold text-slate-300">Fleet Registry</h3>
          <div className="ml-auto flex gap-2">
            {['all', 'active', 'idle', 'error'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2 py-0.5 rounded text-xs transition-colors ${filter === f ? 'bg-dreamco-accent text-white' : 'text-slate-400 hover:text-white'}`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
        <div className="divide-y divide-slate-700/30 max-h-96 overflow-y-auto">
          {visible.map((bot) => (
            <div
              key={bot.name}
              className="px-5 py-3 flex items-center gap-4 hover:bg-slate-700/20 transition-colors"
            >
              <input
                type="checkbox"
                checked={selected.has(bot.name)}
                onChange={() => toggleSelect(bot.name)}
                className="rounded"
              />
              <div className={`w-2 h-2 rounded-full shrink-0 ${STATUS_DOT[bot.status] ?? 'bg-slate-500'}`} />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-white text-sm truncate">{bot.name}</div>
                <div className="text-xs text-slate-400">{bot.team ?? 'unassigned'} · {bot.tier ?? 'FREE'}</div>
              </div>
              <span className={`text-xs font-medium ${STATUS_COLOR[bot.status] ?? 'text-slate-400'}`}>
                {bot.status}
              </span>
              <div className="flex gap-1">
                {['Restart', 'Logs', 'Config'].map((a) => (
                  <button
                    key={a}
                    className="px-2 py-1 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
                  >
                    {a}
                  </button>
                ))}
              </div>
            </div>
          ))}
          {visible.length === 0 && (
            <p className="px-5 py-6 text-slate-500 text-sm">No bots in this category.</p>
          )}
        </div>
      </div>
    </div>
  );
}
