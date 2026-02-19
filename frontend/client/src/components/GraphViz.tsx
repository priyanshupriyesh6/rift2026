import React, { useRef, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { useAppStore } from '@/store';
import { useResizeObserver } from '@/hooks/useResizeObserver';

export const GraphViz: React.FC = () => {
    const { graphData, analysisResult } = useAppStore();
    const containerRef = useRef<HTMLDivElement>(null);
    const { width, height } = useResizeObserver(containerRef);
    const graphRef = useRef<any>(null);

    // Prepare data with visualization properties
    const data = useMemo(() => {
        if (!graphData) return { nodes: [], links: [] };

        const nodes = graphData.nodes.map(node => {
            // Determine color based on risk
            let color = '#64748b'; // slate-500 (neutral)
            let val = 5; // size

            const suspicious = analysisResult?.suspicious_accounts.find(sa => sa.account_id === node.id);

            if (suspicious) {
                if (suspicious.suspicion_score > 80) {
                    color = '#ef4444'; // red-500
                    val = 15;
                } else if (suspicious.suspicion_score > 50) {
                    color = '#f97316'; // orange-500
                    val = 10;
                } else {
                    color = '#eab308'; // yellow-500
                    val = 7;
                }
            }

            return { ...node, color, val };
        });

        const links = graphData.links.map(link => ({
            ...link,
            color: '#334155' // slate-700
        }));

        return { nodes, links };
    }, [graphData, analysisResult]);

    return (
        <div ref={containerRef} className="w-full h-full min-h-[500px] bg-slate-950 rounded-xl overflow-hidden border border-slate-800 relative">
            <div className="absolute top-4 left-4 z-10 bg-slate-900/80 p-2 rounded text-xs text-slate-300 backdrop-blur">
                <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> High Risk</div>
                <div className="flex items-center gap-2 mt-1"><span className="w-3 h-3 rounded-full bg-orange-500"></span> Medium Risk</div>
                <div className="flex items-center gap-2 mt-1"><span className="w-3 h-3 rounded-full bg-yellow-500"></span> Low Risk</div>
                <div className="flex items-center gap-2 mt-1"><span className="w-3 h-3 rounded-full bg-slate-500"></span> Normal</div>
            </div>

            {width > 0 && height > 0 && (
                <ForceGraph2D
                    ref={graphRef}
                    width={width}
                    height={height}
                    graphData={data}
                    nodeLabel="id"
                    nodeRelSize={4}
                    linkColor="color"
                    linkDirectionalArrowLength={3.5}
                    linkDirectionalArrowRelPos={1}
                    onNodeClick={(node) => {
                        graphRef.current?.centerAt(node.x, node.y, 1000);
                        graphRef.current?.zoom(4, 2000);
                    }}
                    cooldownTicks={100}
                    d3AlphaDecay={0.02}
                    d3VelocityDecay={0.3}
                />
            )}
        </div>
    );
};
