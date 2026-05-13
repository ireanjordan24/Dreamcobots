import { useState } from 'react';

const FORMULAS = [
  { id: 'roi', name: 'ROI Calculator', category: 'Finance', icon: '💹', desc: 'Return on investment for any campaign or bot deployment', fields: [{ label: 'Net Profit ($)', key: 'profit' }, { label: 'Cost of Investment ($)', key: 'cost' }], compute: (v) => `${((v.profit / v.cost) * 100).toFixed(2)}%`, result: 'ROI' },
  { id: 'cac', name: 'Customer Acquisition Cost', category: 'Marketing', icon: '🎯', desc: 'Total cost to acquire one new customer', fields: [{ label: 'Total Marketing Spend ($)', key: 'spend' }, { label: 'New Customers Acquired', key: 'customers' }], compute: (v) => `$${(v.spend / v.customers).toFixed(2)}`, result: 'CAC' },
  { id: 'ltv', name: 'Customer Lifetime Value', category: 'Revenue', icon: '🏆', desc: 'Predicted revenue from a customer over their lifetime', fields: [{ label: 'Avg Order Value ($)', key: 'aov' }, { label: 'Purchase Frequency/yr', key: 'freq' }, { label: 'Customer Lifespan (yrs)', key: 'life' }], compute: (v) => `$${(v.aov * v.freq * v.life).toFixed(2)}`, result: 'LTV' },
  { id: 'margin', name: 'Profit Margin', category: 'Finance', icon: '📈', desc: 'Net profit as a percentage of revenue', fields: [{ label: 'Net Profit ($)', key: 'profit' }, { label: 'Revenue ($)', key: 'revenue' }], compute: (v) => `${((v.profit / v.revenue) * 100).toFixed(2)}%`, result: 'Margin' },
  { id: 'burnrate', name: 'Burn Rate', category: 'Operations', icon: '🔥', desc: 'Monthly cash expenditure rate', fields: [{ label: 'Total Cash Spent ($)', key: 'spent' }, { label: 'Period (months)', key: 'months' }], compute: (v) => `$${(v.spent / v.months).toFixed(2)}/mo`, result: 'Burn Rate' },
  { id: 'runway', name: 'Runway Calculator', category: 'Operations', icon: '✈️', desc: 'How long cash reserves will last', fields: [{ label: 'Cash Reserves ($)', key: 'cash' }, { label: 'Monthly Burn ($)', key: 'burn' }], compute: (v) => `${(v.cash / v.burn).toFixed(1)} months`, result: 'Runway' },
];

const CATEGORIES = ['All', ...new Set(FORMULAS.map((f) => f.category))];

export default function FormulaVault() {
  const [cat, setCat] = useState('All');
  const [active, setActive] = useState(null);
  const [values, setValues] = useState({});
  const [result, setResult] = useState(null);

  const visible = cat === 'All' ? FORMULAS : FORMULAS.filter((f) => f.category === cat);
  const formula = FORMULAS.find((f) => f.id === active);

  function runFormula() {
    try {
      const nums = Object.fromEntries(Object.entries(values).map(([k, v]) => [k, parseFloat(v) || 0]));
      setResult(formula.compute(nums));
    } catch {
      setResult('Invalid input');
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🗄️</span>
        <div>
          <h2 className="text-xl font-bold text-white">Formula Vault</h2>
          <p className="text-xs text-slate-400">Business formulas, calculators &amp; financial models</p>
        </div>
      </div>

      {/* Category filter */}
      <div className="flex gap-2 mb-5 flex-wrap">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setCat(c)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${cat === c ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
          >
            {c}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {visible.map((f) => (
          <button
            key={f.id}
            onClick={() => { setActive(active === f.id ? null : f.id); setValues({}); setResult(null); }}
            className={`text-left bg-dreamco-card rounded-xl p-5 border transition-all hover:scale-[1.01] ${active === f.id ? 'border-dreamco-accent' : 'border-slate-700'}`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{f.icon}</span>
              <span className="text-xs text-slate-500 px-2 py-0.5 bg-slate-700 rounded-full">{f.category}</span>
            </div>
            <div className="font-semibold text-white mb-1">{f.name}</div>
            <div className="text-xs text-slate-400">{f.desc}</div>
          </button>
        ))}
      </div>

      {formula && (
        <div className="bg-dreamco-card rounded-xl border border-dreamco-accent/30 p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span>{formula.icon}</span> {formula.name}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {formula.fields.map((field) => (
              <div key={field.key}>
                <label className="block text-xs text-slate-400 mb-1">{field.label}</label>
                <input
                  type="number"
                  value={values[field.key] ?? ''}
                  onChange={(e) => setValues((v) => ({ ...v, [field.key]: e.target.value }))}
                  className="w-full bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-dreamco-accent"
                />
              </div>
            ))}
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={runFormula}
              className="px-6 py-2 bg-dreamco-accent hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              Calculate
            </button>
            {result && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400 text-sm">{formula.result}:</span>
                <span className="text-2xl font-bold text-green-400">{result}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
