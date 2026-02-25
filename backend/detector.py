import pandas as pd
import networkx as nx
from collections import defaultdict, deque
import numpy as np
from datetime import datetime, timedelta
import uuid
import time
import random

class MoneyMulingDetector:
    def __init__(self):
        self.transactions = None
        self.graph = None
        self.rings = {}  # Store identified rings

    def load_transactions(self, transactions_df):
        """Load transaction data"""
        self.transactions = transactions_df.copy()
        self._build_graph()

    def _build_graph(self):
        """Build transaction graph from data"""
        self.graph = nx.DiGraph()

        # Add nodes (accounts)
        accounts = set(self.transactions['from_account']).union(set(self.transactions['to_account']))
        self.graph.add_nodes_from(accounts)

        # Add edges (transactions)
        for _, row in self.transactions.iterrows():
            self.graph.add_edge(
                row['from_account'],
                row['to_account'],
                amount=row['amount'],
                timestamp=row['timestamp'],
                transaction_id=row['transaction_id']
            )

    def detect_circular_fund_routing(self, max_cycle_length=8, max_cycles=1000, timeout_seconds=300):
        """Detect circular fund routing patterns with scalability limits"""
        cycles = []
        start_time = time.time()
        
        try:
            # For large graphs, limit cycle detection to avoid exponential time
            if self.graph.number_of_nodes() > 10000 or self.graph.number_of_edges() > 50000:
                print(f"[DETECTOR] Large graph detected ({self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges)")
                print("[DETECTOR] Using optimized cycle detection for large datasets")
                
                # Use a more efficient approach for large graphs
                cycles = self._detect_cycles_efficiently(max_cycle_length, max_cycles, timeout_seconds)
            else:
                # For smaller graphs, use the original approach
                all_cycles = list(nx.simple_cycles(self.graph))
                
                for cycle in all_cycles[:max_cycles]:  # Limit number of cycles
                    if len(cycle) <= max_cycle_length:
                        if time.time() - start_time > timeout_seconds:
                            print(f"[DETECTOR] Cycle detection timed out after {timeout_seconds}s")
                            break
                            
                        cycle_data = self._analyze_cycle(cycle)
                        if cycle_data:
                            cycles.append(cycle_data)
                            
            print(f"[DETECTOR] Found {len(cycles)} circular routing patterns")
            return cycles
            
        except Exception as e:
            print(f"[DETECTOR] Error in cycle detection: {e}")
            return cycles

    def _detect_cycles_efficiently(self, max_cycle_length=8, max_cycles=1000, timeout_seconds=300):
        """Efficient cycle detection for large graphs"""
        cycles = []
        start_time = time.time()
        
        # Sample high-degree nodes for cycle detection
        degrees = dict(self.graph.degree())
        high_degree_nodes = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)[:min(1000, len(degrees))]
        
        print(f"[DETECTOR] Sampling from {len(high_degree_nodes)} high-degree nodes")
        
        for node in high_degree_nodes[:100]:  # Limit starting nodes
            if time.time() - start_time > timeout_seconds:
                break
                
            try:
                # Find cycles starting from this node
                node_cycles = self._find_cycles_from_node(node, max_cycle_length, max_cycles // 100)
                for cycle in node_cycles:
                    if len(cycles) >= max_cycles:
                        break
                    cycle_data = self._analyze_cycle(cycle)
                    if cycle_data:
                        cycles.append(cycle_data)
            except:
                continue
                
        return cycles

    def _find_cycles_from_node(self, start_node, max_length=8, max_cycles=10):
        """Find cycles starting from a specific node using DFS"""
        cycles = []
        visited = set()
        path = []
        
        def dfs(current, depth=0):
            if depth > max_length:
                return
            if len(cycles) >= max_cycles:
                return
                
            path.append(current)
            visited.add(current)
            
            for neighbor in self.graph.successors(current):
                if neighbor == start_node and len(path) > 2:
                    # Found a cycle
                    cycles.append(path + [start_node])
                elif neighbor not in visited:
                    dfs(neighbor, depth + 1)
                    
            path.pop()
            visited.remove(current)
        
        dfs(start_node)
        return cycles
    
    def _analyze_cycle(self, cycle):
        """Analyze a single cycle and return cycle data"""
        try:
            cycle_edges = []
            total_amount = 0
            timestamps = []

            for i in range(len(cycle)):
                from_acc = cycle[i]
                to_acc = cycle[(i + 1) % len(cycle)]

                if self.graph.has_edge(from_acc, to_acc):
                    edge_data = self.graph.get_edge_data(from_acc, to_acc)
                    if isinstance(edge_data, dict):
                        cycle_edges.append((from_acc, to_acc, edge_data))
                        total_amount += edge_data.get('amount', 0)
                        timestamps.append(edge_data.get('timestamp'))

            if cycle_edges:
                time_span = max(timestamps) - min(timestamps) if len(timestamps) > 1 else timedelta(0)
                
                ring_id = f"RING_{len(self.rings):03d}"
                self.rings[ring_id] = {
                    'type': 'circular_routing',
                    'members': cycle,
                    'edges': cycle_edges,
                    'total_amount': total_amount
                }

                return {
                    'cycle': cycle,
                    'length': len(cycle),
                    'total_amount': total_amount,
                    'time_span_seconds': time_span.total_seconds(),
                    'ring_id': ring_id
                }
        except Exception as e:
            print(f"[DETECTOR] Error analyzing cycle: {e}")
            
        return None

    def detect_smurfing_patterns(self, threshold_amount=10000, min_splits=3):

        # Group transactions by source account and time window
        grouped = self.transactions.groupby(['from_account', pd.Grouper(key='timestamp', freq='1h')])

        for (source_account, time_window), group in grouped:
            if len(group) >= min_splits:
                total_outflow = group['amount'].sum()
                avg_amount = group['amount'].mean()
                max_amount = group['amount'].max()

                # Check if this looks like smurfing
                if (total_outflow > threshold_amount and
                    avg_amount < threshold_amount * 0.1 and
                    max_amount < threshold_amount * 0.5):

                    recipients = list(group['to_account'].unique())
                    ring_id = f"RING_{len(self.rings):03d}"
                    
                    self.rings[ring_id] = {
                        'type': 'smurfing',
                        'members': [source_account] + recipients,
                        'source': source_account,
                        'recipients': recipients,
                        'total_amount': total_outflow
                    }

                    smurfing_groups.append({
                        'source_account': source_account,
                        'time_window': time_window,
                        'total_amount': total_outflow,
                        'num_transactions': len(group),
                        'recipients': recipients,
                        'avg_amount': avg_amount,
                        'suspicious_score': self._calculate_smurfing_score(group, threshold_amount),
                        'ring_id': ring_id
                    })

        return smurfing_groups

    def detect_layered_shell_networks(self, min_layer_depth=3):
        """Detect layered shell network patterns"""
        shell_networks = []

        # Find accounts with high centrality but low legitimate activity
        try:
            # Calculate centrality measures
            betweenness = nx.betweenness_centrality(self.graph)
            degree = dict(self.graph.degree())

            # Calculate transaction volumes
            account_volumes = defaultdict(float)
            for _, row in self.transactions.iterrows():
                account_volumes[row['from_account']] += row['amount']
                account_volumes[row['to_account']] += row['amount']

            # Identify potential shell accounts
            potential_shells = []
            for account in self.graph.nodes():
                centrality_score = betweenness.get(account, 0)
                degree_score = degree.get(account, 0)
                volume = account_volumes.get(account, 0)

                # Shell accounts typically have high centrality but low volume
                if centrality_score > np.percentile(list(betweenness.values()), 75) and volume < np.percentile(list(account_volumes.values()), 25):
                    potential_shells.append({
                        'account': account,
                        'centrality': centrality_score,
                        'degree': degree_score,
                        'volume': volume
                    })

            # Find connected components of shell accounts
            shell_subgraph = self.graph.subgraph([s['account'] for s in potential_shells])
            components = list(nx.connected_components(shell_subgraph.to_undirected()))

            for component in components:
                if len(component) >= min_layer_depth:
                    ring_id = f"RING_{len(self.rings):03d}"
                    component_list = list(component)
                    
                    self.rings[ring_id] = {
                        'type': 'shell_network',
                        'members': component_list,
                        'size': len(component_list),
                        'total_volume': sum(account_volumes.get(acc, 0) for acc in component_list)
                    }

                    shell_networks.append({
                        'accounts': component_list,
                        'size': len(component),
                        'total_volume': sum(account_volumes.get(acc, 0) for acc in component),
                        'avg_centrality': np.mean([betweenness.get(acc, 0) for acc in component]),
                        'ring_id': ring_id
                    })

        except Exception as e:
            print(f"Error detecting shell networks: {e}")

        return shell_networks

    def _detect_cycles_efficiently(self, max_cycle_length=8, max_cycles=1000, timeout_seconds=300):
        """Efficient cycle detection for large graphs"""
        cycles = []
        start_time = time.time()
        
        # Sample high-degree nodes for cycle detection
        degrees = dict(self.graph.degree())
        high_degree_nodes = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)[:min(1000, len(degrees))]
        
        print(f"[DETECTOR] Sampling from {len(high_degree_nodes)} high-degree nodes")
        
        for node in high_degree_nodes[:100]:  # Limit starting nodes
            if time.time() - start_time > timeout_seconds:
                break
                
            try:
                # Find cycles starting from this node
                node_cycles = self._find_cycles_from_node(node, max_cycle_length, max_cycles // 100)
                for cycle in node_cycles:
                    if len(cycles) >= max_cycles:
                        break
                    cycle_data = self._analyze_cycle(cycle)
                    if cycle_data:
                        cycles.append(cycle_data)
            except:
                continue
                
        return cycles
    
    def _find_cycles_from_node(self, start_node, max_length=8, max_cycles=10):
        """Find cycles starting from a specific node using DFS"""
        cycles = []
        visited = set()
        path = []
        
        def dfs(current, depth=0):
            if depth > max_length:
                return
            if len(cycles) >= max_cycles:
                return
                
            path.append(current)
            visited.add(current)
            
            for neighbor in self.graph.successors(current):
                if neighbor == start_node and len(path) > 2:
                    # Found a cycle
                    cycles.append(path + [start_node])
                elif neighbor not in visited:
                    dfs(neighbor, depth + 1)
                    
            path.pop()
            visited.remove(current)
        
        dfs(start_node)
        return cycles
    
    def _analyze_cycle(self, cycle):
        """Analyze a single cycle and return cycle data"""
        try:
            cycle_edges = []
            total_amount = 0
            timestamps = []

            for i in range(len(cycle)):
                from_acc = cycle[i]
                to_acc = cycle[(i + 1) % len(cycle)]

                if self.graph.has_edge(from_acc, to_acc):
                    edge_data = self.graph.get_edge_data(from_acc, to_acc)
                    if isinstance(edge_data, dict):
                        cycle_edges.append((from_acc, to_acc, edge_data))
                        total_amount += edge_data.get('amount', 0)
                        timestamps.append(edge_data.get('timestamp'))

            if cycle_edges:
                time_span = max(timestamps) - min(timestamps) if len(timestamps) > 1 else timedelta(0)
                
                ring_id = f"RING_{len(self.rings):03d}"
                self.rings[ring_id] = {
                    'type': 'circular_routing',
                    'members': cycle,
                    'edges': cycle_edges,
                    'total_amount': total_amount
                }

                return {
                    'cycle': cycle,
                    'length': len(cycle),
                    'total_amount': total_amount,
                    'time_span_seconds': time_span.total_seconds(),
                    'ring_id': ring_id
                }
        except Exception as e:
            print(f"[DETECTOR] Error analyzing cycle: {e}")
            
        return None

    def _calculate_smurfing_score(self, transaction_group, threshold):
        """Calculate suspicious score for smurfing pattern"""
        amounts = transaction_group['amount'].values
        total = amounts.sum()

        # Score based on amount distribution uniformity
        std_dev = np.std(amounts)
        mean = np.mean(amounts)

        # Lower std/mean ratio indicates more uniform splitting (more suspicious)
        uniformity_ratio = std_dev / mean if mean > 0 else 0

        # Score based on how well amounts avoid detection thresholds
        amounts_below_threshold = sum(1 for amt in amounts if amt < threshold * 0.1)
        threshold_avoidance_score = amounts_below_threshold / len(amounts)

        return (1 - uniformity_ratio) * 0.6 + threshold_avoidance_score * 0.4

    def run_full_detection(self):
        """Run all detection algorithms"""
        results = {
            'circular_routing': self.detect_circular_fund_routing(),
            'smurfing': self.detect_smurfing_patterns(),
            'shell_networks': self.detect_layered_shell_networks(),
            'rings': self.rings
        }

        return results

    def get_all_accounts(self):
        """Get all accounts in the graph"""
        return list(self.graph.nodes())

    def get_account_transactions(self, account):
        """Get all transactions for a specific account"""
        if self.transactions is None:
            return []
        
        return self.transactions[
            (self.transactions['from_account'] == account) | 
            (self.transactions['to_account'] == account)
        ].to_dict('records')