#!/usr/bin/env python
"""
Direct debugging of the entire API workflow using Flask test client
"""
import sys
import os
os.chdir(r'c:\Users\priya\Desktop\rift2026\backend')
sys.path.insert(0, r'c:\Users\priya\Desktop\rift2026\backend')

from main import app
import json
from io import BytesIO

# Create test CSV with clear circular routing pattern
csv_data = b"""transaction_id,sender_id,receiver_id,amount,timestamp
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

print("=" * 70)
print("DIRECT API TEST WITH DETAILED DEBUGGING")
print("=" * 70)

client = app.test_client()

# Step 1: Upload
print("\n[STEP 1] Uploading CSV...")
response = client.post(
    '/api/upload-transactions',
    data={'file': (BytesIO(csv_data), 'test.csv')},
    content_type='multipart/form-data'
)
print(f"Response Status: {response.status_code}")
upload_result = json.loads(response.data)
print(f"Upload success: {upload_result.get('success')}")
if upload_result.get('data'):
    data = upload_result['data']
    print(f"  - numTransactions: {data.get('num_transactions')}")
    print(f"  - numAccounts: {data.get('num_accounts')}")

# Step 2: Check detector state after upload
from main import detector, scorer
print(f"\n[CHECK] Detector state after upload:")
print(f"  - transactions loaded: {detector.transactions is not None}")
if detector.transactions is not None:
    print(f"  - transaction count: {len(detector.transactions)}")
    print(f"  - graph nodes: {detector.graph.number_of_nodes()}")
    print(f"  - graph edges: {detector.graph.number_of_edges()}")

# Step 3: Run detection manually
print(f"\n[STEP 2] Running detection manually (not via API)...")
detection_results = detector.run_full_detection()
print(f"  - detection_results keys: {detection_results.keys()}")
print(f"  - circular_routing cycles: {len(detection_results.get('circular_routing', []))}")
print(f"  - smurfing patterns: {len(detection_results.get('smurfing', []))}")
print(f"  - shell_networks: {len(detection_results.get('shell_networks', []))}")

# Step 4: Check scoring
print(f"\n[STEP 3] Scoring detection results...")
scoring_report = scorer.generate_overall_report(detection_results)
print(f"  - scoring_report keys: {scoring_report.keys()}")

# Step 5: Generate fraud rings
print(f"\n[STEP 4] Generating fraud ring output...")
fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)
print(f"  - fraud_ring_output keys: {fraud_ring_output.keys()}")
print(f"  - fraud rings: {len(fraud_ring_output.get('fraud_rings', []))}")
print(f"  - suspicious accounts: {len(fraud_ring_output.get('suspicious_accounts', []))}")

if fraud_ring_output.get('fraud_rings'):
    print(f"\n  Fraud Rings Details:")
    for ring in fraud_ring_output['fraud_rings']:
        print(f"    - {ring}")

# Now compare with API call
print(f"\n[STEP 5] Calling /api/run-detection endpoint...")
response = client.post('/api/run-detection')
print(f"Response Status: {response.status_code}")
detection_api_result = json.loads(response.data)
print(f"API success: {detection_api_result.get('success')}")
if detection_api_result.get('data'):
    data = detection_api_result['data']
    fraud_ring_api = data.get('fraud_ring_output', {})
    print(f"  - fraud rings from API: {len(fraud_ring_api.get('fraud_rings', []))}")
    print(f"  - suspicious accounts from API: {len(fraud_ring_api.get('suspicious_accounts', []))}")
    
    if fraud_ring_api.get('fraud_rings'):
        print(f"\n  Fraud Rings from API:")
        for ring in fraud_ring_api['fraud_rings']:
            print(f"    - {ring}")

print("\n" + "=" * 70)
print("Test complete")
