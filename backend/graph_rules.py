import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import numpy as np
from datetime import datetime

class TransactionGraphAnalyzer:
    def __init__(self, detector):
        self.detector = detector
        self.graph = detector.graph
        self.color_scheme = {
            'normal': '#1f77b4',           # Blue
            'suspicious': '#ff7f0e',       # Orange
            'high_risk': '#d62728',        # Red
            'critical': '#9467bd',         # Purple
            'minimal': '#2ca02c'           # Green
        }
        self.ring_colors = [
            '#FF6B6B',  # Red
            '#4ECDC4',  # Teal
            '#45B7D1',  # Blue
            '#FFA07A',  # Light Salmon
            '#98D8C8',  # Mint
            '#F7DC6F',  # Yellow
            '#BB8FCE',  # Purple
            '#85C1E2'   # Sky Blue
        ]

    def create_enhanced_network_visualization(self, detection_results, scorer, rings=None):
        """Create enhanced interactive visualization with ring highlighting"""
        fig = go.Figure()

        if not self.graph or self.graph.number_of_nodes() == 0:
            return self._create_empty_chart()

        # Get positions for nodes using spring layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

        # Determine node colors and sizes based on rings and risk
        node_colors = []
        node_sizes = []
        node_risk_levels = {}
        node_to_ring = {}

        # Map nodes to rings
        if rings:
            for ring_id, ring_data in rings.items():
                members = ring_data.get('members', [])
                for member in members:
                    node_to_ring[member] = ring_id

        # Assign colors based on ring membership and risk
        ring_color_map = {}
        ring_counter = 0

        for node in self.graph.nodes():
            if node in node_to_ring:
                ring_id = node_to_ring[node]
                if ring_id not in ring_color_map:
                    ring_color_map[ring_id] = self.ring_colors[ring_counter % len(self.ring_colors)]
                    ring_counter += 1
                node_colors.append(ring_color_map[ring_id])
                node_sizes.append(25)  # Larger for ring members
                node_risk_levels[node] = 'HIGH'
            else:
                node_colors.append(self.color_scheme['normal'])
                node_sizes.append(15)  # Smaller for normal nodes
                node_risk_levels[node] = 'MINIMAL'

        # Create edge traces with directional arrows
        edge_traces = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # Check if edge is part of a ring
            edge_color = '#888'
            edge_width = 1
            if edge[0] in node_to_ring and edge[1] in node_to_ring:
                if node_to_ring[edge[0]] == node_to_ring[edge[1]]:
                    edge_color = ring_color_map[node_to_ring[edge[0]]]
                    edge_width = 3

            edge_trace = go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines',
                line=dict(width=edge_width, color=edge_color),
                hoverinfo='text',
                text=f"{edge[0]} → {edge[1]}",
                showlegend=False
            )
            edge_traces.append(edge_trace)

        # Add all edge traces
        for edge_trace in edge_traces:
            fig.add_trace(edge_trace)

        # Create node trace with enhanced properties
        node_x = [pos[node][0] for node in self.graph.nodes()]
        node_y = [pos[node][1] for node in self.graph.nodes()]

        node_text = []
        for node in self.graph.nodes():
            ring_info = f"<br>Ring: {node_to_ring.get(node, 'N/A')}" if node in node_to_ring else ""
            node_text.append(
                f"<b>Account: {node}</b>"
                f"<br>Risk Level: {node_risk_levels.get(node, 'MINIMAL')}"
                f"{ring_info}"
            )

        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers + text',
            text=[node for node in self.graph.nodes()],
            textposition='top center',
            textfont=dict(size=10, color='black'),
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                color=node_colors,
                size=node_sizes,
                line=dict(
                    color=['#FFD700' if node in node_to_ring else '#888' for node in self.graph.nodes()],
                    width=3 if any(node in node_to_ring for node in self.graph.nodes()) else 1
                ),
                opacity=0.9
            ),
            name='Accounts'
        ))

        # Update layout with legend
        fig.update_layout(
            title="<b>Money Muling Detection Network</b><br><sub>Colored nodes = Fraud rings detected</sub>",
            titlefont_size=16,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=60),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(240,240,240,0.5)',
            height=700,
            width=1200
        )

        return fig

    def create_risk_distribution_chart(self, fraud_ring_output):
        """Create risk distribution pie chart"""
        if not fraud_ring_output or 'fraud_rings' not in fraud_ring_output:
            return self._create_empty_chart()

        fraud_rings = fraud_ring_output['fraud_rings']
        risk_counts = defaultdict(int)

        for ring in fraud_rings:
            risk_score = ring.get('risk_score', 0)
            if risk_score >= 80:
                risk_level = 'CRITICAL'
            elif risk_score >= 60:
                risk_level = 'HIGH'
            elif risk_score >= 40:
                risk_level = 'MEDIUM'
            elif risk_score >= 20:
                risk_level = 'LOW'
            else:
                risk_level = 'MINIMAL'

            risk_counts[risk_level] += 1

        if not risk_counts:
            risk_counts['MINIMAL'] = 1

        risk_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']
        levels = [level for level in risk_order if level in risk_counts]
        values = [risk_counts[level] for level in levels]

        color_map = {
            'CRITICAL': '#d62728',
            'HIGH': '#ff7f0e',
            'MEDIUM': '#ffc107',
            'LOW': '#28a745',
            'MINIMAL': '#6c757d'
        }
        colors = [color_map.get(level, '#1f77b4') for level in levels]

        fig = go.Figure(data=[go.Pie(
            labels=levels,
            values=values,
            marker_colors=colors,
            title="Risk Level Distribution"
        )])

        fig.update_layout(
            title="<b>Fraud Ring Risk Distribution</b>",
            font_size=14,
            height=500
        )

        return fig

    def create_fraud_ring_details_table(self, fraud_ring_output):
        """Create detailed fraud ring table data"""
        if not fraud_ring_output or 'fraud_rings' not in fraud_ring_output:
            return []

        table_data = []
        for ring in fraud_ring_output['fraud_rings']:
            table_data.append({
                'ring_id': ring.get('ring_id', 'N/A'),
                'pattern_type': ring.get('pattern_type', 'Unknown'),
                'member_count': len(ring.get('member_accounts', [])),
                'risk_score': ring.get('risk_score', 0),
                'member_accounts': ', '.join(ring.get('member_accounts', []))
            })

        return sorted(table_data, key=lambda x: x['risk_score'], reverse=True)

    def _get_risk_priority(self, risk_level):
        """Get numerical priority for risk levels"""
        priorities = {
            'MINIMAL': 0,
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        return priorities.get(risk_level, 0)

    def _create_empty_chart(self):
        """Create empty chart when no data available"""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color='gray')
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        return fig

    def analyze_graph_metrics(self):
        """Calculate comprehensive graph metrics"""
        if not self.graph:
            return {}

        metrics = {}

        # Basic metrics
        metrics['num_nodes'] = self.graph.number_of_nodes()
        metrics['num_edges'] = self.graph.number_of_edges()
        metrics['density'] = nx.density(self.graph)

        # Centrality measures
        try:
            metrics['degree_centrality'] = nx.degree_centrality(self.graph)
            metrics['betweenness_centrality'] = nx.betweenness_centrality(self.graph)
            metrics['closeness_centrality'] = nx.closeness_centrality(self.graph)
        except:
            metrics['centrality_error'] = "Could not calculate centrality"

        # Connected components
        undirected = self.graph.to_undirected()
        metrics['connected_components'] = len(list(nx.connected_components(undirected)))

        # Clustering coefficient
        try:
            metrics['clustering_coefficient'] = nx.average_clustering(undirected)
        except:
            metrics['clustering_error'] = "Could not calculate clustering"

        return metrics