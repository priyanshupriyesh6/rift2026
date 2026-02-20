import urllib.request
import json
from datetime import datetime, timedelta

# Create a test CSV with patterns that SHOULD be detected
# Pattern 1: Circular routing (A -> B -> C -> A)
# Pattern 2: Smurfing (large amount split into small transactions)

csv_content = '''transaction_id,sender_id,receiver_id,amount,timestamp
CIRC_001,ACC_A,ACC_B,10000.00,2026-02-15 10:00:00
CIRC_002,ACC_B,ACC_C,9500.00,2026-02-15 10:05:00
CIRC_003,ACC_C,ACC_A,9000.00,2026-02-15 10:10:00
SMURF_001,SMURF_SOURCE,ACC_D,2000.00,2026-02-16 09:00:00
SMURF_002,SMURF_SOURCE,ACC_E,2100.00,2026-02-16 09:05:00
SMURF_003,SMURF_SOURCE,ACC_F,2050.00,2026-02-16 09:10:00
SMURF_004,SMURF_SOURCE,ACC_G,2150.00,2026-02-16 09:15:00
SMURF_005,SMURF_SOURCE,ACC_H,2000.00,2026-02-16 09:20:00
NORMAL_001,USER_1,USER_2,500.00,2026-02-14 08:00:00
NORMAL_002,USER_2,USER_3,600.00,2026-02-14 09:00:00'''

print("Test CSV Content:")
print(csv_content)
print("\n" + "="*60)

with open('test-comprehensive.csv', 'w') as f:
    f.write(csv_content)

# Test 1: Upload
print("\n[TEST 1] UPLOADING...")
try:
    url = 'http://localhost:5000/api/upload-transactions'
    with open('test-comprehensive.csv', 'rb') as f:
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="test-comprehensive.csv"\r\n'
            f'Content-Type: text/csv\r\n\r\n'
        ).encode() + f.read() + f'\r\n--{boundary}--\r\n'.encode()
        
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        print("✓ Upload successful!")
        if result.get('data'):
            print(f"  - Loaded {result['data'].get('num_transactions')} transactions")
            print(f"  - {result['data'].get('num_accounts')} accounts in network")
except Exception as e:
    print(f"✗ Upload failed: {e}")
    import sys
    sys.exit(1)

# Test 2: Run Detection
print("\n[TEST 2] RUNNING DETECTION...")
try:
    url = 'http://localhost:5000/api/run-detection'
    req = urllib.request.Request(url, data=b'', method='POST')
    req.add_header('Content-Type', 'application/json')
    
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    
    if result.get('data') and result['data'].get('fraud_ring_output'):
        fraud_rings = result['data']['fraud_ring_output'].get('fraud_rings', [])
        suspicious_accounts = result['data']['fraud_ring_output'].get('suspicious_accounts', [])
        print(f"✓ Detection completed!")
        print(f"  - Found {len(fraud_rings)} fraud rings")
        print(f"  - Found {len(suspicious_accounts)} suspicious accounts")
        
        if fraud_rings:
            print("\nFraud Rings:")
            for ring in fraud_rings[:5]:
                print(f"  - {ring.get('ring_id')}: {ring.get('pattern_type')} (Risk: {ring.get('risk_score')})")
        
        if suspicious_accounts:
            print("\nSuspicious Accounts:")
            for acc in suspicious_accounts[:5]:
                print(f"  - {acc.get('account_id')}: Score {acc.get('suspicion_score')}")
    else:
        print("✗ No fraud rings in response!")
        print(json.dumps(result, indent=2)[:500])
        
except Exception as e:
    print(f"✗ Detection failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Get Fraud Rings
print("\n[TEST 3] FETCHING FRAUD RINGS...")
try:
    url = 'http://localhost:5000/api/fraud-rings'
    req = urllib.request.Request(url)
    
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    
    if result.get('data') and result['data'].get('fraud_rings'):
        fraud_rings = result['data']['fraud_rings']
        print(f"✓ Retrieved {len(fraud_rings)} fraud rings")
        for ring in fraud_rings[:3]:
            print(f"  - {ring}")
    else:
        print("✗ No fraud rings returned!")
        print(json.dumps(result, indent=2)[:300])
except Exception as e:
    print(f"✗ Get fraud rings failed: {e}")

print("\n" + "="*60)
print("Test Summary: Check backend logs for [UPLOAD] and [DETECTION] messages")
