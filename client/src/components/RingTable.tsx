import React from 'react';
import { useAppStore } from '../store';
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

    const getPatternDescription = (type: string) => {
        const descriptions: { [key: string]: string } = {
            'cycle': 'Circular Fund Routing',
            'fan_in': 'Smurfing (Aggregation)',
            'fan_out': 'Smurfing (Dispersion)',
            'shell': 'Layered Shell Network',
            'mixed': 'Mixed Patterns'
        };
        return descriptions[type] || type;
    };

    return (
        <div className="space-y-4">
            <div className="space-y-2">
                <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6 text-red-600" />
                    Detected Fraud Rings Summary ({analysisResult.summary.fraud_rings_detected})
                </h3>
                <p className="text-sm text-slate-600">
                    Comprehensive analysis of identified money-muling patterns and associated accounts
                </p>
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-lg">
                <table className="w-full text-left text-sm text-slate-700">
                    <thead className="bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
                        <tr>
                            <th className="p-4 font-semibold text-slate-900">Ring ID</th>
                            <th className="p-4 font-semibold text-slate-900">Pattern Type</th>
                            <th className="p-4 font-semibold text-slate-900">Members</th>
                            <th className="p-4 font-semibold text-slate-900">Risk Score</th>
                            <th className="p-4 font-semibold text-slate-900">Member Accounts</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                        {analysisResult.fraud_rings.map((ring, idx) => (
                            <motion.tr
                                key={ring.ringId}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="hover:bg-blue-50 transition-colors duration-200"
                            >
                                <td className="p-4 font-mono text-xs font-semibold text-slate-600 bg-slate-50">{ring.ringId}</td>
                                <td className="p-4 flex items-center gap-2">
                                    {getIcon(ring.patternType)}
                                    <div>
                                        <div className="font-semibold text-slate-900">{getPatternDescription(ring.patternType)}</div>
                                        <div className="text-xs text-slate-500 capitalize">{ring.patternType}</div>
                                    </div>
                                </td>
                                <td className="p-4 font-bold text-blue-600">{ring.memberAccounts.length}</td>
                                <td className="p-4">
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${ring.riskScore >= 90 ? 'bg-red-100 text-red-700' :
                                            ring.riskScore >= 70 ? 'bg-orange-100 text-orange-700' :
                                                'bg-yellow-100 text-yellow-700'
                                        }`}>
                                        {ring.riskScore.toFixed(1)}
                                    </span>
                                </td>
                                <td className="p-4">
                                    <div className="text-xs text-slate-600 font-mono break-all" title={ring.memberAccounts.join(', ')}>
                                        <div className="max-h-12 overflow-y-auto pr-2">
                                            {ring.memberAccounts.map((acc, i) => (
                                                <div key={i} className="py-0.5 text-blue-600 font-semibold">{acc}</div>
                                            ))}
                                        </div>
                                    </div>
                                </td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-900">
                <div className="font-semibold mb-2">📊 Detection Pattern Reference</div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="font-semibold text-xs uppercase text-blue-700 mb-1">Cycle</p>
                        <p className="text-xs">Money flows in a loop (A→B→C→A)</p>
                    </div>
                    <div>
                        <p className="font-semibold text-xs uppercase text-blue-700 mb-1">Fan-In/Out</p>
                        <p className="text-xs">Aggregation or dispersion patterns</p>
                    </div>
                    <div>
                        <p className="font-semibold text-xs uppercase text-blue-700 mb-1">Shell</p>
                        <p className="text-xs">Layered networks with intermediaries</p>
                    </div>
                    <div>
                        <p className="font-semibold text-xs uppercase text-blue-700 mb-1">Mixed</p>
                        <p className="text-xs">Multiple pattern combinations</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
