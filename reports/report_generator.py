"""
Report Generator Module
Author: morningstar
Poster: morningstar's Ethical Hacking Suite
Description: Generates detailed reports for port scans and wireless attacks
"""

import json
import datetime
import matplotlib.pyplot as plt

def generate_report(scan_results, filename=None):
    report = {
        "scan_date": datetime.datetime.now().isoformat(),
        "results": scan_results
    }
    if not filename:
        filename = f"scan_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)
        print(f"Report saved to {filename}")
    except Exception as e:
        print(f"Failed to save report: {e}")

def generate_scan_report(scan_results, output_file="scan_report.png"):
    """Generate a graphical report for scan results."""
    open_ports = [result['port'] for result in scan_results if result['open']]
    closed_ports = [result['port'] for result in scan_results if not result['open']]

    labels = ['Open Ports', 'Closed Ports']
    sizes = [len(open_ports), len(closed_ports)]
    colors = ['green', 'red']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Port Scan Results')
    plt.savefig(output_file)
    print(f"Scan report saved to {output_file}")
