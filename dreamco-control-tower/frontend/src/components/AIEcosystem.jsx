import { useState } from 'react';

const ECOSYSTEM_NODES = [
  { id: 'core', name: 'Core Engine', emoji: '⚙️', type: 'core', desc: 'BuddyOrchestrator + BaseBot framework', connections: ['models', 'bots', 'data'], status: 'active' },
  { id: 'models', name: 'AI Models', emoji: '🧠', type: 'ai', desc: 'GPT-4o, Claude, Gemini, Llama', connections: ['bots', 'learning'], status: 'active' },
  { id: 'bots', name: 'Bot Fleet', emoji: '🤖', type: 'bots', desc: '40+ autonomous bots deployed', connections: ['revenue', 'marketplace'], status: 'active' },
  { id: 'data', name: 'Data Layer', emoji: '📊', type: 'data', desc: 'bots.json, analytics, heartbeat', connections: ['learning', 'dashboard'], status: 'active' },
  { id: 'learning', name: 'Deep Learning', emoji: '🎓', type: 'ai', desc: 'API scraper, competitor analysis, sandbox', connections: ['models', 'bots'], status: 'active' },
  { id: 'revenue', name: 'Revenue Engine', emoji: '💰', type: 'finance', desc: 'Payments, crypto, deal tracking', connections: ['marketplace'], status: 'active' },
  { id: 'marketplace', name: 'Marketplace', emoji: '🏪', type: 'commerce', desc: 'Bot listings, subscriptions, white-label', connections: ['revenue'], status: 'active' },
  { id: 'dashboard', name: 'Control Tower', emoji: '🏰', type: 'core', desc: 'This very interface you are using', connections: ['data', 'bots'], status: 'active' },
];

const TYPE_COLOR = {
  core: 'border-blue-500/50 bg-blue-500/10',
  ai: 'border-purple-500/50 bg-purple-500/10',
  bots: 'border-dreamco-accent/50 bg-dreamco-accent/10',
  data: 'border-cyan-500/50 bg-cyan-500/10',
  finance: 'border-green-500/50 bg-green-500/10',
  commerce: 'border-yellow-500/50 bg-yellow-500/10',
};

const INTEGRATIONS = [
  { name: 'GitHub Actions', status: 'connected', icon: '🐙' },
  { name: 'Stripe Payments', status: 'connected', icon: '💳' },
  { name: 'OpenAI API', status: 'connected', icon: '🤖' },
  { name: 'Anthropic API', status: 'connected', icon: '🧬' },
  { name: 'Replit', status: 'connected', icon: '🖥️' },
  { name: 'Slack Webhooks', status: 'configured', icon: '💬' },
  { name: 'Discord Bot', status: 'configured', icon: '🎮' },
  { name: 'CoinGecko API', status: 'connected', icon: '🪙' },
];

export default function AIEcosystem() {
  const [selected, setSelected] = useState(null);
  const node = ECOSYSTEM_NODES.find((n) => n.id === selected);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🌐</span>
        <div>
          <h2 className="text-xl font-bold text-white">AI Ecosystem</h2>
          <p className="text-xs text-slate-400">Full view of your interconnected AI systems and integrations</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {ECOSYSTEM_NODES.map((n) => (
          <button
            key={n.id}
            onClick={() => setSelected(selected === n.id ? null : n.id)}
            className={`text-left rounded-xl p-4 border transition-all hover:scale-[1.02] ${selected === n.id ? 'ring-2 ring-dreamco-accent' : ''} ${TYPE_COLOR[n.type] ?? 'border-slate-700 bg-dreamco-card'}`}
          >
            <div className="text-2xl mb-2">{n.emoji}</div>
            <div className="font-semibold text-white text-sm mb-1">{n.name}</div>
            <div className="text-xs text-slate-400 leading-tight">{n.desc}</div>
            <div className="mt-2 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
              <span className="text-xs text-green-400">{n.status}</span>
            </div>
          </button>
        ))}
      </div>

      {node && (
        <div className="bg-dreamco-card rounded-xl border border-dreamco-accent/30 p-5 mb-6">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-2xl">{node.emoji}</span>
            <h3 className="text-lg font-bold text-white">{node.name}</h3>
          </div>
          <p className="text-sm text-slate-300 mb-3">{node.desc}</p>
          <div className="flex gap-2 flex-wrap">
            <span className="text-xs text-slate-400 mr-1">Connected to:</span>
            {node.connections.map((c) => {
              const cn = ECOSYSTEM_NODES.find((x) => x.id === c);
              return cn ? (
                <span key={c} className="px-2 py-0.5 bg-slate-700 rounded-full text-xs text-slate-300">
                  {cn.emoji} {cn.name}
                </span>
              ) : null;
            })}
          </div>
        </div>
      )}

      <div className="bg-dreamco-card rounded-xl border border-slate-700 p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">🔌 External Integrations</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {INTEGRATIONS.map((int) => (
            <div key={int.name} className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700">
              <span className="text-xl">{int.icon}</span>
              <div>
                <div className="text-xs font-medium text-white">{int.name}</div>
                <div className={`text-xs ${int.status === 'connected' ? 'text-green-400' : 'text-yellow-400'}`}>{int.status}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
