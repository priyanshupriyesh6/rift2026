# Money Muling Detector - Setup Guide

## Project Structure

```
rift2026/
├── backend/              # Python Flask API
│   ├── detector.py      # Core detection algorithms
│   ├── scoring.py       # Risk scoring and fraud ring output
│   ├── graph_rules.py   # Network visualization
│   ├── main.py          # Flask API server
│   └── requirements.txt # Python dependencies
├── fronted/             # React frontend (note: folder named "fronted")
│   ├── src/
│   │   ├── app.jsx      # Main React component
│   │   ├── App.css      # Styling
│   │   └── index.js     # Entry point
│   └── public/
│       ├── index.html   # HTML template
│       └── manifest.json
└── package.json         # Frontend dependencies
```

## Prerequisites

- Python 3.13+
- Node.js 16+ and npm
- Git

## Backend Setup

### 1. Install Python Dependencies

```bash
cd rift2026/backend
pip install -r requirements.txt
```

### 2. Start Flask Server

```bash
python main.py
```

The API will be available at `http://localhost:5000`

#### API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload-transactions` - Upload CSV file with transaction data
- `POST /api/run-detection` - Run detection algorithms and return fraud rings
- `GET /api/fraud-rings` - Get detected fraud rings
- `GET /api/download-fraud-report` - Download JSON report
- `GET /api/visualizations/network` - Get network visualization data
- `GET /api/visualizations/risk-distribution` - Get risk distribution chart
- `GET /api/sample-data` - Generate sample data for testing

#### CSV Format (Required Columns)

```
transaction_id,sender_id,receiver_id,amount,timestamp
TXN_0001,ACC_001,ACC_002,1000.00,2026-02-01 10:00:00
```

## Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm start
```

The frontend will open at `http://localhost:3000`

The backend proxy is configured to `http://localhost:5000`, so API calls work without CORS issues.

## Features

### Detection Algorithms

1. **Circular Fund Routing** - Detects money flowing in circles between accounts
2. **Smurfing Patterns** - Identifies when large amounts are split into smaller transfers
3. **Shell Network Detection** - Finds shell company networks with high centrality

### Output Features

1. **Interactive Network Visualization** - See fraud ring nodes highlighted with distinct colors
2. **Fraud Ring Summary Table** - View Ring ID, Pattern Type, Member Count, Risk Score
3. **Suspicious Accounts Table** - See top accounts flagged with scores and patterns
4. **Downloadable JSON Report** - Export results as structured JSON file

## Data Flow

1. User uploads CSV file with transaction data
2. Backend analyzes transactions and detects fraud patterns
3. System assigns unique Ring IDs (RING_000, RING_001, etc.) to fraud rings
4. Results returned as:
   - `fraud_ring_output`: Complete JSON structure with suspicious accounts, fraud rings, and summary
   - `detection_results`: Raw detection patterns with ring assignments
   - Visualization data: Network graph with colored ring members

## Troubleshooting

### Backend Won't Start

- Ensure Python 3.13+ is in PATH: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`
- Check port 5000 is available: `netstat -ano | findstr :5000`

### Frontend Won't Connect to Backend

- Ensure backend is running on `http://localhost:5000`
- Check proxy setting in `package.json`: `"proxy": "http://localhost:5000"`
- Browser console may show CORS errors if backend API is on different host

### Files Not Found or Import Errors

- Run from correct directory: `cd backend` before `python main.py`
- Ensure all `.py` files are in same `backend/` directory
- For frontend: `npm install` must complete successfully

## Testing

### Quick Test with Sample Data

1. Start backend: `python main.py` (from backend folder)
2. Start frontend: `npm start` (from root)
3. Click "Use Sample Data" button
4. Click "Run Detection & View Visualizations"
5. View fraud rings, suspicious accounts, and network graph
6. Click "Download JSON Report" to export results
