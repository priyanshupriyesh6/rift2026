import type { Transaction, Node, Link, GraphData } from '../types';

export class GraphBuilder {
    private transactions: Transaction[];
    private nodes: Map<string, Node>;
    private links: Link[];

    constructor(transactions: Transaction[]) {
        this.transactions = transactions;
        this.nodes = new Map();
        this.links = [];
    }

    build(): GraphData {
        this.transactions.forEach(tx => {
            // Create or update Sender Node
            if (!this.nodes.has(tx.sender_id)) {
                this.nodes.set(tx.sender_id, {
                    id: tx.sender_id,
                    isSuspicious: false,
                    riskScore: 0,
                    details: { inDegree: 0, outDegree: 0, totalIncoming: 0, totalOutgoing: 0, flags: [] }
                });
            }
            const sender = this.nodes.get(tx.sender_id)!;
            sender.details!.outDegree++;
            sender.details!.totalOutgoing += tx.amount;

            // Create or update Receiver Node
            if (!this.nodes.has(tx.receiver_id)) {
                this.nodes.set(tx.receiver_id, {
                    id: tx.receiver_id,
                    isSuspicious: false,
                    riskScore: 0,
                    details: { inDegree: 0, outDegree: 0, totalIncoming: 0, totalOutgoing: 0, flags: [] }
                });
            }
            const receiver = this.nodes.get(tx.receiver_id)!;
            receiver.details!.inDegree++;
            receiver.details!.totalIncoming += tx.amount;

            // Add Link
            this.links.push({
                source: tx.sender_id,
                target: tx.receiver_id,
                amount: tx.amount,
                timestamp: tx.timestamp
            });
        });

        return {
            nodes: Array.from(this.nodes.values()),
            links: this.links
        };
    }

    getAdjacencyList(): Map<string, string[]> {
        const adj = new Map<string, string[]>();
        this.nodes.forEach(node => adj.set(node.id, []));
        this.links.forEach(link => {
            adj.get(link.source)?.push(link.target);
        });
        return adj;
    }
}
