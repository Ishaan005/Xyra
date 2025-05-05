import axios from 'axios';
import { getSession } from 'next-auth/react';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
});

// Optionally set token manually
export function setAuthToken(token: string) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// Attach token before each request if available
api.interceptors.request.use(async config => {
  // Use NextAuth session token if available
  const session = await getSession();
  if (session?.user?.accessToken) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${session.user.accessToken}`;
  }
  return config;
});

export default api;
