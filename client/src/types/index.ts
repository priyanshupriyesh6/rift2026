export interface Transaction {
    transaction_id: string;
    sender_id: string;
    receiver_id: string;
    amount: number;
    timestamp: string;
}

export interface Node {
    id: string;
    isSuspicious: boolean;
    riskScore: number;
    details?: NodeDetails;
}

export interface Link {
    source: string;
    target: string;
    amount: number;
    timestamp: string;
}

export interface GraphData {
    nodes: Node[];
    links: Link[];
}

export interface NodeDetails {
    inDegree: number;
    outDegree: number;
    totalIncoming: number;
    totalOutgoing: number;
    flags: string[];
}

export interface FraudRing {
    ringId: string;
    memberAccounts: string[];
    patternType: 'cycle' | 'fan_in' | 'fan_out' | 'shell' | 'mixed';
    riskScore: number;
}

export interface SuspiciousAccount {
    account_id: string;
    suspicion_score: number;
    detected_patterns: string[];
    ring_id?: string;
}

export interface AnalysisResult {
    suspicious_accounts: SuspiciousAccount[];
    fraud_rings: FraudRing[];
    summary: {
        total_accounts_analyzed: number;
        suspicious_accounts_flagged: number;
        fraud_rings_detected: number;
        processing_time_seconds: number;
    };
    graphData: GraphData; // For visualization
}
