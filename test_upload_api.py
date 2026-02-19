import urllib.request
import json
import csv

# Create test CSV with new headers
csv_content = '''transaction_id,sender_id,receiver_id,amount,timestamp
TXN_001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00'''

print("CSV Content to upload:")
print(csv_content)
print()

# Verify headers
headers = csv_content.split('\n')[0].split(',')
print(f"CSV headers: {headers}")
print()

with open('test-upload.csv', 'w') as f:
    f.write(csv_content)

# Test upload using urllib
try:
    url = 'http://localhost:5000/api/upload-transactions'
    with open('test-upload.csv', 'rb') as f:
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="test-upload.csv"\r\n'
            f'Content-Type: text/csv\r\n\r\n'
        ).encode() + f.read() + f'\r\n--{boundary}--\r\n'.encode()
        
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        print('✓ Upload successful!')
        print(json.dumps(result, indent=2))
except urllib.error.HTTPError as e:
    print(f'✗ HTTP Error {e.code}')
    error_body = e.read().decode()
    print(f'Response: {error_body}')
    try:
        error_json = json.loads(error_body)
        print(json.dumps(error_json, indent=2))
    except:
        print(error_body)
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()


