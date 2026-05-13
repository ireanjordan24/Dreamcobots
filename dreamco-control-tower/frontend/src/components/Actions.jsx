import { useState } from 'react';

const ACTION_BUTTONS = [
  // ── Command Center ─────────────────────────────────────────────────────────
  { id: 'elite',        icon: '👑', label: 'ELITE',          description: 'Unlock premium tier — white-label, custom AI, priority support.',  category: 'Command Center', color: 'from-yellow-600 to-yellow-800'  },
  { id: 'empire-hq',   icon: '🏰', label: 'Empire HQ',      description: 'Central command hub for your entire DreamCo empire.',              category: 'Command Center', color: 'from-purple-700 to-purple-900'  },
  { id: 'autonomy',    icon: '🤖', label: 'Autonomy',        description: 'Full autonomous bot operations — zero manual intervention.',        category: 'Command Center', color: 'from-cyan-700 to-cyan-900'      },
  { id: 'orchestration', icon: '🎛️', label: 'Orchestration', description: 'Coordinate all bots, workflows, and automation sequences.',        category: 'Command Center', color: 'from-indigo-700 to-indigo-900'   },

  // ── Operations ─────────────────────────────────────────────────────────────
  { id: 'bot-fleet',   icon: '🚀', label: 'Bot Fleet',       description: 'Deploy, monitor, and scale your entire bot fleet.',               category: 'Operations', color: 'from-blue-700 to-blue-900'       },
  { id: 'ai-leaders',  icon: '🏆', label: 'AI Leaders',      description: 'Leaderboard of top-performing AI bots and agents.',               category: 'Operations', color: 'from-orange-600 to-orange-800'   },
  { id: 'divisions',   icon: '🏢', label: 'Divisions',       description: 'Manage business divisions and assign dedicated bot teams.',        category: 'Operations', color: 'from-slate-600 to-slate-800'     },
  { id: 'connections', icon: '🔗', label: 'Connections',     description: 'Manage integrations: Replit, Stripe, Slack, GitHub, and more.',   category: 'Operations', color: 'from-teal-700 to-teal-900'       },

  // ── Intelligence ───────────────────────────────────────────────────────────
  { id: 'ai-models-hub',  icon: '🧠', label: 'AI Models Hub',   description: 'Registry of all AI models powering your bot fleet.',          category: 'Intelligence', color: 'from-violet-700 to-violet-900'  },
  { id: 'ai-ecosystem',   icon: '🌐', label: 'AI Ecosystem',    description: 'Full map of integrated AI services and data pipelines.',       category: 'Intelligence', color: 'from-fuchsia-700 to-fuchsia-900'},
  { id: 'learning-matrix',icon: '📚', label: 'Learning Matrix', description: 'Track bot learning progress across all training categories.',   category: 'Intelligence', color: 'from-emerald-700 to-emerald-900'},
  { id: 'debug-intel',    icon: '🔍', label: 'Debug Intel',     description: 'AI bug detection, error analysis, and fix recommendations.',   category: 'Intelligence', color: 'from-red-700 to-red-900'        },
  { id: 'formula-vault',  icon: '🔬', label: 'Formula Vault',   description: 'Proprietary income and growth formulas for every module.',      category: 'Intelligence', color: 'from-lime-700 to-lime-900'      },

  // ── Commerce ───────────────────────────────────────────────────────────────
  { id: 'deal-analyzer', icon: '💡', label: 'Deal Analyzer',   description: 'AI-powered analysis of deals, contracts, and opportunities.',   category: 'Commerce', color: 'from-amber-600 to-amber-800'    },
  { id: 'marketplace',   icon: '🛒', label: 'Marketplace',     description: 'Browse and install bots, templates, and AI modules.',          category: 'Commerce', color: 'from-sky-700 to-sky-900'         },
  { id: 'crypto',        icon: '₿',  label: 'Crypto',          description: 'Crypto trading, mining, and portfolio management.',             category: 'Commerce', color: 'from-yellow-700 to-yellow-900'   },
  { id: 'payments',      icon: '💳', label: 'Payments',        description: 'Process payments, subscriptions, and revenue splits.',          category: 'Commerce', color: 'from-green-700 to-green-900'     },
  { id: 'biz-launch',    icon: '🚀', label: 'Biz Launch',      description: 'Launch a new business unit with bots, branding, and workflows.',category: 'Commerce', color: 'from-pink-700 to-pink-900'       },
  { id: 'loans-deals',   icon: '🤝', label: 'Loans & Deals',   description: 'Access business funding, loan options, and partnerships.',      category: 'Commerce', color: 'from-blue-800 to-blue-950'       },
  { id: 'revenue',       icon: '💰', label: 'Revenue',         description: 'Track, forecast, and optimize all revenue streams.',            category: 'Commerce', color: 'from-green-600 to-green-800'     },
  { id: 'pricing',       icon: '🏷️', label: 'Pricing',         description: 'Manage pricing tiers, coupons, and dynamic pricing rules.',    category: 'Commerce', color: 'from-orange-700 to-orange-900'   },
  { id: 'cost-tracking', icon: '📉', label: 'Cost Tracking',   description: 'Monitor operational costs, AI API spend, and ROI per bot.',    category: 'Commerce', color: 'from-rose-700 to-rose-900'       },

  // ── Tools ──────────────────────────────────────────────────────────────────
  { id: 'chat',         icon: '💬', label: 'Chat',            description: 'Buddy AI chat — send commands, get answers, train your bot.',   category: 'Tools', color: 'from-indigo-600 to-indigo-800'   },
  { id: 'code-lab',    icon: '⚙️', label: 'Code Lab',        description: 'AI-assisted workspace — generate, debug, and deploy code.',    category: 'Tools', color: 'from-gray-700 to-gray-900'       },
  { id: 'time-capsule',icon: '⏳', label: 'Time Capsule',    description: 'Archive milestones, snapshots, and empire version history.',    category: 'Tools', color: 'from-purple-800 to-purple-950'   },
];

