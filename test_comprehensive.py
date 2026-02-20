#!/usr/bin/env python
"""
Comprehensive End-to-End Test of Fraud Detection System
Uses Flask test_client for in-process testing with full state management
"""
import sys
import os
os.chdir(r'c:\Users\priya\Desktop\rift2026\backend')
sys.path.insert(0, r'c:\Users\priya\Desktop\rift2026\backend')

from main import app
import json
from io import BytesIO

def test_circular_routing():
    """Test detection of circular routing pattern"""
    csv_data = b"""transaction_id,sender_id,receiver_id,amount,timestamp
TX001,ACC_A,ACC_B,10000.00,2026-02-15 10:00:00
TX002,ACC_B,ACC_C,9500.00,2026-02-15 10:05:00
TX003,ACC_C,ACC_A,9000.00,2026-02-15 10:10:00"""
    
    client = app.test_client()
    
    # Upload
    response = client.post(
        '/api/upload-transactions',
        data={'file': (BytesIO(csv_data), 'test.csv')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200, f"Upload failed with {response.status_code}"
    
    # Run detection
    response = client.post('/api/run-detection')
    assert response.status_code == 200, f"Detection failed with {response.status_code}"
    
    result = json.loads(response.data)
    fraud_rings = result['data']['fraud_ring_output']['fraud_rings']
    
    assert len(fraud_rings) == 1, f"Expected 1 fraud ring, got {len(fraud_rings)}"
    assert fraud_rings[0]['pattern_type'] == 'circular_routing'
    assert set(fraud_rings[0]['member_accounts']) == {'ACC_A', 'ACC_B', 'ACC_C'}
    
    print("[PASS] Circular routing detection works correctly")
    return True

def test_comprehensive_patterns():
    """Test detection with multiple fraud patterns"""
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
    
    client = app.test_client()
    
    # Upload
    response = client.post(
        '/api/upload-transactions',
        data={'file': (BytesIO(csv_data), 'test.csv')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    
    upload_data = json.loads(response.data)
    assert upload_data['data']['num_transactions'] == 10
    assert upload_data['data']['num_accounts'] == 12
    
    # Run detection
    response = client.post('/api/run-detection')
    assert response.status_code == 200
    
    result = json.loads(response.data)
    assert result['success'] == True
    
    fraud_ring_output = result['data']['fraud_ring_output']
    fraud_rings = fraud_ring_output['fraud_rings']
    suspicious_accounts = fraud_ring_output['suspicious_accounts']
    
    assert len(fraud_rings) >= 1, f"Expected at least 1 fraud ring, got {len(fraud_rings)}"
    assert len(suspicious_accounts) >= 3, f"Expected at least 3 suspicious accounts, got {len(suspicious_accounts)}"
    
    # Verify circular routing was detected
    circular_rings = [r for r in fraud_rings if r['pattern_type'] == 'circular_routing']
    assert len(circular_rings) >= 1, "Circular routing pattern not detected"
    
    # Verify accounts from circular pattern are flagged
    circular_accounts = set()
    for ring in circular_rings:
        circular_accounts.update(ring['member_accounts'])
    
    suspicious_account_ids = {acc['account_id'] for acc in suspicious_accounts}
    assert circular_accounts.issubset(suspicious_account_ids), "Not all circular routing accounts are flagged as suspicious"
    
    print("[PASS] Comprehensive pattern detection works correctly")
    print(f"  - Found {len(fraud_rings)} fraud ring(s)")
    print(f"  - Flagged {len(suspicious_accounts)} suspicious account(s)")
    return True

def test_api_response_format():
    """Test that API responses have correct format"""
    csv_data = b"""transaction_id,sender_id,receiver_id,amount,timestamp
TX001,ACC_A,ACC_B,1000.00,2026-02-15 10:00:00"""
    
    client = app.test_client()
    
    # Upload
    response = client.post(
        '/api/upload-transactions',
        data={'file': (BytesIO(csv_data), 'test.csv')},
        content_type='multipart/form-data'
    )
    
    result = json.loads(response.data)
    
    # Check response format
    assert 'success' in result, "Missing 'success' field"
    assert 'data' in result, "Missing 'data' field"
    assert isinstance(result['success'], bool), "'success' should be boolean"
    assert isinstance(result['data'], dict), "'data' should be dict"
    
    # Check no serialization errors
    assert 'error' not in result or result['error'] is None, f"Error field present: {result.get('error')}"
    
    print("[PASS] API response format is correct")
    return True

# Run all tests
print("=" * 70)
print("RUNNING COMPREHENSIVE FRAUD DETECTION TESTS")
print("=" * 70)

try:
    print("\n[TEST 1] API Response Format...")
    test_api_response_format()
    
    print("\n[TEST 2] Circular Routing Detection...")
    test_circular_routing()
    
    print("\n[TEST 3] Comprehensive Pattern Detection...")
    test_comprehensive_patterns()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED - SYSTEM IS WORKING CORRECTLY")
    print("=" * 70)
    
except AssertionError as e:
    print(f"\n[FAIL] {e}")
    import sys
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)
