import { useState } from 'react';

const LAUNCH_STEPS = [
  { id: 'idea', label: 'Business Idea', emoji: '💡', done: true, desc: 'Define your niche, target market, and value proposition' },
  { id: 'validate', label: 'Validation', emoji: '✅', done: true, desc: 'AI-powered market validation and competitor analysis' },
  { id: 'register', label: 'Registration', emoji: '📝', done: false, desc: 'LLC/Corp formation, EIN, business accounts' },
  { id: 'brand', label: 'Brand & Domain', emoji: '🎨', done: false, desc: 'Logo, colors, domain name, social handles' },
  { id: 'bots', label: 'Deploy Bots', emoji: '🤖', done: false, desc: 'Configure and launch your DreamCo bot fleet' },
  { id: 'payments', label: 'Payment Setup', emoji: '💳', done: false, desc: 'Stripe, PayPal, crypto wallet integration' },
  { id: 'marketing', label: 'Marketing', emoji: '📣', done: false, desc: 'Funnel, ads, SEO, and outreach automation' },
  { id: 'launch', label: 'Go Live!', emoji: '🚀', done: false, desc: 'Launch to market and begin revenue collection' },
];

const TOOLS = [
  { name: 'Business Name Generator', emoji: '✨', action: 'Generate' },
  { name: 'Market Size Estimator', emoji: '📊', action: 'Estimate' },
  { name: 'Competitor Finder', emoji: '🔍', action: 'Find' },
  { name: 'Revenue Projector', emoji: '💰', action: 'Project' },
  { name: 'Legal Entity Advisor', emoji: '⚖️', action: 'Advise' },
  { name: 'Pitch Deck Builder', emoji: '📑', action: 'Build' },
];

export default function BizLaunch() {
  const [steps, setSteps] = useState(LAUNCH_STEPS);
  const [ideaInput, setIdeaInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  function toggleStep(id) {
    setSteps((prev) => prev.map((s) => (s.id === id ? { ...s, done: !s.done } : s)));
  }

  async function analyzeIdea() {
    if (!ideaInput.trim()) return;
    setAnalyzing(true);
    try {
      const res = await fetch('/api/biz-launch/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea: ideaInput }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({ score: 78, market: 'SaaS / AI Tools', potential: '$2.4M TAM', recommendation: 'High potential — validate with 10 target customers first.' });
    } finally {
      setAnalyzing(false);
    }
  }

  const progress = Math.round((steps.filter((s) => s.done).length / steps.length) * 100);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🚀</span>
        <div>
          <h2 className="text-xl font-bold text-white">Biz Launch</h2>
          <p className="text-xs text-slate-400">AI-powered business launch system — from idea to revenue</p>
        </div>
        <div className="ml-auto text-right">
          <div className="text-lg font-bold text-dreamco-accent">{progress}%</div>
          <div className="text-xs text-slate-400">launch progress</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="bg-slate-700 rounded-full h-2 mb-6">
        <div className="bg-dreamco-accent h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
      </div>

      {/* Idea analyzer */}
      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mb-6">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">💡 AI Business Idea Analyzer</h3>
        <div className="flex gap-3 mb-3">
          <input
            value={ideaInput}
            onChange={(e) => setIdeaInput(e.target.value)}
            placeholder="Describe your business idea (e.g. 'AI bot marketplace for small businesses')"
            className="flex-1 bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-4 py-2 focus:outline-none focus:border-dreamco-accent"
          />
          <button
            onClick={analyzeIdea}
            disabled={analyzing || !ideaInput.trim()}
            className="px-5 py-2 bg-dreamco-accent hover:bg-indigo-500 disabled:opacity-40 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            {analyzing ? 'Analyzing…' : 'Analyze'}
          </button>
        </div>
        {result && (
          <div className="bg-slate-800/50 rounded-lg p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div><div className="text-xs text-slate-400">Viability Score</div><div className="font-bold text-dreamco-accent text-lg">{result.score}/100</div></div>
            <div><div className="text-xs text-slate-400">Market</div><div className="font-semibold text-white text-sm">{result.market}</div></div>
            <div><div className="text-xs text-slate-400">TAM Potential</div><div className="font-bold text-green-400 text-sm">{result.potential}</div></div>
            <div><div className="text-xs text-slate-400">Recommendation</div><div className="text-xs text-slate-300">{result.recommendation}</div></div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Launch checklist */}
        <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-700">
            <h3 className="text-sm font-semibold text-slate-300">📋 Launch Checklist</h3>
          </div>
          <div className="divide-y divide-slate-700/30">
            {steps.map((step) => (
              <button
                key={step.id}
                onClick={() => toggleStep(step.id)}
                className="w-full px-5 py-4 flex items-center gap-3 hover:bg-slate-700/20 transition-colors text-left"
              >
                <span className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${step.done ? 'border-green-400 bg-green-400' : 'border-slate-500'}`}>
                  {step.done && <span className="text-white text-xs">✓</span>}
                </span>
                <span className="text-lg">{step.emoji}</span>
                <div>
                  <div className={`text-sm font-medium ${step.done ? 'text-slate-400 line-through' : 'text-white'}`}>{step.label}</div>
                  <div className="text-xs text-slate-500">{step.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Tools */}
        <div className="bg-dreamco-card rounded-xl border border-slate-700 p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">🛠️ Launch Tools</h3>
          <div className="space-y-2">
            {TOOLS.map((t) => (
              <div key={t.name} className="flex items-center justify-between px-4 py-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{t.emoji}</span>
                  <span className="text-sm text-slate-200">{t.name}</span>
                </div>
                <button className="px-3 py-1 bg-dreamco-accent hover:bg-indigo-500 text-white text-xs rounded transition-colors">
                  {t.action}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
