import React from 'react';
import { useAppStore } from '@/store';
import { GraphViz } from './GraphViz';
import { RingTable } from './RingTable';
import { SuspiciousList } from './SuspiciousList';
import { Download } from 'lucide-react';
import { motion } from 'framer-motion';

export const Dashboard: React.FC = () => {
    const { analysisResult, reset } = useAppStore();

    const handleDownload = () => {
        if (!analysisResult) return;
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analysisResult, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "forensic_report.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    if (!analysisResult) return null;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full h-full flex flex-col gap-6"
        >
            {/* Header Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Total Accounts" value={analysisResult.summary.total_accounts_analyzed} />
                <StatCard label="Suspicious Accounts" value={analysisResult.summary.suspicious_accounts_flagged} highlight="red" />
                <StatCard label="Fraud Rings" value={analysisResult.summary.fraud_rings_detected} highlight="orange" />
                <StatCard label="Processing Time" value={`${analysisResult.summary.processing_time_seconds.toFixed(2)}s`} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
                {/* Main Graph - Takes 2 cols */}
                <div className="lg:col-span-2 h-full flex flex-col gap-2">
                    <div className="flex justify-between items-center">
                        <h2 className="text-xl font-bold">Transaction Network</h2>
                        <div className="flex gap-2">
                            <button onClick={handleDownload} className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                                <Download className="w-3 h-3" /> Export JSON
                            </button>
                            <button onClick={reset} className="px-3 py-1.5 text-xs font-medium bg-muted text-muted-foreground rounded-md hover:bg-muted/80 transition-colors">
                                Reset
                            </button>
                        </div>
                    </div>
                    <GraphViz />
                </div>

                {/* Sidebar - Takes 1 col */}
                <div className="h-full flex flex-col gap-6 overflow-hidden">
                    <SuspiciousList />
                </div>
            </div>

            {/* Bottom Section - Tables */}
            <div className="pb-10">
                <RingTable />
            </div>
        </motion.div>
    );
};

const StatCard = ({ label, value, highlight }: { label: string, value: string | number, highlight?: 'red' | 'orange' }) => (
    <div className={`p-4 rounded-xl border bg-card flex flex-col ${highlight === 'red' ? 'border-red-500/20' :
            highlight === 'orange' ? 'border-orange-500/20' : 'border-border'
        }`}>
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className={`text-2xl font-bold ${highlight === 'red' ? 'text-red-500' :
                highlight === 'orange' ? 'text-orange-500' : 'text-foreground'
            }`}>{value}</span>
    </div>
);
