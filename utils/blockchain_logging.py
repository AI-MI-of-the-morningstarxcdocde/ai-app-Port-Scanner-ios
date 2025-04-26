"""
Blockchain Logging Module
Author: morningstar
Description: Provides blockchain-backed logging for scan results.
"""

import hashlib
import json
import os
from datetime import datetime

LOG_FILE = "scan_blockchain_log.json"

def hash_data(data: str) -> str:
    """Generate SHA-256 hash of the given data string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def log_scan_result(scan_result: dict) -> None:
    """
    Logs the scan result with a hash to simulate blockchain immutability.
    Appends to a local JSON file as a simple ledger.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": scan_result,
    }
    entry_str = json.dumps(entry, sort_keys=True)
    entry_hash = hash_data(entry_str)
    entry["hash"] = entry_hash

    # Load existing log
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            ledger = json.load(f)
    else:
        ledger = []

    # Append new entry
    ledger.append(entry)

    # Save updated ledger
    with open(LOG_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

def verify_ledger_integrity() -> bool:
    """
    Verifies the integrity of the ledger by checking hashes.
    Returns True if all entries are valid, False otherwise.
    """
    if not os.path.exists(LOG_FILE):
        return True
    with open(LOG_FILE, "r") as f:
        ledger = json.load(f)
    for entry in ledger:
        entry_copy = entry.copy()
        entry_hash = entry_copy.pop("hash", None)
        entry_str = json.dumps(entry_copy, sort_keys=True)
        if hash_data(entry_str) != entry_hash:
            return False
    return True
