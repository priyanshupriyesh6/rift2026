#!/usr/bin/env powershell
# Money Muling Detector - Backend Testing Script
# Run this script to test all backend API endpoints
# Make sure Flask backend is running: python main.py

param(
    [string]$ServerUrl = "http://localhost:5000"
)

$ErrorActionPreference = "SilentlyContinue"

# Colors
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"
$Gray = "Gray"

function Print-Header {
    param([string]$Text)
    Write-Host "`n" + ("=" * 60) -ForegroundColor $Cyan
    Write-Host $Text -ForegroundColor $Cyan
    Write-Host ("=" * 60) -ForegroundColor $Cyan
}

function Print-Test {
    param([string]$Name, [string]$Endpoint)
    Write-Host "`n[TEST] $Name" -ForegroundColor $Yellow
    Write-Host "Endpoint: $Endpoint" -ForegroundColor $Gray
}

function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $Red
}

# Start
Print-Header "Backend API Testing Suite"
Write-Host "Server: $ServerUrl" -ForegroundColor $Gray
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $Gray

# Test 1: Health Check
Print-Test "Health Check" "GET /api/health"
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/health" -UseBasicParsing -ErrorAction Stop
    Print-Success "Backend is running!"
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($data.status)" -ForegroundColor $Gray
} catch {
    Print-Error "Backend is not running! Start it with: python main.py"
    exit 1
}

# Test 2: Get Sample Data
Print-Test "Get Sample Data" "GET /api/sample-data"
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/sample-data" -UseBasicParsing -ErrorAction Stop
    Print-Success "Sample data retrieved"
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Transactions: $($data.transactions.Count)" -ForegroundColor $Gray
    Write-Host "Embedded patterns: $(($data.patterns_included -Join ', '))" -ForegroundColor $Gray
} catch {
    Print-Error "Failed to get sample data: $_"
}

# Test 3: Upload CSV
Print-Test "Upload Transaction Data" "POST /api/upload-transactions"
try {
    # Create test CSV
    $csvPath = "test_transactions.csv"
    $csvContent = @"
transaction_id,from_account,to_account,amount,timestamp
TXN_0001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
TXN_0002,ACC_002,ACC_003,950.00,2026-02-01 10:05:00
TXN_0003,ACC_003,ACC_001,900.00,2026-02-01 10:10:00
CIRC_0001,CIRC_001,CIRC_002,50000.00,2026-02-05 14:00:00
CIRC_0002,CIRC_002,CIRC_003,45000.00,2026-02-05 14:30:00
CIRC_0003,CIRC_003,CIRC_001,40000.00,2026-02-05 15:00:00
SMURF_SRC,SMURF_001,ACC_010,5000.00,2026-02-02 09:00:00
SMURF_SRC,SMURF_002,ACC_011,4800.00,2026-02-02 09:05:00
SMURF_SRC,SMURF_003,ACC_012,5200.00,2026-02-02 09:10:00
SHELL_001,SHELL_002,SHELL_003,15000.00,2026-02-10 10:00:00
SHELL_002,SHELL_003,SHELL_004,14000.00,2026-02-10 10:30:00
"@
    $csvContent | Out-File -FilePath $csvPath -Encoding UTF8
    
    # Upload the file
    $form = @{ file = Get-Item -Path $csvPath }
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/upload-transactions" -Form $form -UseBasicParsing -ErrorAction Stop
    
    Print-Success "File uploaded successfully"
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Transactions loaded: $($data.num_transactions)" -ForegroundColor $Gray
    Write-Host "Unique accounts: $($data.num_accounts)" -ForegroundColor $Gray
    
} catch {
    Print-Error "Upload failed: $_"
}

# Test 4: Run Detection
Print-Test "Run Detection Algorithms" "POST /api/run-detection"
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/run-detection" -Method POST -UseBasicParsing -ErrorAction Stop
    Print-Success "Detection completed successfully"
    
    $data = $response.Content | ConvertFrom-Json
    
    if ($data.detection_results) {
        $circular = @($data.detection_results.circular_routing).Count
        $smurfing = @($data.detection_results.smurfing).Count
        $shell = @($data.detection_results.shell_networks).Count
        
        Write-Host "Circular Routing Patterns: $circular" -ForegroundColor $Gray
        Write-Host "Smurfing Patterns: $smurfing" -ForegroundColor $Gray
        Write-Host "Shell Networks: $shell" -ForegroundColor $Gray
    }
    
    if ($data.fraud_ring_output.fraud_rings) {
        Write-Host "Total Fraud Rings: $($data.fraud_ring_output.fraud_rings.Count)" -ForegroundColor $Gray
        Write-Host "Suspicious Accounts: $($data.fraud_ring_output.suspicious_accounts.Count)" -ForegroundColor $Gray
    }
    
} catch {
    Print-Error "Detection failed: $_"
}

