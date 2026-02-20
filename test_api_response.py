import requests
import json

BASE_URL = "http://localhost:5000"

# First, clear by running through test workflow
print("=" * 60)
print("Testing Detection Endpoint Response")
print("=" * 60)

response = requests.post(f"{BASE_URL}/api/run-detection")
print(f"\nStatus Code: {response.status_code}")
print(f"Response:")
result = response.json()

# Pretty print key parts
print(f"\nTesting data loaded: {result.get('success')}")
if result.get('success'):
    fraud_ring_output = result.get('data', {}).get('fraud_ring_output', {})
    print(f"\nFraud Ring Output Keys: {fraud_ring_output.keys()}")
    print(f"Number of fraud rings: {len(fraud_ring_output.get('fraud_rings', []))}")
    print(f"Fraud rings:")
    for ring in fraud_ring_output.get('fraud_rings', []):
        print(f"  {ring}")
    print(f"\nNumber of suspicious accounts: {len(fraud_ring_output.get('suspicious_accounts', []))}")
    print(f"Suspicious accounts:")
    for acc in fraud_ring_output.get('suspicious_accounts', []):
        print(f"  {acc}")
