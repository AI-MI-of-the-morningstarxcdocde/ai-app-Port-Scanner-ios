"""
API Server for Advanced Port Scanner
Author: morningstar
Description: Provides a RESTful API for third-party integration
with the Port Scanner
"""

from flask import Flask, request, jsonify
import socket
import threading
import json
from scanner.port_scanner import (
    detect_service,
    validate_ssl_certificate,
    fingerprint_service
)
from utils.blockchain_logging import BlockchainLogger
import ipaddress
import os
import logging
from functools import wraps
from flask import g
import time
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restx import Api, Resource, fields

app = Flask(__name__)

API_KEY = os.getenv('PORT_SCANNER_API_KEY', 'YOUR_API_KEY')
logger = logging.getLogger("api_server")
# Set up logging only once (avoid duplicate handlers in production)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

# NOTE: For real production, use a secrets manager or environment variable for API_KEY.
# Never hardcode secrets in code or in public repos.

# Enable CORS for all routes (customize origins as needed)
CORS(app)

# Add rate limiting (e.g., 60 requests/minute per IP)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"]
)

# Authentication middleware (production-ready)
def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        g.request_start_time = time.time()
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            logger.warning(f"Unauthorized API access attempt from {request.remote_addr}")
            return jsonify({"error": "Invalid or missing API key"}), 401
        response = view_function(*args, **kwargs)
        duration = time.time() - g.request_start_time
        logger.info(f"{request.method} {request.path} from {request.remote_addr} - {response.status_code} in {duration:.3f}s")
        return response
    decorated_function.__name__ = view_function.__name__
    return decorated_function

# Initialize Flask-RESTX for OpenAPI docs
api = Api(app, version='1.0', title='Advanced Port Scanner API',
          description='RESTful API for Advanced Port Scanner',
          doc='/docs')

scan_model = api.model('Scan', {
    'target': fields.String(required=True, description='Target IP address'),
    'ports': fields.String(required=False, description='Ports to scan (e.g. 1-1000)'),
    'scan_type': fields.String(required=False, description='Scan type (tcp/udp)')
})

@api.route('/health')
class Health(Resource):
    @api.doc('health')
    def get(self):
        """Health check endpoint."""
        return {
            "status": "ok",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }


@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler."""
    import traceback
    return jsonify({
        "error": str(e),
        "trace": traceback.format_exc()
    }), 500


# Replace @app.route('/api/v1/scan', ...) with RESTX Resource
@api.route('/api/v1/scan')
class Scan(Resource):
    @api.expect(scan_model)
    @require_api_key
    def post(self):
        """Start a port scan with the provided parameters."""
        data = request.json

        # Validate required parameters
        if not data or 'target' not in data:
            return {"error": "Missing required parameter: target"}, 400

        target = data.get('target')
        ports = data.get('ports', '1-1000')
        scan_type = data.get('scan_type', 'tcp')

        # Validate IP address (IPv4 or IPv6)
        try:
            ipaddress.ip_address(target)
        except ValueError:
            return {"error": "Invalid IP address"}, 400

        # Validate ports
        try:
            port_list = parse_ports(ports)
            if not port_list or any(p < 1 or p > 65535 for p in port_list):
                raise ValueError
        except Exception:
            return {"error": "Invalid port(s) specified"}, 400

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

        return {
            "message": "Scan started successfully",
            "scan_id": scan_id
        }


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
        return jsonify(
            {"error": "Missing required parameters: ip and port"}
        ), 400

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
                port_list.extend(range(int(start), int(end) + 1))
            else:
                port_list.append(int(part))
    elif "-" in ports:
        start, end = ports.split("-")
        port_list = list(range(int(start), int(end) + 1))
    else:
        port_list = [int(ports)]
    return port_list


if __name__ == '__main__':
    import os
    ssl_context = None
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        ssl_context = ('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, ssl_context=ssl_context)
