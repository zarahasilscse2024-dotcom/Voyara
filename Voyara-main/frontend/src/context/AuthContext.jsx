import { createContext, useContext, useEffect, useState } from 'react';
import api from '../services/api';
const AuthContext = createContext(null);
export function AuthProvider({ children }) { const [user, setUser] = useState(null); const [loading, setLoading] = useState(true); const [favoriteIds, setFavoriteIds] = useState(new Set());
  useEffect(() => { if (localStorage.getItem('voyara_token')) api.get('/auth/me').then(r => setUser(r.data)).catch(() => localStorage.removeItem('voyara_token')).finally(() => setLoading(false)); else setLoading(false); }, []);
  useEffect(() => { if (user) api.get('/favorites').then(r => setFavoriteIds(new Set(r.data.map(item => item.id)))).catch(error => { console.error('Unable to load favorites', error); setFavoriteIds(new Set()); }); else setFavoriteIds(new Set()); }, [user]);
  const authenticate = (data) => { localStorage.setItem('voyara_token', data.token); setUser(data.user); };
  const logout = () => { localStorage.removeItem('voyara_token'); setUser(null); setFavoriteIds(new Set()); };
  async function toggleFavorite(packageId) { if (!user) return false; const saved = favoriteIds.has(packageId); try { if (saved) await api.delete(`/favorites/${packageId}`); else await api.post(`/favorites/${packageId}`); } catch (error) { console.error('Unable to update favorite', error); throw error; } setFavoriteIds(current => { const next = new Set(current); if (saved) next.delete(packageId); else next.add(packageId); return next; }); return !saved; }
  return <AuthContext.Provider value={{ user, loading, authenticate, logout, favoriteIds, toggleFavorite }}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);