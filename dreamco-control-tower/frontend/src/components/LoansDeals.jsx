import { useState } from 'react';

const LOANS = [
  { id: 'L001', name: 'SBA Bot Infrastructure Loan', type: 'SBA', amount: '$250,000', rate: '6.5%', term: '60 months', status: 'active', balance: '$187,400', monthly: '$4,850' },
  { id: 'L002', name: 'AI Equipment Line of Credit', type: 'LOC', amount: '$100,000', rate: '8.9%', term: 'Revolving', status: 'active', balance: '$32,000', monthly: '$2,400' },
  { id: 'L003', name: 'Startup Growth Capital', type: 'VC', amount: '$500,000', rate: 'Equity 4%', term: 'N/A', status: 'approved', balance: '$500,000', monthly: 'N/A' },
];

const ACTIVE_DEALS = [
  { id: 'AD001', name: 'Bot Fleet Expansion — Phase 2', value: '$320,000', stage: 'Negotiating', close: 'May 30', probability: '75%' },
  { id: 'AD002', name: 'Enterprise White-Label Contract', value: '$1,200,000', stage: 'Due Diligence', close: 'Jun 15', probability: '60%' },
  { id: 'AD003', name: 'API Partnership — TechCorp', value: '$84,000', stage: 'Contract Review', close: 'May 20', probability: '90%' },
  { id: 'AD004', name: 'SaaS Acquisition Target', value: '$2,800,000', stage: 'Initial Contact', close: 'Jul 1', probability: '35%' },
];

const PROB_COLOR = (p) => {
  const n = parseInt(p);
  return n >= 80 ? 'text-green-400' : n >= 60 ? 'text-yellow-400' : 'text-red-400';
};

export default function LoansDeals() {
  const [tab, setTab] = useState('loans');

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🤝</span>
        <div>
          <h2 className="text-xl font-bold text-white">Loans &amp; Deals</h2>
          <p className="text-xs text-slate-400">Manage financing, active deals, and business development pipeline</p>
        </div>
        <button className="ml-auto px-4 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-sm rounded-lg transition-colors">
          + New Deal
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <div className="text-2xl font-bold text-white">3</div>
          <div className="text-sm text-slate-300 mt-1">Active Loans</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <div className="text-2xl font-bold text-red-400">$219.4k</div>
          <div className="text-sm text-slate-300 mt-1">Total Debt</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <div className="text-2xl font-bold text-green-400">$4.4M</div>
          <div className="text-sm text-slate-300 mt-1">Pipeline Value</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700">
          <div className="text-2xl font-bold text-dreamco-accent">4</div>
          <div className="text-sm text-slate-300 mt-1">Active Deals</div>
        </div>
      </div>

      {/* Tab selector */}
      <div className="flex gap-2 mb-5">
        {['loans', 'deals'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${tab === t ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
          >
            {t === 'loans' ? '🏦 Loans' : '🤝 Deals'}
          </button>
        ))}
      </div>

      {tab === 'loans' && (
        <div className="space-y-4">
          {LOANS.map((loan) => (
            <div key={loan.id} className="bg-dreamco-card rounded-xl border border-slate-700 p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="font-semibold text-white">{loan.name}</div>
                  <div className="text-xs text-slate-400">{loan.type} · {loan.rate} · {loan.term}</div>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${loan.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'}`}>
                  {loan.status}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div><div className="text-xs text-slate-400">Total Amount</div><div className="font-semibold text-white">{loan.amount}</div></div>
                <div><div className="text-xs text-slate-400">Remaining Balance</div><div className="font-semibold text-red-400">{loan.balance}</div></div>
                <div><div className="text-xs text-slate-400">Monthly Payment</div><div className="font-semibold text-slate-200">{loan.monthly}</div></div>
              </div>
            </div>
          ))}
          <button className="w-full py-3 rounded-xl border-2 border-dashed border-slate-700 text-slate-400 hover:border-dreamco-accent hover:text-dreamco-accent transition-colors text-sm">
            + Apply for New Loan
          </button>
        </div>
      )}

      {tab === 'deals' && (
        <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
          <div className="divide-y divide-slate-700/30">
            {ACTIVE_DEALS.map((deal) => (
              <div key={deal.id} className="px-5 py-4 flex items-center gap-4">
                <div className="flex-1">
                  <div className="font-medium text-white text-sm">{deal.name}</div>
                  <div className="text-xs text-slate-400">Stage: {deal.stage} · Close: {deal.close}</div>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-semibold text-sm">{deal.value}</div>
                  <div className={`text-xs font-medium ${PROB_COLOR(deal.probability)}`}>{deal.probability} prob.</div>
                </div>
                <div className="flex gap-1">
                  {['View', 'Edit', 'Close'].map((a) => (
                    <button key={a} className="px-2 py-1 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors">{a}</button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
