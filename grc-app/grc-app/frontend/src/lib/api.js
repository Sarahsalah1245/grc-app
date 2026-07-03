// عنوان الـ Backend - في الإنتاج هيكون رابط Render بتاعك، حطيه في .env كـ VITE_API_URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('grc_token');
}

export function setToken(token) {
  localStorage.setItem('grc_token', token);
}

export function clearToken() {
  localStorage.removeItem('grc_token');
}

export function isAuthenticated() {
  return !!getToken();
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = 'حصل خطأ غير متوقع';
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch (_) {}
    if (res.status === 401) clearToken();
    throw new Error(detail);
  }

  return res.json();
}

export const api = {
  register: (payload) => request('/auth/register', { method: 'POST', body: payload, auth: false }),
  login: (payload) => request('/auth/login', { method: 'POST', body: payload, auth: false }),

  qualitative: (payload) => request('/risks/qualitative/explain', { method: 'POST', body: payload }),
  quantitative: (payload) => request('/risks/quantitative/explain', { method: 'POST', body: payload }),
  rosi: (payload) => request('/risks/rosi', { method: 'POST', body: payload }),
  monteCarlo: (payload) => request('/risks/monte-carlo/explain', { method: 'POST', body: payload }),
  fmea: (payload) => request('/risks/fmea/explain', { method: 'POST', body: payload }),
  bowtie: (payload) => request('/risks/bowtie/explain', { method: 'POST', body: payload }),
  fullAnalysis: (payload) => request('/risks/full-analysis', { method: 'POST', body: payload }),

  swotAnalyze: (entries) => request('/swot/analyze', { method: 'POST', body: { entries } }),

  cobitObjectives: () => request('/cobit/objectives', { auth: false }),
  cobitMap: (risk_description) => request('/cobit/map', { method: 'POST', body: { risk_description } }),
};
