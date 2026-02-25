from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
os.environ['PANDAS_NO_CALAMINE'] = '1'
import pandas as pd
import json
from datetime import datetime, timedelta
import traceback
import time
import io
import numpy as np

from detector import MoneyMulingDetector
from scoring import SuspiciousActivityScorer
from graph_rules import TransactionGraphAnalyzer

print("\n" + "="*60)
# Set up logging to file
import logging
logging.basicConfig(
    filename='backend.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'  # Overwrite log file each run
)
def log(msg):
    """Log message to both file and stdout"""
    print(msg)
    logging.info(msg)

log(f"MODULE MAIN.PY LOADED - timestamp: {datetime.now().isoformat()}")
log("="*60)

app = Flask(__name__)
CORS(app, origins=["https://financail-forensic-engine.onrender.com", "http://localhost:5173", "http://localhost:3000"])

# Configure Flask for better performance with large requests
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['TIMEOUT'] = 600  # 10 minutes timeout

# Helper function to wrap responses in standard ApiResponse format
def make_serializable(obj):
    """Convert non-JSON-serializable objects to strings or primitives"""
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # datetime and like objects
        return obj.isoformat()
    elif isinstance(obj, timedelta):  # pandas/python Timedelta
        return str(obj)  # Convert to string like "0 days 00:10:00"
    elif isinstance(obj, (np.integer, np.floating)):  # numpy types
        return obj.item()  # Convert to native Python type
    elif pd.isna(obj):  # NaN values
        return None
    else:
        return obj

def api_response(data=None, error=None, status_code=200):
    """Wrap response in standard {success, data, error} format"""
    print(f"\n[API_RESPONSE] Called with error={error}, status_code={status_code}")
    
    # Make data JSON serializable
    if data is not None:
        data = make_serializable(data)
    
    if error:
        response = jsonify({'success': False, 'error': error}), status_code
    else:
        response = jsonify({'success': True, 'data': data}), status_code
    print(f"[API_RESPONSE] Returning: {response[0].get_json()}")
    return response

# Global instances
detector = MoneyMulingDetector()
scorer = SuspiciousActivityScorer()
analyzer = None
last_detection_results = None
processing_start_time = None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with system resource info"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system': {
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_available_gb': round(disk.free / (1024**3), 2)
            },
            'detector': {
                'loaded': detector.transactions is not None,
                'transactions': len(detector.transactions) if detector.transactions is not None else 0,
                'accounts': detector.graph.number_of_nodes() if detector.graph else 0
            }
        }
        
        # Warn if system resources are low
        if memory.percent > 90 or disk.percent > 90:
            health_data['status'] = 'warning'
            health_data['warnings'] = []
            if memory.percent > 90:
                health_data['warnings'].append('High memory usage')
            if disk.percent > 90:
                health_data['warnings'].append('Low disk space')
        
        return jsonify(health_data)
        
    except ImportError:
        # Fallback if psutil not available
        return jsonify({
            'status': 'healthy', 
            'timestamp': datetime.now().isoformat(),
            'system': 'monitoring not available'
        })

