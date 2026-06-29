import * as SecureStore from 'expo-secure-store';

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:5000/api/v1';

async function getToken(): Promise<string | null> {
  return SecureStore.getItemAsync('access_token');
}

async function request(path: string, options: RequestInit = {}) {
  const token = await getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message ?? `HTTP ${res.status}`);
  return data;
}

export const api = {
  async register(payload: {
    email: string;
    password: string;
    full_name: string;
    age: number;
    handedness?: string;
    language_pref?: string;
  }) {
    const data = await request('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    await SecureStore.setItemAsync('access_token', data.access_token);
    return data;
  },

  async login(email: string, password: string) {
    const data = await request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    await SecureStore.setItemAsync('access_token', data.access_token);
    return data;
  },

  async logout() {
    await SecureStore.deleteItemAsync('access_token');
  },

  async submitSession(session: Record<string, unknown>) {
    return request('/games/sessions', { method: 'POST', body: JSON.stringify(session) });
  },

  async getProgress() {
    return request('/games/progress');
  },

  async analyze() {
    return request('/predictions/analyze', { method: 'POST' });
  },

  async generateReport() {
    return request('/reports/generate', { method: 'POST' });
  },

  async getExercises() {
    return request('/exercises/recommended');
  },
};

export function getTimeOfDay(): string {
  const h = new Date().getHours();
  if (h < 12) return 'morning';
  if (h < 17) return 'afternoon';
  if (h < 21) return 'evening';
  return 'night';
}

export function nowISO() {
  return new Date().toISOString();
}

export function highResTimestamp(): number {
  return performance.now();
}
