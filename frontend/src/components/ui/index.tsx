import React from 'react';

import { cn } from '../../utils/cn';
import type { TestStatus } from '../../types';

// --- Card ---
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
}
export const Card: React.FC<CardProps> = ({ className, glass = true, children, ...props }) => (
  <div className={cn(glass ? "glass-panel" : "bg-dark-card border border-white/5", "p-6 rounded-2xl", className)} {...props}>
    {children}
  </div>
);

// --- Button ---
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  isLoading?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  isLoading, 
  children, 
  className, 
  size = 'md',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'px-4 py-1.5 text-sm rounded-lg',
    md: 'px-6 py-2.5 rounded-xl',
    lg: 'px-8 py-3 rounded-2xl text-lg'
  };

  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'bg-dark-bg border border-white/10 hover:bg-white/5 text-slate-300',
    ghost: 'bg-transparent hover:bg-white/5 text-slate-300',
    danger: 'bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30'
  };

  return (
    <button 
      className={cn(
        variantClasses[variant],
        sizeClasses[size],
        'font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2',
        className
      )}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading && <span className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></span>}
      {children}
    </button>
  );
};

// --- Badge ---
interface BadgeProps {
  status: TestStatus | 'Passed' | 'Failed' | 'Warning' | 'Skipped' | string;
  size?: 'sm' | 'md';
}
export const Badge: React.FC<BadgeProps> = ({ status, size = 'md' }) => {
  // Normalize status to known values
  const normalizedStatus = status === 'Pass' ? 'Passed' : 
                           status === 'Fail' ? 'Failed' : 
                           status === 'Warning' ? 'Warning' : 
                           status === 'Skipped' ? 'Skipped' : 
                           status === 'Healthy' ? 'Passed' :
                           status === 'Stable' ? 'Warning' :
                           status === 'Requires Review' ? 'Warning' :
                           status === 'processing' ? 'Skipped' :
                           status;

  const styles = {
    Passed: 'badge-passed',
    Failed: 'badge-failed',
    Warning: 'badge-skipped',
    Skipped: 'badge-skipped'
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[8px]',
    md: 'px-3 py-1 text-[10px]'
  };

  const baseStyle = styles[normalizedStatus as keyof typeof styles] || 'badge-skipped';
  
  return (
    <span className={cn(baseStyle, sizeClasses[size])} role="status" aria-label={`Status: ${normalizedStatus}`}>
      {normalizedStatus}
    </span>
  );
};

// --- Loading Skeleton ---
interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'circle' | 'rect';
}
export const Skeleton: React.FC<SkeletonProps> = ({ className, variant = 'text' }) => {
  const variants = {
    text: 'h-4 rounded',
    card: 'h-32 rounded-2xl',
    circle: 'rounded-full',
    rect: 'rounded-lg'
  };

  return (
    <div 
      className={cn(
        'bg-white/5 animate-pulse',
        variants[variant],
        className
      )}
    />
  );
};

// --- Progress Bar ---
interface ProgressBarProps {
  value: number;
  max?: number;
  color?: 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}
export const ProgressBar: React.FC<ProgressBarProps> = ({ 
  value, 
  max = 100, 
  color = 'primary', 
  size = 'md',
  showLabel = false 
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  const colors = {
    primary: 'bg-primary',
    success: 'bg-status-passed',
    warning: 'bg-status-skipped',
    danger: 'bg-status-failed'
  };

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  return (
    <div className="w-full">
      <div className={cn('w-full bg-white/10 rounded-full overflow-hidden', sizes[size])}>
        <div 
          className={cn('h-full transition-all duration-1000 ease-out', colors[color])} 
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="text-xs text-slate-400 mt-1 text-right">{percentage.toFixed(0)}%</div>
      )}
    </div>
  );
};

// --- Empty State ---
interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}
export const EmptyState: React.FC<EmptyStateProps> = ({ 
  title, 
  description, 
  icon,
  action 
}) => (
  <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
    {icon && (
      <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mb-4">
        {icon}
      </div>
    )}
    <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
    <p className="text-slate-400 text-sm max-w-md mb-6">{description}</p>
    {action}
  </div>
);