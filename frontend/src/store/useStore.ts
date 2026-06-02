import { create } from 'zustand';
import { api } from '../services/api';
import type { ScanResult, ReportData, TestProject, DashboardStat, RecentTest } from '../types';

interface AppStore {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  targetUrl: string;
  setTargetUrl: (url: string) => void;
  isScanning: boolean;
  isBackgroundScanning: boolean;
  isSyncingCases: boolean;
  isSyncingReports: boolean;
  isLoading: boolean;
  scanResults: ScanResult | null;
  stats: DashboardStat[];
  recentTests: RecentTest[];
  allTestCases: TestProject[];
  reportsData: ReportData[];
  trendData: { day: string; value: number }[];
  error: string | null;
  
  // Auth
  isAuthenticated: boolean;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  
  // Actions
  fetchDashboardData: () => Promise<void>;
  runScan: (url: string) => Promise<ScanResult | { status: string; scan_id: string; message: string } | null>;
  fetchScanResults: (url: string) => Promise<void>;
  fetchTestCases: () => Promise<void>;
  fetchReports: () => Promise<void>;
  clearError: () => void;
  setTrendData: (data: { day: string; value: number }[]) => void;
}

// Generate realistic trend data for the last 7 days
const generateTrendData = (): { day: string; value: number }[] => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map(day => ({
    day,
    value: Math.floor(Math.random() * 30) + 60 // Random values between 60-90
  }));
};

export const useStore = create<AppStore>((set, get) => ({
  activeTab: 'dashboard',
  setActiveTab: (tab) => set({ activeTab: tab }),
  targetUrl: '',
  setTargetUrl: (url) => set({ targetUrl: url }),
  isScanning: false,
  isBackgroundScanning: false,
  isSyncingCases: false,
  isSyncingReports: false,
  isLoading: false,
  scanResults: null,
  stats: [],
  recentTests: [],
  allTestCases: [],
  reportsData: [],
  trendData: generateTrendData(),
  error: null,
  
  isAuthenticated: !!localStorage.getItem('token'),
  token: localStorage.getItem('token'),

  clearError: () => set({ error: null }),

  setTrendData: (data) => set({ trendData: data }),

  login: async (username, password) => {
    const response = await api.login(username, password);
    localStorage.setItem('token', response.access_token);
    set({ token: response.access_token, isAuthenticated: true, error: null });
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, isAuthenticated: false });
  },

  fetchDashboardData: async () => {
    set({ isLoading: true, error: null });
    try {
      const targetUrl = get().targetUrl;
      const [statsData, recentData] = await Promise.all([
        api.getStats(targetUrl),
        api.getRecentTests(targetUrl)
      ]);
      
      // Parse the system_health value properly
      let healthValue = '0';
      if (statsData.system_health) {
        healthValue = statsData.system_health.replace('/100', '');
      }
      
      const healthNum = parseInt(healthValue) || 0;
      
      const newStats: DashboardStat[] = [
        { label: "Tests Executed", value: statsData.total_tests || 0, icon: "📊" },
        { label: "Pass Rate", value: statsData.pass_rate || "0%", color: "text-status-passed", icon: "✅" },
        { label: "Risk Level", value: healthNum < 50 ? "High" : "Low", color: healthNum < 50 ? "text-status-failed" : "text-status-passed", icon: "🛡️" },
        { label: "Health Score", value: `${healthNum}/100`, color: "text-primary", icon: "❤️‍🔥" },
      ];

      set({
        stats: newStats,
        recentTests: recentData || [],
        isLoading: false
      });

      // Also refresh scan results if we have a target
      if (targetUrl && !get().isBackgroundScanning) {
        await get().fetchScanResults(targetUrl);
      }
    } catch (e) {
      console.error("Store sync failed", e);
      set({ 
        error: 'Failed to fetch dashboard data. Please try again.',
        isLoading: false,
        stats: [
          { label: "Tests Executed", value: "0", icon: "📊" },
          { label: "Pass Rate", value: "0%", color: "text-slate-400", icon: "✅" },
          { label: "Risk Level", value: "N/A", color: "text-slate-400", icon: "🛡️" },
          { label: "Health Score", value: "N/A", color: "text-slate-400", icon: "❤️‍🔥" },
        ]
      });
    }
  },

  fetchScanResults: async (url: string) => {
    try {
      const results = await api.getScanResults(url);
      if (results.status === 'success') {
        set({ scanResults: results, isBackgroundScanning: false });
        // Automatically sync all other views
        const [statsData, recentData] = await Promise.all([
          api.getStats(url),
          api.getRecentTests(url),
          api.getTestCases(),
          api.getReports()
        ]);
        
        let healthValue = '0';
        if (statsData.system_health) {
          healthValue = statsData.system_health.replace('/100', '');
        }
        const healthNum = parseInt(healthValue) || 0;
        
        const newStats: DashboardStat[] = [
          { label: "Tests Executed", value: statsData.total_tests || 0, icon: "📊" },
          { label: "Pass Rate", value: statsData.pass_rate || "0%", color: "text-status-passed", icon: "✅" },
          { label: "Risk Level", value: healthNum < 50 ? "High" : "Low", color: healthNum < 50 ? "text-status-failed" : "text-status-passed", icon: "🛡️" },
          { label: "Health Score", value: `${healthNum}/100`, color: "text-primary", icon: "❤️‍🔥" },
        ];

        set({
          stats: newStats,
          recentTests: recentData || [],
          allTestCases: recentData ? await api.getTestCases() : [],
          reportsData: recentData ? await api.getReports() : []
        });
      } else if (results.status === 'processing') {
        set({ isBackgroundScanning: true });
      }
    } catch (e) {
      console.error("Failed to fetch scan results", e);
    }
  },

  runScan: async (url) => {
    set({ isScanning: true, scanResults: null, error: null });
    try {
      const response = await api.runScan(url);
      if (response.security && response.performance) {
        set({ scanResults: response, isScanning: false });
        await get().fetchDashboardData();
        await get().fetchTestCases();
        await get().fetchReports();
      } else if (response.status === 'initiated') {
        set({ isBackgroundScanning: true, isScanning: false });
        return response;
      }
      return response;
    } catch (e) {
      set({ error: 'Scan failed. Please check the URL and try again.', isScanning: false });
      throw e;
    }
  },

  fetchTestCases: async () => {
    set({ isSyncingCases: true });
    try {
      const data = await api.getTestCases();
      set({ allTestCases: data });
    } catch (e) {
      console.error("Failed to fetch test cases", e);
    } finally {
      set({ isSyncingCases: false });
    }
  },

  fetchReports: async () => {
    set({ isSyncingReports: true });
    try {
      const data = await api.getReports();
      set({ reportsData: data });
    } catch (e) {
      console.error("Failed to fetch reports", e);
    } finally {
      set({ isSyncingReports: false });
    }
  }
}));