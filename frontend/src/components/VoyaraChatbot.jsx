import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import VoyaraLogo from './VoyaraLogo';
import { useAuth } from '../context/AuthContext';

const quickPrompts = ['Suggest a destination', 'Find trips by budget', 'Best hill stations', 'Family trips', 'Honeymoon destinations', 'Help me compare packages'];

export default function VoyaraChatbot() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([{ role: 'assistant', content: "Hi, I'm Voyara AI. Tell me where you want to go, what you want to spend, or what kind of trip feels right." }]);
  const navigate = useNavigate();
  const { user } = useAuth();

  async function send(value = message) {
    const text = value.trim();
    if (!text || busy) return;
    const history = messages.slice(-10).map(item => ({ role: item.role === 'assistant' ? 'assistant' : 'user', content: item.content }));
    setMessage('');
    setMessages(current => [...current, { role: 'user', content: text }]);
    setBusy(true);
    try {
      const response = await api.post('/chat', { message: text, conversation: history });
      setMessages(current => [...current, { role: 'assistant', content: response.data.reply, suggestions: response.data.suggestions || [] }]);
    } catch {
      setMessages(current => [...current, { role: 'assistant', content: "Sorry, I'm having trouble connecting right now. Please try again." }]);
    } finally {
      setBusy(false);
    }
  }

  function compare(item) {
    const selected = JSON.parse(localStorage.getItem('voyara_compare') || '[]');
    if (!selected.some(existing => existing.id === item.id)) localStorage.setItem('voyara_compare', JSON.stringify([...selected, item].slice(-4)));
    navigate('/compare');
    setOpen(false);
  }

  async function save(item) {
    if (!user) { navigate('/login'); setOpen(false); return; }
    await api.post(`/favorites/${item.id}`);
    setMessages(current => [...current, { role: 'assistant', content: `${item.name} is saved to your Favorites.` }]);
  }

  return <>
    {open && <section className="chat-panel" aria-label="Voyara AI travel assistant">
      <header className="chat-header"><VoyaraLogo compact/><div><strong>Voyara AI</strong><span>Your travel assistant</span></div><button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">×</button></header>
      <div className="chat-messages">{messages.map((item, index) => <div key={`${item.role}-${index}`} className={`chat-message ${item.role === 'user' ? 'chat-message-user' : ''}`}><p>{item.content}</p>{item.suggestions?.length > 0 && <div className="chat-suggestions">{item.suggestions.map(suggestion => <article key={suggestion.id}><div><strong>{suggestion.name}</strong><small>{suggestion.destination} · ₹{suggestion.price.toLocaleString()} · ★ {suggestion.rating}</small><small>{suggestion.operator_name}</small></div><div className="chat-actions"><button onClick={() => { navigate(`/package/${suggestion.id}`); setOpen(false); }}>View</button><button onClick={() => compare(suggestion)}>Compare</button><button onClick={() => save(suggestion)}>Save</button></div></article>)}</div>}</div>)}{busy && <div className="chat-message"><p className="chat-typing">Voyara AI is thinking...</p></div>}</div>
      {messages.length === 1 && <div className="chat-quick-prompts">{quickPrompts.map(prompt => <button key={prompt} onClick={() => send(prompt)}>{prompt}</button>)}</div>}
      <form className="chat-input" onSubmit={event => { event.preventDefault(); send(); }}><input value={message} onChange={event => setMessage(event.target.value)} placeholder="Ask about your next trip..." maxLength={1000} aria-label="Message Voyara AI"/><button disabled={busy || !message.trim()} aria-label="Send message">↗</button></form>
    </section>}
    {!open && <button className="chat-launcher" onClick={() => setOpen(true)} aria-label="Open Voyara AI"><VoyaraLogo compact/><span>Ask Voyara AI</span></button>}
  </>;
}
