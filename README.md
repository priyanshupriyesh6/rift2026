# Money Muling Detection Engine

# Money Muling Detection Engine

## Problem Statement

Money muling is a sophisticated financial crime where criminals recruit individuals to transfer illicit funds through legitimate bank accounts. This creates complex transaction networks that are difficult to detect using traditional rule-based systems. The Money Muling Detection Engine addresses this challenge by applying advanced graph analysis algorithms to identify suspicious patterns in transaction data.

## Solution Overview

This web-based application provides an end-to-end solution for detecting money muling patterns through:

- **Graph-based Analysis**: Transaction networks are modeled as directed graphs
- **Pattern Recognition**: Three specialized algorithms detect different muling techniques
- **Interactive Visualization**: Real-time network visualization with fraud highlighting
- **Risk Assessment**: Automated scoring and reporting of suspicious activities

## Deployment on Render

### Backend Deployment

1. Create a new **Web Service** on Render
2. Connect your GitHub repository
3. Set the **Root Directory** to `backend`
4. Set **Build Command** to `pip install -r requirements.txt`
5. Set **Start Command** to `gunicorn --bind 0.0.0.0:$PORT wsgi:app` (or leave blank to use the Procfile)
6. **Important**: The `backend/runtime.txt` file specifies Python 3.12.0 to ensure compatibility with pandas (Python 3.14 has compatibility issues)
7. Deploy the service

### Frontend Deployment

1. Create a new **Static Site** on Render
2. Connect your GitHub repository
3. Set the **Root Directory** to `frontend/client`
4. Set **Build Command** to `npm run build`
5. Set **Publish Directory** to `dist`
6. Add environment variable: `VITE_API_URL` = `https://your-backend-service.onrender.com`
7. Deploy the static site

### Connecting Frontend to Backend

- After deploying both services, update the frontend's `VITE_API_URL` environment variable with your backend's Render URL
- Redeploy the frontend to apply the changes

## Architecture

### Frontend (React)

- **Framework**: React 18.2 with functional components
- **Visualization**: Vis.js network graphs with deterministic layouts
- **Styling**: Plain CSS with responsive design
- **State Management**: React hooks for simple, predictable state

### Backend (Python/Flask)

- **Framework**: Flask 2.3.3 with CORS support
- **Graph Analysis**: NetworkX for transaction network modeling
- **Data Processing**: Pandas for efficient CSV handling
- **Detection Engine**: Custom algorithms for pattern recognition

### Detection Pipeline

1. **Data Ingestion**: CSV upload with validation
2. **Graph Construction**: Transaction-to-account relationships
3. **Pattern Detection**: Parallel execution of detection algorithms
4. **Risk Scoring**: Multi-factor assessment of suspicious activities
5. **Visualization**: Interactive network rendering with fraud highlighting

## Detection Rules

### 1. Circular Fund Routing

- **Pattern**: Closed transaction loops (A→B→C→A)
- **Logic**: NetworkX cycle detection with size constraints
- **Indicators**: Transaction frequency, amount consistency, time windows

### 2. Smurfing (Structuring)

- **Pattern**: Large amounts split into smaller transactions
- **Logic**: Hourly aggregation with statistical analysis
- **Indicators**: Amount distribution uniformity, threshold avoidance

### 3. Layered Shell Networks

- **Pattern**: Multi-level account hierarchies for fund movement
- **Logic**: Centrality analysis and connected component detection
- **Indicators**: Betweenness centrality, transaction volume anomalies

## Suspicion Scoring

Each detected pattern receives a risk score (0-100) based on:

- **Pattern Strength**: How well the transaction matches the fraud signature
- **Network Position**: Account centrality and connectivity metrics
- **Behavioral Anomalies**: Deviation from normal transaction patterns
- **Temporal Factors**: Timing and frequency of suspicious activities

## Setup & Run Instructions

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ with pip
- Git

### Backend Setup

```bash
cd backend
pip install flask flask-cors pandas networkx matplotlib plotly numpy scikit-learn
python main.py
```

### Frontend Setup

```bash
cd fronted
npm install
npm start
```

### Usage

1. Open http://localhost:3000 in your browser
2. Upload a CSV file with transaction data
3. Click "Analyze Transactions"
4. View results in the interactive dashboard

### CSV Format Requirements

Required columns:

