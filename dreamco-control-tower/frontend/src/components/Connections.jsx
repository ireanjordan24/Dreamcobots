import { useState } from 'react';

const CONNECTIONS = [
  { id: 'github', name: 'GitHub', icon: '🐙', category: 'Dev', status: 'connected', desc: 'Repository webhooks, Actions, CI/CD', features: ['Webhooks', 'Actions dispatch', 'PR monitoring'] },
  { id: 'stripe', name: 'Stripe', icon: '💳', category: 'Payments', status: 'connected', desc: 'Payment processing and subscription management', features: ['Payments', 'Subscriptions', 'Invoicing'] },
  { id: 'openai', name: 'OpenAI', icon: '🤖', category: 'AI', status: 'connected', desc: 'GPT-4o, Whisper, DALL-E', features: ['Chat', 'Embeddings', 'Vision'] },
  { id: 'anthropic', name: 'Anthropic', icon: '🧬', category: 'AI', status: 'connected', desc: 'Claude 3 Sonnet & Haiku', features: ['Chat', 'Analysis'] },
  { id: 'replit', name: 'Replit', icon: '🖥️', category: 'Dev', status: 'connected', desc: 'Live code environment and deployment', features: ['Live preview', 'Deploy', 'Collaborate'] },
  { id: 'slack', name: 'Slack', icon: '💬', category: 'Alerts', status: 'configured', desc: 'Team notifications and bot alerts', features: ['Webhooks', 'Commands'] },
  { id: 'discord', name: 'Discord', icon: '🎮', category: 'Community', status: 'configured', desc: 'Community bot and server management', features: ['Bot commands', 'Notifications'] },
  { id: 'coingecko', name: 'CoinGecko', icon: '🦎', category: 'Crypto', status: 'connected', desc: 'Crypto price data and market metrics', features: ['Prices', 'Market cap', 'Trends'] },
  { id: 'aws', name: 'AWS', icon: '☁️', category: 'Infrastructure', status: 'connected', desc: 'Cloud hosting and serverless functions', features: ['EC2', 'Lambda', 'S3', 'RDS'] },
  { id: 'mongodb', name: 'MongoDB', icon: '🍃', category: 'Database', status: 'configured', desc: 'NoSQL database for bot data', features: ['Atlas', 'Queries', 'Aggregation'] },
  { id: 'twilio', name: 'Twilio', icon: '📱', category: 'Comms', status: 'disconnected', desc: 'SMS and voice automation', features: ['SMS', 'Voice', 'WhatsApp'] },
  { id: 'zapier', name: 'Zapier', icon: '⚡', category: 'Automation', status: 'disconnected', desc: '5000+ app integrations via Zapier', features: ['Zaps', 'Webhooks'] },
];

const STATUS_CONFIG = {
  connected: { badge: 'bg-green-500/20 text-green-400', dot: 'bg-green-400' },
  configured: { badge: 'bg-yellow-500/20 text-yellow-400', dot: 'bg-yellow-400' },
  disconnected: { badge: 'bg-slate-600 text-slate-400', dot: 'bg-slate-500' },
};

const CATS = ['All', 'AI', 'Dev', 'Payments', 'Crypto', 'Alerts', 'Infrastructure', 'Database', 'Comms', 'Automation', 'Community'];

export default function Connections() {
  const [cat, setCat] = useState('All');
  const [search, setSearch] = useState('');

  const visible = CONNECTIONS.filter((c) => {
    const matchCat = cat === 'All' || c.category === cat;
    const matchSearch = !search || c.name.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  const connectedCount = CONNECTIONS.filter((c) => c.status === 'connected').length;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🔌</span>
        <div>
          <h2 className="text-xl font-bold text-white">Connections</h2>
          <p className="text-xs text-slate-400">Manage all external integrations and API connections</p>
        </div>
        <button className="ml-auto px-4 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-sm rounded-lg transition-colors">
          + Add Connection
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-green-400">{connectedCount}</div>
          <div className="text-xs text-slate-400 mt-1">Connected</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-yellow-400">{CONNECTIONS.filter((c) => c.status === 'configured').length}</div>
          <div className="text-xs text-slate-400 mt-1">Configured</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-slate-400">{CONNECTIONS.filter((c) => c.status === 'disconnected').length}</div>
          <div className="text-xs text-slate-400 mt-1">Available</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-5">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search connections…"
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        />
        <div className="flex gap-1 flex-wrap">
          {CATS.map((c) => (
            <button
              key={c}
              onClick={() => setCat(c)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${cat === c ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visible.map((conn) => {
          const sc = STATUS_CONFIG[conn.status];
          return (
            <div key={conn.id} className="bg-dreamco-card rounded-xl p-5 border border-slate-700 hover:border-slate-500 transition-all">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">{conn.icon}</span>
                <div className="flex-1">
                  <div className="font-semibold text-white">{conn.name}</div>
                  <div className="text-xs text-slate-400">{conn.category}</div>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${sc.badge}`}>
                  {conn.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 mb-3 leading-relaxed">{conn.desc}</p>
              <div className="flex gap-1 flex-wrap mb-3">
                {conn.features.map((f) => (
                  <span key={f} className="px-1.5 py-0.5 bg-slate-700 rounded text-xs text-slate-300">{f}</span>
                ))}
              </div>
              <div className="flex gap-2">
                {conn.status === 'connected' ? (
                  <>
                    <button className="flex-1 py-1.5 text-xs rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors">Configure</button>
                    <button className="flex-1 py-1.5 text-xs rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors">Disconnect</button>
                  </>
                ) : conn.status === 'configured' ? (
                  <button className="flex-1 py-1.5 text-xs rounded-lg bg-green-600 hover:bg-green-500 text-white transition-colors">Activate</button>
                ) : (
                  <button className="flex-1 py-1.5 text-xs rounded-lg bg-dreamco-accent hover:bg-indigo-500 text-white transition-colors">Connect</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
