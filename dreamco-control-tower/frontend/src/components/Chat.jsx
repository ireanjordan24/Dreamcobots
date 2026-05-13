import { useEffect, useRef, useState } from 'react';

const WELCOME = { role: 'buddy', text: 'Hey! I\'m Buddy AI 🤖 — your DreamCo assistant. Ask me anything about your bots, revenue, or empire.' };

export default function Chat() {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setLoading(true);
    try {
      const res = await fetch('/api/actions/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: 'buddy', text: data.reply ?? 'Got it! Processing your request...' }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'buddy', text: '⚠️ Connection error — please try again.' }]);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  const QUICK = ['Show bot status', 'What\'s my revenue today?', 'Run diagnostics', 'List active deals', 'Deploy latest bot'];

  return (
    <div className="flex flex-col h-full" style={{ minHeight: '70vh' }}>
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">💬</span>
        <div>
          <h2 className="text-xl font-bold text-white">Buddy AI Chat</h2>
          <p className="text-xs text-slate-400">Talk directly to your AI command center</p>
        </div>
        <span className="ml-auto flex items-center gap-1.5 text-xs text-green-400">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" /> Online
        </span>
      </div>

      {/* Quick prompts */}
      <div className="flex flex-wrap gap-2 mb-4">
        {QUICK.map((q) => (
          <button
            key={q}
            onClick={() => { setInput(q); }}
            className="text-xs px-3 py-1 rounded-full bg-slate-700 hover:bg-slate-600 text-slate-300 border border-slate-600 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 bg-dreamco-card rounded-xl border border-slate-700 p-4 overflow-y-auto space-y-3 mb-4" style={{ maxHeight: '50vh' }}>
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'buddy' && (
              <span className="text-xl mr-2 mt-0.5">🤖</span>
            )}
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2.5 rounded-2xl text-sm ${
                m.role === 'user'
                  ? 'bg-dreamco-accent text-white rounded-br-sm'
                  : 'bg-slate-700 text-slate-100 rounded-bl-sm'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <span className="text-xl mr-2">🤖</span>
            <div className="bg-slate-700 px-4 py-2.5 rounded-2xl rounded-bl-sm text-sm text-slate-400">
              Buddy is thinking<span className="animate-pulse">...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <textarea
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask Buddy anything… (Enter to send)"
          className="flex-1 bg-slate-700 border border-slate-600 text-white text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:border-dreamco-accent resize-none"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="px-5 py-2 bg-dreamco-accent hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold rounded-xl text-sm transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
