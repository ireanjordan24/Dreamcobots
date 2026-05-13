import { useState } from 'react';

const PAYMENT_METHODS = [
  { id: 'stripe', name: 'Stripe', icon: '💳', status: 'connected', type: 'card' },
  { id: 'paypal', name: 'PayPal', icon: '🅿️', status: 'configured', type: 'wallet' },
  { id: 'crypto', name: 'Crypto Wallet', icon: '🪙', status: 'connected', type: 'crypto' },
  { id: 'ach', name: 'ACH Transfer', icon: '🏦', status: 'configured', type: 'bank' },
];

const TRANSACTIONS = [
  { id: 'p001', desc: 'BuddyOrchestrator Pro — Monthly', amount: '+$299.00', status: 'completed', date: 'May 12', type: 'revenue' },
  { id: 'p002', desc: 'MarketplaceBot Subscription', amount: '+$179.00', status: 'completed', date: 'May 11', type: 'revenue' },
  { id: 'p003', desc: 'OpenAI API Credits', amount: '-$84.50', status: 'completed', date: 'May 10', type: 'expense' },
  { id: 'p004', desc: 'DealAnalyzer Suite License', amount: '+$149.00', status: 'completed', date: 'May 9', type: 'revenue' },
  { id: 'p005', desc: 'AWS Infrastructure', amount: '-$210.00', status: 'completed', date: 'May 8', type: 'expense' },
  { id: 'p006', desc: 'White-Label Export Fee', amount: '+$500.00', status: 'pending', date: 'May 8', type: 'revenue' },
];

export default function Payments() {
  const [newAmount, setNewAmount] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [processing, setProcessing] = useState(false);
  const [msg, setMsg] = useState('');

  const totalRevenue = TRANSACTIONS.filter((t) => t.type === 'revenue').reduce((s, t) => s + parseFloat(t.amount.replace(/[$+,]/g, '')), 0);
  const totalExpense = TRANSACTIONS.filter((t) => t.type === 'expense').reduce((s, t) => s + parseFloat(t.amount.replace(/[$\-,]/g, '')), 0);

  async function sendPayment() {
    if (!newAmount || !newDesc) return;
    setProcessing(true);
    try {
      const res = await fetch('/api/payments/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: newAmount, description: newDesc }),
      });
      const data = await res.json();
      setMsg(data.message ?? 'Payment initiated!');
    } catch {
      setMsg('Payment failed — check connection.');
    } finally {
      setProcessing(false);
      setNewAmount('');
      setNewDesc('');
      setTimeout(() => setMsg(''), 4000);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">💳</span>
        <div>
          <h2 className="text-xl font-bold text-white">Payments</h2>
          <p className="text-xs text-slate-400">Payment processing, transactions &amp; revenue collection</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-5 border border-green-500/30">
          <div className="text-2xl font-bold text-green-400">${totalRevenue.toLocaleString()}</div>
          <div className="text-sm text-slate-300 mt-1">Revenue Collected</div>
          <div className="text-xs text-slate-500">this period</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-red-500/20">
          <div className="text-2xl font-bold text-red-400">${totalExpense.toLocaleString()}</div>
          <div className="text-sm text-slate-300 mt-1">Expenses</div>
          <div className="text-xs text-slate-500">this period</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <div className="text-2xl font-bold text-white">${(totalRevenue - totalExpense).toLocaleString()}</div>
          <div className="text-sm text-slate-300 mt-1">Net Balance</div>
          <div className="text-xs text-slate-500">this period</div>
        </div>
      </div>

      {/* Payment methods */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 p-5 mb-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">💳 Payment Methods</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {PAYMENT_METHODS.map((pm) => (
            <div key={pm.id} className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-slate-800/50 border border-slate-700">
              <span className="text-xl">{pm.icon}</span>
              <div>
                <div className="text-xs font-medium text-white">{pm.name}</div>
                <div className={`text-xs ${pm.status === 'connected' ? 'text-green-400' : 'text-yellow-400'}`}>{pm.status}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Initiate payment */}
      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mb-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">➕ Initiate Payment</h3>
        <div className="flex gap-3">
          <input
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
            placeholder="Description"
            className="flex-1 bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent"
          />
          <input
            value={newAmount}
            onChange={(e) => setNewAmount(e.target.value)}
            placeholder="Amount ($)"
            type="number"
            className="w-32 bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent"
          />
          <button
            onClick={sendPayment}
            disabled={processing || !newAmount || !newDesc}
            className="px-5 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-40 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            {processing ? 'Processing…' : 'Send'}
          </button>
        </div>
        {msg && <p className="mt-2 text-xs text-green-400">{msg}</p>}
      </div>

      {/* Transaction history */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">Transaction History</h3>
        </div>
        <div className="divide-y divide-slate-700/30">
          {TRANSACTIONS.map((tx) => (
            <div key={tx.id} className="px-5 py-3 flex items-center gap-4">
              <span className="text-slate-500 text-xs w-14">{tx.date}</span>
              <div className="flex-1 text-sm text-slate-300">{tx.desc}</div>
              <span className={`font-semibold text-sm ${tx.type === 'revenue' ? 'text-green-400' : 'text-red-400'}`}>
                {tx.amount}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-xs ${tx.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                {tx.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
