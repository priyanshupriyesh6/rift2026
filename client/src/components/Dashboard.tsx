import React, { useState } from 'react';
import { useAppStore } from '../store';
import { GraphViz } from './GraphViz';
import { RingTable } from './RingTable';
import { SuspiciousList } from './SuspiciousList';
import { Download, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

export const Dashboard: React.FC = () => {
    const { analysisResult, reset } = useAppStore();
    const [showMethodology, setShowMethodology] = useState(false);

    const handleDownload = () => {
        if (!analysisResult) return;

        // Build the exact JSON format required
        const exportData = {
            suspicious_accounts: analysisResult.suspicious_accounts
                .sort((a, b) => b.suspicion_score - a.suspicion_score) // Sort descending by score
                .map(acc => ({
                    account_id: acc.account_id,
                    suspicion_score: parseFloat(acc.suspicion_score.toFixed(1)),
                    detected_patterns: acc.detected_patterns,
                    ring_id: acc.ring_id || null
                })),
            fraud_rings: analysisResult.fraud_rings.map(ring => ({
                ring_id: ring.ringId,
                member_accounts: ring.memberAccounts,
                pattern_type: ring.patternType,
                risk_score: parseFloat(ring.riskScore.toFixed(1))
            })),
            summary: {
                total_accounts_analyzed: analysisResult.summary.total_accounts_analyzed,
                suspicious_accounts_flagged: analysisResult.summary.suspicious_accounts_flagged,
                fraud_rings_detected: analysisResult.summary.fraud_rings_detected,
                processing_time_seconds: parseFloat(analysisResult.summary.processing_time_seconds.toFixed(2))
            }
        };

        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `forensic_report_${new Date().toISOString().split('T')[0]}.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    if (!analysisResult) return null;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full h-full flex flex-col gap-8"
        >
            {/* Guidance Banner */}
            <div className="bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 rounded-lg p-4">
                <p className="text-sm font-medium text-slate-700">
                    💡 <span className="font-semibold">Start by reviewing the highlighted fraud rings in the network view</span>, then validate risk scores in the summary table below.
                </p>
            </div>

            {/* Early Fraud Alert - Immediate Reassurance */}
            {analysisResult.summary.fraud_rings_detected > 0 && (
                <motion.div 
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-3 bg-orange-50 border border-orange-200 rounded-lg flex items-center gap-3"
                >
                    <span className="text-lg">⚠</span>
                    <span className="font-semibold text-orange-700">Fraud Patterns Detected</span>
                </motion.div>
            )}

            {/* Header Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Total Accounts" value={analysisResult.summary.total_accounts_analyzed} description="Analyzed from uploaded data" />
                <StatCard label="Suspicious Accounts" value={analysisResult.summary.suspicious_accounts_flagged} highlight="red" description="Flagged based on multi-pattern risk score" />
                <StatCard label="Fraud Rings" value={analysisResult.summary.fraud_rings_detected} highlight="orange" description="Distinct coordinated transaction groups" />
                <StatCard label="Processing Time" value={`${analysisResult.summary.processing_time_seconds.toFixed(2)}s`} description="Time to analyze dataset" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
                {/* Main Graph - Takes 2 cols */}
                <div className="lg:col-span-2 h-full flex flex-col gap-3">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-xl font-bold text-slate-900">Network View (Highlighted Fraud Rings)</h2>
                            <p className="text-sm text-slate-500 mt-1">Red clusters indicate coordinated money-muling activity.</p>
                        </div>
                        <div className="flex gap-2">
                            <button onClick={handleDownload} className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg hover:shadow-lg transition-shadow duration-200 shadow-md">
                                <Download className="w-4 h-4" /> Export JSON
                            </button>
                            <button onClick={reset} className="px-4 py-2 text-sm font-semibold bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors duration-200">
                                Reset
                            </button>
                        </div>
                    </div>
                    <div className="flex-1 rounded-xl overflow-hidden border border-slate-200 shadow-lg">
                        <GraphViz />
                    </div>
                </div>

                {/* Sidebar - Takes 1 col */}
                <div className="h-full flex flex-col gap-6 overflow-hidden">
                    <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-lg h-full overflow-hidden">
                        <SuspiciousList />
                    </div>
                </div>
            </div>

            {/* Fraud Alert */}
            {analysisResult.summary.fraud_rings_detected > 0 && (
                <motion.div 
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3"
                >
                    <span className="text-xl">⚠</span>
                    <span className="font-semibold text-red-700">{analysisResult.summary.fraud_rings_detected} Fraud Pattern{analysisResult.summary.fraud_rings_detected > 1 ? 's' : ''} Detected - {analysisResult.summary.suspicious_accounts_flagged} Accounts Flagged</span>
                </motion.div>
            )}

            {/* Collapsible Detection Methodology */}
            <div className="border border-slate-200 rounded-lg overflow-hidden">
                <button
                    onClick={() => setShowMethodology(!showMethodology)}
                    className="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
                >
                    <span className="font-semibold text-slate-900">▶ Detection Methodology (Optional)</span>
                    <ChevronDown className={cn("w-5 h-5 text-slate-600 transition-transform", showMethodology && "rotate-180")} />
                </button>
                {showMethodology && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="px-5 py-4 border-t border-slate-200 space-y-4 bg-slate-50"
                    >
                        <div>
                            <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                                <span>🔍</span> What is Money Muling?
                            </h4>
                            <p className="text-sm text-slate-700">
                                Money muling involves moving illicit funds through multiple accounts to obscure origin and destination, 
                                making it difficult to trace the source of funds in financial crime schemes.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                                <span>📈</span> Detection Methods
                            </h4>
                            <p className="text-sm text-slate-700">
                                This engine identifies suspicious patterns: circular routing (cycles), smurfing (fan-in/fan-out), 
                                and shell networks. Multiple accounts showing these patterns are grouped into fraud rings.
                            </p>
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Bottom Section - Tables */}
            <div className="pb-10">
                <RingTable />
            </div>
        </motion.div>
    );
};

const StatCard = ({ label, value, highlight, description }: { label: string, value: string | number, highlight?: 'red' | 'orange', description?: string }) => (
    <div className={cn(
        "p-5 rounded-xl border transition-all duration-300 bg-white",
        highlight === 'red' 
            ? 'border-red-200 shadow-md hover:shadow-lg' 
            : highlight === 'orange' 
            ? 'border-orange-200 shadow-md hover:shadow-lg'
            : 'border-slate-200 shadow-sm hover:shadow-md'
    )}>
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{label}</span>
        <span className={cn(
            "text-3xl font-bold mt-2 block",
            highlight === 'red' ? 'text-red-600' :
            highlight === 'orange' ? 'text-orange-600' : 'text-slate-900'
        )}>{value}</span>
        {description && (
            <span className="text-xs text-slate-400 mt-2 block">{description}</span>
        )}
    </div>
);
