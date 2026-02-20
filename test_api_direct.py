import sys
import os

# Change to backend directory for proper imports
os.chdir(r'c:\Users\priya\Desktop\rift2026\backend')
sys.path.insert(0, r'c:\Users\priya\Desktop\rift2026\backend')

# Now import flask app
from main import app
import json
from io import BytesIO

# Create test CSV
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

print("=" * 60)
print("Testing API Direct")
print("=" * 60)

client = app.test_client()

# Upload
print("\n[1] Uploading test data...")
response = client.post(
    '/api/upload-transactions',
    data={'file': (BytesIO(csv_data), 'test.csv')},
    content_type='multipart/form-data'
)
print(f"Upload status: {response.status_code}")
upload_result = json.loads(response.data)
print(f"Upload success: {upload_result.get('success')}")
if upload_result.get('success'):
    print(f"Upload data: {upload_result.get('data')}")

# Run detection
print("\n[2] Running detection...")
response = client.post('/api/run-detection')
print(f"Detection status: {response.status_code}")
detection_result = json.loads(response.data)
print(f"Detection success: {detection_result.get('success')}")
if detection_result.get('success'):
    data = detection_result.get('data', {})
    fraud_ring_output = data.get('fraud_ring_output', {})
    print(f"Fraud rings found: {len(fraud_ring_output.get('fraud_rings', []))}")
    print(f"\nFraud rings:")
    for ring in fraud_ring_output.get('fraud_rings', []):
        print(f"  {ring}")

# Get fraud rings  
print("\n[3] Getting fraud rings...")
response = client.get('/api/fraud-rings')
print(f"Fraud rings status: {response.status_code}")
fraud_rings_result = json.loads(response.data)
print(f"Fraud rings success: {fraud_rings_result.get('success')}")
print(f"Fraud rings found: {len(fraud_rings_result.get('data', {}).get('fraud_rings', []))}")
for ring in fraud_rings_result.get('data', {}).get('fraud_rings', []):
    print(f"  {ring}")
