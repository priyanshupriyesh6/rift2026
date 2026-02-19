import React, { useCallback } from 'react';
import { useAppStore } from '../store';
import { Upload, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

export const UploadZone: React.FC = () => {
    const { processFile, isAnalyzing, error } = useAppStore();

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0]);
        }
    }, [processFile]);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            processFile(e.target.files[0]);
        }
    }, [processFile]);

    return (
        <div className="w-full max-w-3xl mx-auto py-16 space-y-8">
            <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                className={cn(
                    "relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 cursor-pointer",
                    isAnalyzing 
                        ? "border-slate-400 bg-slate-50" 
                        : "border-slate-300 hover:border-slate-400 hover:bg-slate-50/50 bg-white"
                )}
            >
                <input
                    type="file"
                    accept=".csv"
                    onChange={handleChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isAnalyzing}
                />

                <div className="flex flex-col items-center gap-6">
                    <div className={cn(
                        "p-4 rounded-full transition-colors duration-300",
                        isAnalyzing 
                            ? "bg-slate-200 text-slate-600" 
                            : "bg-slate-100 text-slate-600"
                    )}>
                        {isAnalyzing ? (
                            <Loader2 className="w-12 h-12 animate-spin" />
                        ) : (
                            <Upload className="w-12 h-12" />
                        )}
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-3xl font-bold text-slate-900">
                            {isAnalyzing ? 'Running Forensic Analysis...' : 'Transaction Dataset for Investigation'}
                        </h2>
                        <p className="text-base text-slate-600 max-w-md mx-auto leading-relaxed">
                            {isAnalyzing ? (
                                <span className="inline-block">Building transaction graph → Detecting patterns → Scoring risk</span>
                            ) : (
                                <>Provide a transaction dataset for forensic analysis</>
                            )}
                        </p>
                        {!isAnalyzing && (
                            <p className="text-sm text-slate-500">
                                Format: transaction_id, sender_id, receiver_id, amount, timestamp
                            </p>
                        )}
                        {!isAnalyzing && (
                            <p className="text-xs text-slate-400">
                                Data is processed locally for analysis and not retained.
                            </p>
                        )}
                    </div>
                </div>
            </div>

            {/* Call to Action */}
            {!isAnalyzing && (
                <div className="text-center">
                    <p className="text-base font-medium text-slate-700">Begin investigation by uploading a transaction dataset.</p>
                </div>
            )}

            {/* Investigation Flow */}
            {!isAnalyzing && (
                <div className="text-center space-y-4">
                    <p className="text-sm font-bold text-slate-700 tracking-widest">INVESTIGATION PIPELINE (AUTOMATED)</p>
                    <p className="text-slate-600 font-mono text-sm">
                        Ingest Data → Build Transaction Graph → Detect Patterns → Flag Fraud Rings
                    </p>
                </div>
            )}

            {/* Disclaimer */}
            {!isAnalyzing && (
                <div className="text-center pt-4 border-t border-slate-200">
                    <p className="text-xs text-slate-500 italic">For internal forensic analysis only</p>
                </div>
            )}

            {error && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-3 border border-red-200"
                >
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p className="text-sm font-medium">{error}</p>
                </motion.div>
            )}
        </div>
    );
};
