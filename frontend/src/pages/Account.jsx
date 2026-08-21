import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export function Profile() {
  const { user } = useAuth();
  const [form, setForm] = useState({ full_name: user?.full_name || '', phone: user?.phone || '' });
  const [message, setMessage] = useState('');
  async function submit(event) { event.preventDefault(); const response = await api.patch('/auth/me', form); setForm({ full_name: response.data.full_name, phone: response.data.phone }); setMessage('Profile updated successfully.'); }
  return <section className="section form-card account-form"><span className="kicker">Your profile</span><h1>Keep your<br/><em>details current.</em></h1><form onSubmit={submit}><label>Full name<input required value={form.full_name} onChange={event => setForm({ ...form, full_name: event.target.value })}/></label><label>Email<input disabled value={user?.email || ''}/></label><label>Phone<input required value={form.phone} onChange={event => setForm({ ...form, phone: event.target.value })}/></label><label>Role<input disabled value={user?.role || ''}/></label>{message && <div className="success">{message}</div>}<button className="button full">Save profile ↗</button></form></section>;
}

export function Bookings() {
  const [items, setItems] = useState([]); const [error, setError] = useState('');
  useEffect(() => { api.get('/bookings').then(response => setItems(response.data)).catch(requestError => { console.error('Unable to load bookings', requestError); setError('Unable to load your bookings.'); }); }, []);
  return <section className="section account-page"><span className="kicker">Your travel plans</span><h1>My<br/><em>bookings.</em></h1>{error && <div className="error">{error}</div>}<div className="management-list">{items.map(item => <article key={item.id}><div><h3>{item.package_name}</h3><p>{item.destination} · {item.travel_date} · {item.travelers} traveller(s)</p><p>₹{item.total_amount?.toLocaleString()} · {item.payment_status} · {item.status}</p></div><Link className="button small" to={`/package/${item.package_id}`}>View package</Link></article>)}{!items.length && !error && <div className="empty">Your booking enquiries will appear here.</div>}</div></section>;
}
