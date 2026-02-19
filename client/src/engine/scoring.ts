import type { Node, FraudRing, SuspiciousAccount } from '../types';

export class RiskScorer {
    static calculateScores(nodes: Node[], rings: FraudRing[]): SuspiciousAccount[] {
        const scores = new Map<string, number>();
        const patterns = new Map<string, Set<string>>();
        const ringMap = new Map<string, string>(); // NodeID -> RingID (last one wins or list?)

        // Initialize
        nodes.forEach(n => {
            scores.set(n.id, 0);
            patterns.set(n.id, new Set());
        });

        // 1. Score based on Ring Participation
        rings.forEach(ring => {
            ring.memberAccounts.forEach(memberId => {
                const currentScore = scores.get(memberId) || 0;
                // Add ring risk score (max 100)
                // If member is detecting in multiple rings, score increases?
                // Use max or specialized logic.
                const newScore = Math.min(100, currentScore + ring.riskScore);
                scores.set(memberId, newScore);

                patterns.get(memberId)?.add(ring.patternType);
                ringMap.set(memberId, ring.ringId);
            });
        });

        // 2. Score based on Individual Metrics (if not in ring but suspicious)
        // E.g. high velocity but not yet a ring?

        // Convert to Result Array
        const result: SuspiciousAccount[] = [];
        nodes.forEach(node => {
            const score = scores.get(node.id) || 0;
            if (score > 0) {
                result.push({
                    account_id: node.id,
                    suspicion_score: score,
                    detected_patterns: Array.from(patterns.get(node.id) || []),
                    ring_id: ringMap.get(node.id) || ''
                });
            }
        });

        // Sort descending
        return result.sort((a, b) => b.suspicion_score - a.suspicion_score);
    }
}
