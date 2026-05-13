import { useState } from 'react';

const CAPSULES = [
  { id: 'tc1', title: 'Empire Launch Day', date: '2024-01-15', type: 'milestone', emoji: '🚀', summary: '1 bot deployed, 0 revenue, 1 founder. The beginning.', bots: 1, revenue: '$0', unlockDate: null },
  { id: 'tc2', title: 'First $10k Month', date: '2024-04-02', type: 'revenue', emoji: '💰', summary: 'Crossed $10,000 MRR milestone. 8 bots active, 3 paying customers.', bots: 8, revenue: '$10,200', unlockDate: null },
  { id: 'tc3', title: 'Bot Fleet at 25', date: '2024-07-20', type: 'milestone', emoji: '🤖', summary: '25 bots deployed. System uptime 99.1%. ELITE tier launched.', bots: 25, revenue: '$64,000', unlockDate: null },
  { id: 'tc4', title: 'Q4 2024 Snapshot', date: '2024-12-31', type: 'snapshot', emoji: '📸', summary: 'Year-end review: 38 bots, $162k MRR, 5 divisions, 12 enterprise clients.', bots: 38, revenue: '$162,000', unlockDate: null },
  { id: 'tc5', title: 'Future Goals: $1M MRR', date: '2025-12-31', type: 'future', emoji: '🔮', summary: 'To the future us: Did we hit $1M MRR? Deploy 100 bots? Reach 1,000 customers?', bots: null, revenue: null, unlockDate: '2025-12-31', locked: true },
];

const TYPE_COLOR = {
  milestone: 'border-yellow-500/40 bg-yellow-500/5',
  revenue: 'border-green-500/40 bg-green-500/5',
  snapshot: 'border-blue-500/40 bg-blue-500/5',
  future: 'border-purple-500/40 bg-purple-500/5',
};

export default function TimeCapsule() {
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ title: '', summary: '', unlockDate: '' });
  const [capsules, setCapsules] = useState(CAPSULES);
  const [saved, setSaved] = useState(false);

  function saveCapsule() {
    if (!form.title || !form.summary) return;
    const newCapsule = {
      id: `tc${capsules.length + 1}`,
      title: form.title,
      date: new Date().toISOString().split('T')[0],
      type: form.unlockDate ? 'future' : 'snapshot',
      emoji: form.unlockDate ? '🔮' : '📸',
      summary: form.summary,
      bots: null,
      revenue: null,
      unlockDate: form.unlockDate || null,
      locked: !!form.unlockDate,
    };
    setCapsules((prev) => [newCapsule, ...prev]);
    setForm({ title: '', summary: '', unlockDate: '' });
    setCreating(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">⏳</span>
        <div>
          <h2 className="text-xl font-bold text-white">Time Capsule</h2>
          <p className="text-xs text-slate-400">Archive milestones, snapshots &amp; messages to your future empire</p>
        </div>
        <button
          onClick={() => setCreating(!creating)}
          className="ml-auto px-4 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-sm rounded-lg transition-colors"
        >
          + Create Capsule
        </button>
      </div>

      {saved && (
        <div className="mb-4 px-4 py-3 bg-green-500/20 border border-green-500/30 rounded-xl text-green-400 text-sm">
          ✅ Time capsule sealed and saved!
        </div>
      )}

      {creating && (
        <div className="bg-dreamco-card rounded-xl border border-dreamco-accent/30 p-6 mb-6">
          <h3 className="text-sm font-semibold text-white mb-4">📦 Seal New Time Capsule</h3>
          <div className="space-y-3">
            <input
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              placeholder="Title (e.g. 'First $500k Month')"
              className="w-full bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent"
            />
            <textarea
              rows={3}
              value={form.summary}
              onChange={(e) => setForm((f) => ({ ...f, summary: e.target.value }))}
              placeholder="What do you want to remember? What are your hopes for the future?"
              className="w-full bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent resize-none"
            />
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <label className="block text-xs text-slate-400 mb-1">Unlock Date (for future capsules)</label>
                <input
                  type="date"
                  value={form.unlockDate}
                  onChange={(e) => setForm((f) => ({ ...f, unlockDate: e.target.value }))}
                  className="w-full bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent"
                />
              </div>
              <button
                onClick={saveCapsule}
                disabled={!form.title || !form.summary}
                className="px-6 py-2 bg-dreamco-accent hover:bg-indigo-500 disabled:opacity-40 text-white text-sm font-semibold rounded-lg transition-colors mt-5"
              >
                Seal
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-700" />

        <div className="space-y-4 pl-16">
          {capsules.map((c) => (
            <div key={c.id} className={`relative bg-dreamco-card rounded-xl border p-5 ${TYPE_COLOR[c.type] ?? 'border-slate-700'} ${c.locked ? 'opacity-60' : ''}`}>
              {/* Timeline dot */}
              <div className="absolute -left-10 top-6 w-4 h-4 rounded-full bg-slate-700 border-2 border-dreamco-accent flex items-center justify-center">
                <span className="text-xs">{c.emoji}</span>
              </div>

              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="font-semibold text-white">{c.locked ? '🔒 ' : ''}{c.title}</div>
                  <div className="text-xs text-slate-400">{c.date}{c.unlockDate ? ` · Unlocks: ${c.unlockDate}` : ''}</div>
                </div>
                <span className="text-xs px-2 py-0.5 bg-slate-700 rounded-full text-slate-400 capitalize">{c.type}</span>
              </div>

              <p className="text-sm text-slate-300 mb-3">{c.locked ? '[Sealed until unlock date]' : c.summary}</p>

              {!c.locked && (c.bots !== null || c.revenue !== null) && (
                <div className="flex gap-4 text-xs">
                  {c.bots !== null && <span className="text-slate-400">🤖 {c.bots} bots</span>}
                  {c.revenue !== null && <span className="text-green-400 font-semibold">{c.revenue} MRR</span>}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
