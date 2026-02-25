import { create } from 'zustand';
import type { AnalysisResult, GraphData, SuspiciousAccount } from '@/types/index.ts';
import { apiService } from '@/lib/api.ts';

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

        try {
            // Basic file validation
            if (!file.name.toLowerCase().endsWith('.csv')) {
                throw new Error('Please upload a CSV file');
            }

            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                throw new Error('File size must be less than 10MB');
            }

            // Step 1: Upload the file to backend
            const uploadResponse = await apiService.uploadTransactions(file);
            if (!uploadResponse.success) {
                throw new Error(uploadResponse.error || 'Failed to upload file');
            }

            // Step 2: Run detection
            const detectionResponse = await apiService.runDetection();
            if (!detectionResponse.success) {
                throw new Error(detectionResponse.error || 'Failed to run detection');
            }

            // Step 3: Get fraud rings data
            const fraudRingsResponse = await apiService.getFraudRings();
            if (!fraudRingsResponse.success) {
                throw new Error(fraudRingsResponse.error || 'Failed to get fraud rings');
            }

            // Transform backend data to match frontend types
            const fraudRings = fraudRingsResponse.data!.fraud_rings.map((ring) => ({
                ringId: ring.ring_id,
                memberAccounts: ring.member_accounts,
                patternType: ring.pattern_type as 'cycle' | 'fan_in' | 'fan_out' | 'shell' | 'mixed',
                riskScore: ring.risk_score
            }));

            const suspiciousAccounts = (detectionResponse.data!.fraud_ring_output as { suspicious_accounts: SuspiciousAccount[] }).suspicious_accounts.map((acc) => ({
                account_id: acc.account_id,
                suspicion_score: acc.suspicion_score,
                detected_patterns: acc.detected_patterns,
                ring_id: acc.ring_id
            }));

            // For now, create a simple graph data structure
            // In a full implementation, you'd get this from the network visualization endpoint
            const graphData: GraphData = {
                nodes: suspiciousAccounts.map((acc: SuspiciousAccount) => ({
                    id: acc.account_id,
                    isSuspicious: acc.suspicion_score > 50,
                    riskScore: acc.suspicion_score,
                    details: {
                        inDegree: 0, // Would need to get from backend
                        outDegree: 0,
                        totalIncoming: 0,
                        totalOutgoing: 0,
                        flags: acc.detected_patterns
                    }
                })),
                links: [] // Would need to get from backend
            };

            const analysisResult: AnalysisResult = {
                suspicious_accounts: suspiciousAccounts,
                fraud_rings: fraudRings,
                summary: detectionResponse.data!.fraud_ring_output.summary,
                graphData: graphData
            };

            set({
                isAnalyzing: false,
                graphData,
                analysisResult
            });

        } catch (error: unknown) {
            set({ isAnalyzing: false, error: error instanceof Error ? error.message : 'An unknown error occurred' });
        }
    }
}));
