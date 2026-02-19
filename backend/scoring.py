import numpy as np
from datetime import datetime, timedelta
import json

class SuspiciousActivityScorer:
    def __init__(self):
        self.weights = {
            'circular_routing': {
                'cycle_length': 0.3,
                'total_amount': 0.4,
                'time_span': 0.3
            },
            'smurfing': {
                'amount_ratio': 0.4,
                'frequency': 0.3,
                'uniformity': 0.3
            },
            'shell_network': {
                'network_size': 0.4,
                'centrality': 0.3,
                'volume_anomaly': 0.3
            }
        }

    def score_circular_routing(self, cycle_data):
        """Score circular fund routing patterns - optimized for precision"""
        cycle_length = cycle_data['length']
        total_amount = cycle_data['total_amount']
        time_span_hours = cycle_data['time_span'].total_seconds() / 3600

        # More conservative scoring to reduce false positives
        # Weight shorter cycles more heavily (3-4 nodes is most suspicious)
        if cycle_length <= 4:
            length_score = min((cycle_length - 2) / 3, 1.0)  # 3-4 nodes = moderate score
        else:
            length_score = min(cycle_length / 15, 1.0)  # Longer cycles = less suspicious
        
        # Amount score - smaller amounts are more suspicious (trying to stay under thresholds)
        if total_amount < 50000:
            amount_score = min((50000 - total_amount) / 50000 * 0.8, 0.8)
        else:
            amount_score = 0.3  # Large cycles unlikely to be fraud
        
        # Time score - very fast cycles are more suspicious
        if time_span_hours < 1:
            time_score = 0.9
        elif time_span_hours < 24:
            time_score = 0.6
        else:
            time_score = max(0, 1 - (time_span_hours / 168))  # Reduce over a week

        score = (
            length_score * self.weights['circular_routing']['cycle_length'] +
            amount_score * self.weights['circular_routing']['total_amount'] +
            time_score * self.weights['circular_routing']['time_span']
        )

        return {
            'score': score,
            'components': {
                'length_score': length_score,
                'amount_score': amount_score,
                'time_score': time_score
            },
            'risk_level': self._classify_risk(score)
        }

    def score_smurfing(self, smurfing_data):
        """Score smurfing patterns - optimized for precision"""
        total_amount = smurfing_data['total_amount']
        num_transactions = smurfing_data['num_transactions']
        suspicious_score = smurfing_data.get('suspicious_score', 0.5)

        # More conservative thresholds for smurfing
        # Only flag extreme cases to reduce false positives
        
        # Amount ratio - very high amounts needed to be flagged
        if total_amount > 100000:
            amount_ratio = min(total_amount / 200000, 1.0)  # Max at $200k
        elif total_amount > 50000:
            amount_ratio = 0.6
        else:
            amount_ratio = 0.3  # Lower amounts = less likely smurfing

        # Frequency score - many transactions in short window
        if num_transactions >= 20:
            frequency_score = min(num_transactions / 50, 1.0)  # Max at 50 transactions
        elif num_transactions >= 10:
            frequency_score = 0.6
        else:
            frequency_score = 0.3

        score = (
            amount_ratio * self.weights['smurfing']['amount_ratio'] +
            frequency_score * self.weights['smurfing']['frequency'] +
            suspicious_score * self.weights['smurfing']['uniformity']
        )

        return {
            'score': score,
            'components': {
                'amount_ratio': amount_ratio,
                'frequency_score': frequency_score,
                'uniformity_score': suspicious_score
            },
            'risk_level': self._classify_risk(score)
        }

    def score_shell_network(self, network_data):
        """Score layered shell networks - optimized for precision"""
        network_size = network_data['size']
        avg_centrality = network_data.get('avg_centrality', 0.5)
        total_volume = network_data['total_volume']

        # Network size score - only very small networks with high bypass activity
        if network_size <= 5:
            size_score = min(network_size / 5, 1.0)
        else:
            size_score = 0.4  # Larger networks likely legitimate

        # Centrality score - must be very high to be suspicious
        if avg_centrality > 0.3:
            centrality_score = min(avg_centrality * 1.5, 1.0)
        else:
            centrality_score = 0.2

        # Volume score - shell networks have VERY low volume relative to activity
        if total_volume < 5000:
            volume_score = 0.9  # Very low volume networks are suspicious
        elif total_volume < 20000:
            volume_score = 0.6
        else:
            volume_score = 0.2  # High volume networks likely legitimate

        score = (
            size_score * self.weights['shell_network']['network_size'] +
            centrality_score * self.weights['shell_network']['centrality'] +
            volume_score * self.weights['shell_network']['volume_anomaly']
        )

        return {
            'score': score,
            'components': {
                'size_score': size_score,
                'centrality_score': centrality_score,
                'volume_score': volume_score
            },
            'risk_level': self._classify_risk(score)
        }

    def _classify_risk(self, score):
        """Classify risk level based on score"""
        if score >= 0.8:
            return 'CRITICAL'
        elif score >= 0.6:
            return 'HIGH'
        elif score >= 0.4:
            return 'MEDIUM'
        elif score >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'

    def generate_fraud_ring_output(self, detection_results, scoring_report):
        """Generate fraud ring output in required JSON format"""
        suspicious_accounts = {}
        fraud_rings = {}

        # Process circular routing patterns
        for cycle in detection_results.get('circular_routing', []):
            ring_id = cycle.get('ring_id', 'UNKNOWN')
            score_data = self.score_circular_routing(cycle)
            risk_score = score_data['score'] * 100

            # Add to fraud_rings
            if ring_id not in fraud_rings:
                fraud_rings[ring_id] = {
                    'ring_id': ring_id,
                    'member_accounts': cycle['cycle'],
                    'pattern_type': 'circular_routing',
                    'risk_score': round(risk_score, 1)
                }

            # Add accounts to suspicious_accounts
            for account in cycle['cycle']:
                if account not in suspicious_accounts:
                    suspicious_accounts[account] = {
                        'account_id': account,
                        'suspicion_score': 0,
                        'detected_patterns': [],
                        'ring_id': ring_id
                    }
                suspicious_accounts[account]['suspicion_score'] = max(
                    suspicious_accounts[account]['suspicion_score'],
                    risk_score
                )
                if 'circular_routing' not in suspicious_accounts[account]['detected_patterns']:
                    suspicious_accounts[account]['detected_patterns'].append('circular_routing')

        # Process smurfing patterns
        for smurf in detection_results.get('smurfing', []):
            ring_id = smurf.get('ring_id', 'UNKNOWN')
            score_data = self.score_smurfing(smurf)
            risk_score = score_data['score'] * 100

            # Add to fraud_rings
            if ring_id not in fraud_rings:
                fraud_rings[ring_id] = {
                    'ring_id': ring_id,
                    'member_accounts': [smurf['source_account']] + smurf.get('recipients', []),
                    'pattern_type': 'smurfing',
                    'risk_score': round(risk_score, 1)
                }

            # Add accounts
            for account in [smurf['source_account']] + smurf.get('recipients', []):
                if account not in suspicious_accounts:
                    suspicious_accounts[account] = {
                        'account_id': account,
                        'suspicion_score': 0,
                        'detected_patterns': [],
                        'ring_id': ring_id
                    }
                suspicious_accounts[account]['suspicion_score'] = max(
                    suspicious_accounts[account]['suspicion_score'],
                    risk_score
                )
                if 'smurfing' not in suspicious_accounts[account]['detected_patterns']:
                    suspicious_accounts[account]['detected_patterns'].append('smurfing')

        # Process shell networks
        for network in detection_results.get('shell_networks', []):
            ring_id = network.get('ring_id', 'UNKNOWN')
            score_data = self.score_shell_network(network)
            risk_score = score_data['score'] * 100

            # Add to fraud_rings
            if ring_id not in fraud_rings:
                fraud_rings[ring_id] = {
                    'ring_id': ring_id,
                    'member_accounts': network['accounts'],
                    'pattern_type': 'shell_network',
                    'risk_score': round(risk_score, 1)
                }

            # Add accounts
            for account in network['accounts']:
                if account not in suspicious_accounts:
                    suspicious_accounts[account] = {
                        'account_id': account,
                        'suspicion_score': 0,
                        'detected_patterns': [],
                        'ring_id': ring_id
                    }
                suspicious_accounts[account]['suspicion_score'] = max(
                    suspicious_accounts[account]['suspicion_score'],
                    risk_score
                )
                if 'shell_network' not in suspicious_accounts[account]['detected_patterns']:
                    suspicious_accounts[account]['detected_patterns'].append('shell_network')

        # Sort suspicious accounts by suspicion score (descending)
        sorted_suspicious = sorted(
            suspicious_accounts.values(),
            key=lambda x: x['suspicion_score'],
            reverse=True
        )

        # Create summary
        summary = {
            'total_accounts_analyzed': scoring_report.get('summary', {}).get('total_accounts', 0),
            'suspicious_accounts_flagged': len(suspicious_accounts),
            'fraud_rings_detected': len(fraud_rings),
            'processing_time_seconds': 0  # Will be updated by caller
        }

        return {
            'suspicious_accounts': sorted_suspicious,
            'fraud_rings': list(fraud_rings.values()),
            'summary': summary
        }

    def generate_overall_report(self, detection_results):
        """Generate comprehensive scoring report"""
        report = {
            'summary': {
                'total_circular_patterns': len(detection_results.get('circular_routing', [])),
                'total_smurfing_groups': len(detection_results.get('smurfing', [])),
                'total_shell_networks': len(detection_results.get('shell_networks', [])),
                'total_accounts': len(set(
                    sum([list(c.get('cycle', [])) for c in detection_results.get('circular_routing', [])], []) +
                    [s['source_account'] for s in detection_results.get('smurfing', [])] +
                    sum([n['accounts'] for n in detection_results.get('shell_networks', [])], [])
                ))
            },
            'detailed_scores': []
        }

        # Score circular routing
        for cycle in detection_results.get('circular_routing', []):
            score_data = self.score_circular_routing(cycle)
            report['detailed_scores'].append({
                'type': 'circular_routing',
                'data': cycle,
                'score': score_data
            })

        # Score smurfing
        for smurf in detection_results.get('smurfing', []):
            score_data = self.score_smurfing(smurf)
            report['detailed_scores'].append({
                'type': 'smurfing',
                'data': smurf,
                'score': score_data
            })

        # Score shell networks
        for network in detection_results.get('shell_networks', []):
            score_data = self.score_shell_network(network)
            report['detailed_scores'].append({
                'type': 'shell_network',
                'data': network,
                'score': score_data
            })

        # Calculate overall risk
        if report['detailed_scores']:
            avg_score = np.mean([item['score']['score'] for item in report['detailed_scores']])
            max_score = max([item['score']['score'] for item in report['detailed_scores']])
            report['overall_risk'] = {
                'average_score': avg_score,
                'max_score': max_score,
                'risk_level': self._classify_risk(max_score)
            }
        else:
            report['overall_risk'] = {
                'average_score': 0,
                'max_score': 0,
                'risk_level': 'MINIMAL'
            }

        return report