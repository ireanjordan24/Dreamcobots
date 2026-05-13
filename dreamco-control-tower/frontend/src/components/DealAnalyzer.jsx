import { useState } from 'react';

const SAMPLE_DEALS = [
  { id: 'D001', name: 'SaaS Platform Acquisition', type: 'Acquisition', value: '$850,000', score: 87, risk: 'medium', status: 'analyzing' },
  { id: 'D002', name: 'API Integration Partnership', type: 'Partnership', value: '$120,000', score: 94, risk: 'low', status: 'approved' },
  { id: 'D003', name: 'Bot White-Label License', type: 'License', value: '$45,000', score: 91, risk: 'low', status: 'approved' },
  { id: 'D004', name: 'Enterprise Bot Fleet Contract', type: 'Contract', value: '$2,400,000', score: 73, risk: 'high', status: 'review' },
  { id: 'D005', name: 'Crypto Yield Fund Entry', type: 'Investment', value: '$500,000', score: 68, risk: 'high', status: 'review' },
];

const RISK_COLOR = { low: 'text-green-400', medium: 'text-yellow-400', high: 'text-red-400' };
const STATUS_COLOR = { approved: 'bg-green-500/20 text-green-400', analyzing: 'bg-blue-500/20 text-blue-400', review: 'bg-yellow-500/20 text-yellow-400' };

function ScoreBar({ score }) {
  const color = score >= 85 ? 'bg-green-500' : score >= 70 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-700 rounded-full h-1.5">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs font-bold text-white w-6">{score}</span>
    </div>
  );
}

export default function DealAnalyzer() {
  const [deals, setDeals] = useState(SAMPLE_DEALS);
  const [analyzing, setAnalyzing] = useState(null);
  const [newDeal, setNewDeal] = useState('');

  async function analyzeDeal() {
    if (!newDeal.trim()) return;
    const id = `D00${deals.length + 1}`;
    setAnalyzing(id);
    try {
      const res = await fetch('/api/deal-analyzer/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: newDeal }),
      });
      const data = await res.json();
      setDeals((prev) => [{ id, name: newDeal, type: data.type ?? 'Unknown', value: data.value ?? 'TBD', score: data.score ?? 75, risk: data.risk ?? 'medium', status: 'analyzing' }, ...prev]);
    } catch {
      setDeals((prev) => [{ id, name: newDeal, type: 'Unknown', value: 'TBD', score: 75, risk: 'medium', status: 'analyzing' }, ...prev]);
    } finally {
      setAnalyzing(null);
      setNewDeal('');
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🔍</span>
        <div>
          <h2 className="text-xl font-bold text-white">Deal Analyzer</h2>
          <p className="text-xs text-slate-400">AI-powered deal scoring, risk assessment &amp; opportunity ranking</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-white">{deals.length}</div>
          <div className="text-sm text-slate-300 mt-1">Total Deals</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-green-400">{deals.filter((d) => d.status === 'approved').length}</div>
          <div className="text-sm text-slate-300 mt-1">Approved</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-yellow-400">{deals.filter((d) => d.status === 'review').length}</div>
          <div className="text-sm text-slate-300 mt-1">Under Review</div>
        </div>
      </div>

      {/* New deal input */}
      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mb-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">🤖 AI Deal Analyzer</h3>
        <div className="flex gap-3">
          <input
            value={newDeal}
            onChange={(e) => setNewDeal(e.target.value)}
            placeholder="Describe a deal to analyze (e.g. 'Acquire SaaS tool for $500k')"
            className="flex-1 bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent"
          />
          <button
            onClick={analyzeDeal}
            disabled={!!analyzing || !newDeal.trim()}
            className="px-5 py-2 bg-dreamco-accent hover:bg-indigo-500 disabled:opacity-40 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            {analyzing ? 'Analyzing…' : 'Analyze'}
          </button>
        </div>
      </div>

      {/* Deals table */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">Deal Pipeline</h3>
        </div>
        <div className="divide-y divide-slate-700/30">
          {deals.map((deal) => (
            <div key={deal.id} className="px-5 py-4 flex items-center gap-4">
              <span className="text-xs text-slate-500 w-12">{deal.id}</span>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-white text-sm truncate">{deal.name}</div>
                <div className="text-xs text-slate-400">{deal.type} · Risk: <span className={RISK_COLOR[deal.risk]}>{deal.risk}</span></div>
              </div>
              <div className="w-32">
                <ScoreBar score={deal.score} />
              </div>
              <span className="text-green-400 font-semibold text-sm w-28 text-right">{deal.value}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOR[deal.status] ?? 'bg-slate-600 text-slate-400'}`}>
                {deal.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
