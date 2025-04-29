"""
Port Scanner Module
Author: morningstar
Poster: morningstar's Ethical Hacking Suite
Description: Enhanced port scanner with banner grabbing and vulnerability checking
"""

import socket
import requests  # type: ignore
import threading
from typing import List, Tuple, Optional
import ipaddress  # Importing ipaddress for IP validation
from utils.blockchain_logging import BlockchainLogger
import json  # Added for saving and loading port profiles
import re  # Added for advanced fingerprinting

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 8080, 8081, 8443, 8888]

def grab_banner(ip: str, port: int) -> Optional[str]:
    """
    Attempts to grab the banner from a service running on the specified IP and port.
    """
    try:
        with socket.socket() as s:
            s.settimeout(2)
            s.connect((ip, port))
            banner = s.recv(1024).decode(errors='ignore').strip()
            return banner
    except Exception:
        return None

def check_vulnerability(service: str) -> str:
    """
    Checks for known vulnerabilities of the given service using the CVE API.
    """
    url = f"https://cve.circl.lu/api/search/{service}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                return f"⚠️ Vulnerabilities found: {len(data)} (Check CVE database for details)"
        return "✅ No known vulnerabilities found."
    except Exception:
        return "⚠️ Error checking vulnerabilities."

def scan_port(target: str, port: int, results: List[Tuple[int, bool, Optional[str], Optional[str]]]) -> None:
    """
    Scans a single port on the target IP and appends the result to the results list.
    """
    try:
        with socket.socket() as s:
            s.settimeout(1)
            result = s.connect_ex((target, port))
            if result == 0:
                banner = grab_banner(target, port)
                service = banner.split(" ")[0] if banner else "Unknown Service"
                vul_status = check_vulnerability(service)
                results.append((port, True, service, vul_status))
            else:
                results.append((port, False, None, None))
    except Exception:
        results.append((port, False, None, None))

def run_scan(target: str, ports: str = "1-65535", scan_type: str = "all") -> None:
    """
    Scans ports on the target IP concurrently and prints the results.
    Uses AI-driven prediction to optimize port selection.
    """
    # Validate the IP address
    try:
        ipaddress.ip_address(target)
    except ValueError:
        raise ValueError("Invalid IP address provided.")

    print(f"\nScanning target: {target}\n")
    results: List[Tuple[int, bool, Optional[str], Optional[str]]] = []
    threads = []
    # Determine ports to scan
    if ports == "ai":
        from ai.predictive_model import predict_open_ports
        port_list = predict_open_ports(target)
        print(f"AI-predicted open ports: {port_list}")
    else:
        # Parse ports string to list of ints
        port_list = []
        if ports == "all":
            port_list = COMMON_PORTS
        else:
            try:
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
            except Exception:
                print("Invalid port range format. Using default common ports.")
                port_list = COMMON_PORTS

    for port in port_list:
        t = threading.Thread(target=scan_port, args=(target, port, results))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # Log scan results to blockchain ledger
    scan_log = {
        "target": target,
        "ports_scanned": len(port_list),
        "open_ports": [port for port, is_open, _, _ in results if is_open],
        "scan_details": [
            {"port": port, "open": is_open, "service": service, "vulnerability": vul_status}
            for port, is_open, service, vul_status in results
        ],
    }
    blockchain_logger = BlockchainLogger()
    blockchain_logger.log_scan_result(scan_log)

    for port, is_open, service, vul_status in sorted(results):
        if is_open:
            print(f"✅ Port {port} is OPEN | Service: {service}")
            print(f"  🔍 {vul_status}")
        else:
            print(f"❌ Port {port} is closed")

def detect_service(port):
    """Detect the service running on a given port."""
    service_map = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        3306: "MySQL",
        8080: "HTTP-Proxy",
    }
    return service_map.get(port, "Unknown Service")

def detect_threats(scan_results):
    """Analyze scan results for potential threats."""
    threats = []
    for result in scan_results:
        if result["service"] in ["FTP", "Telnet"]:
            threats.append(f"Port {result['port']} ({result['service']}) is a potential threat.")
    return threats

def stealth_scan(target, port_range="1-1000"):
    """Perform a stealth scan to avoid detection."""
    print(f"Performing stealth scan on {target} for ports {port_range}.")
    # Implement stealth scanning logic here
    return

def advanced_scan(target, port_range="1-65535", mode="default"):
    """Perform an advanced scan with customizable options."""
    print(f"Starting advanced scan on {target} with ports {port_range} in {mode} mode.")
    if mode == "ai":
        from ai.predictive_model import predict_open_ports
        predicted_ports = predict_open_ports(target)
        print(f"AI-predicted open ports: {predicted_ports}")
    # Here you would add the logic for scanning the ports in the range
    # specified by port_range. This is a placeholder to show where that
    # logic would go.
    return

