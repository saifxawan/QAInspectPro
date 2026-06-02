export interface SecurityIssue {
  status: string;
  issues: string[];
  ssl_info: {
    status: string;
    expiry: string | null;
    issuer: string | null;
  };
  headers_found: Record<string, string>;
  security_score: number;
}

export interface PerformanceStats {
  status: string;
  load_time_seconds: number;
  content_size_kb: number;
  status_code: number;
  performance_score: number;
}

export interface SEOStats {
  status: string;
  score: number;
  failed_count: number;
  issues: string[];
}

export interface ScanResult {
  target_url: string;
  timestamp: string;
  security: SecurityIssue;
  performance: PerformanceStats;
  seo?: SEOStats;
  system_health_score: number;
  summary: {
    critical_issues: number;
    status: string;
  };
}

export interface TestProject {
  project_name: string;
  total_cases: number;
  cases: TestCase[];
}

export interface TestCase {
  id: string;
  title: string;
  category: string;
  expected: string;
  status?: TestStatus;
  notes?: string;
}

export interface ReportData extends TestProject {
  passed: number;
  failed: number;
  skipped: number;
}

export type TestStatus = 'Passed' | 'Failed' | 'Warning' | 'Skipped';

export interface DashboardStat {
  label: string;
  value: string | number;
  icon: string;
  color?: string;
}

export interface RecentTest {
  id: string;
  title: string;
  category: string;
  status: TestStatus;
  execution_time?: string;
  executed_at: string;
  actual?: string;
  expected?: string;
  error?: string | null;
}

export interface Recommendation {
  title: string;
  desc: string;
  type: 'security' | 'performance' | 'general';
}

export interface TrendDataPoint {
  day: string;
  value: number;
}