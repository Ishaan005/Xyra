import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
});

let authToken: string | null = null;

export function setAuthToken(token: string) {
  authToken = token;
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// Attach token before each request if available
api.interceptors.request.use(config => {
  if (authToken) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${authToken}`;
  }
  return config;
});

export default api;
