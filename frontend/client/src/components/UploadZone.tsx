import React, { useCallback } from 'react';
import { useAppStore } from '@/store';
import { Upload, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils.ts';
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
        <div className="w-full max-w-2xl mx-auto mt-10 p-6">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                    "relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300",
                    "hover:border-primary/50 hover:bg-muted/30",
                    isAnalyzing ? "border-primary/50 bg-muted/20" : "border-muted-foreground/20"
                )}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept=".csv"
                    onChange={handleChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isAnalyzing}
                    title="Upload CSV file"
                />

                <div className="flex flex-col items-center gap-4">
                    <div className="p-4 bg-primary/10 rounded-full text-primary">
                        {isAnalyzing ? (
                            <Loader2 className="w-10 h-10 animate-spin" />
                        ) : (
                            <Upload className="w-10 h-10" />
                        )}
                    </div>

                    <div className="space-y-2">
                        <h3 className="text-xl font-semibold">
                            {isAnalyzing ? 'Analyzing Transactions...' : 'Upload Transaction Data'}
                        </h3>
                        <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                            Drag and drop your CSV file here, or click to browse.
                            Supported format: transaction_id, sender_id, receiver_id, amount, timestamp
                        </p>
                    </div>
                </div>
            </motion.div>

            {error && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-4 p-4 bg-destructive/10 text-destructive rounded-lg flex items-center gap-3"
                >
                    <AlertCircle className="w-5 h-5" />
                    <p className="text-sm font-medium">{error}</p>
                </motion.div>
            )}
        </div>
    );
};