@app.route('/api/upload-transactions', methods=['POST'])
def upload_transactions():
    """Upload and process transaction data"""
    try:
        if 'file' not in request.files:
            return api_response(error='No file provided', status_code=400)

        file = request.files['file']

        if file.filename == '':
            return api_response(error='No file selected', status_code=400)

        # Read CSV file in chunks to handle large files
        chunks = []
        chunk_size = 10000  # Process in chunks of 10k rows
        
        # Define expected column formats
        expected_new = ['transaction_id', 'sender_id', 'receiver_id', 'amount', 'timestamp']
        expected_old = ['transaction_id', 'from_account', 'to_account', 'amount', 'timestamp']
        
        try:
            # First, try to read just the header to validate columns
            header_df = pd.read_csv(file, nrows=0)
            file.seek(0)  # Reset file pointer
            
            if all(col in header_df.columns for col in expected_new):
                print("[DEBUG] Found NEW headers - mapping to internal format")
                column_mapping = {'sender_id': 'from_account', 'receiver_id': 'to_account'}
            elif all(col in header_df.columns for col in expected_old):
                print("[DEBUG] Found OLD headers - already in internal format")
                column_mapping = {}
            else:
                missing = [col for col in expected_new if col not in header_df.columns]
                return api_response(
                    error=f'Missing required columns: {missing}. Required: {expected_new}',
                    status_code=400
                )
            
            # Read in chunks
            for chunk in pd.read_csv(file, chunksize=chunk_size):
                if column_mapping:
                    chunk = chunk.rename(columns=column_mapping)
                
                # Validate timestamp format for this chunk
                chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                if chunk['timestamp'].isna().any():
                    return api_response(
                        error='Invalid timestamp format in data. Expected: YYYY-MM-DD HH:MM:SS',
                        status_code=400
                    )
                
                chunks.append(chunk)
                print(f"[UPLOAD] Processed chunk with {len(chunk)} rows")
            
            # Concatenate all chunks
            df = pd.concat(chunks, ignore_index=True)
            print(f"[UPLOAD] Total rows loaded: {len(df)}")
            
        except pd.errors.EmptyDataError:
            return api_response(error='CSV file is empty', status_code=400)
        except Exception as e:
            return api_response(error=f'Error reading CSV: {str(e)}', status_code=400)

        # Load data into detector (detector expects columns 'from_account' and 'to_account')
        detector.load_transactions(df)
        
        # Debug logging
        print(f"[DEBUG] Detector loaded transactions: {detector.transactions is not None}")
        print(f"[DEBUG] Detector rows: {len(detector.transactions) if detector.transactions is not None else 0}")
        print(f"[DEBUG] Detector graph nodes: {detector.graph.number_of_nodes() if detector.graph else 0}")
        print(f"[DEBUG] Detector graph edges: {detector.graph.number_of_edges() if detector.graph else 0}")

        # Update analyzer
        global analyzer
        analyzer = TransactionGraphAnalyzer(detector)

        response_data = {
            'message': 'Transaction data loaded successfully',
            'num_transactions': len(df),
            'num_accounts': len(set(df['from_account']).union(set(df['to_account']))),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            }
        }
        print(f"[UPLOAD] Loaded {len(df)} transactions, {response_data['num_accounts']} accounts")
        import sys
        sys.stdout.flush()
        return api_response(data=response_data, status_code=200)

    except Exception as e:
        return api_response(error=str(e), status_code=500)

@app.route('/api/run-detection', methods=['POST'])
def run_detection():
    """Run money muling detection algorithms with timeout"""
    try:
        global last_detection_results, processing_start_time

        if detector.transactions is None:
            return api_response(error='No transaction data loaded. Please upload data first.', status_code=400)

        processing_start_time = time.time()
        
        # Check data size and warn for large datasets
        num_transactions = len(detector.transactions)
        num_accounts = detector.graph.number_of_nodes() if detector.graph else 0
        
        print(f"[DETECTION] Starting detection on {num_transactions} transactions, {num_accounts} accounts")
        
        if num_transactions > 100000:
            print("[DETECTION] Large dataset detected - using optimized processing")
        
        # Run detection (algorithms have built-in limits to prevent infinite processing)
        detection_results = detector.run_full_detection()
        last_detection_results = detection_results
        
        # Debug logging
        print(f"[DEBUG] Detection results keys: {detection_results.keys()}")
        print(f"[DEBUG] Circular routing patterns: {len(detection_results.get('circular_routing', []))}")
        print(f"[DEBUG] Smurfing patterns: {len(detection_results.get('smurfing', []))}")
        print(f"[DEBUG] Shell networks: {len(detection_results.get('shell_networks', []))}")

        # Generate scoring report
        scoring_report = scorer.generate_overall_report(detection_results)

        # Generate fraud ring output
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)
        
        print(f"[DETECTION] Found {len(fraud_ring_output.get('fraud_rings', []))} fraud rings")
        print(f"[DETECTION] Found {len(fraud_ring_output.get('suspicious_accounts', []))} suspicious accounts")
        
        # Update processing time
        processing_time = time.time() - processing_start_time
        fraud_ring_output['summary']['processing_time_seconds'] = round(processing_time, 2)
        
        print(f"[DETECTION] Processing completed in {processing_time:.2f} seconds")
        import sys
        sys.stdout.flush()

        return api_response(data={
            'detection_results': detection_results,
            'scoring_report': scoring_report,
            'fraud_ring_output': fraud_ring_output,
            'timestamp': datetime.now().isoformat(),
            'processing_stats': {
                'transactions_processed': num_transactions,
                'accounts_analyzed': num_accounts,
                'processing_time_seconds': round(processing_time, 2)
            }
        })

    except Exception as e:
        processing_time = time.time() - processing_start_time if 'processing_start_time' in globals() else 0
        print(f"[DETECTION] Error after {processing_time:.2f}s: {str(e)}")
        return api_response(error=f'Processing failed: {str(e)}', status_code=500)

    except Exception as e:
        return api_response(error=str(e), status_code=500)

