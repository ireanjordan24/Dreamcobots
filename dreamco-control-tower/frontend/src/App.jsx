import { useState } from 'react';
import BotOverview from './components/BotOverview.jsx';
import RepoActivity from './components/RepoActivity.jsx';
import BotDeployment from './components/BotDeployment.jsx';
import Analytics from './components/Analytics.jsx';
import Elite from './components/Elite.jsx';
import Chat from './components/Chat.jsx';
import EmpireHQ from './components/EmpireHQ.jsx';
import Divisions from './components/Divisions.jsx';
import BotFleet from './components/BotFleet.jsx';
import DealAnalyzer from './components/DealAnalyzer.jsx';
import FormulaVault from './components/FormulaVault.jsx';
import LearningMatrix from './components/LearningMatrix.jsx';
import AILeaders from './components/AILeaders.jsx';
import AIModelsHub from './components/AIModelsHub.jsx';
import AIEcosystem from './components/AIEcosystem.jsx';
import Orchestration from './components/Orchestration.jsx';
import Marketplace from './components/Marketplace.jsx';
import Crypto from './components/Crypto.jsx';
import Payments from './components/Payments.jsx';
import BizLaunch from './components/BizLaunch.jsx';
import CodeLab from './components/CodeLab.jsx';
import LoansDeals from './components/LoansDeals.jsx';
import DebugIntel from './components/DebugIntel.jsx';
import Revenue from './components/Revenue.jsx';
import Pricing from './components/Pricing.jsx';
import Connections from './components/Connections.jsx';
import TimeCapsule from './components/TimeCapsule.jsx';
import CostTracking from './components/CostTracking.jsx';
import Autonomy from './components/Autonomy.jsx';

const NAV_GROUPS = [
  {
    label: '🏠 OVERVIEW',
    items: [
      { id: 'overview', label: '🤖 Bot Overview' },
      { id: 'activity', label: '📦 Repo Activity' },
      { id: 'deploy', label: '🚀 Bot Deployment' },
      { id: 'analytics', label: '📊 Analytics' },
    ],
  },
  {
    label: '👑 COMMAND',
    items: [
      { id: 'elite', label: '👑 ELITE' },
      { id: 'chat', label: '💬 Chat' },
      { id: 'empire-hq', label: '🏛️ Empire HQ' },
      { id: 'divisions', label: '🏢 Divisions' },
    ],
  },
  {
    label: '🤖 BOT OPS',
    items: [
      { id: 'bot-fleet', label: '🚀 Bot Fleet' },
      { id: 'orchestration', label: '⚙️ Orchestration' },
      { id: 'autonomy', label: '🧭 Autonomy' },
      { id: 'debug-intel', label: '🔬 Debug Intel' },
    ],
  },
  {
    label: '🧠 AI HUB',
    items: [
      { id: 'ai-leaders', label: '🏆 AI Leaders' },
      { id: 'ai-models-hub', label: '🤖 AI Models Hub' },
      { id: 'ai-ecosystem', label: '🌐 AI Ecosystem' },
      { id: 'learning-matrix', label: '🧬 Learning Matrix' },
    ],
  },
  {
    label: '💰 FINANCE',
    items: [
      { id: 'revenue', label: '💰 Revenue' },
      { id: 'payments', label: '💳 Payments' },
      { id: 'crypto', label: '🪙 Crypto' },
      { id: 'pricing', label: '💲 Pricing' },
      { id: 'cost-tracking', label: '📉 Cost Tracking' },
      { id: 'loans-deals', label: '🤝 Loans & Deals' },
      { id: 'deal-analyzer', label: '🔍 Deal Analyzer' },
    ],
  },
  {
    label: '🚀 BUSINESS',
    items: [
      { id: 'biz-launch', label: '🚀 Biz Launch' },
      { id: 'marketplace', label: '🏪 Marketplace' },
      { id: 'connections', label: '🔌 Connections' },
      { id: 'formula-vault', label: '🗄️ Formula Vault' },
      { id: 'code-lab', label: '🧪 Code Lab' },
      { id: 'time-capsule', label: '⏳ Time Capsule' },
    ],
  },
];

const COMPONENT_MAP = {
  overview: <BotOverview />,
  activity: <RepoActivity />,
  deploy: <BotDeployment />,
  analytics: <Analytics />,
  elite: <Elite />,
  chat: <Chat />,
  'empire-hq': <EmpireHQ />,
  divisions: <Divisions />,
  'bot-fleet': <BotFleet />,
  orchestration: <Orchestration />,
  autonomy: <Autonomy />,
  'debug-intel': <DebugIntel />,
  'ai-leaders': <AILeaders />,
  'ai-models-hub': <AIModelsHub />,
  'ai-ecosystem': <AIEcosystem />,
  'learning-matrix': <LearningMatrix />,
  revenue: <Revenue />,
  payments: <Payments />,
  crypto: <Crypto />,
  pricing: <Pricing />,
  'cost-tracking': <CostTracking />,
  'loans-deals': <LoansDeals />,
  'deal-analyzer': <DealAnalyzer />,
  'biz-launch': <BizLaunch />,
  marketplace: <Marketplace />,
  connections: <Connections />,
  'formula-vault': <FormulaVault />,
  'code-lab': <CodeLab />,
  'time-capsule': <TimeCapsule />,
};

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-dreamco-card border-b border-slate-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏰</span>
          <h1 className="text-xl font-bold text-white">DreamCo Control Tower</h1>
        </div>
        <span className="text-xs text-slate-400">Autonomous Bot Management Hub</span>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <nav className="w-56 bg-dreamco-card border-r border-slate-700 flex flex-col overflow-y-auto shrink-0">
          {NAV_GROUPS.map((group) => (
            <div key={group.label} className="px-3 pt-4 pb-1">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2 mb-1">
                {group.label}
              </div>
              {group.items.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-sm font-medium transition-colors mb-0.5 ${
                    activeTab === item.id
                      ? 'bg-dreamco-accent text-white'
                      : 'text-slate-400 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          ))}
          <div className="h-4" />
        </nav>

        {/* Main content */}
        <main className="flex-1 p-6 overflow-auto">
          {COMPONENT_MAP[activeTab] ?? <p className="text-slate-400">Select a section from the sidebar.</p>}
        </main>
      </div>
    </div>
  );
}
