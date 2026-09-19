import axios from 'axios';

/**
 * Robust API baseURL resolver:
 * - If VITE_API_URL is provided (e.g. from Vercel env), normalizes trailing slashes and ensures /api is appended if needed.
 * - If no env variable is set, defaults to '/api' (which is proxied in local Vite dev).
 */
export function getApiBaseUrl(envUrl = import.meta.env.VITE_API_URL) {
  let url = (envUrl || '').trim();
  if (!url) return '/api';

  // Strip trailing slashes
  url = url.replace(/\/+$/, '');

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url.endsWith('/api') ? url : `${url}/api`;
  }

  if (!url.startsWith('/')) {
    url = `/${url}`;
  }
  return url.endsWith('/api') ? url : `${url.replace(/\/+$/, '')}/api`;
}

const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('voyara_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('voyara_token');
    }
    return Promise.reject(error);
  }
);

export default api;