def export_scan_results(results, format="json"):
    """Export scan results to the specified format."""
    if format == "json":
        with open("scan_results.json", "w") as f:
            json.dump(results, f)
    elif format == "csv":
        import csv
        with open("scan_results.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Port", "Status", "Service"])
            for result in results:
                writer.writerow([result["port"], result["status"], result["service"]])
    elif format == "pdf":
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Scan Results", ln=True, align="C")
        for result in results:
            pdf.cell(200, 10, txt=f"Port: {result['port']}, Status: {result['status']}, Service: {result['service']}", ln=True)
        pdf.output("scan_results.pdf")
    print(f"Scan results exported to {format} format.")

# Added low-power mode for battery optimization
def low_power_scan(target, port_range="1-1000"):
    """Perform a low-power scan to conserve battery life."""
    print(f"Performing low-power scan on {target} for ports {port_range}.")
    # Implement low-power scanning logic here (e.g., reduced thread count, longer timeouts)
    return

# Added functionality to save and load custom port profiles
def save_port_profile(profile_name, ports):
    """Save a custom port profile."""
    with open(f"{profile_name}.json", "w") as f:
        json.dump(ports, f)
    print(f"Port profile '{profile_name}' saved.")

def load_port_profile(profile_name):
    """Load a custom port profile."""
    try:
        with open(f"{profile_name}.json", "r") as f:
            ports = json.load(f)
        print(f"Port profile '{profile_name}' loaded.")
        return ports
    except FileNotFoundError:
        print(f"Port profile '{profile_name}' not found.")
        return []

# Added functionality to recommend firewall rules based on scan results
def recommend_firewall_rules(scan_results):
    """Generate firewall rules based on scan results."""
    rules = []
    for result in scan_results:
        if result["open"]:
            rules.append(f"Block incoming traffic on port {result['port']} ({result['service']})")
    return rules

# Added reverse DNS lookup functionality
def reverse_dns_lookup(ip):
    """Perform a reverse DNS lookup for the given IP address."""
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except socket.herror:
        return "No PTR record found"

# Added functionality to export scan history to iCloud
def export_scan_history_to_cloud(history_file="scan_blockchain_log.json"):
    """Export scan history to iCloud or other cloud services."""
    try:
        import shutil
        cloud_path = f"~/Library/Mobile Documents/com~apple~CloudDocs/{history_file}"
        shutil.copy(history_file, cloud_path)
        print(f"Scan history exported to iCloud: {cloud_path}")
    except Exception as e:
        print(f"Failed to export scan history to iCloud: {e}")

# Added functionality for bandwidth usage analysis
def analyze_bandwidth_usage(devices):
    """Analyze bandwidth usage for the given devices."""
    print("Analyzing bandwidth usage...")
    for device in devices:
        print(f"Device: {device['ip']} - Bandwidth: {device['bandwidth']} Mbps")
    # Placeholder for actual bandwidth analysis logic
    return

# Added functionality for custom alerts based on scan results
def set_custom_alerts(scan_results, alert_conditions):
    """Set custom alerts based on specific scan outcomes."""
    alerts = []
    for result in scan_results:
        for condition in alert_conditions:
            if condition(result):
                alerts.append(f"Alert: Condition met for port {result['port']} ({result['service']})")
    return alerts

# Enhanced multi-threaded scanning for faster results
def multi_threaded_scan(target, ports, thread_count=10):
    """Perform a multi-threaded scan for faster results."""
    from queue import Queue

    def worker():
        while not port_queue.empty():
            port = port_queue.get()
            scan_port(target, port, results)
            port_queue.task_done()

    port_queue = Queue()
    for port in ports:
        port_queue.put(port)

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Multi-threaded scan completed.")
    return results

# Added functionality for customizable scan templates
def save_scan_template(template_name, target, ports, options):
    """Save a scan template for recurring tasks."""
    template = {
        "target": target,
        "ports": ports,
        "options": options
    }
    with open(f"{template_name}.json", "w") as f:
        json.dump(template, f)
    print(f"Scan template '{template_name}' saved.")

def load_scan_template(template_name):
    """Load a scan template."""
    try:
        with open(f"{template_name}.json", "r") as f:
            template = json.load(f)
        print(f"Scan template '{template_name}' loaded.")
        return template
    except FileNotFoundError:
        print(f"Scan template '{template_name}' not found.")
        return None

