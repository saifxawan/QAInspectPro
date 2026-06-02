import React from 'react';
import { useStore } from '../../store/useStore';
import { BarChart3, ClipboardCheck, Terminal } from 'lucide-react';
import { cn } from '../../utils/cn';

interface NavItemProps {
  id: string;
  label: string;
  icon: React.ElementType;
}

const NavItem: React.FC<NavItemProps> = ({ id, label, icon: Icon }) => {
  const { activeTab, setActiveTab } = useStore();
  const isActive = activeTab === id;

  return (
    <button
      onClick={() => setActiveTab(id)}
      className={cn(
        'flex items-center gap-3 px-6 py-3 rounded-2xl font-semibold transition-all duration-300',
        isActive 
          ? 'bg-primary text-white shadow-lg shadow-primary/30 scale-105' 
          : 'text-slate-400 hover:text-white hover:bg-white/5'
      )}
    >
      <Icon size={18} />
      <span className="capitalize">{label}</span>
      {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white shadow-[0_0_10px_white]" />}
    </button>
  );
};

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col pt-8 px-6 md:px-12 pb-20 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-[#0b1120] to-[#0b1120]">
      
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center shadow-lg shadow-primary/20">
            <Terminal className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white">QA<span className="text-primary italic">Inspect</span> Pro</h1>
            <p className="text-slate-400 text-sm font-medium">Next-Gen Software Quality Intelligence</p>
          </div>
        </div>
        
        <nav className="flex bg-dark-card/40 p-1.5 rounded-2xl border border-white/5 backdrop-blur-md">
          <NavItem id="dashboard" label="Dashboard" icon={BarChart3} />
          <NavItem id="testcases" label="Test Cases" icon={Terminal} />
          <NavItem id="reports" label="Reports" icon={ClipboardCheck} />
        </nav>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full animate-fade-in">
        {children}
      </main>

      <footer className="mt-20 pt-10 border-t border-white/5 text-center">
         <p className="text-slate-500 text-[10px] font-bold tracking-[0.3em] uppercase">QAInspect Pro &copy; 2026 | Enterprise Edition v2.2.0</p>
      </footer>
    </div>
  );
};
