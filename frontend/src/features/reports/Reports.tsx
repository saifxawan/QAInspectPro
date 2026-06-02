import React, { useEffect } from 'react';
// No type imports needed here if not used in props/state directly for now
import { useStore } from '../../store/useStore';
import { Card, Button, Badge } from '../../components/ui';
import { Download, Database } from 'lucide-react';
import { cn } from '../../utils/cn';
import { toast } from 'react-toastify';


export const Reports: React.FC = () => {
    const { reportsData, fetchReports, isSyncingReports } = useStore();

    const handleSync = async () => {
        try {
            await fetchReports();
            toast.success("Intelligence analytics compiled successfully.");
        } catch (e) {
            toast.error("Analytics failure. System records unreachable.");
        }
    };

    useEffect(() => {
        if (reportsData.length === 0) handleSync();
    }, []);

    const downloadCSV = (project: any) => {
        const headers = ["ID", "Title", "Category", "Expected", "Status", "Actual"];
        const rows = project.cases.map((c: any) => [c.id, c.title, c.category, c.expected, c.status, c.notes]);
        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e: any[]) => `"${e.join('","')}"`)].join("\n");
        const link = document.createElement("a");
        link.href = encodeURI(csvContent);
        link.download = `QA_Report_${project.project_name.replace(/[^a-z0-9]/gi, '_')}.csv`;
        link.click();
        toast.info(`Exported dataset: ${project.project_name}`);
    };

    return (
        <div className="animate-fade-in space-y-10">
            <Card className="p-8 grow-purple flex flex-col md:flex-row justify-between items-center gap-6">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Database className="text-primary" size={24} /> Quality Assurance Intelligence 
                    </h2>
                    <p className="text-slate-400 mt-1">Export executive-level data for stakeholders and developers.</p>
                </div>
                <Button onClick={handleSync} isLoading={isSyncingReports} className="flex items-center gap-2">
                    Compile Analytics
                </Button>
            </Card>

            <div className="grid grid-cols-1 gap-12">
              {reportsData.length === 0 ? (
                <Card className="py-20 text-center text-slate-500 italic">
                   <p>No analytics found. Compile reports to begin.</p>
                </Card>
              ) : (
                reportsData.map((report: any, idx: number) => (
                  <Card key={idx} className="overflow-hidden border-t-4 border-primary p-0 bg-transparent flex flex-col">
                    <div className="p-8 flex flex-col md:flex-row justify-between items-start gap-6 border-b border-white/5 bg-white/5">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                           <span className="text-xs font-black text-primary uppercase tracking-[0.2em] bg-primary/10 px-3 py-0.5 rounded-full">Report</span>
                           <h3 className="text-2xl font-black text-white">{report.project_name}</h3>
                        </div>
                        <p className="text-slate-500 font-medium">Evaluation of {report.total_cases} system constraints.</p>
                      </div>
                      <Button onClick={() => downloadCSV(report)} variant="secondary" className="bg-slate-900 border-white/5 gap-2 px-8">
                        <Download size={18} /> Export Data
                      </Button>
                    </div>
                    
                    <div className="p-8">
                      <div className="grid grid-cols-3 gap-6 mb-10">
                        <Card className={cn("p-6 bg-status-passed/5 ring-1 ring-status-passed/20 border-0 flex flex-col items-center")}>
                          <span className="text-4xl font-black text-status-passed mb-1">{report.passed}</span>
                          <span className="text-[10px] uppercase font-black text-status-passed/50 tracking-widest text-center">Passed Gates</span>
                        </Card>
                        <Card className="p-6 bg-status-failed/5 ring-1 ring-status-failed/20 border-0 flex flex-col items-center">
                          <span className="text-4xl font-black text-status-failed mb-1">{report.failed}</span>
                          <span className="text-[10px] uppercase font-black text-status-failed/50 tracking-widest text-center">Failures</span>
                        </Card>
                        <Card className="p-6 bg-white/5 ring-1 ring-white/10 border-0 flex flex-col items-center">
                          <span className="text-4xl font-black text-slate-500 mb-1">{report.skipped}</span>
                          <span className="text-[10px] uppercase font-black text-slate-500 tracking-widest text-center">Scheduled</span>
                        </Card>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="flex justify-between items-center mb-2">
                           <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Gate Performance Log</h4>
                        </div>
                        <div className="max-h-80 overflow-y-auto border border-white/5 rounded-2xl bg-black/20">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead className="bg-[#0f172a] sticky top-0 shadow-sm">
                              <tr>
                                <th className="px-6 py-3 text-slate-500 font-bold uppercase tracking-tighter">ID</th>
                                <th className="px-6 py-3 text-slate-500 font-bold uppercase tracking-tighter">Status</th>
                                <th className="px-6 py-3 text-slate-500 font-bold uppercase tracking-tighter w-full">Evaluation Output</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                              {report.cases.map((tc: any, j: number) => (
                                <tr key={j} className="hover:bg-white/[0.01]">
                                  <td className="px-6 py-4 font-mono text-slate-600">{tc.id}</td>
                                  <td className="px-6 py-4">
                                    <Badge status={tc.status} />
                                  </td>
                                  <td className="px-6 py-4 text-slate-400 font-medium truncate max-w-sm">{tc.notes}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
        </div>
    );
};
