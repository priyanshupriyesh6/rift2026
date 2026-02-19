import React, { useRef, useMemo, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { useAppStore } from '../store';
import { useResizeObserver } from '../hooks/useResizeObserver';

export const GraphViz: React.FC = () => {
    const { graphData, analysisResult } = useAppStore();
    const containerRef = useRef<HTMLDivElement>(null);
    const { width, height } = useResizeObserver(containerRef);
    const graphRef = useRef<any>(null);
    const [hoveredNode, setHoveredNode] = useState<string | null>(null);

    // Prepare data with visualization properties
    const data = useMemo(() => {
        if (!graphData) return { nodes: [], links: [] };

        const nodes = graphData.nodes.map(node => {
            // Determine color based on risk
            let color = '#64748b'; // slate-500 (neutral)
            let val = 6; // size
            let borderColor = '#ffffff';
            let borderWidth = 0;

            const suspicious = analysisResult?.suspicious_accounts.find(sa => sa.account_id === node.id);

            if (suspicious) {
                borderWidth = 3;
                if (suspicious.suspicion_score > 80) {
                    color = '#ef4444'; // red-500
                    borderColor = '#991b1b'; // dark red border
                    val = 16;
                } else if (suspicious.suspicion_score > 50) {
                    color = '#f97316'; // orange-500
                    borderColor = '#9a3412'; // dark orange border
                    val = 12;
                } else {
                    color = '#eab308'; // yellow-500
                    borderColor = '#854d0e'; // dark yellow border
                    val = 9;
                }
            }

            return { ...node, color, val, borderColor, borderWidth };
        });

        const links = graphData.links.map(link => ({
            ...link,
            color: '#475569', // slate-700
            width: 1.5
        }));

        return { nodes, links };
    }, [graphData, analysisResult]);

    const handleNodeHover = (node: any) => {
        setHoveredNode(node ? node.id : null);
    };

    const handleNodeClick = (node: any) => {
        if (graphRef.current) {
            graphRef.current.centerAt(node.x, node.y, 800);
            graphRef.current.zoom(3, 1200);
        }
    };

    const nodeCanvasObject = (node: any, ctx: CanvasRenderingContext2D) => {
        const size = node.val;
        
        // Draw node circle
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
        ctx.fill();

        // Draw border for suspicious nodes
        if (node.borderWidth > 0) {
            ctx.strokeStyle = node.borderColor;
            ctx.lineWidth = node.borderWidth;
            ctx.beginPath();
            ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
            ctx.stroke();
        }

        // Highlight on hover
        if (hoveredNode === node.id) {
            ctx.strokeStyle = '#3b82f6'; // blue
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI);
            ctx.stroke();

            // Draw node label on hover
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(node.id, node.x, node.y - size - 15);

            // Show account details
            const account = analysisResult?.suspicious_accounts.find(a => a.account_id === node.id);
            if (account) {
                ctx.font = '10px Arial';
                ctx.fillText(`Score: ${account.suspicion_score.toFixed(1)}`, node.x, node.y - size - 2);
            }
        }
    };

    return (
        <div ref={containerRef} className="w-full h-full min-h-[500px] bg-slate-950 rounded-xl overflow-hidden border border-slate-800 relative shadow-xl">
            <div className="absolute top-4 left-4 z-10 bg-slate-900/95 backdrop-blur-sm p-4 rounded-lg text-xs text-slate-300 border border-slate-700 max-w-xs">
                <div className="font-semibold mb-3 text-blue-300">Legend</div>
                <div className="flex items-center gap-2 mb-2">
                    <span className="w-3 h-3 rounded-full bg-red-500 border-2 border-red-900"></span>
                    <span>High Risk (Score &gt; 80)</span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                    <span className="w-3 h-3 rounded-full bg-orange-500 border-2 border-orange-900"></span>
                    <span>Medium Risk (Score 50-80)</span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                    <span className="w-3 h-3 rounded-full bg-yellow-500 border-2 border-yellow-900"></span>
                    <span>Low Risk (Score &lt; 50)</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-slate-500"></span>
                    <span>Normal Accounts</span>
                </div>
                <div className="mt-3 pt-3 border-t border-slate-700 text-blue-300 text-[10px]">
                    💡 Hover nodes for details • Click to zoom
                </div>
            </div>

            <div className="absolute bottom-4 left-4 z-10 bg-slate-900/95 backdrop-blur-sm p-3 rounded-lg text-xs text-slate-300 border border-slate-700">
                <div className="font-semibold text-blue-300 mb-2">Graph Info</div>
                <div className="space-y-1">
                    <div>Nodes: {data.nodes.length}</div>
                    <div>Money Flows: {data.links.length}</div>
                    <div>Suspicious: {analysisResult?.summary.suspicious_accounts_flagged || 0}</div>
                    <div>Rings: {analysisResult?.summary.fraud_rings_detected || 0}</div>
                </div>
            </div>

            {width > 0 && height > 0 && (
                <ForceGraph2D
                    ref={graphRef}
                    width={width}
                    height={height}
                    graphData={data}
                    nodeLabel="id"
                    nodeRelSize={4}
                    nodeCanvasObject={nodeCanvasObject}
                    linkColor="color"
                    linkWidth="width"
                    linkDirectionalArrowLength={4}
                    linkDirectionalArrowRelPos={1}
                    onNodeHover={handleNodeHover}
                    onNodeClick={handleNodeClick}
                    cooldownTicks={100}
                    d3AlphaDecay={0.02}
                    d3VelocityDecay={0.3}
                />
            )}
        </div>
    );
};
