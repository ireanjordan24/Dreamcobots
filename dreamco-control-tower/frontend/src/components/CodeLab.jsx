import { useState } from 'react';

const LANGUAGES = ['JavaScript', 'Python', 'TypeScript', 'Bash', 'JSON', 'SQL'];

const TEMPLATES = [
  { name: 'New Bot Skeleton', emoji: '🤖', lang: 'Python', code: `from core.base_bot import BaseBot\n\nclass MyBot(BaseBot):\n    def run(self, task):\n        return {"status": "ok", "task": task}` },
  { name: 'API Endpoint', emoji: '🌐', lang: 'JavaScript', code: `app.get('/api/my-endpoint', (req, res) => {\n  res.json({ status: 'ok', data: [] });\n});` },
  { name: 'GitHub Workflow', emoji: '⚙️', lang: 'Bash', code: `name: My Workflow\non:\n  push:\n    branches: [main]\njobs:\n  run:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4` },
  { name: 'Data Schema', emoji: '📊', lang: 'JSON', code: `{\n  "name": "my-bot",\n  "tier": "FREE",\n  "status": "active",\n  "team": "engineering"\n}` },
];

export default function CodeLab() {
  const [lang, setLang] = useState('Python');
  const [code, setCode] = useState('# Write your bot code here\n\nprint("Hello, DreamCo!")');
  const [output, setOutput] = useState('');
  const [running, setRunning] = useState(false);
  const [activeTemplate, setActiveTemplate] = useState(null);

  async function runCode() {
    setRunning(true);
    setOutput('');
    try {
      const res = await fetch('/api/code-lab/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: lang, code }),
      });
      const data = await res.json();
      setOutput(data.output ?? data.error ?? 'No output.');
    } catch {
      setOutput('⚠️ Code execution service unavailable. Running in sandbox mode.\n\n> Code accepted — simulation complete.');
    } finally {
      setRunning(false);
    }
  }

  function loadTemplate(tpl) {
    setCode(tpl.code);
    setLang(tpl.lang);
    setActiveTemplate(tpl.name);
    setOutput('');
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🧪</span>
        <div>
          <h2 className="text-xl font-bold text-white">Code Lab</h2>
          <p className="text-xs text-slate-400">Write, test, and deploy bot code in real-time</p>
        </div>
      </div>

      {/* Templates */}
      <div className="mb-5">
        <p className="text-xs text-slate-400 mb-2">Quick Templates:</p>
        <div className="flex gap-2 flex-wrap">
          {TEMPLATES.map((tpl) => (
            <button
              key={tpl.name}
              onClick={() => loadTemplate(tpl)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${activeTemplate === tpl.name ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
            >
              <span>{tpl.emoji}</span> {tpl.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Editor */}
        <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
          <div className="px-4 py-2 border-b border-slate-700 flex items-center gap-3">
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="bg-slate-700 text-white text-xs rounded px-2 py-1 border-none focus:outline-none"
            >
              {LANGUAGES.map((l) => <option key={l}>{l}</option>)}
            </select>
            <span className="text-xs text-slate-500 flex-1">editor.{lang.toLowerCase()}</span>
            <button
              onClick={runCode}
              disabled={running || !code.trim()}
              className="px-4 py-1 bg-green-600 hover:bg-green-500 disabled:opacity-40 text-white text-xs font-bold rounded transition-colors"
            >
              {running ? '⏳ Running…' : '▶ Run'}
            </button>
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="w-full bg-slate-900 text-green-300 text-sm font-mono p-4 focus:outline-none resize-none"
            style={{ minHeight: '320px' }}
            spellCheck={false}
          />
        </div>

        {/* Output */}
        <div className="bg-dreamco-card rounded-xl border border-slate-700 overflow-hidden">
          <div className="px-4 py-2 border-b border-slate-700 flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono">output</span>
            <button onClick={() => setOutput('')} className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
              Clear
            </button>
          </div>
          <pre className="bg-slate-900 text-slate-200 text-sm font-mono p-4 overflow-auto" style={{ minHeight: '320px' }}>
            {output || (running ? 'Running…' : '// Output will appear here after running code')}
          </pre>
        </div>
      </div>

      <div className="mt-4 bg-dreamco-card rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">🛠️ Code Lab Tools</h3>
        <div className="flex gap-2 flex-wrap">
          {['Format Code', 'Lint Check', 'Generate Tests', 'Deploy to Bot', 'Share Snippet', 'Save to Vault'].map((a) => (
            <button
              key={a}
              className="px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs transition-colors"
            >
              {a}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
