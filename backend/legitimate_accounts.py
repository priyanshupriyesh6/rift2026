import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class LegitimateAccountDetector:
    """Identifies legitimate high-volume accounts to prevent false positives"""
    
    def __init__(self):
        self.thresholds = {
            'payroll_min_recipients': 5,  # Payroll distributes to multiple employees
            'merchant_min_transactions': 20,  # High transaction volume
            'merchant_min_total_volume': 100000,  # High total volume
            'consistent_pattern_threshold': 0.7,  # 70% consistency = legitimate pattern
        }
    
    def identify_legitimate_accounts(self, transactions_df, graph):
        """
        Identify legitimate account patterns that should not be flagged:
        - Payroll/distribution accounts: Regular, consistent payments to many recipients
        - Merchant/aggregator accounts: High-volume legitimate businesses
        - Platform/gateway accounts: Regular structured transfers
        """
        legitimate_accounts = set()
        account_profiles = {}
        
        # Analyze each account's transaction patterns
        all_accounts = set(transactions_df['from_account']).union(set(transactions_df['to_account']))
        
        for account in all_accounts:
            out_transactions = transactions_df[transactions_df['from_account'] == account]
            in_transactions = transactions_df[transactions_df['to_account'] == account]
            
            if len(out_transactions) == 0:
                continue
            
            profile = self._analyze_account_profile(account, out_transactions, in_transactions)
            account_profiles[account] = profile
            
            # Check if account matches legitimate patterns
            if self._is_payroll_account(profile):
                legitimate_accounts.add(account)
                profile['legitimate_type'] = 'PAYROLL'
            elif self._is_merchant_account(profile):
                legitimate_accounts.add(account)
                profile['legitimate_type'] = 'MERCHANT'
            elif self._is_platform_account(profile):
                legitimate_accounts.add(account)
                profile['legitimate_type'] = 'PLATFORM'
        
        return legitimate_accounts, account_profiles
    
    def _analyze_account_profile(self, account, out_transactions, in_transactions):
        """Analyze account's transaction patterns"""
        profile = {
            'account_id': account,
            'out_count': len(out_transactions),
            'in_count': len(in_transactions),
            'out_total': out_transactions['amount'].sum(),
            'in_total': in_transactions['amount'].sum(),
            'out_avg': out_transactions['amount'].mean(),
            'out_std': out_transactions['amount'].std(),
            'in_avg': in_transactions['amount'].mean(),
            'in_std': in_transactions['amount'].std(),
        }
        
        # Calculate distribution metrics
        if len(out_transactions) > 0:
            recipients = out_transactions['to_account'].value_counts()
            profile['unique_recipients'] = len(recipients)
            profile['out_concentration'] = recipients.iloc[0] / len(out_transactions) if len(recipients) > 0 else 0
            profile['out_regularity'] = self._calculate_regularity(out_transactions)
            profile['out_amount_consistency'] = self._calculate_amount_consistency(out_transactions)
        
        if len(in_transactions) > 0:
            senders = in_transactions['from_account'].value_counts()
            profile['unique_senders'] = len(senders)
            profile['in_concentration'] = senders.iloc[0] / len(in_transactions) if len(senders) > 0 else 0
            profile['in_regularity'] = self._calculate_regularity(in_transactions)
        
        return profile
    
    def _is_payroll_account(self, profile):
        """
        Payroll accounts characteristics:
        - Regular outgoing transactions
        - Multiple recipients (employees)
        - Consistent amounts
        - Regular timing
        """
        if profile.get('out_count', 0) < 5:
            return False
        
        if profile.get('unique_recipients', 0) < self.thresholds['payroll_min_recipients']:
            return False
        
        # Payroll is consistent and regular
        regularity = profile.get('out_regularity', 0)
        consistency = profile.get('out_amount_consistency', 0)
        
        return (regularity > 0.6 and consistency > 0.5)
    
    def _is_merchant_account(self, profile):
        """
        Merchant accounts characteristics:
        - High transaction volume
        - Diverse recipients (unless aggregator)
        - Consistent amounts
        - Regular pattern
        """
        if profile.get('out_count', 0) < self.thresholds['merchant_min_transactions']:
            return False
        
        if profile.get('out_total', 0) < self.thresholds['merchant_min_total_volume']:
            return False
        
        # Merchants have relatively consistent transaction amounts
        consistency = profile.get('out_amount_consistency', 0)
        
        return consistency > 0.4
    
    def _is_platform_account(self, profile):
        """
        Platform/gateway accounts characteristics:
        - High volume both in and out
        - Balanced transactions
        - Regular timing
        - Acts as intermediary for legitimate purposes
        """
        if profile.get('out_count', 0) < 10 or profile.get('in_count', 0) < 10:
            return False
        
        # Platform should have both significant in and out volume
        total_volume = profile.get('out_total', 0) + profile.get('in_total', 0)
        if total_volume < self.thresholds['merchant_min_total_volume']:
            return False
        
        # Check if balanced (not hoarding)
        ratio = profile.get('out_total', 1) / (profile.get('in_total', 1) + 1)
        if not (0.3 < ratio < 3.0):  # Not extreme in or out imbalance
            return False
        
        regularity_out = profile.get('out_regularity', 0)
        regularity_in = profile.get('in_regularity', 0)
        
        return (regularity_out > 0.5 or regularity_in > 0.5)
    
    def _calculate_regularity(self, transactions):
        """
        Calculate how regular/periodic transactions are (0-1).
        Higher = more regular pattern (like payroll)
        """
        if len(transactions) < 2:
            return 0
        
        # Get time intervals between transactions
        sorted_trans = transactions.sort_values('timestamp')
        timestamps = sorted_trans['timestamp'].values
        
        if len(timestamps) < 2:
            return 0
        
        # Calculate intervals in days
        intervals = []
        for i in range(1, len(timestamps)):
            # Convert numpy datetime64 to timedelta
            delta = (timestamps[i] - timestamps[i-1]) / np.timedelta64(1, 'D')
            intervals.append(delta)
        
        if len(intervals) == 0:
            return 0
        
        # Regularity: 1 - (stdev of intervals / mean interval)
        intervals = np.array(intervals)
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if mean_interval == 0:
            return 0
        
        regularity = 1 - min(std_interval / mean_interval, 1.0)
        return max(0, regularity)
    
    def _calculate_amount_consistency(self, transactions):
        """
        Calculate how consistent transaction amounts are (0-1).
        Higher = more consistent (like salary payments)
        """
        if len(transactions) < 2:
            return 0
        
        amounts = transactions['amount'].values
        if len(amounts) == 0:
            return 0
        
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        if mean_amount == 0:
            return 0
        
        # Consistency: 1 - (stdev / mean)
        consistency = 1 - min(std_amount / mean_amount, 1.0)
        return max(0, consistency)
    
    def should_flag_account(self, account_id, suspicious_reasons, legitimate_accounts):
        """
        Determine if account should be flagged despite suspicious patterns.
        Legitimate accounts can have suspicious-looking patterns without being fraudulent.
        """
        if account_id in legitimate_accounts:
            return False
        
        return True
    
    def filter_suspicious_accounts(self, suspicious_accounts, legitimate_accounts, account_profiles):
        """
        Filter out false positives from legitimate accounts.
        """
        filtered = []
        
        for account in suspicious_accounts:
            # If it's a known legitimate account, skip it
            if account in legitimate_accounts:
                continue
            
            # Additional check: if account has very high volume, be more conservative
            profile = account_profiles.get(account, {})
            out_total = profile.get('out_total', 0)
            
            # High-volume accounts need stronger evidence of fraud
            if out_total > 500000:
                # Require more patterns or higher score for high-volume accounts
                suspicious_accounts[account]['confidence_multiplier'] = 0.8
            
            filtered.append(account)
        
        return filtered
