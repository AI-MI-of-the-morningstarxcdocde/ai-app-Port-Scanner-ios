"""
API Server for Advanced Port Scanner
Author: morningstar
Description: Provides a RESTful API for third-party integration with the Port Scanner
"""

from flask import Flask, request, jsonify
import socket
import threading
import json
from scanner.port_scanner import detect_service, validate_ssl_certificate, fingerprint_service
from utils.blockchain_logging import BlockchainLogger
import ipaddress

app = Flask(__name__)

# Authentication middleware (placeholder - implement proper auth in production)
def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != "YOUR_API_KEY":  # Replace with secure API key storage/validation
            return jsonify({"error": "Invalid or missing API key"}), 401
        return view_function(*args, **kwargs)
    decorated_function.__name__ = view_function.__name__
    return decorated_function

@app.route('/api/v1/scan', methods=['POST'])
@require_api_key
def start_scan():
    """Start a port scan with the provided parameters."""
    data = request.json
    
    # Validate required parameters
    if not data or 'target' not in data:
        return jsonify({"error": "Missing required parameter: target"}), 400
    
    target = data.get('target')
    ports = data.get('ports', '1-1000')
    scan_type = data.get('scan_type', 'tcp')
    
    # Validate IP address
    try:
        ipaddress.ip_address(target)
    except ValueError:
        return jsonify({"error": "Invalid IP address"}), 400
    
    # Start scan in a separate thread
    scan_id = str(hash(f"{target}_{ports}_{scan_type}"))
    
    def run_scan_thread():
        results = []
        port_list = parse_ports(ports)
        
        for port in port_list:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((target, port))
                    if result == 0:
                        service = detect_service(port)
                        results.append({
                            "port": port,
                            "status": "open",
                            "service": service
                        })
            except Exception:
                pass
        
        # Store results in a way that can be retrieved later
        with open(f"scan_{scan_id}.json", "w") as f:
            json.dump(results, f)
        
        # Log scan to blockchain
        blockchain_logger = BlockchainLogger()
        blockchain_logger.log_scan_result({
            "scan_id": scan_id,
            "target": target,
            "ports": ports,
            "scan_type": scan_type,
            "result_count": len(results)
        })
    
    threading.Thread(target=run_scan_thread).start()
    
    return jsonify({
        "message": "Scan started successfully",
        "scan_id": scan_id
    })

@app.route('/api/v1/scan/<scan_id>', methods=['GET'])
@require_api_key
def get_scan_results(scan_id):
    """Get the results of a previously started scan."""
    try:
        with open(f"scan_{scan_id}.json", "r") as f:
            results = json.load(f)
        return jsonify({"results": results})
    except FileNotFoundError:
        return jsonify({"error": "Scan not found"}), 404

@app.route('/api/v1/certificate', methods=['POST'])
@require_api_key
def validate_certificate():
    """Validate an SSL/TLS certificate for a given hostname."""
    data = request.json
    
    if not data or 'hostname' not in data:
        return jsonify({"error": "Missing required parameter: hostname"}), 400
    
    hostname = data.get('hostname')
    port = data.get('port', 443)
    
    try:
        result = validate_ssl_certificate(hostname, port)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/fingerprint', methods=['POST'])
@require_api_key
def fingerprint():
    """Fingerprint a service to identify its version and OS."""
    data = request.json
    
    if not data or 'ip' not in data or 'port' not in data:
        return jsonify({"error": "Missing required parameters: ip and port"}), 400
    
    ip = data.get('ip')
    port = data.get('port')
    
    try:
        result = fingerprint_service(ip, port)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def parse_ports(ports):
    """Parse the ports string into a list of port numbers."""
    port_list = []
    if "," in ports:
        parts = ports.split(",")
        for part in parts:
            if "-" in part:
                start, end = part.split("-")
                port_list.extend(range(int(start), int(end)+1))
            else:
                port_list.append(int(part))
    elif "-" in ports:
        start, end = ports.split("-")
        port_list = list(range(int(start), int(end)+1))
    else:
        port_list = [int(ports)]
    return port_list

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
