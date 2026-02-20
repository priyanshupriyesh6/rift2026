import sys
sys.path.insert(0, r'c:\Users\priya\Desktop\rift2026\backend')

import pandas as pd
from detector import MoneyMulingDetector
from scoring import SuspiciousActivityScorer

# Create test data
data = {
    'transaction_id': ['CIRC_001', 'CIRC_002', 'CIRC_003'],
    'from_account': ['ACC_A', 'ACC_B', 'ACC_C'],
    'to_account': ['ACC_B', 'ACC_C', 'ACC_A'],
    'amount': [10000.00, 9500.00, 9000.00],
    'timestamp': pd.to_datetime([
        '2026-02-15 10:00:00', '2026-02-15 10:05:00', '2026-02-15 10:10:00'
    ])
}

df = pd.DataFrame(data)

# Test detector
detector = MoneyMulingDetector()
detector.load_transactions(df)
detection_results = detector.run_full_detection()

print("=" * 60)
print("Detection Results Test")
print("=" * 60)
print(f"\nDetection results keys: {detection_results.keys()}")
print(f"Circular routing cycles found: {len(detection_results.get('circular_routing', []))}")
print(f"Detection results for circular_routing:")
print(f"  {detection_results.get('circular_routing')}")

# Test scoring
scorer = SuspiciousActivityScorer()
scoring_report = scorer.generate_overall_report(detection_results)
print(f"\nScoring report keys: {scoring_report.keys()}")

fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)
print(f"\nFraud ring output keys: {fraud_ring_output.keys()}")
print(f"Fraud rings found: {len(fraud_ring_output.get('fraud_rings', []))}")
print(f"Fraud rings:")
for ring in fraud_ring_output.get('fraud_rings', []):
    print(f"  {ring}")