@app.route('/api/graph-metrics', methods=['GET'])
def get_graph_metrics():
    """Get graph analysis metrics"""
    try:
        if analyzer is None:
            return api_response(error='No data loaded. Please upload transactions first.', status_code=400)

        metrics = analyzer.analyze_graph_metrics()

        return api_response(data={
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return api_response(error=str(e), status_code=500)

@app.route('/api/visualizations/network', methods=['GET'])
def get_network_visualization():
    """Get enhanced network visualization data"""
    try:
        if analyzer is None or detector.transactions is None:
            return api_response(error='No data loaded. Please upload transactions and run detection first.', status_code=400)

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

        return api_response(data={
            'plotly_data': fig.to_dict(),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return api_response(error=str(e), status_code=500)

@app.route('/api/visualizations/risk-distribution', methods=['GET'])
def get_risk_distribution():
    """Get risk distribution visualization"""
    try:
        if detector.transactions is None:
            return api_response(error='No data loaded. Please upload transactions first.', status_code=400)

        if last_detection_results is None:
            detection_results = detector.run_full_detection()
        else:
            detection_results = last_detection_results

        scoring_report = scorer.generate_overall_report(detection_results)
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)

        fig = analyzer.create_risk_distribution_chart(fraud_ring_output)

        return api_response(data={
            'plotly_data': fig.to_dict(),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return api_response(error=str(e), status_code=500)

@app.route('/api/fraud-rings', methods=['GET'])
def get_fraud_rings():
    """Get fraud ring summary data"""
    try:
        if detector.transactions is None or last_detection_results is None:
            return api_response(error='No detection results available.', status_code=400)

        detection_results = last_detection_results
        scoring_report = scorer.generate_overall_report(detection_results)
        fraud_ring_output = scorer.generate_fraud_ring_output(detection_results, scoring_report)

        return api_response(data={
            'fraud_rings': fraud_ring_output['fraud_rings'],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return api_response(error=str(e), status_code=500)

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
            return api_response(error='No file provided', status_code=400)

        file = request.files['file']
        if file.filename == '':
            return api_response(error='No file selected', status_code=400)

        # Read and validate CSV. Accept new input spec (sender_id/receiver_id) or old (from_account/to_account)
        df = pd.read_csv(file)
        expected_new = ['transaction_id', 'sender_id', 'receiver_id', 'amount', 'timestamp']
        expected_old = ['transaction_id', 'from_account', 'to_account', 'amount', 'timestamp']

        if all(col in df.columns for col in expected_new):
            df = df.rename(columns={'sender_id': 'from_account', 'receiver_id': 'to_account'})
        elif all(col in df.columns for col in expected_old):
            pass
        else:
            missing = [col for col in expected_new if col not in df.columns]
            return api_response(
                error=f'Missing required columns for input spec: {missing}. Required columns: {expected_new}',
                status_code=400
            )

        # Convert timestamp using strict format
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        if df['timestamp'].isna().any():
            return api_response(
                error='One or more timestamps could not be parsed. Expected format: YYYY-MM-DD HH:MM:SS',
                status_code=400
            )

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