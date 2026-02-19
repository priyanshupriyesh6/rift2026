import React from 'react';
import { useAppStore } from '@/store/index.ts';
import { motion } from 'framer-motion';
import { AlertTriangle, Users, Share2, Shuffle } from 'lucide-react';

export const RingTable: React.FC = () => {
    const { analysisResult } = useAppStore();

    if (!analysisResult || analysisResult.fraud_rings.length === 0) {
        return (
            <div className="p-6 text-center text-muted-foreground border border-dashed rounded-lg">
                No fraud rings detected yet.
            </div>
        );
    }

    const getIcon = (type: string) => {
        switch (type) {
            case 'cycle': return <Shuffle className="w-4 h-4 text-purple-400" />;
            case 'fan_in': return <Share2 className="w-4 h-4 text-orange-400 rotate-180" />;
            case 'fan_out': return <Share2 className="w-4 h-4 text-blue-400" />;
            case 'shell': return <Users className="w-4 h-4 text-yellow-400" />;
            default: return <AlertTriangle className="w-4 h-4 text-red-400" />;
        }
    };

    return (
        <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-destructive" />
                Detected Fraud Rings ({analysisResult.summary.fraud_rings_detected})
            </h3>

            <div className="overflow-x-auto rounded-lg border border-border bg-card">
                <table className="w-full text-left text-sm">
                    <thead className="bg-muted/50 text-muted-foreground">
                        <tr>
                            <th className="p-3 font-medium">Ring ID</th>
                            <th className="p-3 font-medium">Pattern</th>
                            <th className="p-3 font-medium">Risk Score</th>
                            <th className="p-3 font-medium">Members</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                        {analysisResult.fraud_rings.map((ring, idx) => (
                            <motion.tr
                                key={ring.ringId}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="hover:bg-muted/50 transition-colors"
                            >
                                <td className="p-3 font-mono text-xs">{ring.ringId}</td>
                                <td className="p-3 flex items-center gap-2 capitalize">
                                    {getIcon(ring.patternType)}
                                    {ring.patternType.replace('_', ' ')}
                                </td>
                                <td className="p-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${ring.riskScore >= 90 ? 'bg-red-500/20 text-red-400' :
                                            ring.riskScore >= 70 ? 'bg-orange-500/20 text-orange-400' :
                                                'bg-yellow-500/20 text-yellow-400'
                                        }`}>
                                        {ring.riskScore.toFixed(0)}
                                    </span>
                                </td>
                                <td className="p-3 max-w-[200px] truncate text-muted-foreground" title={ring.memberAccounts.join(', ')}>
                                    {ring.memberAccounts.length} accounts
                                </td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