- `transaction_id`: Unique transaction identifier
- `sender_id`: Source account ID
- `receiver_id`: Destination account ID
- `amount`: Transaction amount (numeric)
- `timestamp`: Datetime in format YYYY-MM-DD HH:MM:SS (strict)

## Known Limitations

### Technical Constraints

- **Memory Usage**: Large datasets (>100K transactions) may require optimization
- **Real-time Processing**: Current implementation processes data in batches
- **False Positives**: Some legitimate business patterns may trigger alerts

### Algorithm Limitations

- **Historical Context**: Limited analysis of long-term account behavior
- **External Data**: No integration with external risk databases
- **Currency Effects**: Multi-currency transactions not fully normalized

### Performance Considerations

- **Graph Layout**: Deterministic positioning may not scale to 10K+ nodes
- **Browser Limits**: Large network visualizations may impact browser performance
- **API Timeouts**: Complex analyses may exceed default timeout limits

## Team

- **Lead Developer**: Academic Research Team
- **Algorithm Design**: Graph Theory Specialists
- **Frontend Development**: React Engineers
- **Backend Development**: Python/Flask Developers

---

# _This project demonstrates advanced graph analysis techniques for financial crime detection. For production deployment, additional security measures, performance optimization, and regulatory compliance would be required._

# Financial Forensics Engine

**Live Demo**: [Start App](#) (Instructions to run locally below)

## Project Overview

A web-based Financial Forensics Engine designed to detect money muling networks and fraudulent transaction patterns. The system processes transaction data (CSV) and exposes complex money laundering rings through graph analysis and visualization.

## Key Features

- **Interactive Graph Visualization**: Visualizes account connections and suspicious flows.
- **Fraud Ring Detection**:
  - **Cycles**: Detects circular money flow (A -> B -> C -> A).
  - **Smurfing**: Identifies fan-in (aggregation) and fan-out (dispersion) patterns.
  - **Layered Shells**: Flags chains of low-volume intermediate accounts.
- **Risk Scoring**: Assigns suspicion scores (0-100) based on pattern participation.
- **Privacy-First**: All processing happens client-side in the browser.

## Tech Stack

- **Frontend**: React (Vite) + TypeScript
- **Styling**: TailwindCSS + Framer Motion (Glassmorphism UI)
- **Visualization**: `react-force-graph-2d`
- **Logic**: Custom Graph Algorithms (DFS, Clustering) in pure TypeScript
- **State Management**: Zustand

## System Architecture

The application follows a client-side architecture for maximum performance and security:

1. **Data Ingestion**: `PapaParse` reads CSV files into memory.

---

© 2026 BugbyteY. This project is provided for educational use only and is not intended for professional or production use. 2. **Graph Construction**: `GraphBuilder` converts flat transactions into an in-memory graph (Nodes & Links). 3. **Pattern Detection**: `PatternDetector` runs algorithms:

- _Cycle Detection_: Depth-First Search (DFS) with depth limit 5. `O(V * D)`
- _Smurfing_: Degree centrality analysis. `O(V)`
- _Shell Analysis_: Connected component analysis on low-volume nodes.

4. **Scoring**: `RiskScorer` aggregates findings into account-level risk scores.

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd money/client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run development server:
   ```bash
   npm run dev
   ```
4. Build for production:
   ```bash
   npm run build
   ```

## Usage Instructions

1. Open the application in your browser.
2. Drag & drop a CSV file containing transaction data.
   - Required columns: `transaction_id`, `sender_id`, `receiver_id`, `amount`, `timestamp`.
3. Explore the dashboard:
   - **Graph View**: Scroll to zoom, drag to pan, click nodes for details.
   - **Risk List**: Click high-risk accounts to highlight them in the graph.
   - **Export**: Click "Export JSON" to download the forensic report.

## Suspicion Score Methodology

Scores are calculated based on pattern participation:

- **Cycle Participation**: +90 points (High confidence of muling)
- **Smurfing (Fan-in/Fan-out)**: +80 points
- **Shell Chain**: +85 points
- **Base Score**: 0

Scores are capped at 100. Accounts involved in multiple patterns allow analysts to prioritize investigations.

## Known Limitations

- **Browser Memory**: Extremely large datasets (>100k transactions) may cause UI lag as processing is client-side.
- **Cycle Depth**: Limited to length 5 for performance reasons.

## Team

- **Developer**: Antigravity (AI Agent)
  > > > > > > > 41e90b8b6c6cd5739e204028ea807095e564fe40
