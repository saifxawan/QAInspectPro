import { Suspense, lazy, useEffect } from 'react';
import { Helmet, HelmetProvider } from 'react-helmet-async';
import { useStore } from './store/useStore';
import { Layout } from './components/layout/Layout';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Lazy load features for performance (Phase 3 & 4)
const Dashboard = lazy(() => import('./features/dashboard/Dashboard').then(m => ({ default: m.Dashboard })));
const TestCases = lazy(() => import('./features/test-cases/TestCases').then(m => ({ default: m.TestCases })));
const Reports = lazy(() => import('./features/reports/Reports').then(m => ({ default: m.Reports })));

const LoadingFallback = () => (
  <div className="min-h-[60vh] flex flex-col items-center justify-center gap-6 animate-pulse">
    <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center shadow-lg animate-spin">
       <div className="w-10 h-10 border-2 border-white/20 border-t-white rounded-full"></div>
    </div>
    <p className="text-slate-500 font-mono text-xs uppercase tracking-[0.3em]">Initializing QA Intelligence...</p>
  </div>
);

function App() {
  const { activeTab, fetchDashboardData, isAuthenticated, setActiveTab } = useStore();

  // Force dashboard on load and skip auth
  useEffect(() => {
    setActiveTab('dashboard');
    fetchDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Skip authentication - go directly to dashboard
  if (!isAuthenticated) {
    // Auto-login as admin for demo purposes
    const autoLogin = async () => {
      try {
        await useStore.getState().login('admin', 'admin123');
      } catch (e) {
        console.error('Auto-login failed:', e);
      }
    };
    autoLogin();
    
    return (
      <HelmetProvider>
        <div className="min-h-screen flex items-center justify-center bg-[#0b1120]">
          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center shadow-lg animate-spin mx-auto mb-4">
              <div className="w-10 h-10 border-2 border-white/20 border-t-white rounded-full"></div>
            </div>
            <p className="text-slate-500 font-mono text-xs uppercase tracking-[0.3em]">Initializing QA Intelligence...</p>
          </div>
        </div>
        <ToastContainer position="bottom-right" theme="dark" autoClose={3000} />
      </HelmetProvider>
    );
  }

  const renderContent = () => {

    switch (activeTab) {
      case 'dashboard': return <Dashboard />;
      case 'testcases': return <TestCases />;
      case 'reports': return <Reports />;
      default: return <Dashboard />;
    }
  };

  return (
    <HelmetProvider>
      <Helmet>
        <title>QAInspect Pro | Enterprise SQA Intelligence Dashboard</title>
        <meta name="description" content="Automated SQA platform for security, performance, and functional intelligence." />
        <meta property="og:title" content="QAInspect Pro" />
        <meta property="og:description" content="Next-Gen Software Quality Intelligence" />
      </Helmet>

      <Layout>
        <Suspense fallback={<LoadingFallback />}>
          {renderContent()}
        </Suspense>
      </Layout>
      <ToastContainer position="bottom-right" theme="dark" autoClose={3000} />
    </HelmetProvider>
  );
}

export default App;
