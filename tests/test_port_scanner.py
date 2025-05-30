import sys
import os

# Add the project root directory to sys.path to fix import issues
# This needs to be at the very top before other project imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import unittest
from scanner.port_scanner import run_scan
from utils.blockchain_logging import BlockchainLogger


class TestPortScanner(unittest.TestCase):
    def test_log_scan_result(self):
        """Test logging scan results to the blockchain."""
        logger = BlockchainLogger()
        scan_result = {
            "target": "127.0.0.1",
            "ports_scanned": 2,
            "open_ports": [22, 80],
            "scan_details": [
                {"port": 22, "open": True, "service": "SSH",
                 "vulnerability": "None"},
                {"port": 80, "open": True, "service": "HTTP",
                 "vulnerability": "None"}
            ]
        }
        try:
            logger.log_scan_result(scan_result)
        except Exception as e:
            self.fail(f"log_scan_result raised an exception: {str(e)}")

    def test_run_scan_valid(self):
        """Test scanning valid ports."""
        # Here we would need to capture printed output or refactor run_scan
        # to return results. For now, we will just check if it runs
        # without error.
        try:
            run_scan("127.0.0.1", "22,80")  # Example IP and ports
        except Exception as e:
            self.fail(f"run_scan raised an exception: {str(e)}")

    def test_run_scan_invalid_ip(self):
        """Test scanning with an invalid IP address."""
        with self.assertRaises(ValueError):
            run_scan("invalid_ip", "22,80")

    def test_run_scan_no_open_ports(self):
        """Test scanning with no open ports."""
        # Similar to the valid test, we would need to capture output
        try:
            run_scan("127.0.0.1", "9999")  # Assuming port 9999 is closed
        except Exception as e:
            self.fail(f"run_scan raised an exception: {str(e)}")


if __name__ == "__main__":
    unittest.main()
