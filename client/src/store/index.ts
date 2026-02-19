import { create } from 'zustand';
import type { AnalysisResult, GraphData } from '../types';
import Papa from 'papaparse';
import { GraphBuilder } from '../engine/graph';
import { PatternDetector } from '../engine/detectors';
import { RiskScorer } from '../engine/scoring';

interface AppState {
    isAnalyzing: boolean;
    graphData: GraphData | null;
    analysisResult: AnalysisResult | null;
    error: string | null;

    processFile: (file: File) => Promise<void>;
    reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
    isAnalyzing: false,
    graphData: null,
    analysisResult: null,
    error: null,

    reset: () => set({ isAnalyzing: false, graphData: null, analysisResult: null, error: null }),

    processFile: async (file: File) => {
        set({ isAnalyzing: true, error: null });
        const startTime = performance.now();

        try {
            Papa.parse(file, {
                header: true,
                skipEmptyLines: true,
                complete: (results) => {
                    try {
                        const rawData = results.data as any[];
                        // Validate first row roughly
                        if (!rawData[0].sender_id || !rawData[0].receiver_id || !rawData[0].amount) {
                            throw new Error("Invalid CSV format. Missing required columns.");
                        }

                        const transactions = rawData.map(row => ({
                            transaction_id: row.transaction_id || Math.random().toString(),
                            sender_id: row.sender_id,
                            receiver_id: row.receiver_id,
                            amount: parseFloat(row.amount),
                            timestamp: row.timestamp || new Date().toISOString()
                        }));

                        // 1. Build Graph
                        const builder = new GraphBuilder(transactions);
                        const graphData = builder.build();
                        const adjacency = builder.getAdjacencyList();

                        // 2. Detect Patterns
                        const detector = new PatternDetector(graphData, adjacency);
                        const rings = detector.detectAll();

                        // 3. Score Risk
                        const suspiciousAccounts = RiskScorer.calculateScores(graphData.nodes, rings);

                        const endTime = performance.now();
                        const processingTime = (endTime - startTime) / 1000;

                        const analysisResult: AnalysisResult = {
                            suspicious_accounts: suspiciousAccounts,
                            fraud_rings: rings,
                            summary: {
                                total_accounts_analyzed: graphData.nodes.length,
                                suspicious_accounts_flagged: suspiciousAccounts.length,
                                fraud_rings_detected: rings.length,
                                processing_time_seconds: processingTime
                            },
                            graphData: graphData
                        };

                        set({
                            isAnalyzing: false,
                            graphData,
                            analysisResult
                        });

                    } catch (err: any) {
                        set({ isAnalyzing: false, error: err.message || "Failed to process data" });
                    }
                },
                error: (err) => {
                    set({ isAnalyzing: false, error: "CSV Parsing Error: " + err.message });
                }
            });
        } catch (e: any) {
            set({ isAnalyzing: false, error: e.message });
        }
    }
}));
