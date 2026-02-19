from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
os.environ['PANDAS_NO_CALAMINE'] = '1'
import pandas as pd
import json
from datetime import datetime
import traceback
import time
import io
import numpy as np

from detector import MoneyMulingDetector
from scoring import SuspiciousActivityScorer
from graph_rules import TransactionGraphAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global instances
detector = MoneyMulingDetector()
scorer = SuspiciousActivityScorer()
analyzer = None
last_detection_results = None
processing_start_time = None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/upload-transactions', methods=['POST'])
def upload_transactions():
    """Upload and process transaction data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read CSV file
        df = pd.read_csv(file)

        # Validate required columns
        required_columns = ['transaction_id', 'from_account', 'to_account', 'amount', 'timestamp']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {missing_columns}',
                'required_columns': required_columns
            }), 400

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Load data into detector
        detector.load_transactions(df)

        # Update analyzer
        global analyzer
        analyzer = TransactionGraphAnalyzer(detector)

        return jsonify({
            'message': 'Transaction data loaded successfully',
            'num_transactions': len(df),
            'num_accounts': len(set(df['from_account']).union(set(df['to_account']))),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            }
        })

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/run-detection', methods=['POST'])
def run_detection():
    """Run money muling detection algorithms"""
    try:
        global last_detection_results, processing_start_time

        if detector.transactions is None:
            return jsonify({'error': 'No transaction data loaded. Please upload data first.'}), 400

        processing_start_time = time.time()

        # Run detection
        detection_results = detector.run_full_detection()
        last_detection_results = detection_results

        # Generate scoring report
        scoring_report = scorer.generate_overall_report(detection_results)

        # Generate fraud ring output
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)
        
        # Update processing time
        processing_time = time.time() - processing_start_time
        fraud_ring_output['summary']['processing_time_seconds'] = round(processing_time, 2)

        return jsonify({
            'detection_results': detection_results,
            'scoring_report': scoring_report,
            'fraud_ring_output': fraud_ring_output,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/graph-metrics', methods=['GET'])
def get_graph_metrics():
    """Get graph analysis metrics"""
    try:
        if analyzer is None:
            return jsonify({'error': 'No data loaded. Please upload transactions first.'}), 400

        metrics = analyzer.analyze_graph_metrics()

        return jsonify({
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/visualizations/network', methods=['GET'])
def get_network_visualization():
    """Get enhanced network visualization data"""
    try:
        if analyzer is None or detector.transactions is None:
            return jsonify({'error': 'No data loaded. Please upload transactions and run detection first.'}), 400

        # Get latest detection results
        if last_detection_results is None:
            detection_results = detector.run_full_detection()
        else:
            detection_results = last_detection_results

        fig = analyzer.create_enhanced_network_visualization(
            detection_results,
            scorer,
            rings=detection_results.get('rings', {})
        )

        return jsonify({
            'plotly_data': fig.to_dict(),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/visualizations/risk-distribution', methods=['GET'])
def get_risk_distribution():
    """Get risk distribution visualization"""
    try:
        if detector.transactions is None:
            return jsonify({'error': 'No data loaded. Please upload transactions first.'}), 400

        if last_detection_results is None:
            detection_results = detector.run_full_detection()
        else:
            detection_results = last_detection_results

        scoring_report = scorer.generate_overall_report(detection_results)
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)

        fig = analyzer.create_risk_distribution_chart(fraud_ring_output)

        return jsonify({
            'plotly_data': fig.to_dict(),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/fraud-rings', methods=['GET'])
def get_fraud_rings():
    """Get fraud ring summary data"""
    try:
        if detector.transactions is None or last_detection_results is None:
            return jsonify({'error': 'No detection results available.'}), 400

        detection_results = last_detection_results
        scoring_report = scorer.generate_overall_report(detection_results)
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)

        return jsonify({
            'fraud_rings': fraud_ring_output['fraud_rings'],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/download-fraud-report', methods=['GET'])
def download_fraud_report():
    """Download fraud detection report as JSON"""
    try:
        if detector.transactions is None or last_detection_results is None:
            return jsonify({'error': 'No detection results available.'}), 400

        detection_results = last_detection_results
        scoring_report = scorer.generate_overall_report(detection_results)
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)

        # Create JSON output with required format
        output = {
            'suspicious_accounts': fraud_ring_output['suspicious_accounts'],
            'fraud_rings': fraud_ring_output['fraud_rings'],
            'summary': fraud_ring_output['summary']
        }

        # Create file-like object
        json_str = json.dumps(output, indent=2, default=str)
        json_bytes = io.BytesIO(json_str.encode('utf-8'))

        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name='fraud_detection_report.json'
        )

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/sample-data', methods=['GET'])
def generate_sample_data():
    """Generate sample transaction data for testing"""
    try:
        # Generate sample data with some suspicious patterns
        np.random.seed(42)

        # Normal accounts
        normal_accounts = [f'ACC_{i:03d}' for i in range(100)]

        # Suspicious accounts for circular routing
        circular_accounts = [f'CIRC_{i:03d}' for i in range(5)]

        # Smurfing source account
        smurf_source = 'SMURF_SRC'

        # Shell network accounts
        shell_accounts = [f'SHELL_{i:03d}' for i in range(8)]

        transactions = []

        # Generate normal transactions
        for i in range(500):
            from_acc = np.random.choice(normal_accounts)
            to_acc = np.random.choice([acc for acc in normal_accounts if acc != from_acc])
            amount = np.random.exponential(1000)
            timestamp = datetime.now() - pd.Timedelta(days=np.random.randint(0, 30))

            transactions.append({
                'transaction_id': f'TXN_{i:04d}',
                'from_account': from_acc,
                'to_account': to_acc,
                'amount': round(amount, 2),
                'timestamp': timestamp.isoformat()
            })

        # Add circular routing pattern
        base_time = datetime.now() - pd.Timedelta(days=5)
        amounts = [50000, 45000, 40000, 35000, 30000]

        for i in range(5):
            from_acc = circular_accounts[i]
            to_acc = circular_accounts[(i + 1) % 5]
            timestamp = base_time + pd.Timedelta(hours=i*2)

            transactions.append({
                'transaction_id': f'CIRC_{i:04d}',
                'from_account': from_acc,
                'to_account': to_acc,
                'amount': amounts[i],
                'timestamp': timestamp.isoformat()
            })

        # Add smurfing pattern
        base_time = datetime.now() - pd.Timedelta(days=2)
        total_smurf_amount = 75000
        num_smurf_transactions = 15
        smurf_amount = total_smurf_amount / num_smurf_transactions

        for i in range(num_smurf_transactions):
            to_acc = np.random.choice(normal_accounts)
            timestamp = base_time + pd.Timedelta(minutes=i*5)

            transactions.append({
                'transaction_id': f'SMURF_{i:04d}',
                'from_account': smurf_source,
                'to_account': to_acc,
                'amount': round(smurf_amount + np.random.normal(0, smurf_amount*0.1), 2),
                'timestamp': timestamp.isoformat()
            })

        # Add shell network pattern
        base_time = datetime.now() - pd.Timedelta(days=10)
        for i in range(len(shell_accounts) - 1):
            from_acc = shell_accounts[i]
            to_acc = shell_accounts[i + 1]
            amount = np.random.uniform(10000, 50000)
            timestamp = base_time + pd.Timedelta(hours=i*6)

            transactions.append({
                'transaction_id': f'SHELL_{i:04d}',
                'from_account': from_acc,
                'to_account': to_acc,
                'amount': round(amount, 2),
                'timestamp': timestamp.isoformat()
            })

        return jsonify({
            'transactions': transactions,
            'message': 'Sample data generated with embedded suspicious patterns',
            'patterns_included': [
                'Circular fund routing (5 accounts)',
                'Smurfing pattern (1 source to 15 destinations)',
                'Layered shell network (8 accounts in chain)'
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/analyze', methods=['POST'])
def analyze_csv():
    """Complete analysis endpoint: upload CSV, run detection, return full results"""
    try:
        # Step 1: Upload and validate CSV
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read and validate CSV
        df = pd.read_csv(file)
        required_columns = ['transaction_id', 'from_account', 'to_account', 'amount', 'timestamp']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {missing_columns}',
                'required_columns': required_columns
            }), 400

        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Step 2: Load data and run detection
        detector.load_transactions(df)
        global analyzer
        analyzer = TransactionGraphAnalyzer(detector)

        # Run detection
        detection_results = detector.run_full_detection()

        # Generate scoring and fraud ring output
        scoring_report = scorer.generate_overall_report(detection_results)
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)

        # Step 3: Generate visualization data
        network_viz = analyzer.create_enhanced_network_visualization(
            detection_results, scorer, rings=detection_results.get('rings', {})
        )

        # Step 4: Return complete analysis
        return jsonify({
            'success': True,
            'data': {
                'fraud_rings': fraud_ring_output.get('fraud_rings', []),
                'suspicious_accounts': fraud_ring_output.get('suspicious_accounts', []),
                'graph_data': network_viz.to_dict() if network_viz else None,
                'summary': fraud_ring_output.get('summary', {}),
                'detection_details': detection_results
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Money Muling Detector API on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)