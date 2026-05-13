import { useState } from 'react';

const TIERS = [
  {
    id: 'free',
    name: 'FREE',
    price: '$0',
    period: '/forever',
    color: 'border-slate-600',
    badge: 'bg-slate-600 text-slate-300',
    features: [
      '5 bots',
      '1 division',
      'Community support',
      'Basic analytics',
      'Public marketplace access',
      'Code Lab (limited)',
    ],
    cta: 'Get Started',
    ctaStyle: 'bg-slate-700 hover:bg-slate-600 text-white',
  },
  {
    id: 'pro',
    name: 'PRO',
    price: '$149',
    period: '/month',
    color: 'border-dreamco-accent ring-1 ring-dreamco-accent/30',
    badge: 'bg-dreamco-accent text-white',
    popular: true,
    features: [
      '25 bots',
      '5 divisions',
      'Priority support',
      'Advanced analytics',
      'Deal Analyzer',
      'Formula Vault',
      'Marketplace selling',
      'Slack/Discord alerts',
      'Code Lab (full)',
    ],
    cta: 'Start PRO',
    ctaStyle: 'bg-dreamco-accent hover:bg-indigo-500 text-white',
  },
  {
    id: 'elite',
    name: 'ELITE',
    price: '$499',
    period: '/month',
    color: 'border-yellow-500/50',
    badge: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    features: [
      'Unlimited bots',
      'Unlimited divisions',
      'White-label export',
      'ELITE leaderboard',
      'Revenue share program',
      'Custom AI models',
      'Dedicated orchestration',
      'SLA + dedicated support',
      'All PRO features',
    ],
    cta: 'Go ELITE',
    ctaStyle: 'bg-yellow-500 hover:bg-yellow-400 text-black font-bold',
  },
  {
    id: 'enterprise',
    name: 'ENTERPRISE',
    price: 'Custom',
    period: '',
    color: 'border-purple-500/50',
    badge: 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
    features: [
      'Everything in ELITE',
      'On-premise deployment',
      'Custom bot development',
      'Dedicated AI trainer',
      'Custom integrations',
      'Volume pricing',
      'Executive support',
    ],
    cta: 'Contact Sales',
    ctaStyle: 'bg-purple-600 hover:bg-purple-500 text-white',
  },
];

export default function Pricing() {
  const [billing, setBilling] = useState('monthly');

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">💲</span>
        <div>
          <h2 className="text-xl font-bold text-white">Pricing</h2>
          <p className="text-xs text-slate-400">Transparent pricing for every stage of your empire</p>
        </div>
        <div className="ml-auto flex items-center gap-1 bg-slate-700 rounded-lg p-1">
          {['monthly', 'annual'].map((b) => (
            <button
              key={b}
              onClick={() => setBilling(b)}
              className={`px-3 py-1 rounded text-xs font-medium capitalize transition-colors ${billing === b ? 'bg-dreamco-accent text-white' : 'text-slate-300'}`}
            >
              {b} {b === 'annual' && <span className="text-green-400">-20%</span>}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {TIERS.map((tier) => (
          <div
            key={tier.id}
            className={`bg-dreamco-card rounded-xl border p-5 flex flex-col ${tier.color}`}
          >
            {tier.popular && (
              <div className="text-center mb-3">
                <span className="px-3 py-0.5 bg-dreamco-accent text-white text-xs font-bold rounded-full">MOST POPULAR</span>
              </div>
            )}
            <div className="flex items-center justify-between mb-4">
              <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${tier.badge}`}>{tier.name}</span>
            </div>
            <div className="mb-4">
              <span className="text-3xl font-bold text-white">{billing === 'annual' && tier.price !== 'Custom' ? `$${Math.round(parseFloat(tier.price.replace('$', '')) * 0.8)}` : tier.price}</span>
              <span className="text-slate-400 text-sm">{tier.period}</span>
            </div>
            <ul className="space-y-2 flex-1 mb-5">
              {tier.features.map((f) => (
                <li key={f} className="flex items-center gap-2 text-xs text-slate-300">
                  <span className="text-green-400">✓</span> {f}
                </li>
              ))}
            </ul>
            <button className={`w-full py-2.5 rounded-lg text-sm font-semibold transition-colors ${tier.ctaStyle}`}>
              {tier.cta}
            </button>
          </div>
        ))}
      </div>

      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">❓ Pricing FAQ</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {[
            { q: 'Can I upgrade anytime?', a: 'Yes — upgrades take effect immediately and are prorated.' },
            { q: 'Is there a free trial?', a: 'PRO and ELITE offer a 14-day free trial, no credit card needed.' },
            { q: 'What payment methods?', a: 'Credit card, ACH, PayPal, and crypto (BTC, ETH, USDC).' },
            { q: 'Can I cancel anytime?', a: 'Yes — cancel any time, access continues until end of billing period.' },
          ].map((faq) => (
            <div key={faq.q} className="bg-slate-800/50 rounded-lg p-4">
              <div className="font-medium text-white mb-1">{faq.q}</div>
              <div className="text-slate-400 text-xs">{faq.a}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
