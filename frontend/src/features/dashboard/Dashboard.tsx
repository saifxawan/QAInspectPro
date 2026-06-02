import React, { useState, useCallback } from 'react';
import { useStore } from '../../store/useStore';
import { Lightbulb, Zap, Search, RefreshCw, Activity, Shield, Clock, TrendingUp, AlertTriangle, CheckCircle, XCircle, Globe } from 'lucide-react';
import { Card, Button, Badge, Skeleton, ProgressBar, EmptyState } from '../../components/ui';
import { cn } from '../../utils/cn';
import { toast } from 'react-toastify';
import type { Recommendation, TrendDataPoint } from '../../types';

export const Dashboard: React.FC = () => {
  const { 
    targetUrl, 
    setTargetUrl, 
    isScanning,
    isBackgroundScanning,
    scanResults, 
    runScan, 
    stats, 
    recentTests, 
    fetchDashboardData,
    trendData,
    isLoading,
    error
  } = useStore();

  const [localError, setLocalError] = useState<string | null>(null);
  const [expandedTestId, setExpandedTestId] = useState<string | null>(null);

  // Lifecycle sync with proper cleanup
  React.useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    let pollCount = 0;
    const MAX_POLLS = 30; // Stop polling after 30 attempts (150 seconds)
    
    if (isBackgroundScanning) {
      interval = setInterval(async () => {
        pollCount++;
        if (pollCount > MAX_POLLS) {
          useStore.getState().isBackgroundScanning = false;
          toast.warning("Scan is taking longer than expected. Results will appear when ready.");
          if (interval) clearInterval(interval);
          return;
        }
        await fetchDashboardData();
      }, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isBackgroundScanning, fetchDashboardData]);

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLocalError(null);
    
    if (!targetUrl || !targetUrl.trim()) {
      toast.error("Please enter a valid URL target.");
      setLocalError("URL is required");
      return;
    }
    
    // Normalize URL
    let finalUrl = targetUrl.trim();
    if (!finalUrl.startsWith('http')) {
      finalUrl = 'https://' + finalUrl;
      setTargetUrl(finalUrl);
    }

    // Basic URL validation
    try {
      new URL(finalUrl);
    } catch {
      toast.error("Please enter a valid URL format.");
      setLocalError("Invalid URL format");
      return;
    }

    try {
      const response = await runScan(finalUrl);
      if (response && 'status' in response && response.status === 'initiated') {
        toast.success(('message' in response ? response.message : '') || "Scan initiated successfully!");
      } else if (response && 'system_health_score' in response) {
        toast.success("Scan completed successfully!");
      }
    } catch {
      toast.error("Scan failed. Please verify the URL and try again.");
      setLocalError("Scan failed - check URL and connectivity");
    }
  };

  const syncAll = async () => {
    try {
      await fetchDashboardData();
      toast.info("Dashboard data refreshed.");
    } catch (e) {
      toast.error("Failed to refresh data.");
    }
  };

  const getRecommendations = useCallback((): Recommendation[] => {
    if (!scanResults) return [];
    
    const recs: Recommendation[] = [];
    
    if (scanResults.security?.issues && scanResults.security.issues.length > 0) {
      recs.push({ 
        title: "Security Headers Required", 
        desc: `${scanResults.security.issues.length} security issue(s) detected. Review and implement missing security headers (CSP, HSTS, X-Frame-Options).`, 
        type: "security" 
      });
    }
    
    if (scanResults.performance?.load_time_seconds > 2.0) {
      recs.push({ 
        title: "Performance Optimization Needed", 
        desc: `Page load time is ${scanResults.performance.load_time_seconds.toFixed(2)}s. Target should be under 2.0s. Consider optimizing images, enabling caching, and minifying resources.`, 
        type: "performance" 
      });
    }
    
    if (scanResults.security?.ssl_info?.status !== 'Valid' && scanResults.security?.ssl_info?.status) {
      recs.push({ 
        title: "SSL Certificate Review", 
        desc: `SSL status: ${scanResults.security.ssl_info.status}. Ensure your certificate is valid and not expiring soon.`, 
        type: "security" 
      });
    }

    if (scanResults.seo?.failed_count && scanResults.seo.failed_count > 0) {
      recs.push({
        title: "SEO & Accessibility Issues",
        desc: `${scanResults.seo.failed_count} accessibility/SEO issue(s) detected. Review image alt text, headings structure, and HTML semantic elements to improve user experience and search ranking.`,
        type: "general"
      });
    }

    if (recs.length === 0 && scanResults) {
      recs.push({
        title: "System Running Optimally",
        desc: "No critical issues detected. Continue monitoring for optimal performance.",
        type: "general"
      });
    }
    
    return recs;
  }, [scanResults]);

  // Quality Trend Chart Component
  const QualityTrendChart: React.FC = () => {
    const data: TrendDataPoint[] = trendData || [];
    const maxValue = Math.max(...data.map(d => d.value), 100);
    
    return (
      <Card className="bg-white/5 border-0 p-6 flex-1">
        <div className="flex justify-between items-center mb-6">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Quality Trend (Last 7 Days)</h4>
          <TrendingUp className="text-primary/50" size={16} />
        </div>
        <div className="h-32 flex items-end gap-2">
          {data.map((point, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-2 group">
              <span className="text-[10px] text-primary font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                {point.value}%
              </span>
              <div 
                className="w-full bg-gradient-to-t from-primary/20 to-primary/60 rounded-t-md group-hover:from-primary/40 group-hover:to-primary/80 transition-all duration-300 relative"
                style={{ height: `${(point.value / maxValue) * 100}%`, minHeight: '8px' }}
              />
              <span className="text-[9px] text-slate-500 font-mono">{point.day}</span>
            </div>
          ))}
        </div>
      </Card>
    );
  };

  // Health Score Gauge Component
  const HealthScoreGauge: React.FC<{ score: number; status: string }> = ({ score, status }) => {
    const circumference = 2 * Math.PI * 44;
    const offset = circumference - (score / 100) * circumference;
    
    const getColor = () => {
      if (score >= 80) return 'text-status-passed';
      if (score >= 50) return 'text-status-skipped';
      return 'text-status-failed';
    };

    return (
      <Card className="bg-white/5 p-6 border-0 flex flex-col items-center justify-center text-center w-full lg:w-64">
        <div className="relative w-28 h-28 mb-4">
          <svg className="w-full h-full transform -rotate-90">
            <circle 
              cx="56" cy="56" r="44" 
              stroke="currentColor" strokeWidth="8" fill="transparent" 
              className="text-white/5" 
            />
            <circle 
              cx="56" cy="56" r="44" 
              stroke="currentColor" strokeWidth="8" fill="transparent" 
              strokeDasharray={circumference} 
              strokeDashoffset={offset} 
              strokeLinecap="round"
              className={cn(getColor(), "transition-all duration-1000")} 
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn("text-3xl font-black", getColor())}>{score}</span>
            <span className="text-[10px] text-slate-500 uppercase">/100</span>
          </div>
        </div>
        <h3 className="font-bold text-white text-sm mb-1">Health Score</h3>
        <Badge status={status} size="sm" />
      </Card>
    );
  };

  // Loading State
  if (isLoading && stats.length === 0) {
    return (
      <div className="space-y-8">
        <Card className="p-8">
          <div className="flex items-center gap-4 mb-6">
            <Skeleton variant="circle" className="w-10 h-10" />
            <Skeleton className="w-48 h-8" />
          </div>
          <Skeleton className="w-full h-14 mb-6" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Skeleton variant="card" className="h-40" />
            <Skeleton variant="card" className="h-40" />
          </div>
        </Card>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} variant="card" className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Error Banner */}
      {error && (
        <Card className="bg-status-failed/10 border border-status-failed/30 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-status-failed" size={20} />
            <span className="text-status-failed text-sm font-medium">{error}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => useStore.getState().clearError()}>
            Dismiss
          </Button>
        </Card>
      )}

      {/* Intelligence Scan Panel */}
      <Card className="p-8 glow-purple border border-white/10">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <Zap className="text-primary" size={24} /> 
            <span>Intelligence Scan</span>
          </h2>
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              onClick={syncAll} 
              size="sm"
              className="text-[10px] font-bold uppercase tracking-widest border-white/5 bg-white/5"
              disabled={isLoading}
            >
              <RefreshCw className={cn(isLoading && "animate-spin", "mr-2")} size={14} />
              Refresh
            </Button>
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest bg-white/5 px-3 py-1 rounded-full">
              v2.2.0
            </span>
          </div>
        </div>
        
        <form onSubmit={handleFormSubmit} className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="relative flex-1 group">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors pointer-events-none" size={20} />
            <input 
              type="text" 
              value={targetUrl}
              onChange={(e) => { setTargetUrl(e.target.value); setLocalError(null); }}
              placeholder="Enter target URL (e.g., https://example.com)" 
              className={cn(
                "w-full bg-slate-950/50 border rounded-2xl pl-14 pr-6 py-4 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white placeholder-slate-600 transition-all text-base font-medium",
                localError ? "border-status-failed/50" : "border-white/10 group-hover:border-white/20"
              )}
              autoFocus
              autoComplete="off"
              disabled={isScanning}
            />
            {localError && (
              <p className="text-status-failed text-xs mt-2 ml-2">{localError}</p>
            )}
          </div>
          <Button 
            type="submit" 
            isLoading={isScanning} 
            disabled={!targetUrl.trim() || isScanning} 
            className="min-w-[180px] h-[58px] text-base"
          >
            {isScanning ? 'Scanning...' : 'Execute Scan'}
          </Button>
        </form>

        <div className="flex flex-col lg:flex-row gap-6">
          <QualityTrendChart />
          
          {scanResults && scanResults.performance && scanResults.security ? (
            <HealthScoreGauge 
              score={scanResults.system_health_score || 0} 
              status={scanResults.summary?.status || 'Unknown'} 
            />
          ) : isBackgroundScanning || isScanning ? (
            <Card className="bg-white/5 border-0 p-6 flex flex-col items-center justify-center text-center w-full lg:w-64">
              <div className="flex flex-col items-center gap-4">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
                  <Activity className="absolute inset-0 m-auto text-primary" size={24} />
                </div>
                <div>
                  <span className="text-white font-bold block mb-1">Analyzing Target</span>
                  <span className="text-slate-400 text-xs">Running security & performance checks...</span>
                </div>
              </div>
            </Card>
          ) : (
            <Card className="bg-white/5 border-0 p-6 flex flex-col items-center justify-center text-center w-full lg:w-64">
              <EmptyState
                title="No Scan Data"
                description="Enter a URL above and click Execute Scan to begin analysis."
                icon={<Search className="text-slate-600" size={24} />}
              />
            </Card>
          )}
        </div>

        {/* Detailed Results */}
        {scanResults && scanResults.performance && scanResults.security && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in pt-6 border-t border-white/5">
            {/* Performance Detail */}
            <Card className="bg-white/5 p-6 border-0">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-primary/10 rounded-xl">
                    <Activity className="text-primary" size={16} />
                  </div>
                  <span className="font-bold text-white text-sm">Performance Metrics</span>
                </div>
                <Badge status={scanResults.performance?.status} size="sm" />
              </div>
              <div className="space-y-5">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-400 text-sm">Response Time</span>
                    <span className="text-lg font-bold text-white">{scanResults.performance?.load_time_seconds?.toFixed(2) || '0.00'}s</span>
                  </div>
                  <ProgressBar 
                    value={scanResults.performance?.performance_score || 0} 
                    color={scanResults.performance?.load_time_seconds > 2 ? 'warning' : 'success'}
                    showLabel
                  />
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Status Code</span>
                    <span className="text-white font-mono font-bold">
                      {scanResults.performance?.status_code || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Content Size</span>
                    <span className="text-white font-mono font-bold">
                      {scanResults.performance?.content_size_kb ? `${(scanResults.performance.content_size_kb / 1024).toFixed(1)}MB` : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Security Detail */}
            <Card className="bg-white/5 p-6 border-0">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-accent/10 rounded-xl">
                    <Shield className="text-accent" size={16} />
                  </div>
                  <span className="font-bold text-white text-sm">Security Analysis</span>
                </div>
                <Badge status={scanResults.security?.status} size="sm" />
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-3">
                    {scanResults.security?.ssl_info?.status === 'Valid' ? (
                      <CheckCircle className="text-status-passed" size={18} />
                    ) : (
                      <XCircle className="text-status-failed" size={18} />
                    )}
                    <span className="text-slate-300 text-sm">SSL Certificate</span>
                  </div>
                  <span className={cn(
                    "font-bold text-sm",
                    scanResults.security?.ssl_info?.status === 'Valid' ? 'text-status-passed' : 'text-status-failed'
                  )}>
                    {scanResults.security?.ssl_info?.status || 'N/A'}
                  </span>
                </div>
                
                {scanResults.security?.issues && scanResults.security.issues.length > 0 ? (
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-3">
                      Detected Issues ({scanResults.security.issues.length})
                    </span>
                    <ul className="space-y-2">
                      {scanResults.security.issues.slice(0, 3).map((issue: string, i: number) => (
                        <li key={i} className="text-xs text-status-failed flex gap-2 items-start bg-status-failed/5 p-2 rounded">
                          <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
                          <span>{issue}</span>
                        </li>
                      ))}
                      {scanResults.security.issues.length > 3 && (
                        <li className="text-xs text-slate-400 text-center py-2">
                          +{scanResults.security.issues.length - 3} more issues
                        </li>
                      )}
                    </ul>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 p-3 bg-status-passed/5 rounded-lg">
                    <CheckCircle className="text-status-passed" size={18} />
                    <span className="text-status-passed text-sm font-medium">No security issues detected</span>
                  </div>
                )}
              </div>
            </Card>

            {/* SEO & Accessibility Detail */}
            <Card className="bg-white/5 p-6 border-0">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-status-passed/10 rounded-xl">
                    <Globe className="text-status-passed" size={16} />
                  </div>
                  <span className="font-bold text-white text-sm">SEO & Accessibility SQA</span>
                </div>
                <Badge status={scanResults.seo?.status || 'Passed'} size="sm" />
              </div>
              <div className="space-y-5">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-400 text-sm">a11y Compliance</span>
                    <span className="text-lg font-bold text-white">{(scanResults.seo?.score ?? 100)}%</span>
                  </div>
                  <ProgressBar 
                    value={scanResults.seo?.score ?? 100} 
                    color={(scanResults.seo?.score ?? 100) < 80 ? 'warning' : 'success'}
                    showLabel
                  />
                </div>
                
                {scanResults.seo?.issues && scanResults.seo.issues.length > 0 ? (
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-3">
                      Accessibility & SEO Findings ({scanResults.seo.issues.length})
                    </span>
                    <ul className="space-y-2">
                      {scanResults.seo.issues.slice(0, 3).map((issue: string, i: number) => (
                        <li key={i} className="text-xs text-amber-400 flex gap-2 items-start bg-amber-400/5 p-2 rounded">
                          <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
                          <span>{issue}</span>
                        </li>
                      ))}
                      {scanResults.seo.issues.length > 3 && (
                        <li className="text-xs text-slate-400 text-center py-2">
                          +{scanResults.seo.issues.length - 3} more findings
                        </li>
                      )}
                    </ul>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 p-3 bg-status-passed/5 rounded-lg pt-4 border-t border-white/5">
                    <CheckCircle className="text-status-passed" size={18} />
                    <span className="text-status-passed text-sm font-medium">100% semantic HTML & a11y compliant</span>
                  </div>
                )}
              </div>
            </Card>
          </div>
        )}
      </Card>

      {/* Recommendations Section */}
      {scanResults && getRecommendations().length > 0 && (
        <section className="animate-slide-up">
          <h3 className="text-lg font-bold text-white mb-5 flex items-center gap-3">
            <Lightbulb className="text-accent" size={20} /> 
            <span>Actionable Intelligence</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {getRecommendations().map((rec: Recommendation, i: number) => (
              <Card 
                key={i} 
                className={cn(
                  "border-l-4 transition-all duration-300 hover:translate-x-1",
                  rec.type === 'security' ? 'border-l-accent' : 
                  rec.type === 'performance' ? 'border-l-primary' : 'border-l-status-passed'
                )}
              >
                <div className="flex items-start gap-4">
                  <div className={cn(
                    "p-2 rounded-lg flex-shrink-0",
                    rec.type === 'security' ? 'bg-accent/10' : 
                    rec.type === 'performance' ? 'bg-primary/10' : 'bg-status-passed/10'
                  )}>
                    {rec.type === 'security' ? <Shield size={18} className="text-accent" /> :
                     rec.type === 'performance' ? <Activity size={18} className="text-primary" /> :
                     <CheckCircle size={18} className="text-status-passed" />}
                  </div>
                  <div>
                    <h4 className="font-bold text-white mb-1.5">{rec.title}</h4>
                    <p className="text-sm text-slate-400 leading-relaxed">{rec.desc}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Stats Grid */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {stats.map((stat, idx) => (
          <Card key={idx} className="group hover:bg-white/5 transition-all duration-300">
            <div className="flex justify-between items-start mb-3">
              <span className="text-2xl group-hover:scale-110 transition-transform duration-300">{stat.icon}</span>
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            </div>
            <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">{stat.label}</h3>
            <div className={cn("text-2xl font-black truncate", stat.color || "text-white")}>
              {stat.value}
            </div>
          </Card>
        ))}
      </section>

      {/* Recent Tests Table */}
      <Card className="overflow-hidden p-0 bg-transparent border-white/5">
        <div className="p-5 border-b border-white/5 flex justify-between items-center">
          <h2 className="text-lg font-bold text-white flex items-center gap-3">
            <Clock className="text-slate-400" size={20} />
            Real-time Test Stream
          </h2>
          <div className="flex items-center gap-3">
            <span className="text-[10px] text-slate-400 bg-white/5 px-2.5 py-1 rounded-full font-mono">
              Click rows to inspect findings
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              {recentTests.length} entries
            </span>
          </div>
        </div>
        
        {recentTests.length === 0 ? (
          <EmptyState
            title="No Test Data Available"
            description="Test results will appear here once scans are executed. Run your first scan to get started."
            icon={<Activity className="text-slate-600" size={32} />}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-950/50 text-slate-500 text-[10px] uppercase font-bold tracking-widest">
                <tr>
                  <th className="px-6 py-4 w-28">Test ID</th>
                  <th className="px-6 py-4">Title</th>
                  <th className="px-6 py-4 w-48">Category</th>
                  <th className="px-6 py-4 w-32">Executed At</th>
                  <th className="px-6 py-4 w-28">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-sm">
                {recentTests.map((rt, i) => {
                  const isExpanded = expandedTestId === rt.id;
                  
                  // Helper inside map or inline
                  const getRelativeTime = (iso: string) => {
                    try {
                      const d = new Date(iso);
                      const now = new Date();
                      const diff = now.getTime() - d.getTime();
                      const mins = Math.floor(diff / 60000);
                      const hrs = Math.floor(diff / 3600000);
                      
                      if (mins < 1) return 'Just now';
                      if (mins < 60) return `${mins}m ago`;
                      if (hrs < 24) return `${hrs}h ago`;
                      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
                    } catch {
                      return '-';
                    }
                  };

                  return (
                    <React.Fragment key={i}>
                      <tr 
                        onClick={() => setExpandedTestId(isExpanded ? null : rt.id)}
                        className={cn(
                          "hover:bg-white/[0.03] transition-colors group cursor-pointer",
                          isExpanded && "bg-white/[0.02]"
                        )}
                      >
                        <td className="px-6 py-4 font-mono text-xs text-slate-500 group-hover:text-primary transition-colors">
                          {rt.id}
                        </td>
                        <td className="px-6 py-4 text-slate-300 font-medium group-hover:text-white transition-colors" title={rt.title}>
                          <div className="flex items-center gap-2">
                            <span className="truncate max-w-sm">{rt.title}</span>
                            <span className="text-[10px] text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">
                              {isExpanded ? '▲ hide' : '▼ expand'}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-slate-400 text-xs">
                          <span className="bg-white/5 px-2.5 py-1 rounded text-[10px] border border-white/5">{rt.category}</span>
                        </td>
                        <td className="px-6 py-4 text-slate-400 text-xs font-mono">
                          {getRelativeTime(rt.executed_at)}
                        </td>
                        <td className="px-6 py-4">
                          <Badge status={rt.status} size="sm" />
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-slate-950/20">
                          <td colSpan={5} className="px-8 py-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs bg-slate-950/60 p-6 rounded-2xl border border-white/5 shadow-2xl animate-slide-down">
                              <div className="space-y-2">
                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Expected Outcome</span>
                                <div className="p-3 bg-white/5 rounded-lg text-slate-300 border border-white/5 font-medium leading-relaxed">
                                  {rt.expected || "Verify standard quality metrics."}
                                </div>
                              </div>
                              <div className="space-y-2">
                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Observed Findings</span>
                                <div className={cn(
                                  "p-3 rounded-lg border font-medium leading-relaxed",
                                  rt.status === 'Passed' ? 'bg-status-passed/5 border-status-passed/20 text-status-passed' :
                                  rt.status === 'Failed' ? 'bg-status-failed/5 border-status-failed/20 text-status-failed' :
                                  'bg-status-skipped/5 border-status-skipped/20 text-status-skipped'
                                )}>
                                  {rt.actual || "Verified successfully."}
                                </div>
                              </div>
                              {rt.error && (
                                <div className="col-span-1 md:col-span-2 space-y-2 pt-3 border-t border-white/5">
                                  <span className="text-[10px] font-bold text-status-failed uppercase tracking-widest flex items-center gap-1.5">
                                    <AlertTriangle size={12} /> SQA Automated Quality Gate Failure Detail
                                  </span>
                                  <div className="p-3 bg-status-failed/5 border border-status-failed/20 rounded-lg text-slate-300 font-mono text-[11px] whitespace-pre-wrap">
                                    {rt.error}
                                  </div>
                                </div>
                              )}
                              <div className="col-span-1 md:col-span-2 flex justify-between items-center text-[10px] text-slate-500 font-mono pt-3 border-t border-white/5">
                                <span>Automation Code: SQA-AUTO-GATE-{rt.id.split('-')[1] || rt.id}</span>
                                <span>Executed At: {new Date(rt.executed_at).toLocaleString()}</span>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};