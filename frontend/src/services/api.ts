import axios from 'axios';
import type { ReportData, TestProject } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to add auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  login: async (username: string, password: string): Promise<{ access_token: string }> => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const { data } = await client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Scans
  runScan: async (url: string): Promise<any> => {
    const { data } = await client.post('/scan/', { url });
    return data;
  },

  getScanResults: async (url: string): Promise<any> => {
    const { data } = await client.get(`/scan/results/${encodeURIComponent(url)}`);
    return data;
  },



  // Dashboard
  getStats: async (url?: string) => {
    const { data } = await client.get('/dashboard/stats', {
      params: url ? { target_url: url } : undefined
    });
    return data;
  },

  getRecentTests: async (url?: string) => {
    const { data } = await client.get('/dashboard/recent-tests', {
      params: url ? { target_url: url } : undefined
    });
    return data.data;
  },

  // Test Cases
  getTestCases: async (): Promise<TestProject[]> => {
    const { data } = await client.get('/testcases/');
    return data.data;
  },

  // Reports
  getReports: async (): Promise<ReportData[]> => {
    const { data } = await client.get('/reports/');
    return data.data;
  },
};
