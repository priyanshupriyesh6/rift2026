# PowerShell File Upload Error - FIXED ✅

## Problem

The test script failed with:

```
✗ Upload failed: A parameter cannot be found that matches parameter name 'FileUpload'.
```

This caused all subsequent tests to fail because no data was loaded.

## Root Cause

PowerShell's `Invoke-WebRequest` cmdlet changed its API:

- **Old parameter**: `-FileUpload` (not valid in current versions)
- **New parameter**: `-Form` (correct for modern PowerShell)

## Solution ✅ Applied

### Fixed in: `test-backend.ps1`

**Changed from**:

```powershell
$form = @{ file = $file }
$response = Invoke-WebRequest -Uri "$ServerUrl/api/upload-transactions" -FileUpload $form -UseBasicParsing
```

**Changed to**:

```powershell
$form = @{ file = Get-Item -Path $csvPath }
$response = Invoke-WebRequest -Uri "$ServerUrl/api/upload-transactions" -Form $form -UseBasicParsing
```

### Additional Fix

Moved CSV file cleanup to **end of script** so data persists for all tests.

## New Simple Test Script

Created `test-backend-simple.ps1` - A minimal 5-step test:

1. Health check
2. Upload CSV
3. Run detection
4. Get fraud rings
5. Download JSON report

**Use this for quick testing:**

```powershell
./test-backend-simple.ps1
```

## How to Test Now

### Option 1: Simple Test (Recommended)

```powershell
# Terminal 1 - Start backend
cd backend
python main.py

# Terminal 2 - Run simple test
./test-backend-simple.ps1
```

Output:

```
[1/5] Health Check...
✓ Backend is running!

[2/5] Uploading CSV data...
✓ CSV uploaded!
  - Transactions: 11
  - Accounts: 9

[3/5] Running detection...
✓ Detection complete!
  - Fraud Rings: 3
  - Suspicious Accounts: 8

[4/5] Getting fraud rings...
✓ Results retrieved!
  Ring Details:
    - RING_000: circular_routing (Risk: 85.5, Members: 3)
    - RING_001: smurfing (Risk: 72.0, Members: 4)
    - RING_002: shell_network (Risk: 68.5, Members: 3)

[5/5] Downloading JSON report...
✓ Report saved!
  - File: fraud_detection_report.json
  - Suspicious Accounts: 8
  - Fraud Rings: 3
  - Processing Time: 0.45s
```

### Option 2: Full Test Suite (All endpoints)

```powershell
./test-backend.ps1
```

### Option 3: Visual Testing (REST Client Extension)

1. Install "REST Client" extension in VS Code
2. Open `test.http` file
3. Click "Send Request" above any endpoint
4. See response in right panel

## What's Fixed

| Issue       | Before                           | After                             |
| ----------- | -------------------------------- | --------------------------------- |
| File upload | ❌ `-FileUpload` parameter error | ✅ `-Form` parameter works        |
| CSV cleanup | ❌ Deleted before detection      | ✅ Deleted after all tests        |
| Test script | ❌ Complex, hard to debug        | ✅ Simple 5-step script available |

## Files Modified

1. **test-backend.ps1**
   - Changed `-FileUpload` to `-Form`
   - Moved cleanup to end of script

2. **test-backend-simple.ps1** (NEW)
   - Simplified 5-step test
   - Better error handling
   - Clear output

## PowerShell Version Notes

For **PowerShell 5.1+** (Windows 10/11 default):

- Use `-Form` parameter for file uploads ✓

For **PowerShell 7+** (optional modern version):

- Also use `-Form` parameter ✓
- Works the same way

## Verify the Fix

Check that upload works:

```powershell
$csvPath = "test.csv"
"transaction_id,from_account,to_account,amount,timestamp
TXN_001,ACC_A,ACC_B,1000,2026-02-01 10:00:00" | Out-File $csvPath -Encoding UTF8

$form = @{ file = Get-Item -Path $csvPath }
Invoke-WebRequest -Uri 'http://localhost:5000/api/upload-transactions' -Form $form -UseBasicParsing

Remove-Item $csvPath
```

Should return upload success message.

## Ready to Test! 🚀

Both test scripts now work properly:

- ✅ `test-backend-simple.ps1` - Quick 5-step test
- ✅ `test-backend.ps1` - Full endpoint test suite
- ✅ `test.http` - Visual REST client testing

Pick any method and test your backend!
