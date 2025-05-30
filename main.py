"""
Main entry point for Advanced Port Scanner and Wireless Attack Tool
Author: morningstarxcdcode
Poster: morningstarxcdcode's Ethical Hacking Suite
Description: CLI and GUI launcher with modular scanning and wireless attack
options
"""

import argparse
from scanner import port_scanner
from wireless import wireless_attacks
from gui import run_gui
from utils import logger


def main():
    parser = argparse.ArgumentParser(
        description="Ultimate Advanced Port Scanner and Wireless Attack Tool"
    )
    parser.add_argument("--mode", choices=["cli", "gui"], default="cli",
                        help="Run mode: cli or gui")
    parser.add_argument("--target", help="Target IP or hostname")
    parser.add_argument("--ports", default="1-65535",
                        help="Port range to scan, e.g. 1-1000")
    parser.add_argument("--scan-type", default="all",
                        help="Scan type or combination of scan types")
    parser.add_argument("--wireless-attack", action="store_true",
                        help="Enable wireless attack mode")
    args = parser.parse_args()

    logger.setup_logger()

    if args.mode == "gui":
        run_gui()
    else:
        if args.wireless_attack:
            if not args.target:
                print("Error: Target IP is required for wireless attack mode.")
                return
            wireless_attacks.run_attack(args.target)
        else:
            if not args.target:
                print("Error: Target IP is required for port scanning.")
                return
            port_scanner.run_scan(args.target, args.ports, args.scan_type)


if __name__ == "__main__":
    main()
