import socket

# Create test CSV
csv_content = b'''transaction_id,sender_id,receiver_id,amount,timestamp
TXN_001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00'''

# HTTP multipart form-data boundary
boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'

# Build the HTTP request body
body = b'--' + boundary + b'\r\n'
body += b'Content-Disposition: form-data; name="file"; filename="test.csv"\r\n'
body += b'Content-Type: text/csv\r\n\r\n'
body += csv_content + b'\r\n'
body += b'--' + boundary + b'--\r\n'

# Build the HTTP request
request = b'POST /api/upload-transactions HTTP/1.1\r\n'
request += b'Host: localhost:5000\r\n'
request += b'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
request += b'Content-Length: ' + str(len(body)).encode() + b'\r\n'
request += b'Connection: close\r\n'
request += b'\r\n'

# Send the request
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(('localhost', 5000))
    sock.sendall(request + body)
    
    # Receive the response
    response = b''
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    
    print(response.decode('utf-8', errors='replace'))
    
finally:
    sock.close()
