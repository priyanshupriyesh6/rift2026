# Backend Testing Guide for VS Code

## Option 1: Using REST Client Extension (Recommended)

### Install REST Client Extension
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "REST Client" by Huachao Mao
4. Click Install

### Create Test File
Create a file named `test.http` in the project root with this content:

```http
### Health Check
GET http://localhost:5000/api/health

### Get Sample Data
GET http://localhost:5000/api/sample-data

### Upload Sample Transactions
POST http://localhost:5000/api/upload-transactions
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="sample.csv"
Content-Type: text/csv

transaction_id,from_account,to_account,amount,timestamp
TXN_0001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_0002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_0003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00
------WebKitFormBoundary7MA4YWxkTrZu0gW--

### Run Detection (after uploading data)
POST http://localhost:5000/api/run-detection

### Get Fraud Rings
GET http://localhost:5000/api/fraud-rings

### Get Network Visualization
GET http://localhost:5000/api/visualizations/network

### Get Risk Distribution
GET http://localhost:5000/api/visualizations/risk-distribution

### Download Fraud Report
GET http://localhost:5000/api/download-fraud-report
```

### How to Use
1. Open `test.http` file in VS Code
2. You'll see "Send Request" link above each request
3. Click "Send Request" to test any endpoint
4. Response appears in split panel on the right

---

## Option 2: Using PowerShell (Built-in)

### Test Health Endpoint
```powershell
# Simple health check
Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test Get Sample Data
```powershell
$response = Invoke-WebRequest -Uri 'http://localhost:5000/api/sample-data' -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

### Test Upload with CSV File
```powershell
# First, create a sample CSV file
@"
transaction_id,from_account,to_account,amount,timestamp
TXN_0001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_0002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_0003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00
CIRC_0001,CIRC_001,CIRC_002,50000.00,2026-02-05 14:00:00
CIRC_0002,CIRC_002,CIRC_003,45000.00,2026-02-05 14:30:00
CIRC_0003,CIRC_003,CIRC_001,40000.00,2026-02-05 15:00:00
"@ | Out-File -FilePath "sample.csv" -Encoding UTF8

# Upload the file
$file = Get-Item "sample.csv"
$form = @{ file = $file }
$response = Invoke-WebRequest -Uri 'http://localhost:5000/api/upload-transactions' -FileUpload $form -UseBasicParsing
$response.Content
```

### Full Backend Test Script
Save this as `test-backend.ps1`:

```powershell
# Backend API Testing Script

$baseUrl = "http://localhost:5000"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "=== Backend API Testing ===" -ForegroundColor Cyan
Write-Host "Time: $timestamp" -ForegroundColor Gray
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/health" -UseBasicParsing
    Write-Host "✓ Status: 200 OK" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Get Sample Data
Write-Host "Test 2: Get Sample Data" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/sample-data" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✓ Status: 200 OK" -ForegroundColor Green
    Write-Host "  - Generated $(($data.transactions | Measure-Object).Count) transactions"
    Write-Host "  - Patterns: $(($data.patterns_included -Join ', '))"
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Upload & Run Detection
Write-Host "Test 3: Upload Data & Run Detection" -ForegroundColor Yellow
try {
    # Create sample CSV
    $csvContent = @"
transaction_id,from_account,to_account,amount,timestamp
TXN_0001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_0002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_0003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00
CIRC_0001,CIRC_001,CIRC_002,50000.00,2026-02-05 14:00:00
CIRC_0002,CIRC_002,CIRC_003,45000.00,2026-02-05 14:30:00
CIRC_0003,CIRC_003,CIRC_001,40000.00,2026-02-05 15:00:00
SMURF_0001,SMURF_SRC,ACC_010,5000.00,2026-02-02 09:00:00
SMURF_0002,SMURF_SRC,ACC_011,4800.00,2026-02-02 09:05:00
"@
    
    $csvContent | Out-File -FilePath "test-data.csv" -Encoding UTF8
    
    # Upload file
    $file = Get-Item "test-data.csv"
    $form = @{ file = $file }
    $uploadResponse = Invoke-WebRequest -Uri "$baseUrl/api/upload-transactions" -FileUpload $form -UseBasicParsing
    Write-Host "✓ Upload Status: 200 OK" -ForegroundColor Green
    
    # Run detection
    $detectionResponse = Invoke-WebRequest -Uri "$baseUrl/api/run-detection" -Method POST -UseBasicParsing
    $detectionData = $detectionResponse.Content | ConvertFrom-Json
    
    Write-Host "✓ Detection Status: 200 OK" -ForegroundColor Green
    Write-Host "  - Circular Routing: $(($detectionData.detection_results.circular_routing | Measure-Object).Count) patterns"
    Write-Host "  - Smurfing: $(($detectionData.detection_results.smurfing | Measure-Object).Count) patterns"
    Write-Host "  - Shell Networks: $(($detectionData.detection_results.shell_networks | Measure-Object).Count) patterns"
    
    if ($detectionData.fraud_ring_output) {
        Write-Host "  - Fraud Rings Detected: $(($detectionData.fraud_ring_output.fraud_rings | Measure-Object).Count)"
        Write-Host "  - Suspicious Accounts: $(($detectionData.fraud_ring_output.suspicious_accounts | Measure-Object).Count)"
    }
    
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Get Fraud Rings
Write-Host "Test 4: Get Fraud Rings" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/fraud-rings" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✓ Status: 200 OK" -ForegroundColor Green
    Write-Host "  - Fraud Rings: $(($data.fraud_rings | Measure-Object).Count)"
    if ($data.fraud_rings.Count -gt 0) {
        foreach ($ring in $data.fraud_rings[0..([Math]::Min(2, $data.fraud_rings.Count-1))]) {
            Write-Host "    - $($ring.ring_id): $($ring.pattern_type) (Risk: $($ring.risk_score))"
        }
    }
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: Get Network Visualization
Write-Host "Test 5: Get Network Visualization Data" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/visualizations/network" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✓ Status: 200 OK" -ForegroundColor Green
    Write-Host "  - Data format: Plotly JSON"
    Write-Host "  - Has Traces: $($data.plotly_data.data.Count -gt 0)"
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 6: Download Fraud Report
Write-Host "Test 6: Download Fraud Report (JSON)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/download-fraud-report" -UseBasicParsing -OutFile "fraud_report.json"
    Write-Host "✓ Status: 200 OK" -ForegroundColor Green
    Write-Host "✓ Report saved to: fraud_report.json"
    
    # Show report summary
    $report = Get-Content "fraud_report.json" | ConvertFrom-Json
    Write-Host "  - Suspicious Accounts: $(($report.suspicious_accounts | Measure-Object).Count)"
    Write-Host "  - Fraud Rings: $(($report.fraud_rings | Measure-Object).Count)"
    if ($report.summary) {
        Write-Host "  - Summary: $(($report.summary | ConvertTo-Json))"
    }
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Testing Complete ===" -ForegroundColor Cyan
```

