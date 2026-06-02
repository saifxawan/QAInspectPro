import React, { useEffect } from 'react';
import { useStore } from '../../store/useStore';
import { Card, Button } from '../../components/ui';
import { RefreshCw, ClipboardList } from 'lucide-react';
import { toast } from 'react-toastify';


export const TestCases: React.FC = () => {
    const { allTestCases, fetchTestCases, setActiveTab, isSyncingCases } = useStore();

    const handleSync = async () => {
        try {
            await fetchTestCases();
            toast.success("Assertion repository synchronized.");
        } catch (e) {
            toast.error("Failed to sync repository.");
        }
    };

    useEffect(() => {
        if (allTestCases.length === 0) handleSync();
    }, []);

    return (
        <div className="animate-fade-in space-y-8">
            <Card className="p-8 grow-purple flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <ClipboardList className="text-primary" size={24} /> Assertion Repository
                    </h2>
                    <p className="text-slate-400 mt-1 max-w-xl">1000+ Pre-defined Quality Gates mapping Functional, Performance, and Security targets.</p>
                </div>
                <Button onClick={handleSync} isLoading={isSyncingCases} variant="ghost" className="flex items-center gap-2">
                    <RefreshCw size={16} /> Sync Data
                </Button>
            </Card>

            <div className="p-0">
                {allTestCases.length === 0 ? (
                    <Card className="text-center py-20 text-slate-500">
                        <p className="mb-4">Repository is empty.</p>
                        <button onClick={() => setActiveTab('dashboard')} className="text-primary font-bold hover:underline">Launch a Scan to Provision Cases →</button>
                    </Card>
                ) : (
                    <div className="grid grid-cols-1 gap-8">
                        {allTestCases.map((project: any, i: number) => (
                            <Card key={i} className="overflow-hidden p-0 border-white/5">
                                <div className="flex bg-slate-950/80 px-6 py-4 items-center justify-between border-b border-white/5">
                                    <div className="flex items-center gap-3">
                                        <div className="w-2 h-2 rounded-full bg-primary shadow-[0_0_10px_#3B82F6]" />
                                        <h3 className="font-bold text-white">{project.project_name}</h3>
                                    </div>
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-tighter bg-white/5 px-2 py-1 rounded-full">{project.total_cases} Assertions</span>
                                </div>
                                <div className="max-h-[500px] overflow-y-auto">
                                    <table className="w-full text-left text-xs">
                                        <tbody className="divide-y divide-white/5">
                                            {project.cases.map((tc: any, j: number) => (
                                                <tr key={j} className="hover:bg-white/[0.02] group transition-colors">
                                                    <td className="px-6 py-4 font-mono text-slate-600 w-24 group-hover:text-primary">{tc.id}</td>
                                                    <td className="px-6 py-4 text-slate-300 font-medium">{tc.title}</td>
                                                    <td className="px-6 py-4">
                                                        <span className="bg-white/5 text-slate-400 px-2 py-1 rounded text-[10px] uppercase font-black tracking-widest">{tc.category}</span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
