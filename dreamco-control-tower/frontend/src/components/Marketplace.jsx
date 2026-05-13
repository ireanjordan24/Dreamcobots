import { useState } from 'react';

const LISTINGS = [
  { id: 'm1', name: 'BuddyOrchestrator Pro', category: 'Command', price: '$299/mo', rating: 4.9, downloads: 1240, desc: 'Full autonomous orchestration with revenue tracking', badge: 'BEST SELLER' },
  { id: 'm2', name: 'DealAnalyzer Suite', category: 'Finance', price: '$149/mo', rating: 4.8, downloads: 890, desc: 'AI-powered deal scoring and risk assessment', badge: 'NEW' },
  { id: 'm3', name: 'RevenueEngine Bot', category: 'Revenue', price: '$199/mo', rating: 4.7, downloads: 760, desc: 'Automated revenue forecasting and optimization', badge: '' },
  { id: 'm4', name: 'CryptoSentinel', category: 'Crypto', price: '$99/mo', rating: 4.6, downloads: 640, desc: 'Real-time crypto tracking and alert system', badge: '' },
  { id: 'm5', name: 'MarketplaceBot', category: 'Commerce', price: '$179/mo', rating: 4.8, downloads: 540, desc: 'Full e-commerce automation with Stripe integration', badge: '' },
  { id: 'm6', name: 'DebugIntel Pro', category: 'DevOps', price: '$79/mo', rating: 4.5, downloads: 410, desc: 'Intelligent error detection and self-healing', badge: '' },
  { id: 'm7', name: 'CodeLab Assistant', category: 'Dev', price: 'FREE', rating: 4.4, downloads: 2100, desc: 'Code generation, review, and testing automation', badge: 'FREE' },
  { id: 'm8', name: 'BizLaunch Starter', category: 'Business', price: '$49/mo', rating: 4.6, downloads: 320, desc: 'Full business launch automation in one bot', badge: '' },
];

const CATS = ['All', 'Command', 'Finance', 'Revenue', 'Crypto', 'Commerce', 'DevOps', 'Dev', 'Business'];

function Stars({ rating }) {
  return (
    <span className="text-yellow-400 text-xs">
      {'★'.repeat(Math.round(rating))}{'☆'.repeat(5 - Math.round(rating))} {rating}
    </span>
  );
}

export default function Marketplace() {
  const [cat, setCat] = useState('All');
  const [search, setSearch] = useState('');

  const visible = LISTINGS.filter((l) => {
    const matchCat = cat === 'All' || l.category === cat;
    const matchSearch = !search || l.name.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🏪</span>
        <div>
          <h2 className="text-xl font-bold text-white">Marketplace</h2>
          <p className="text-xs text-slate-400">Deploy, license, and monetize DreamCo bots</p>
        </div>
        <button className="ml-auto px-4 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-sm rounded-lg transition-colors">
          + List Bot
        </button>
      </div>

      <div className="flex flex-wrap gap-3 mb-5">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search marketplace…"
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        />
        <div className="flex gap-1 flex-wrap">
          {CATS.map((c) => (
            <button
              key={c}
              onClick={() => setCat(c)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${cat === c ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
            >
              {c}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-400 self-center">{visible.length} listings</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visible.map((item) => (
          <div key={item.id} className="bg-dreamco-card rounded-xl p-5 border border-slate-700 hover:border-dreamco-accent/50 transition-all">
            <div className="flex items-start justify-between mb-3">
              <div>
                <span className="text-xs px-2 py-0.5 bg-slate-700 text-slate-400 rounded-full">{item.category}</span>
                {item.badge && (
                  <span className="ml-2 text-xs px-2 py-0.5 bg-dreamco-accent/20 text-dreamco-accent rounded-full font-bold">
                    {item.badge}
                  </span>
                )}
              </div>
              <span className={`font-bold text-sm ${item.price === 'FREE' ? 'text-green-400' : 'text-white'}`}>
                {item.price}
              </span>
            </div>
            <h3 className="font-semibold text-white mb-1">{item.name}</h3>
            <p className="text-xs text-slate-400 mb-3 leading-relaxed">{item.desc}</p>
            <div className="flex items-center justify-between mb-3">
              <Stars rating={item.rating} />
              <span className="text-xs text-slate-500">{item.downloads.toLocaleString()} installs</span>
            </div>
            <div className="flex gap-2">
              <button className="flex-1 px-3 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors">
                {item.price === 'FREE' ? 'Install Free' : 'Subscribe'}
              </button>
              <button className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs rounded-lg transition-colors">
                Preview
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
