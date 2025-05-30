"""
Port Scanner Module
Author: morningstar
Poster: morningstar's Ethical Hacking Suite
Description: Enhanced port scanner with banner grabbing and vulnerability
checking
"""

import socket
import requests  # type: ignore
import threading
from typing import List, Tuple, Optional
import ipaddress  # Importing ipaddress for IP validation
from utils.blockchain_logging import BlockchainLogger
import json  # Added for saving and loading port profiles
import re  # Added for advanced fingerprinting

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 8080, 8081, 8443, 8888
]


def grab_banner(ip: str, port: int) -> Optional[str]:
    """
    Attempts to grab the banner from a service running on the specified IP and
    port.
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
                return (
                    f"⚠️ Vulnerabilities found: {len(data)} "
                    f"(Check CVE database for details)"
                )
        return "✅ No known vulnerabilities found."
    except Exception:
        return "⚠️ Error checking vulnerabilities."


def scan_port(target: str, port: int, results: List[Tuple[int, bool,
              Optional[str], Optional[str]]]) -> None:
    """
    Scans a single port on the target IP and appends the result to the
    results list.
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
        port_list = parse_ports_string(ports) # Refactored for clarity

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
            {
                "port": port,
                "open": is_open,
                "service": service,
                "vulnerability": vul_status
            } for port, is_open, service, vul_status in results
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


def parse_ports_string(ports_str: str) -> List[int]:
    """Parses a port string (e.g., "80,443,1000-2000") into a list of ints."""
    port_list_result = []
    if ports_str == "all": # Handle "all" case for common ports
        return COMMON_PORTS
    try:
        if "," in ports_str:
            parts = ports_str.split(",")
            for part in parts:
                if "-" in part:
                    start, end = part.split("-")
                    port_list_result.extend(range(int(start), int(end) + 1))
                else:
                    port_list_result.append(int(part))
        elif "-" in ports_str:
            start, end = ports_str.split("-")
            port_list_result = list(range(int(start), int(end) + 1))
        else:
            port_list_result = [int(ports_str)]
    except ValueError: # More specific exception
        print("Invalid port range format. Using default common ports.")
        return COMMON_PORTS # Fallback to common ports
    return port_list_result


def detect_service(port):
    """Detect the service running on a given port."""
    service_map = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
        3306: "MySQL", 8080: "HTTP-Proxy",
    }
    return service_map.get(port, "Unknown Service")


def detect_threats(scan_results):
    """Analyze scan results for potential threats."""
    threats = []
    for result in scan_results:
        if result["service"] in ["FTP", "Telnet"]:
            threats.append(
                f"Port {result['port']} ({result['service']}) is a potential threat."
            )
    return threats


def stealth_scan(target, port_range="1-1000"):
    """Perform a stealth scan to avoid detection."""
    print(f"Performing stealth scan on {target} for ports {port_range}.")
    # Implement stealth scanning logic here
    return


def advanced_scan(target, port_range="1-65535", mode="default"):
    """Perform an advanced scan with customizable options."""
    print(f"Starting advanced scan on {target} with ports {port_range} "
          f"in {mode} mode.")
    if mode == "ai":
        from ai.predictive_model import predict_open_ports
        predicted_ports = predict_open_ports(target)
        print(f"AI-predicted open ports: {predicted_ports}")
    # Here you would add the logic for scanning the ports in the range
    # specified by port_range. This is a placeholder to show where that
    # logic would go.
    return


def export_scan_results(results, format_type="json"): # Renamed format to format_type
    """Export scan results to the specified format."""
    if format_type == "json":
        with open("scan_results.json", "w") as f:
            json.dump(results, f)
    elif format_type == "csv":
        import csv
        with open("scan_results.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Port", "Status", "Service"])
            for result in results:
                writer.writerow(
                    [result["port"], result["status"], result["service"]]
                )
    elif format_type == "pdf":
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Scan Results", ln=True, align="C")
        for result in results:
            pdf.cell(
                200, 10,
                txt=f"Port: {result['port']}, Status: {result['status']}, "
                    f"Service: {result['service']}",
                ln=True
            )
        pdf.output("scan_results.pdf")
    print(f"Scan results exported to {format_type} format.")


