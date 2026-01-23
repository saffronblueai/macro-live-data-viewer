"""
Macro Data Dashboard Server

A simple Flask server to serve the dashboard and provide API endpoints
for data management.

Usage:
    python server.py              # Run on default port 5000
    python server.py --port 8080  # Run on custom port
    python server.py --host 0.0.0.0  # Allow external connections
"""

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, send_from_directory, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("Required packages not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
    from flask import Flask, send_from_directory, jsonify, request
    from flask_cors import CORS

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.resolve()

app = Flask(__name__, static_folder=str(BASE_DIR))
CORS(app)  # Enable CORS for all routes


# ============================================================================
# Static File Routes
# ============================================================================

@app.route('/')
def index():
    """Serve the main dashboard HTML."""
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (JS, CSS, CSV, etc.)."""
    return send_from_directory(BASE_DIR, filename)


# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/status')
def api_status():
    """Get server status and data freshness info."""
    data_js_path = BASE_DIR / 'data.js'
    
    status = {
        'status': 'running',
        'server_time': datetime.now().isoformat(),
        'data_file_exists': data_js_path.exists(),
        'data_last_modified': None,
        'available_files': []
    }
    
    if data_js_path.exists():
        mtime = datetime.fromtimestamp(data_js_path.stat().st_mtime)
        status['data_last_modified'] = mtime.isoformat()
    
    # List available data files
    for ext in ['*.csv', '*.js', '*.html']:
        for f in BASE_DIR.glob(ext):
            status['available_files'].append(f.name)
    
    return jsonify(status)


@app.route('/api/refresh', methods=['POST'])
def api_refresh_data():
    """
    Trigger data refresh by running fetch_data.py.
    
    POST body (optional):
        {
            "type": "all" | "data" | "sentiment",
            "force": true | false
        }
    """
    try:
        body = request.get_json() or {}
        refresh_type = body.get('type', 'all')
        
        results = {'success': True, 'operations': []}
        
        # Run fetch_data.py generate
        if refresh_type in ['all', 'data']:
            fetch_data_script = BASE_DIR / 'fetch_data.py'
            if fetch_data_script.exists():
                result = subprocess.run(
                    [sys.executable, str(fetch_data_script), 'generate'],
                    capture_output=True,
                    text=True,
                    cwd=str(BASE_DIR)
                )
                results['operations'].append({
                    'script': 'fetch_data.py',
                    'success': result.returncode == 0,
                    'message': result.stdout if result.returncode == 0 else result.stderr
                })
        
        # Run fetch_sentiment.py if needed
        if refresh_type in ['all', 'sentiment']:
            fetch_sentiment_script = BASE_DIR / 'fetch_sentiment.py'
            if fetch_sentiment_script.exists():
                result = subprocess.run(
                    [sys.executable, str(fetch_sentiment_script)],
                    capture_output=True,
                    text=True,
                    cwd=str(BASE_DIR)
                )
                results['operations'].append({
                    'script': 'fetch_sentiment.py',
                    'success': result.returncode == 0,
                    'message': result.stdout if result.returncode == 0 else result.stderr
                })
        
        # Check overall success
        results['success'] = all(op['success'] for op in results['operations'])
        results['timestamp'] = datetime.now().isoformat()
        
        return jsonify(results), 200 if results['success'] else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/data')
def api_get_data():
    """
    Get the current data as JSON.
    Reads from data.js and returns the ALL_DATA object.
    """
    data_js_path = BASE_DIR / 'data.js'
    
    if not data_js_path.exists():
        return jsonify({'error': 'data.js not found. Run refresh first.'}), 404
    
    try:
        with open(data_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract ALL_DATA from the JavaScript file
        # The file format is: const ALL_DATA = { ... };
        start_marker = 'const ALL_DATA = '
        start_idx = content.find(start_marker)
        
        if start_idx == -1:
            return jsonify({'error': 'ALL_DATA not found in data.js'}), 500
        
        # Find the JSON object
        json_start = start_idx + len(start_marker)
        
        # Find matching closing brace
        brace_count = 0
        json_end = json_start
        for i, char in enumerate(content[json_start:], start=json_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
        
        json_str = content[json_start:json_end]
        data = json.loads(json_str)
        
        return jsonify(data)
        
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Failed to parse data.js: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/csv/<filename>')
def api_get_csv(filename):
    """
    Get CSV data as JSON.
    
    Parameters:
        filename: Name of the CSV file (without path)
    """
    # Security: only allow specific CSV files
    allowed_files = [
        'sentiment_data.csv',
        'sentiment_data_domestic.csv',
        'bond_yields_10y.csv',
        'currencies.csv',
        'stock_indices.csv',
        'countries_tickers.csv'
    ]
    
    if filename not in allowed_files:
        return jsonify({'error': 'File not allowed'}), 403
    
    csv_path = BASE_DIR / filename
    
    if not csv_path.exists():
        return jsonify({'error': f'{filename} not found'}), 404
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Macro Data Dashboard Server')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host to bind to (default: 127.0.0.1, use 0.0.0.0 for external)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run on (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--refresh', action='store_true',
                        help='Refresh data before starting server')
    
    args = parser.parse_args()
    
    # Optionally refresh data before starting
    if args.refresh:
        print("Refreshing data before starting server...")
        fetch_data_script = BASE_DIR / 'fetch_data.py'
        if fetch_data_script.exists():
            subprocess.run(
                [sys.executable, str(fetch_data_script), 'generate'],
                cwd=str(BASE_DIR)
            )
    
    # Check if data.js exists
    data_js_path = BASE_DIR / 'data.js'
    if not data_js_path.exists():
        print("\nWarning: data.js not found!")
        print("Run 'python fetch_data.py generate' to generate data,")
        print("or start the server with --refresh flag.\n")
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           Macro Data Dashboard Server                        ║
╠══════════════════════════════════════════════════════════════╣
║  Dashboard:     http://{args.host}:{args.port}/                       
║  API Status:    http://{args.host}:{args.port}/api/status             
║  Refresh Data:  POST http://{args.host}:{args.port}/api/refresh       
║  Get Data:      http://{args.host}:{args.port}/api/data               
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
