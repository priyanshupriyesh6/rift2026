# Quick Backend Testing Reference

## Fastest Way to Test in VS Code

### Method 1: REST Client Extension (Most Visual) ⭐
**Best for**: Interactive testing with clear response display

1. Install "REST Client" extension by Huachao Mao
2. Open `test.http` file in VS Code
3. Click "Send Request" links above each API call
4. View responses in right panel

```
✓ No command line needed
✓ See request/response side-by-side
✓ Easy to modify and retry
```

### Method 2: PowerShell Script (Automated) ⭐⭐
**Best for**: Testing all endpoints at once

```powershell
# Run from project root
./test-backend.ps1
```

Automatically tests:
- Health check
- Sample data generation
- File upload
- Detection algorithms
- All visualization endpoints
- Report download
- Prints organized results

### Method 3: VS Code Terminal (Manual)
**Best for**: Quick one-off tests

```powershell
# Test health
Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -UseBasicParsing

# Get sample data
Invoke-WebRequest -Uri 'http://localhost:5000/api/sample-data' -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json

# Run detection (requires data to be uploaded first)
Invoke-WebRequest -Uri 'http://localhost:5000/api/run-detection' -Method POST -UseBasicParsing
```

---

## Step-by-Step Testing Process

### Step 1: Start Backend (Keep Running)
```bash
cd backend
python main.py
```

Expected output:
```
Starting Money Muling Detector API...
* Running on http://127.0.0.1:5000
```

### Step 2: In VS Code (New Terminal - Ctrl+`)

**Option A: Visual Testing with test.http**
1. Open `test.http` file
2. Click blue "Send Request" link
3. Watch response appear on right
4. Try each endpoint in order

**Option B: Automated Testing**
```powershell
./test-backend.ps1
```

---

## API Endpoints to Test

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check if server is running |
| `/api/sample-data` | GET | Generate test transactions |
| `/api/upload-transactions` | POST | Upload CSV file |
| `/api/run-detection` | POST | Run detection algorithms |
| `/api/fraud-rings` | GET | Get detected fraud rings |
| `/api/graph-metrics` | GET | Get network metrics |
| `/api/visualizations/network` | GET | Get network graph data |
| `/api/visualizations/risk-distribution` | GET | Get risk chart data |
| `/api/download-fraud-report` | GET | Download JSON report |

---

## Expected Test Results

### Successful Output Shows:
```
✓ Health Check: 200 OK
✓ Sample Data: 600+ transactions with 3 pattern types
✓ Upload: CSV loaded successfully
✓ Detection: Patterns detected, rings identified
✓ Fraud Rings: List of RING_000, RING_001, etc.
✓ Visualizations: Plotly data ready
✓ Report Downloaded: fraud_detection_report.json created
```

---

## Troubleshooting

### "Connection refused" Error
**Problem**: Backend not running
**Solution**:
```bash
cd backend
python main.py
```

### 404 Not Found on Upload
**Problem**: Try uploading before running detection
**Solution**: Order matters!
1. First: Upload file → `/api/upload-transactions`
2. Then: Run detection → `/api/run-detection`
3. Then: Get results → `/api/fraud-rings`

### Module Import Errors
**Problem**: Missing dependencies
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### "No module named 'flask'"
**Problem**: Dependencies not installed
**Solution**:
```bash
pip install flask flask-cors pandas networkx plotly numpy
```

---

## File Locations

| File | Purpose |
|------|---------|
| `test.http` | REST client requests (use with REST Client extension) |
| `test-backend.ps1` | Automated testing script |
| `BACKEND_TESTING.md` | Detailed testing guide |
| `backend/main.py` | Flask server |
| `backend/detector.py` | Detection algorithms |
| `backend/scoring.py` | Risk scoring |
| `backend/graph_rules.py` | Visualizations |

---

## Testing Workflow (Recommended)

```
1. Open VS Code Terminal
   ↓
2. cd backend && python main.py
   ↓
3. Open test.http file
   ↓
4. Click "Send Request" on /api/health
   ↓
5. Click "Send Request" on /api/sample-data
   ↓
6. Click "Send Request" on /api/upload-transactions
   ↓
7. Click "Send Request" on /api/run-detection
   ↓
8. View fraud_ring_output in response
   ↓
9. Click "Send Request" on /api/download-fraud-report
   ↓
10. Check fraud_detection_report.json file
```

---

## What Each Test Validates

| Test | Validates |
|------|-----------|
| Health | Server is running |
| Sample Data | Detection works with generated data |
| Upload | CSV parsing and data loading |
| Detection | All 3 algorithms execute |
| Fraud Rings | Ring identification and scoring |
| Metrics | Graph analysis works |
| Network Viz | Plotly graph generation |
| Risk Dist | Chart generation |
| Report Download | JSON export functionality |

---

## Common Test Scenarios

### Scenario 1: Quick Smoke Test (2 min)
1. Run health check
2. Get sample data
3. Done - confirms backend works

### Scenario 2: Full Function Test (5 min)
1. Upload CSV
2. Run detection
3. Get fraud rings
4. Download report
5. Inspect report

### Scenario 3: Complete Test Suite (10 min)
```powershell
./test-backend.ps1
```
Tests everything automatically with organized output

---

## Tips

✓ Test in this order: health → upload → run-detection → get-results  
✓ Keep backend running in one terminal while testing  
✓ Use test.http for visual feedback  
✓ Use script for automated regression testing  
✓ Check fraud_detection_report.json for full output  
✓ Look at backend console for error details  

---

**Ready to test?** Pick your method above and start! 🚀