# Added low-power mode for battery optimization
def low_power_scan(target, port_range="1-1000"):
    """Perform a low-power scan to conserve battery life."""
    print(f"Performing low-power scan on {target} for ports {port_range}.")
    # Implement low-power scanning logic here
    # (e.g., reduced thread count, longer timeouts)
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
        if result["open"]: # Assuming result is a dict with "open" key
            rules.append(
                f"Block incoming traffic on port {result['port']} "
                f"({result['service']})"
            )
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
def export_scan_history_to_cloud(
        history_file="scan_blockchain_log.json"):
    """Export scan history to iCloud or other cloud services."""
    try:
        import shutil
        # Ensure user's home directory is correctly expanded
        cloud_path = os.path.expanduser(
            f"~/Library/Mobile Documents/com~apple~CloudDocs/{history_file}"
        )
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(cloud_path), exist_ok=True)
        shutil.copy(history_file, cloud_path)
        print(f"Scan history exported to iCloud: {cloud_path}")
    except Exception as e:
        print(f"Failed to export scan history to iCloud: {e}")


# Added functionality for bandwidth usage analysis
def analyze_bandwidth_usage(devices):
    """Analyze bandwidth usage for the given devices."""
    print("Analyzing bandwidth usage...")
    for device in devices:
        print(f"Device: {device['ip']} - "
              f"Bandwidth: {device['bandwidth']} Mbps")
    # Placeholder for actual bandwidth analysis logic
    return


# Added functionality for custom alerts based on scan results
def set_custom_alerts(scan_results, alert_conditions):
    """Set custom alerts based on specific scan outcomes."""
    alerts = []
    for result in scan_results: # Assuming scan_results is a list of dicts
        for condition in alert_conditions:
            if condition(result):
                alerts.append(
                    f"Alert: Condition met for port {result['port']} "
                    f"({result['service']})"
                )
    return alerts


# Enhanced multi-threaded scanning for faster results
def multi_threaded_scan(target, ports_to_scan, thread_count=10): # Renamed ports
    """Perform a multi-threaded scan for faster results."""
    from queue import Queue

    # results needs to be defined in this scope for worker to access
    scan_results_list: List[Tuple[int, bool, Optional[str], Optional[str]]] = []

    def worker():
        while not port_queue.empty():
            port = port_queue.get()
            # scan_port appends to the list passed to it
            scan_port(target, port, scan_results_list)
            port_queue.task_done()

    port_queue = Queue()
    for port_item in ports_to_scan: # Iterate over renamed ports_to_scan
        port_queue.put(port_item)

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    port_queue.join() # Wait for all tasks to be processed

    print("Multi-threaded scan completed.")
    return scan_results_list


# Added functionality for customizable scan templates
def save_scan_template(template_name, target, ports_config, options): # Renamed ports
    """Save a scan template for recurring tasks."""
    template = {
        "target": target,
        "ports": ports_config, # Use renamed ports_config
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
    # import socket # Already imported at top-level

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
    # results dict init seems fine
    results_fp = {"port": port, "ip": ip, "service": "Unknown",
                  "version": "Unknown", "os": "Unknown"}

    if not banner:
        banner = grab_banner(ip, port)

    if banner:
        # Check for common service signatures
        if "SSH" in banner:
            results_fp["service"] = "SSH"
            if "OpenSSH" in banner:
                version_match = re.search(r"OpenSSH[_-](\d+\.\d+[^ ]*)", banner)
                if version_match:
                    results_fp["version"] = version_match.group(1)
                results_fp["os"] = "Unix/Linux" if "Ubuntu" in banner else "Unknown"
        elif "HTTP" in banner or "Server:" in banner:
            results_fp["service"] = "HTTP"
            if "Apache" in banner:
                version_match = re.search(r"Apache/(\d+\.\d+\.\d+)", banner)
                if version_match:
                    results_fp["version"] = version_match.group(1)
                results_fp["os"] = "Unix/Linux"
            elif "nginx" in banner:
                version_match = re.search(r"nginx/(\d+\.\d+\.\d+)", banner)
                if version_match:
                    results_fp["version"] = version_match.group(1)
            elif "IIS" in banner:
                version_match = re.search(r"IIS/(\d+\.\d+)", banner)
                if version_match:
                    results_fp["version"] = version_match.group(1)
                results_fp["os"] = "Windows"

    # Attempt OS fingerprinting based on TTL and response patterns
    try:
        # Send crafted packet and analyze response
        s_fp = socket.socket() # Renamed to avoid conflict
        s_fp.settimeout(1)
        s_fp.connect((ip, port))
        s_fp.send(b"HEAD / HTTP/1.0\r\n\r\n")
        response = s_fp.recv(4096)
        s_fp.close()

        # Analyze response headers for OS fingerprints
        if b"Server:" in response:
            if b"Ubuntu" in response or b"Debian" in response:
                results_fp["os"] = "Linux"
            elif b"Win" in response: # Broad check for Windows
                results_fp["os"] = "Windows"
            elif b"FreeBSD" in response:
                results_fp["os"] = "FreeBSD"
            elif b"Darwin" in response:
                results_fp["os"] = "macOS"
    except socket.error: # More specific exception for socket errors
        pass # Silently ignore if fingerprinting packet fails

    return results_fp


# Added IPv6 support
def scan_port_ipv6(target, port,
                   results_ipv6: List[Tuple[int, bool, Optional[str], Optional[str]]]):
    """
    Scans a single port on the IPv6 target and appends the result to the
    results list.
    """
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((target, port))
            if result == 0:
                banner = grab_banner_ipv6(target, port)
                service = banner.split(" ")[0] if banner else "Unknown Service"
                vul_status = check_vulnerability(service)
                results_ipv6.append((port, True, service, vul_status))
            else:
                results_ipv6.append((port, False, None, None))
    except Exception:
        results_ipv6.append((port, False, None, None))


def grab_banner_ipv6(ip, port):
    """
    Attempts to grab the banner from a service running on the specified IPv6
    address.
    """
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, port))
            banner = s.recv(1024).decode(errors='ignore').strip()
            return banner
    except Exception:
        return None


