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
from utils.blockchain_logging import log_scan_result
from ai.predictive_model import predict_open_ports

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
        port_list = predict_open_ports(target)
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
    log_scan_result(scan_log)

    for port, is_open, service, vul_status in sorted(results):
        if is_open:
            print(f"✅ Port {port} is OPEN | Service: {service}")
            print(f"  🔍 {vul_status}")
        else:
            print(f"❌ Port {port} is closed")
