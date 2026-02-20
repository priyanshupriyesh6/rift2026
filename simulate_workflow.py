import sys
sys.path.insert(0, r'c:\Users\priya\Desktop\rift2026\backend')

import pandas as pd
from detector import MoneyMulingDetector
from scoring import SuspiciousActivityScorer
from graph_rules import TransactionGraphAnalyzer
import json
from io import BytesIO

# Simulate what happens in the API

# Create test CSV
csv_content = """transaction_id,sender_id,receiver_id,amount,timestamp
CIRC_001,ACC_A,ACC_B,10000.00,2026-02-15 10:00:00
CIRC_002,ACC_B,ACC_C,9500.00,2026-02-15 10:05:00
CIRC_003,ACC_C,ACC_A,9000.00,2026-02-15 10:10:00
SMURF_001,SMURF_SOURCE,ACC_D,2000.00,2026-02-16 09:00:00
SMURF_002,SMURF_SOURCE,ACC_E,2100.00,2026-02-16 09:05:00
SMURF_003,SMURF_SOURCE,ACC_F,2050.00,2026-02-16 09:10:00
SMURF_004,SMURF_SOURCE,ACC_G,2150.00,2026-02-16 09:15:00
SMURF_005,SMURF_SOURCE,ACC_H,2000.00,2026-02-16 09:20:00
NORMAL_001,USER_1,USER_2,500.00,2026-02-14 08:00:00
NORMAL_002,USER_2,USER_3,600.00,2026-02-14 09:00:00"""

# Simulate upload step
print("=" * 60)
print("SIMULATING API WORKFLOW")
print("=" * 60)

df = pd.read_csv(BytesIO(csv_content.encode()))
df.rename(columns={'sender_id': 'from_account', 'receiver_id': 'to_account'}, inplace=True)
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

detector = MoneyMulingDetector()
detector.load_transactions(df)
analyzer = TransactionGraphAnalyzer(detector)

print(f"\n[UPLOAD] Loaded {len(df)} transactions, {len(set(df['from_account']).union(set(df['to_account'])))} accounts")

# Simulate detection step
print(f"\n[DETECTION] Running detection...")
detection_results = detector.run_full_detection()
print(f"[DETECTION] Detection complete: {detection_results.keys()}")

scorer = SuspiciousActivityScorer()
scoring_report = scorer.generate_overall_report(detection_results)
fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)

print(f"[DETECTION] Found {len(fraud_ring_output.get('fraud_rings', []))} fraud rings")
print(f"[DETECTION] Found {len(fraud_ring_output.get('suspicious_accounts', []))} suspicious accounts")

# Simulate fraud-rings step
print(f"\n[FRAUD-RINGS] Called after detection...")
print(f"[FRAUD-RINGS] Available detection results: {detection_results.get('circular_routing') is not None}")

# Now simulate what /api/fraud-rings does
fraud_ring_output_2 = scorer.generate_fraud_ring_output(detection_results, scoring_report)
print(f"[FRAUD-RINGS] Generated fraud ring output: {len(fraud_ring_output_2.get('fraud_rings', []))} rings")

print(f"\n\nFinal fraud rings:")
for ring in fraud_ring_output_2.get('fraud_rings', []):
    print(f"  {ring}")