Run it with:
```powershell
./test-backend.ps1
```

---

## Option 3: Using curl (Command Line)

### Basic Tests
```bash
# Health check
curl http://localhost:5000/api/health

# Get sample data
curl http://localhost:5000/api/sample-data

# Create CSV file with sample data
cat > sample.csv << EOF
transaction_id,from_account,to_account,amount,timestamp
TXN_0001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_0002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_0003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00
EOF

# Upload file
curl -F "file=@sample.csv" http://localhost:5000/api/upload-transactions

# Run detection
curl -X POST http://localhost:5000/api/run-detection

# Get fraud rings
curl http://localhost:5000/api/fraud-rings

# Download report
curl http://localhost:5000/api/download-fraud-report > fraud_report.json
```

---

## Option 4: Built-in VS Code Debugging

### Step 1: Install Python Extension
- Go to Extensions (Ctrl+Shift+X)
- Search for "Python" by Microsoft
- Install it

### Step 2: Create Debug Configuration
1. Create `.vscode/launch.json` in project root
2. Add this configuration:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask Backend",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "main.py",
                "FLASK_ENV": "development"
            },
            "args": ["run", "--host=0.0.0.0", "--port=5000"],
            "jinja": true,
            "cwd": "${workspaceFolder}/backend",
            "console": "integratedTerminal"
        }
    ]
}
```

### Step 3: Debug the Backend
1. Set breakpoints in `detector.py`, `scoring.py`, etc.
2. Press F5 to start debugging
3. Test API endpoints
4. Debugger will pause at breakpoints

---

## Step-by-Step Testing Procedure

### 1. **Ensure Backend is Running**
```bash
cd backend
python main.py
```
You should see:
```
* Running on http://127.0.0.1:5000
* Debugger is active!
```

### 2. **Open VS Code Terminal**
- Ctrl+` (backtick) to open integrated terminal
- Or use Command Palette: Terminal: Create New Terminal

### 3. **Quick Test with PowerShell**
```powershell
# Test health
Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -UseBasicParsing
```

### 4. **Full Automated Test**
Save the PowerShell script above as `test-backend.ps1` and run:
```powershell
./test-backend.ps1
```

### 5. **View Results**
- Check terminal output for test results
- Check `fraud_report.json` for exported data
- Check backend console for debug output

---

## Expected Outputs

### Health Check Response
```json
{"status": "healthy", "timestamp": "2026-02-19T..."}
```

### Sample Data Response
```json
{
  "transactions": [...array of transaction objects...],
  "message": "Sample data generated with embedded suspicious patterns",
  "patterns_included": [
    "Circular fund routing (5 accounts)",
    "Smurfing pattern (1 source to 15 destinations)",
    "Layered shell network (8 accounts in chain)"
  ]
}
```

### Detection Response (after upload + run-detection)
```json
{
  "detection_results": {...},
  "scoring_report": {...},
  "fraud_ring_output": {
    "suspicious_accounts": [...],
    "fraud_rings": [...],
    "summary": {...}
  }
}
```

---

## Recommended Workflow

1. **Start Backend**: `python main.py` (keep running)
2. **Open test.http file** in VS Code
3. **Test endpoints one by one**:
   - Click "Send Request" on each endpoint
   - View responses in right panel
4. **Check result files**:
   - `fraud_report.json` - exported report
   - `test-data.csv` - uploaded test data
   - VS Code Debug Console - detailed logs

This way you can fully test all backend functionality without needing the frontend! 🎯
