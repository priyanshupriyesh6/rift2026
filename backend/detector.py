import pandas as pd
import networkx as nx
from collections import defaultdict, deque
import numpy as np
from datetime import datetime, timedelta
import uuid
import time

class MoneyMulingDetector:
    def __init__(self):
        self.transactions = None
        self.graph = None
        self.rings = {}  # Store identified rings
        self.start_time = None
        self.legitimate_accounts = set()
        self.MAX_CYCLE_LENGTH = 7  # Reduced from 10 for performance
        self.MIN_CYCLE_LENGTH = 3
        self.PROCESSING_TIME_LIMIT = 25  # Leave 5 seconds buffer for upload/download

    def load_transactions(self, transactions_df):
        """Load transaction data"""
        self.transactions = transactions_df.copy()
        self.start_time = time.time()
        self._build_graph()
        self._identify_legitimate_accounts()

    def _build_graph(self):
        """Build transaction graph from data"""
        self.graph = nx.DiGraph()

        # Add nodes (accounts)
        accounts = set(self.transactions['from_account']).union(set(self.transactions['to_account']))
        self.graph.add_nodes_from(accounts)

        # Add edges (transactions) - use single weight per edge pair
        edge_data = defaultdict(lambda: {'count': 0, 'total_amount': 0, 'amounts': []})
        
        for _, row in self.transactions.iterrows():
            key = (row['from_account'], row['to_account'])
            edge_data[key]['count'] += 1
            edge_data[key]['total_amount'] += row['amount']
            edge_data[key]['amounts'].append(row['amount'])
            edge_data[key]['last_timestamp'] = row['timestamp']
        
        # Add aggregated edges to graph
        for (src, dst), data in edge_data.items():
            avg_amount = data['total_amount'] / data['count']
            self.graph.add_edge(
                src, dst,
                amount=avg_amount,
                total_amount=data['total_amount'],
                count=data['count'],
                timestamp=data['last_timestamp']
            )

    def _identify_legitimate_accounts(self):
        """Identify legitimate accounts to exclude from fraud detection"""
        from legitimate_accounts import LegitimateAccountDetector
        
        detector = LegitimateAccountDetector()
        self.legitimate_accounts, self.account_profiles = detector.identify_legitimate_accounts(
            self.transactions, self.graph
        )

    def detect_circular_fund_routing(self, max_cycle_length=None):
        """Detect circular fund routing patterns - optimized for performance"""
        if max_cycle_length is None:
            max_cycle_length = self.MAX_CYCLE_LENGTH
        
        cycles = []
        
        try:
            # Early exit if processing time exceeded
            if time.time() - self.start_time > self.PROCESSING_TIME_LIMIT:
                return cycles
            
            # Find all simple cycles using built-in algorithm
            all_cycles = []
            cycle_count = 0
            
            # Use a more efficient cycle detection with length limit
            for node in list(self.graph.nodes())[:100]:  # Limit analysis to first 100 nodes
                if time.time() - self.start_time > self.PROCESSING_TIME_LIMIT:
                    break
                
                try:
                    # Find cycles starting from this node
                    node_cycles = nx.simple_cycles(self.graph.subgraph(
                        list(self.graph.neighbors(node)) + [node]
                    ))
                    
                    for cycle in node_cycles:
                        if self.MIN_CYCLE_LENGTH <= len(cycle) <= max_cycle_length:
                            all_cycles.append(list(cycle))
                            cycle_count += 1
                            
                            if cycle_count > 1000:  # Limit total cycles
                                break
                except:
                    continue
                
                if cycle_count > 1000:
                    break

            seen_cycles = set()
            
            for cycle in all_cycles:
                # Skip if already detected (different rotation of same cycle)
                cycle_key = tuple(sorted(cycle))
                if cycle_key in seen_cycles:
                    continue
                seen_cycles.add(cycle_key)
                
                # Skip if contains legitimate accounts
                if any(acc in self.legitimate_accounts for acc in cycle):
                    continue
                
                # Calculate cycle properties
                cycle_edges = []
                total_amount = 0
                timestamps = []

                for i in range(len(cycle)):
                    from_acc = cycle[i]
                    to_acc = cycle[(i + 1) % len(cycle)]

                    if self.graph.has_edge(from_acc, to_acc):
                        edge_data = self.graph.get_edge_data(from_acc, to_acc)
                        cycle_edges.append((from_acc, to_acc, edge_data))
                        total_amount += edge_data.get('amount', 0)
                        timestamps.append(edge_data.get('timestamp'))

                if not cycle_edges:
                    continue

                # Calculate time span
                if timestamps and len(timestamps) > 1:
                    time_span = max(timestamps) - min(timestamps)
                else:
                    time_span = timedelta(0)

                # Filter: skip if cycle has legitimate high-volume accounts
                if total_amount > 500000:  # Large cycles are less likely to be fraud
                    continue

                # Assign unique ring ID
                ring_id = f"RING_{len(self.rings):03d}"
                self.rings[ring_id] = {
                    'type': 'circular_routing',
                    'members': cycle,
                    'edges': cycle_edges,
                    'total_amount': total_amount
                }

                cycles.append({
                    'cycle': cycle,
                    'length': len(cycle),
                    'total_amount': total_amount,
                    'time_span': time_span,
                    'edges': cycle_edges,
                    'ring_id': ring_id
                })

        except Exception as e:
            print(f"Error detecting circular routing: {e}")

        return cycles

    def detect_smurfing_patterns(self, threshold_amount=10000, min_splits=5):
        """Detect smurfing patterns - optimized with false positive reduction"""
        smurfing_groups = []

        # Early exit if processing time exceeded
        if time.time() - self.start_time > self.PROCESSING_TIME_LIMIT:
            return smurfing_groups

        # Group transactions by source account and time window (12 hours for better granularity)
        grouped = self.transactions.groupby(['from_account', pd.Grouper(key='timestamp', freq='12h')])

        for (source_account, time_window), group in grouped:
            # Skip legitimate accounts
            if source_account in self.legitimate_accounts:
                continue
            
            if len(group) < min_splits:
                continue

            total_outflow = group['amount'].sum()
            avg_amount = group['amount'].mean()
            max_amount = group['amount'].max()
            min_amount = group['amount'].min()

            # Check if this looks like smurfing
            # More conservative thresholds to reduce false positives
            if (total_outflow > threshold_amount and
                avg_amount < threshold_amount * 0.15 and  # Increased from 0.1
                max_amount < threshold_amount * 0.6):     # Increased from 0.5

                recipients = list(group['to_account'].unique())
                
                # Skip if recipients are mostly legitimate accounts
                legitimate_recipients = sum(1 for r in recipients if r in self.legitimate_accounts)
                if legitimate_recipients / len(recipients) > 0.7:
                    continue

                suspicious_score = self._calculate_smurfing_score(group, threshold_amount)
                
                # Only flag if score is high enough
                if suspicious_score < 0.4:  # Raised threshold from implicit
                    continue

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
                    'suspicious_score': suspicious_score,
                    'ring_id': ring_id
                })

        return smurfing_groups

    def detect_layered_shell_networks(self, min_layer_depth=3):
        """Detect layered shell network patterns - optimized for precision"""
        shell_networks = []

        # Early exit if processing time exceeded
        if time.time() - self.start_time > self.PROCESSING_TIME_LIMIT:
            return shell_networks

        try:
            # Calculate centrality measures only for high-degree nodes (faster)
            high_degree_nodes = [node for node, degree in dict(self.graph.degree()).items() if degree > 2]
            
            if not high_degree_nodes:
                return shell_networks
            
            # Only compute betweenness for relevant subset
            subgraph = self.graph.subgraph(high_degree_nodes)
            betweenness = nx.betweenness_centrality(subgraph)
            degree = dict(subgraph.degree())

            # Calculate transaction volumes
            account_volumes = defaultdict(float)
            for _, row in self.transactions.iterrows():
                account_volumes[row['from_account']] += row['amount']
                account_volumes[row['to_account']] += row['amount']

            # Identify potential shell accounts with stricter criteria
            potential_shells = []
            for account in high_degree_nodes:
                # Skip legitimate accounts
                if account in self.legitimate_accounts:
                    continue
                
                centrality_score = betweenness.get(account, 0)
                degree_score = degree.get(account, 0)
                volume = account_volumes.get(account, 0)

                # Shell accounts: high centrality, low volume, low transaction amounts
                # More strict: require 85th percentile for centrality, 25th for volume
                centrality_threshold = np.percentile(list(betweenness.values()), 85)
                volume_threshold = np.percentile(list(account_volumes.values()), 25)
                
                if (centrality_score > centrality_threshold and 
                    volume < volume_threshold and
                    degree_score < 10):  # Shell accounts don't have huge degree
                    potential_shells.append({
                        'account': account,
                        'centrality': centrality_score,
                        'degree': degree_score,
                        'volume': volume
                    })

            # Find connected components of shell accounts
            if potential_shells:
                shell_accounts = [s['account'] for s in potential_shells]
                shell_subgraph = self.graph.subgraph(shell_accounts)
                components = list(nx.connected_components(shell_subgraph.to_undirected()))

                for component in components:
                    if len(component) >= min_layer_depth:
                        # Additional validation: components shouldn't be too large
                        if len(component) > 20:
                            continue
                        
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