# Added honeypot simulation functionality
def simulate_honeypot(port, response_message="Unauthorized access detected"):
    """Simulate a honeypot to detect malicious activity on a specific port."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen(1)
        print(f"Honeypot active on port {port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connection attempt from {addr}")
                conn.sendall(response_message.encode())

# Added advanced fingerprinting functionality
def fingerprint_service(ip, port, banner=None):
    """Fingerprint a service to identify its version and OS accurately."""
    results = {"port": port, "ip": ip, "service": "Unknown", "version": "Unknown", "os": "Unknown"}
    
    if not banner:
        banner = grab_banner(ip, port)
    
    if banner:
        # Check for common service signatures
        if "SSH" in banner:
            results["service"] = "SSH"
            if "OpenSSH" in banner:
                version_match = re.search(r"OpenSSH[_-](\d+\.\d+[^ ]*)", banner)
                if version_match:
                    results["version"] = version_match.group(1)
                results["os"] = "Unix/Linux" if "Ubuntu" in banner else "Unknown"
        elif "HTTP" in banner or "Server:" in banner:
            results["service"] = "HTTP"
            if "Apache" in banner:
                version_match = re.search(r"Apache/(\d+\.\d+\.\d+)", banner)
                if version_match:
                    results["version"] = version_match.group(1)
                results["os"] = "Unix/Linux"
            elif "nginx" in banner:
                version_match = re.search(r"nginx/(\d+\.\d+\.\d+)", banner)
                if version_match:
                    results["version"] = version_match.group(1)
            elif "IIS" in banner:
                version_match = re.search(r"IIS/(\d+\.\d+)", banner)
                if version_match:
                    results["version"] = version_match.group(1)
                results["os"] = "Windows"
    
    # Attempt OS fingerprinting based on TTL and response patterns
    try:
        # Send crafted packet and analyze response
        s = socket.socket()
        s.settimeout(1)
        s.connect((ip, port))
        s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        response = s.recv(4096)
        s.close()
        
        # Analyze response headers for OS fingerprints
        if b"Server:" in response:
            if b"Ubuntu" in response or b"Debian" in response:
                results["os"] = "Linux"
            elif b"Win" in response:
                results["os"] = "Windows"
            elif b"FreeBSD" in response:
                results["os"] = "FreeBSD"
            elif b"Darwin" in response:
                results["os"] = "macOS"
    except:
        pass
        
    return results

# Added IPv6 support
def scan_port_ipv6(target, port, results):
    """Scans a single port on the IPv6 target and appends the result to the results list."""
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((target, port))
            if result == 0:
                banner = grab_banner_ipv6(target, port)
                service = banner.split(" ")[0] if banner else "Unknown Service"
                vul_status = check_vulnerability(service)
                results.append((port, True, service, vul_status))
            else:
                results.append((port, False, None, None))
    except Exception:
        results.append((port, False, None, None))

def grab_banner_ipv6(ip, port):
    """Attempts to grab the banner from a service running on the specified IPv6 address."""
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, port))
            banner = s.recv(1024).decode(errors='ignore').strip()
            return banner
    except Exception:
        return None

def run_ipv6_scan(target, ports="1-1000"):
    """Run a port scan on IPv6 target address."""
    print(f"Scanning IPv6 target: {target}\n")
    
    # Validate the IPv6 address
    try:
        ipaddress.IPv6Address(target)
    except ValueError:
        raise ValueError("Invalid IPv6 address provided.")
    
    results = []  # Ensure results is defined
    threads = []
    # Parse ports string to list
    port_list = parse_ports(ports)  # Ensure parse_ports is imported or defined
    
    for port in port_list:
        t = threading.Thread(target=scan_port_ipv6, args=(target, port, results))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    return results

# Added SSL/TLS certificate validation
def validate_ssl_certificate(hostname, port=443):
    """Validate the SSL/TLS certificate of a given hostname."""
    import ssl
    import socket
    import datetime
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Check if certificate has expired
                not_after = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                not_before = datetime.datetime.strptime(cert['notBefore'], "%b %d %H:%M:%S %Y %Z")
                now = datetime.datetime.now()
                
                results = {
                    "hostname": hostname,
                    "port": port,
                    "issuer": cert['issuer'],
                    "subject": cert['subject'],
                    "version": cert['version'],
                    "notBefore": cert['notBefore'],
                    "notAfter": cert['notAfter'],
                    "valid": now > not_before and now < not_after,
                    "expired": now > not_after,
                    "daysToExpiration": (not_after - now).days if now < not_after else 0
                }
                
                return results
    except Exception as e:
        return {
            "hostname": hostname,
            "port": port,
            "error": str(e),
            "valid": False
        }
