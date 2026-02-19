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
2. **Graph Construction**: `GraphBuilder` converts flat transactions into an in-memory graph (Nodes & Links).
3. **Pattern Detection**: `PatternDetector` runs algorithms:
   - *Cycle Detection*: Depth-First Search (DFS) with depth limit 5. `O(V * D)`
   - *Smurfing*: Degree centrality analysis. `O(V)`
   - *Shell Analysis*: Connected component analysis on low-volume nodes.
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
