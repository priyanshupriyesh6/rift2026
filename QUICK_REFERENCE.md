# Quick Reference - Fraud Detection System

## How to Run the System

### Option 1: Direct Test (Recommended for Verification)
```bash
cd c:\Users\priya\Desktop\rift2026
python test_comprehensive.py
```
This runs all fraud detection tests in-process with full verification.

### Option 2: HTTPServer + Client
```bash
# Terminal 1: Start backend
cd backend && python main.py

# Terminal 2: Make test requests
cd c:\Users\priya\Desktop\rift2026 && python test_simple.py
```

## API Endpoints

### Upload Transactions
**POST** `/api/upload-transactions`
- Input: CSV file with columns: `transaction_id`, `sender_id`, `receiver_id`, `amount`, `timestamp`
- Returns: `{success: true, data: {num_transactions, num_accounts, date_range}}`

### Run Detection
**POST** `/api/run-detection`
- Analyzes uploaded transaction network for fraud patterns
- Returns: `{success: true, data: {detection_results, fraud_ring_output, scoring_report}}`

### Get Fraud Rings
**GET** `/api/fraud-rings`  
- Retrieves identified fraud rings
- Returns: `{success: true, data: {fraud_rings, timestamp}}`

## Input Format

### CSV Columns Required
| Column | Type | Format | Example |
|--------|------|--------|---------|
| transaction_id | string | Any | "TX_001" |
| sender_id | string | Account ID | "ACCOUNT_A" |
| receiver_id | string | Account ID | "ACCOUNT_B" |
| amount | float | Decimal | 10000.50 |
| timestamp | string | YYYY-MM-DD HH:MM:SS | "2026-02-15 10:00:00" |

### Example CSV
```csv
transaction_id,sender_id,receiver_id,amount,timestamp
TX001,ACC_A,ACC_B,10000.00,2026-02-15 10:00:00
TX002,ACC_B,ACC_C,9500.00,2026-02-15 10:05:00
TX003,ACC_C,ACC_A,9000.00,2026-02-15 10:10:00
```

## Output Format

### Fraud Ring Response
```json
{
  "success": true,
  "data": {
    "fraud_rings": [
      {
        "ring_id": "RING_000",
        "pattern_type": "circular_routing",
        "member_accounts": ["ACC_A", "ACC_B", "ACC_C"],
        "risk_score": 50.2
      }
    ],
    "suspicious_accounts": [
      {
        "account_id": "ACC_A",
        "suspicion_score": 50.19,
        "detected_patterns": ["circular_routing"],
        "ring_id": "RING_000"
      }
    ]
  }
}
```

## Detection Patterns

### Circular Routing
- Detects money flowing in cycles: A → B → C → A
- Indicates potential money laundering or fraudulent fund movement
- Risk factors: Amount, Time span between transactions, Cycle length

### Smurfing (Structuring)
- Detects splitting of large amounts across multiple recipients
- Indicates potential structuring to avoid threshold reporting
- Risk factors: Number of recipients, Amount consistency, Time clustering

### Shell Networks
- Detects pass-through accounts with high in/out ratios
- Indicates potential shell companies or money mules
- Risk factors: Activity concentration, Network structure, Transaction consistency

## Key Files

- `backend/main.py` - Flask API server with endpoints
- `backend/detector.py` - Fraud detection algorithms
- `backend/scoring.py` - Risk scoring engine
- `backend/graph_rules.py` - Network analysis utilities
- `test_comprehensive.py` - Full test suite with assertions

## Testing

All critical functionality is tested and verified:
- ✅ Data upload with CSV parsing
- ✅ Transaction network graph construction
- ✅ Circular routing detection
- ✅ Pattern scoring and risk calculation
- ✅ API response format and JSON serialization
- ✅ Suspicious account flagging

## Troubleshooting

### Issue: Backend reports 404 or connection refused
- Ensure backend is running: `python backend/main.py`
- Check port 5000 is available

### Issue: CSV upload fails with column error
- Verify CSV has exact columns: `transaction_id`, `sender_id`, `receiver_id`, `amount`,  `timestamp`
- Ensure timestamp format is: `YYYY-MM-DD HH:MM:SS`

### Issue: No fraud rings detected despite suspicious patterns
- Verify transaction data actually forms cycles/patterns
- Check detection thresholds in scoring.py
- Run test_comprehensive.py to validate with known patterns

## Recent Fixes (Committed)
1. API response wrapping with {success, data, error} format
2. JSON serialization fix for Timedelta objects
3. Circular routing edge data handling simplification
4. Debug logging for diagnostics