const CATEGORIES = ['Command Center', 'Operations', 'Intelligence', 'Commerce', 'Tools'];

function ResultPanel({ result, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60" onClick={onClose}>
      <div
        className="bg-slate-800 border border-slate-600 rounded-2xl p-6 max-w-lg w-full max-h-[80vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-bold text-lg">{result.label}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl leading-none">&times;</button>
        </div>
        <div className="space-y-2">
          {Object.entries(result.data).map(([key, value]) => (
            <div key={key} className="bg-slate-700 rounded-lg px-4 py-3">
              <div className="text-xs text-slate-400 mb-1 uppercase tracking-wide">{key.replace(/_/g, ' ')}</div>
              <div className="text-sm text-slate-100 break-words">
                {Array.isArray(value)
                  ? (
                    <ul className="space-y-1 mt-1">
                      {value.map((item, i) => (
                        <li key={i} className="text-slate-200">
                          {typeof item === 'object' ? (
                            <span className="flex flex-wrap gap-2">
                              {Object.entries(item).map(([k, v]) => (
                                <span key={k} className="bg-slate-600 rounded px-2 py-0.5 text-xs">
                                  <span className="text-slate-400">{k}:</span> {String(v)}
                                </span>
                              ))}
                            </span>
                          ) : (
                            <span className="bg-slate-600 rounded px-2 py-0.5 text-xs">{String(item)}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  )
                  : typeof value === 'object' && value !== null
                  ? (
                    <ul className="space-y-1 mt-1">
                      {Object.entries(value).map(([k, v]) => (
                        <li key={k} className="text-xs text-slate-300">
                          <span className="text-slate-400">{k}:</span> {String(v)}
                        </li>
                      ))}
                    </ul>
                  )
                  : <span className="text-slate-100">{String(value)}</span>
                }
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500 mt-4">{result.timestamp}</p>
      </div>
    </div>
  );
}

function ActionCard({ btn, onResult }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/actions/${btn.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const json = await res.json();
      if (!res.ok) {
        setError(json.error ?? 'Action failed.');
      } else {
        onResult(json);
      }
    } catch {
      setError('Could not reach Control Tower API.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`relative group w-full text-left rounded-xl border border-slate-700 bg-gradient-to-br ${btn.color} p-4 hover:scale-105 active:scale-95 transition-all duration-150 shadow-lg disabled:opacity-60 disabled:cursor-wait`}
    >
      <div className="flex items-start gap-3">
        <span className="text-3xl drop-shadow">{btn.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="text-white font-bold text-sm leading-tight">{btn.label}</div>
          <div className="text-slate-300 text-xs mt-1 leading-snug">{btn.description}</div>
        </div>
      </div>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-xl">
          <span className="text-white text-xs animate-pulse">Running…</span>
        </div>
      )}
      {error && (
        <div className="mt-2 text-xs text-red-300 bg-red-900/40 rounded px-2 py-1">{error}</div>
      )}
    </button>
  );
}

export default function Actions() {
  const [result, setResult] = useState(null);

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white">⚡ Actions</h2>
        <p className="text-slate-400 text-sm mt-1">Click any button to activate its module. Results appear in a panel.</p>
      </div>

      {CATEGORIES.map((cat) => {
        const buttons = ACTION_BUTTONS.filter((b) => b.category === cat);
        return (
          <div key={cat} className="mb-8">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">{cat}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {buttons.map((btn) => (
                <ActionCard key={btn.id} btn={btn} onResult={setResult} />
              ))}
            </div>
          </div>
        );
      })}

      {result && <ResultPanel result={result} onClose={() => setResult(null)} />}
    </div>
  );
}
