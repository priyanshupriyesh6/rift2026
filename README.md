# Money Muling Detection Engine

## Problem Statement

Money muling is a sophisticated financial crime where criminals recruit individuals to transfer illicit funds through legitimate bank accounts. This creates complex transaction networks that are difficult to detect using traditional rule-based systems. The Money Muling Detection Engine addresses this challenge by applying advanced graph analysis algorithms to identify suspicious patterns in transaction data.

## Solution Overview

This web-based application provides an end-to-end solution for detecting money muling patterns through:

- **Graph-based Analysis**: Transaction networks are modeled as directed graphs
- **Pattern Recognition**: Three specialized algorithms detect different muling techniques
- **Interactive Visualization**: Real-time network visualization with fraud highlighting
- **Risk Assessment**: Automated scoring and reporting of suspicious activities

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
- `from_account`: Source account ID
- `to_account`: Destination account ID
- `amount`: Transaction amount (numeric)
- `timestamp`: ISO format datetime string

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

*This project demonstrates advanced graph analysis techniques for financial crime detection. For production deployment, additional security measures, performance optimization, and regulatory compliance would be required.*