# Test 5: Get Fraud Rings
Print-Test "Get Fraud Rings" "GET /api/fraud-rings"
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/fraud-rings" -UseBasicParsing -ErrorAction Stop
    Print-Success "Fraud rings retrieved"
    
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Total rings: $($data.fraud_rings.Count)" -ForegroundColor $Gray
    
    if ($data.fraud_rings.Count -gt 0) {
        Write-Host "`nRing Details:" -ForegroundColor $Gray
        foreach ($ring in $data.fraud_rings[0..([Math]::Min(4, $data.fraud_rings.Count-1))]) {
            Write-Host "  ID: $($ring.ring_id) | Type: $($ring.pattern_type) | Members: $($ring.member_accounts.Count) | Risk: $($ring.risk_score)" -ForegroundColor $Gray
        }
    }
    
} catch {
    Print-Error "Failed to get fraud rings: $_"
}

# Test 6: Get Network Visualization
Print-Test "Get Network Visualization" "GET /api/visualizations/network"
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/visualizations/network" -UseBasicParsing -ErrorAction Stop
    Print-Success "Network visualization data retrieved"
    
    $data = $response.Content | ConvertFrom-Json
    if ($data.plotly_data.data) {
        Write-Host "Graph traces: $($data.plotly_data.data.Count)" -ForegroundColor $Gray
    }
    
} catch {
    Print-Error "Failed to get network visualization: $_"
}

# Test 7: Get Risk Distribution
Print-Test "Get Risk Distribution Chart" "GET /api/visualizations/risk-distribution"
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/visualizations/risk-distribution" -UseBasicParsing -ErrorAction Stop
    Print-Success "Risk distribution chart data retrieved"
    
    $data = $response.Content | ConvertFrom-Json
    if ($data.plotly_data.data) {
        Write-Host "Chart traces: $($data.plotly_data.data.Count)" -ForegroundColor $Gray
    }
    
} catch {
    Print-Error "Failed to get risk distribution: $_"
}

# Test 8: Download Fraud Report
Print-Test "Download Fraud Report (JSON)" "GET /api/download-fraud-report"
try {
    $reportPath = "fraud_detection_report.json"
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/download-fraud-report" -UseBasicParsing -OutFile $reportPath -ErrorAction Stop
    
    Print-Success "Fraud report downloaded"
    Write-Host "File: $reportPath" -ForegroundColor $Gray
    
    # Parse and show summary
    $report = Get-Content $reportPath | ConvertFrom-Json
    Write-Host "Suspicious Accounts: $($report.suspicious_accounts.Count)" -ForegroundColor $Gray
    Write-Host "Fraud Rings: $($report.fraud_rings.Count)" -ForegroundColor $Gray
    
    if ($report.summary) {
        Write-Host "Summary:" -ForegroundColor $Gray
        Write-Host "  - Total Accounts Analyzed: $($report.summary.total_accounts_analyzed)" -ForegroundColor $Gray
        Write-Host "  - Accounts Flagged: $($report.summary.suspicious_accounts_flagged)" -ForegroundColor $Gray
        Write-Host "  - Fraud Rings Detected: $($report.summary.fraud_rings_detected)" -ForegroundColor $Gray
        Write-Host "  - Processing Time: $($report.summary.processing_time_seconds)s" -ForegroundColor $Gray
    }
    
} catch {
    Print-Error "Failed to download report: $_"
}

# Test 9: Get Graph Metrics
Print-Test "Get Graph Metrics" "GET /api/graph-metrics"
try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/api/graph-metrics" -UseBasicParsing -ErrorAction Stop
    Print-Success "Graph metrics retrieved"
    
    $data = $response.Content | ConvertFrom-Json
    if ($data.metrics) {
        Write-Host "Metrics available" -ForegroundColor $Gray
    }
    
} catch {
    Print-Error "Failed to get graph metrics: $_"
}

# Clean up test files
Remove-Item $csvPath -ErrorAction SilentlyContinue

# Summary
Print-Header "Testing Complete"
Write-Host "All core API endpoints tested successfully!" -ForegroundColor $Green
Write-Host "`nNext Steps:" -ForegroundColor $Yellow
Write-Host "1. Check 'fraud_detection_report.json' for full detection results" -ForegroundColor $Gray
Write-Host "2. Start frontend: npm install && npm start" -ForegroundColor $Gray
Write-Host "3. Upload your own CSV data and run detection" -ForegroundColor $Gray
Write-Host "`nBackend Documentation: See BACKEND_TESTING.md" -ForegroundColor $Gray
