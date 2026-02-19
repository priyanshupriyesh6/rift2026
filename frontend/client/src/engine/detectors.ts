import type { GraphData, Node, Link, FraudRing } from '../types';

// Constants
const FAN_THRESHOLD_IN = 10;
const FAN_THRESHOLD_OUT = 10;
const SHELL_TX_LIMIT = 5; // Low volume for shell accounts
const MIN_CYCLE_LEN = 3;
const MAX_CYCLE_LEN = 5;

export class PatternDetector {
    private nodes: Map<string, Node>;
    private links: Link[];
    private adjacency: Map<string, string[]>;

    constructor(graphData: GraphData, adjacency: Map<string, string[]>) {
        this.nodes = new Map(graphData.nodes.map(n => [n.id, n]));
        this.links = graphData.links;
        this.adjacency = adjacency;
    }

    detectAll(): FraudRing[] {
        const cycles = this.detectCycles();
        const smurfing = this.detectSmurfing();
        const shells = this.detectShells();
        return [...cycles, ...smurfing, ...shells];
    }

    // 1. Cycle Detection (DFS)
    detectCycles(): FraudRing[] {
        const rings: FraudRing[] = [];
        const seenCycles = new Set<string>();

        const dfs = (
            current: string,
            start: string,
            path: string[],
            visited: Set<string>
        ) => {
            const depth = path.length;
            if (depth > MAX_CYCLE_LEN) return;

            const neighbors = this.adjacency.get(current) || [];
            for (const next of neighbors) {
                if (next === start && depth >= MIN_CYCLE_LEN) {
                    const members = [...path];
                    const sortedKey = members.slice().sort().join(',');

                    if (!seenCycles.has(sortedKey)) {
                        seenCycles.add(sortedKey);
                        rings.push({
                            ringId: `CYC_${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
                            memberAccounts: members,
                            patternType: 'cycle',
                            riskScore: 90
                        });
                    }
                } else if (!visited.has(next)) {
                    visited.add(next);
                    path.push(next);
                    dfs(next, start, path, visited);
                    path.pop();
                    visited.delete(next);
                }
            }
        };

        this.nodes.forEach(node => {
            if (node.details!.inDegree > 0 && node.details!.outDegree > 0) {
                dfs(node.id, node.id, [node.id], new Set([node.id]));
            }
        });

        return rings;
    }

    // 2. Smurfing (Fan-in / Fan-out)
    detectSmurfing(): FraudRing[] {
        const rings: FraudRing[] = [];

        this.nodes.forEach(node => {
            if (node.details!.inDegree >= FAN_THRESHOLD_IN) {
                const sources = this.links
                    .filter(l => l.target === node.id)
                    .map(l => l.source);

                rings.push({
                    ringId: `FANIN_${node.id}`,
                    memberAccounts: [node.id, ...sources],
                    patternType: 'fan_in',
                    riskScore: 80
                });
            }

            if (node.details!.outDegree >= FAN_THRESHOLD_OUT) {
                const targets = this.links
                    .filter(l => l.source === node.id)
                    .map(l => l.target);

                rings.push({
                    ringId: `FANOUT_${node.id}`,
                    memberAccounts: [node.id, ...targets],
                    patternType: 'fan_out',
                    riskScore: 80
                });
            }
        });

        return rings;
    }

    // 3. Shell Detection (Layered Networks)
    detectShells(): FraudRing[] {
        const rings: FraudRing[] = [];
        const shellCandidates = new Set<string>();

        this.nodes.forEach(node => {
            const totalTx = (node.details?.inDegree || 0) + (node.details?.outDegree || 0);
            if (totalTx > 0 && totalTx <= SHELL_TX_LIMIT) {
                shellCandidates.add(node.id);
            }
        });

        const visited = new Set<string>();

        shellCandidates.forEach(shellId => {
            if (visited.has(shellId)) return;

            const component: string[] = [];
            const stack = [shellId];
            visited.add(shellId);

            while (stack.length > 0) {
                const current = stack.pop()!;
                component.push(current);

                const neighbors = this.adjacency.get(current) || [];
                neighbors.forEach(next => {
                    if (shellCandidates.has(next) && !visited.has(next)) {
                        visited.add(next);
                        stack.push(next);
                    }
                });
            }

            // If we found a chain/cluster of connected shell accounts
            if (component.length >= 2) {
                rings.push({
                    ringId: `SHELL_${component[0]}`,
                    memberAccounts: component,
                    patternType: 'shell',
                    riskScore: 85
                });
            }
        });

        return rings;
    }
}
