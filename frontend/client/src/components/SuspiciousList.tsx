import React from 'react';
import { useAppStore } from '@/store';
import { motion } from 'framer-motion';
import { ShieldAlert } from 'lucide-react';

export const SuspiciousList: React.FC = () => {
    const { analysisResult } = useAppStore();

    if (!analysisResult) return null;

    return (
        <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-orange-500" />
                High Risk Accounts
            </h3>

            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                {analysisResult.suspicious_accounts.map((acc, idx) => (
                    <motion.div
                        key={acc.account_id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.03 }}
                        className="p-3 rounded-lg border border-border bg-card hover:border-primary/50 transition-colors"
                    >
                        <div className="flex justify-between items-start mb-1">
                            <span className="font-mono text-sm font-medium">{acc.account_id}</span>
                            <span className="text-xs font-bold text-red-400">{acc.suspicion_score.toFixed(1)}</span>
                        </div>

                        <div className="flex flex-wrap gap-1 mt-2">
                            {acc.detected_patterns.map(p => (
                                <span key={p} className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-muted text-muted-foreground border border-border">
                                    {p}
                                </span>
                            ))}
                            {acc.ring_id && (
                                <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
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
