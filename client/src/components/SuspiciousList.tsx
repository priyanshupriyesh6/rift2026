import React from 'react';
import { useAppStore } from '../store';
import { motion } from 'framer-motion';
import { ShieldAlert } from 'lucide-react';

export const SuspiciousList: React.FC = () => {
    const { analysisResult } = useAppStore();

    if (!analysisResult) return null;

    return (
        <div className="space-y-4 h-full flex flex-col">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-orange-600" />
                High Risk Accounts
            </h3>

            <div className="space-y-2 flex-1 overflow-y-auto pr-2">
                {analysisResult.suspicious_accounts.slice(0, 8).map((acc, idx) => (
                    <motion.div
                        key={acc.account_id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.03 }}
                        className="p-3 rounded-lg border border-slate-200 bg-white hover:border-blue-300 hover:shadow-md transition-all duration-200"
                    >
                        <div className="flex justify-between items-start mb-2">
                            <span className="font-mono text-sm font-bold text-slate-900">{acc.account_id}</span>
                            <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                                acc.suspicion_score > 80 ? 'bg-red-100 text-red-700' :
                                acc.suspicion_score > 50 ? 'bg-orange-100 text-orange-700' :
                                'bg-yellow-100 text-yellow-700'
                            }`}>
                                {acc.suspicion_score.toFixed(1)}
                            </span>
                        </div>

                        <div className="flex flex-wrap gap-1 mt-2">
                            {acc.detected_patterns.map(p => (
                                <span key={p} className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 font-semibold">
                                    {p}
                                </span>
                            ))}
                            {acc.ring_id && (
                                <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 border border-blue-200 font-semibold">
                                    In Ring
                                </span>
                            )}
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};
