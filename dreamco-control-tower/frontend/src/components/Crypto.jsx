import { useEffect, useState } from 'react';

const COINS = [
  { symbol: 'BTC', name: 'Bitcoin', price: '$67,420', change: '+2.4%', up: true, balance: '0.12 BTC', value: '$8,090' },
  { symbol: 'ETH', name: 'Ethereum', price: '$3,820', change: '+3.1%', up: true, balance: '2.5 ETH', value: '$9,550' },
  { symbol: 'SOL', name: 'Solana', price: '$182', change: '-1.2%', up: false, balance: '45 SOL', value: '$8,190' },
  { symbol: 'BNB', name: 'BNB', price: '$598', change: '+0.8%', up: true, balance: '8 BNB', value: '$4,784' },
  { symbol: 'USDC', name: 'USD Coin', price: '$1.00', change: '0.0%', up: true, balance: '5,000 USDC', value: '$5,000' },
];

const TRANSACTIONS = [
  { id: 'tx1', type: 'receive', asset: 'ETH', amount: '+0.5 ETH', value: '$1,910', time: '10m ago', from: '0x1a2b…' },
  { id: 'tx2', type: 'send', asset: 'BTC', amount: '-0.01 BTC', value: '$674', time: '2h ago', to: '0x3c4d…' },
  { id: 'tx3', type: 'swap', asset: 'SOL→USDC', amount: '10 SOL', value: '$1,820', time: '5h ago', from: 'DeFi swap' },
  { id: 'tx4', type: 'receive', asset: 'USDC', amount: '+2,500 USDC', value: '$2,500', time: '1d ago', from: 'Stripe payout' },
];

export default function Crypto() {
  const [portfolio, setPortfolio] = useState(COINS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/crypto/portfolio')
      .then((r) => r.json())
      .then((d) => { if (d?.coins) setPortfolio(d.coins); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const totalValue = portfolio.reduce((sum, c) => sum + parseFloat(c.value.replace(/[$,]/g, '')), 0);

  if (loading) return <p className="text-slate-400">Loading crypto data…</p>;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🪙</span>
        <div>
          <h2 className="text-xl font-bold text-white">Crypto</h2>
          <p className="text-xs text-slate-400">Portfolio tracking, transactions &amp; DeFi integration</p>
        </div>
        <div className="ml-auto text-right">
          <div className="text-2xl font-bold text-white">${totalValue.toLocaleString()}</div>
          <div className="text-xs text-slate-400">Portfolio Value</div>
        </div>
      </div>

      {/* Portfolio table */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden mb-6">
        <div className="px-5 py-3 border-b border-slate-700 flex justify-between items-center">
          <h3 className="text-sm font-semibold text-slate-300">Portfolio Holdings</h3>
          <div className="flex gap-2">
            {['Buy', 'Sell', 'Swap'].map((a) => (
              <button
                key={a}
                className="px-3 py-1 bg-dreamco-accent hover:bg-indigo-500 text-white text-xs font-medium rounded transition-colors"
              >
                {a}
              </button>
            ))}
          </div>
        </div>
        <div className="divide-y divide-slate-700/30">
          {portfolio.map((coin) => (
            <div key={coin.symbol} className="px-5 py-4 flex items-center gap-4">
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm font-bold text-white">
                {coin.symbol[0]}
              </div>
              <div className="flex-1">
                <div className="font-medium text-white text-sm">{coin.name}</div>
                <div className="text-xs text-slate-400">{coin.symbol}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-white font-medium">{coin.price}</div>
                <div className={`text-xs font-medium ${coin.up ? 'text-green-400' : 'text-red-400'}`}>{coin.change}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-white">{coin.balance}</div>
                <div className="text-xs text-slate-400">{coin.value}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent transactions */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">Recent Transactions</h3>
        </div>
        <div className="divide-y divide-slate-700/30">
          {TRANSACTIONS.map((tx) => (
            <div key={tx.id} className="px-5 py-4 flex items-center gap-4">
              <span className={`text-xl ${tx.type === 'receive' ? '⬇️' : tx.type === 'send' ? '⬆️' : '🔄'}`}>
                {tx.type === 'receive' ? '⬇️' : tx.type === 'send' ? '⬆️' : '🔄'}
              </span>
              <div className="flex-1">
                <div className="font-medium text-white text-sm capitalize">{tx.type} {tx.asset}</div>
                <div className="text-xs text-slate-400">{tx.from ?? tx.to ?? ''}</div>
              </div>
              <div className="text-right">
                <div className={`text-sm font-semibold ${tx.type === 'receive' ? 'text-green-400' : 'text-white'}`}>{tx.amount}</div>
                <div className="text-xs text-slate-400">{tx.value}</div>
              </div>
              <div className="text-xs text-slate-500 w-16 text-right">{tx.time}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