def run_ipv6_scan(target, ports_str="1-1000"): # Renamed ports to ports_str
    """Run a port scan on IPv6 target address."""
    print(f"Scanning IPv6 target: {target}\n")

    # Validate the IPv6 address
    try:
        ipaddress.IPv6Address(target)
    except ValueError: # More specific error
        raise ValueError("Invalid IPv6 address provided.")

    scan_results_ipv6: List[Tuple[int, bool, Optional[str], Optional[str]]] = []
    threads = []
    # Parse ports string to list
    # Ensure parse_ports_string is used here
    port_list_ipv6 = parse_ports_string(ports_str)
    for port_item in port_list_ipv6:
        t = threading.Thread(target=scan_port_ipv6,
                             args=(target, port_item, scan_results_ipv6))
        threads.append(t)
        t.start()
    for t_item in threads: # Renamed t to t_item
        t_item.join()

    return scan_results_ipv6


# Added SSL/TLS certificate validation


def validate_ssl_certificate(hostname, port=443):
    """Validate the SSL/TLS certificate of a given hostname."""
    import ssl
    # import socket # Already imported
    import datetime
    # import os # Not used here directly, but good for path manipulation if needed

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                if cert is None:  # Handle case where cert is not returned
                    return {
                        "hostname": hostname, "port": port,
                        "error": "No certificate returned.", "valid": False
                    }
                # Check if certificate has expired
                # Handle cases where Z may not be present in timestamp
                not_after_str = cert['notAfter'].replace(" GMT", "").replace(" UTC", "")
                not_before_str = cert['notBefore'].replace(" GMT", "").replace(" UTC", "")
                # More robust date parsing
                try:
                    not_after = datetime.datetime.strptime(not_after_str,
                                                           "%b %d %H:%M:%S %Y")
                    not_before = datetime.datetime.strptime(not_before_str,
                                                            "%b %d %H:%M:%S %Y")
                except ValueError:  # Fallback for different possible formats
                    not_after = datetime.datetime.strptime(not_after_str,
                                                           "%Y%m%d%H%M%SZ")
                    not_before = datetime.datetime.strptime(not_before_str,
                                                            "%Y%m%d%H%M%SZ")

                now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

                is_valid = now > not_before and now < not_after
                is_expired = now > not_after
                days_to_exp = (not_after - now).days if now < not_after else 0
                cert_results = {
                    "hostname": hostname, "port": port,
                    "issuer": dict(x[0] for x in cert.get('issuer', [])),
                    "subject": dict(x[0] for x in cert.get('subject', [])),
                    "version": cert.get('version'),
                    "notBefore": cert.get('notBefore'),
                    "notAfter": cert.get('notAfter'),
                    "valid": is_valid,
                    "expired": is_expired,
                    "daysToExpiration": days_to_exp
                }
                return cert_results
    except Exception as e:
        return {
            "hostname": hostname, "port": port,
            "error": str(e), "valid": False
        }

# Need to import os for os.path.expanduser and os.makedirs
import os
