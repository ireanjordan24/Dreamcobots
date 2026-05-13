import { useEffect, useState } from 'react';

const AUTONOMY_BOTS = [
  { name: 'BuddyOrchestrator', level: 'FULL', autoHeal: true, autoScale: true, autoDeploy: true, autoRevenue: true, alertThreshold: 'critical' },
  { name: 'DealAnalyzerBot', level: 'HIGH', autoHeal: true, autoScale: true, autoDeploy: false, autoRevenue: true, alertThreshold: 'warning' },
  { name: 'RevenueEngineBot', level: 'HIGH', autoHeal: true, autoScale: false, autoDeploy: false, autoRevenue: true, alertThreshold: 'warning' },
  { name: 'MarketplaceBot', level: 'MEDIUM', autoHeal: true, autoScale: false, autoDeploy: false, autoRevenue: false, alertThreshold: 'all' },
  { name: 'CryptoSentinelBot', level: 'MEDIUM', autoHeal: true, autoScale: false, autoDeploy: false, autoRevenue: false, alertThreshold: 'all' },
];

const LEVEL_CONFIG = {
  FULL: { color: 'text-green-400', badge: 'bg-green-500/20 text-green-400 border-green-500/30' },
  HIGH: { color: 'text-blue-400', badge: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  MEDIUM: { color: 'text-yellow-400', badge: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  LOW: { color: 'text-slate-400', badge: 'bg-slate-600 text-slate-300 border-slate-500' },
};

const GLOBAL_SETTINGS = [
  { key: 'masterSwitch', label: 'Master Autonomy Switch', desc: 'Enable all autonomous operations', value: true },
  { key: 'autoHealing', label: 'Global Auto-Healing', desc: 'Bots auto-recover from errors', value: true },
  { key: 'autoScaling', label: 'Auto-Scaling', desc: 'Dynamically scale bot resources', value: true },
  { key: 'revenueAutopilot', label: 'Revenue Autopilot', desc: 'Autonomous revenue optimization', value: true },
  { key: 'learningMode', label: 'Continuous Learning', desc: 'Bots learn and improve autonomously', value: true },
  { key: 'safeMode', label: 'Safe Mode', desc: 'Require approval for high-risk actions', value: false },
];

function Toggle({ value, onChange }) {
  return (
    <button
      onClick={() => onChange(!value)}
      className={`relative w-10 h-5 rounded-full transition-colors ${value ? 'bg-green-500' : 'bg-slate-600'}`}
    >
      <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${value ? 'translate-x-5' : 'translate-x-0.5'}`} />
    </button>
  );
}

export default function Autonomy() {
  const [settings, setSettings] = useState(GLOBAL_SETTINGS);
  const [bots, setBots] = useState(AUTONOMY_BOTS);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch('/api/autonomy/settings')
      .then((r) => r.json())
      .then((d) => { if (d?.settings) setSettings(d.settings); })
      .catch(() => {});
  }, []);

  function toggleSetting(key) {
    setSettings((prev) => prev.map((s) => s.key === key ? { ...s, value: !s.value } : s));
  }

  function toggleBotSetting(botName, field) {
    setBots((prev) => prev.map((b) => b.name === botName ? { ...b, [field]: !b[field] } : b));
  }

  function saveSettings() {
    setSaved(true);
    fetch('/api/autonomy/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings, bots }),
    }).catch(() => {});
    setTimeout(() => setSaved(false), 3000);
  }

  const masterOn = settings.find((s) => s.key === 'masterSwitch')?.value;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🧭</span>
        <div>
          <h2 className="text-xl font-bold text-white">Autonomy</h2>
          <p className="text-xs text-slate-400">Configure autonomous bot behavior, self-healing &amp; autopilot settings</p>
        </div>
        <div className="ml-auto flex items-center gap-3">
          {saved && <span className="text-green-400 text-xs">✅ Saved!</span>}
          <button
            onClick={saveSettings}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            Save Settings
          </button>
        </div>
      </div>

      {!masterOn && (
        <div className="mb-4 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center gap-2">
          ⚠️ Master Autonomy Switch is OFF — all autonomous operations are paused.
        </div>
      )}

      {/* Global settings */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden mb-6">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">🌐 Global Autonomy Settings</h3>
        </div>
        <div className="divide-y divide-slate-700/30">
          {settings.map((s) => (
            <div key={s.key} className="px-5 py-4 flex items-center gap-4">
              <div className="flex-1">
                <div className="font-medium text-white text-sm">{s.label}</div>
                <div className="text-xs text-slate-400">{s.desc}</div>
              </div>
              <Toggle value={s.value} onChange={() => toggleSetting(s.key)} />
            </div>
          ))}
        </div>
      </div>

      {/* Per-bot autonomy */}
      <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden mb-6">
        <div className="px-5 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">🤖 Per-Bot Autonomy Configuration</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm min-w-max">
            <thead>
              <tr className="border-b border-slate-700/50 text-xs text-slate-500">
                <th className="text-left px-5 py-3">Bot</th>
                <th className="text-center px-4 py-3">Level</th>
                <th className="text-center px-4 py-3">Auto-Heal</th>
                <th className="text-center px-4 py-3">Auto-Scale</th>
                <th className="text-center px-4 py-3">Auto-Deploy</th>
                <th className="text-center px-4 py-3">Revenue Autopilot</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/30">
              {bots.map((bot) => {
                const lc = LEVEL_CONFIG[bot.level] ?? LEVEL_CONFIG.LOW;
                return (
                  <tr key={bot.name} className="hover:bg-slate-700/20 transition-colors">
                    <td className="px-5 py-3 font-medium text-white whitespace-nowrap">{bot.name}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-bold border ${lc.badge}`}>{bot.level}</span>
                    </td>
                    {['autoHeal', 'autoScale', 'autoDeploy', 'autoRevenue'].map((field) => (
                      <td key={field} className="px-4 py-3 text-center">
                        <Toggle value={bot[field]} onChange={() => toggleBotSetting(bot.name, field)} />
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">⚡ Autonomy Actions</h3>
        <div className="flex gap-2 flex-wrap">
          {['Run Full Autonomy Check', 'View Autonomy Logs', 'Reset to Defaults', 'Export Config', 'Simulate Failure', 'Set All to FULL'].map((a) => (
            <button key={a} className="px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors">{a}</button>
          ))}
        </div>
      </div>
    </div>
  );
}
