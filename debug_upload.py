import sys
sys.path.insert(0, 'backend')

from main import app
import io

# Create a test CSV file in memory
csv_content = b'''transaction_id,sender_id,receiver_id,amount,timestamp
TXN_001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00'''

# Use Flask test client
with app.test_client() as client:
    response = client.post('/api/upload-transactions', 
                          data={'file': (io.BytesIO(csv_content), 'test.csv')},
                          content_type='multipart/form-data')
    
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(response.get_json() or response.data.decode())
