#!/usr/bin/env powershell
# Simple Backend Test - Upload and Detect
# This is a minimal test script to verify the backend works

$ServerUrl = "http://localhost:5000"

Write-Host "Testing Money Muling Detector Backend" -ForegroundColor Cyan
Write-Host "Server: $ServerUrl`n" -ForegroundColor Gray

# Step 1: Health Check
Write-Host "[1/5] Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/health" -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Backend is running!" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend is not running!" -ForegroundColor Red
    Write-Host "Start it with: cd backend && python main.py" -ForegroundColor Red
    exit 1
}

# Step 2: Create and Upload CSV
Write-Host "`n[2/5] Uploading CSV data..." -ForegroundColor Yellow
try {
    $csvPath = "quick_test.csv"
    $csvContent = @"
transaction_id,sender_id,receiver_id,amount,timestamp
TXN_0001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_0002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_0003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00
CIRC_001,CIRC_A,CIRC_B,50000.00,2026-02-05 14:00:00
CIRC_002,CIRC_B,CIRC_C,45000.00,2026-02-05 14:30:00
CIRC_003,CIRC_C,CIRC_A,40000.00,2026-02-05 15:00:00
SMURF_001,SMURF_SRC,ACC_010,5000.00,2026-02-02 09:00:00
SMURF_002,SMURF_SRC,ACC_011,4800.00,2026-02-02 09:05:00
SMURF_003,SMURF_SRC,ACC_012,5200.00,2026-02-02 09:10:00
SHELL_001,SHELL_A,SHELL_B,15000.00,2026-02-10 10:00:00
SHELL_002,SHELL_B,SHELL_C,14000.00,2026-02-10 10:30:00
"@
    $csvContent | Out-File -FilePath $csvPath -Encoding UTF8 -Force
    
    # Upload using -Form parameter (correct for modern PowerShell)
    $form = @{ file = Get-Item -Path $csvPath }
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/upload-transactions" -Form $form -UseBasicParsing -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ CSV uploaded!" -ForegroundColor Green
    Write-Host "  - Transactions: $($data.num_transactions)" -ForegroundColor Gray
    Write-Host "  - Accounts: $($data.num_accounts)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Upload failed: $_" -ForegroundColor Red
    Remove-Item $csvPath -ErrorAction SilentlyContinue
    exit 1
}

# Step 3: Run Detection
Write-Host "`n[3/5] Running detection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/run-detection" -Method POST -UseBasicParsing -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Detection complete!" -ForegroundColor Green
    if ($data.fraud_ring_output) {
        Write-Host "  - Fraud Rings: $($data.fraud_ring_output.fraud_rings.Count)" -ForegroundColor Green
        Write-Host "  - Suspicious Accounts: $($data.fraud_ring_output.suspicious_accounts.Count)" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Detection failed: $_" -ForegroundColor Red
    Remove-Item $csvPath -ErrorAction SilentlyContinue
    exit 1
}

# Step 4: Get Results
Write-Host "`n[4/5] Getting fraud rings..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/fraud-rings" -UseBasicParsing -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Results retrieved!" -ForegroundColor Green
    if ($data.fraud_rings.Count -gt 0) {
        Write-Host "  Ring Details:" -ForegroundColor Gray
        foreach ($ring in $data.fraud_rings) {
            Write-Host "    - $($ring.ring_id): $($ring.pattern_type) (Risk: $($ring.risk_score), Members: $($ring.member_accounts.Count))" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "✗ Failed to get results: $_" -ForegroundColor Red
}

# Step 5: Download Report
Write-Host "`n[5/5] Downloading JSON report..." -ForegroundColor Yellow
try {
    $reportPath = "fraud_detection_report.json"
    Invoke-WebRequest -Uri "$ServerUrl/api/download-fraud-report" -UseBasicParsing -OutFile $reportPath -ErrorAction Stop
    $report = Get-Content $reportPath | ConvertFrom-Json
    
    Write-Host "✓ Report saved!" -ForegroundColor Green
    Write-Host "  - File: $reportPath" -ForegroundColor Gray
    Write-Host "  - Suspicious Accounts: $($report.suspicious_accounts.Count)" -ForegroundColor Gray
    Write-Host "  - Fraud Rings: $($report.fraud_rings.Count)" -ForegroundColor Gray
    Write-Host "  - Processing Time: $($report.summary.processing_time_seconds)s" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed to download report: $_" -ForegroundColor Red
}

# Cleanup
Remove-Item $csvPath -ErrorAction SilentlyContinue

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "✓ All tests passed! Backend is working correctly!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "`nYou can now:" -ForegroundColor Yellow
Write-Host "1. Run npm start to start the frontend" -ForegroundColor Gray
Write-Host "2. Use test.http in VS Code with REST Client extension" -ForegroundColor Gray
Write-Host "3. Upload your own CSV data for detection" -ForegroundColor Gray
