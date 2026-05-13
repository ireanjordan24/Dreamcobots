import { useState } from 'react';

const MODELS = [
  { id: 'gpt4o', name: 'GPT-4o', provider: 'OpenAI', tier: 'ELITE', status: 'active', bots: 8, latency: '420ms', cost: '$0.005/1k', capabilities: ['Vision', 'Code', 'Reasoning', 'JSON'] },
  { id: 'claude3', name: 'Claude 3 Sonnet', provider: 'Anthropic', tier: 'PRO', status: 'active', bots: 6, latency: '380ms', cost: '$0.003/1k', capabilities: ['Long Context', 'Code', 'Analysis'] },
  { id: 'gemini', name: 'Gemini Pro', provider: 'Google', tier: 'PRO', status: 'active', bots: 4, latency: '510ms', cost: '$0.002/1k', capabilities: ['Multimodal', 'Reasoning'] },
  { id: 'llama3', name: 'Llama 3', provider: 'Meta (Local)', tier: 'FREE', status: 'active', bots: 3, latency: '280ms', cost: 'Free', capabilities: ['Code', 'Chat'] },
  { id: 'mixtral', name: 'Mixtral 8x7B', provider: 'Mistral (Local)', tier: 'FREE', status: 'idle', bots: 2, latency: '350ms', cost: 'Free', capabilities: ['Multilingual', 'Code'] },
  { id: 'gpt4mini', name: 'GPT-4o Mini', provider: 'OpenAI', tier: 'FREE', status: 'active', bots: 5, latency: '180ms', cost: '$0.0002/1k', capabilities: ['Fast', 'Chat', 'Code'] },
];

const TIER_COLOR = { ELITE: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', PRO: 'bg-purple-500/20 text-purple-400 border-purple-500/30', FREE: 'bg-slate-600 text-slate-300 border-slate-500' };

export default function AIModelsHub() {
  const [selected, setSelected] = useState(null);
  const detail = MODELS.find((m) => m.id === selected);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🤖</span>
        <div>
          <h2 className="text-xl font-bold text-white">AI Models Hub</h2>
          <p className="text-xs text-slate-400">Manage, compare, and deploy AI models across your bot fleet</p>
        </div>
        <button className="ml-auto px-4 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-sm rounded-lg transition-colors">
          + Connect Model
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-white">{MODELS.length}</div>
          <div className="text-xs text-slate-400 mt-1">Total Models</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-green-400">{MODELS.filter((m) => m.status === 'active').length}</div>
          <div className="text-xs text-slate-400 mt-1">Active</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-white">{MODELS.reduce((a, m) => a + m.bots, 0)}</div>
          <div className="text-xs text-slate-400 mt-1">Bots Using Models</div>
        </div>
        <div className="bg-dreamco-card rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-dreamco-accent">{MODELS.filter((m) => m.cost === 'Free').length}</div>
          <div className="text-xs text-slate-400 mt-1">Free Models</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {MODELS.map((model) => (
          <button
            key={model.id}
            onClick={() => setSelected(selected === model.id ? null : model.id)}
            className={`text-left bg-dreamco-card rounded-xl p-5 border transition-all hover:scale-[1.01] ${selected === model.id ? 'border-dreamco-accent' : 'border-slate-700'}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="font-bold text-white">{model.name}</div>
                <div className="text-xs text-slate-400">{model.provider}</div>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-xs font-bold border ${TIER_COLOR[model.tier]}`}>
                {model.tier}
              </span>
            </div>
            <div className="flex gap-1 flex-wrap mb-3">
              {model.capabilities.map((c) => (
                <span key={c} className="px-1.5 py-0.5 bg-slate-700 rounded text-xs text-slate-300">{c}</span>
              ))}
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>⚡ {model.latency}</span>
              <span>💰 {model.cost}</span>
              <span className={model.status === 'active' ? 'text-green-400' : 'text-slate-500'}>● {model.status}</span>
            </div>
          </button>
        ))}
      </div>

      {detail && (
        <div className="bg-dreamco-card rounded-xl border border-dreamco-accent/30 p-6">
          <h3 className="text-lg font-bold text-white mb-4">{detail.name} — Configuration</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {[
              { label: 'Provider', val: detail.provider },
              { label: 'Latency', val: detail.latency },
              { label: 'Cost', val: detail.cost },
              { label: 'Bots Assigned', val: detail.bots },
            ].map((s) => (
              <div key={s.label} className="bg-slate-800/50 rounded-lg p-3">
                <div className="text-xs text-slate-400 mb-1">{s.label}</div>
                <div className="font-semibold text-white">{s.val}</div>
              </div>
            ))}
          </div>
          <div className="flex gap-3 flex-wrap">
            {['Assign to Bot', 'Run Benchmark', 'View Usage', 'Disconnect'].map((a) => (
              <button
                key={a}
                className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors"
              >
                {a}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
