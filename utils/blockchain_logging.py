"""
Blockchain Logging Module
Author: morningstar
Description: Provides blockchain-backed logging for scan results.
"""

import hashlib
import json


class BlockchainLogger:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash='0')

    def create_block(self, data=None, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'data': data,
            'previous_hash': previous_hash or (self.hash(self.chain[-1])
                                              if self.chain else '0'),
            'hash': None
        }
        block['hash'] = self.hash(block)
        self.chain.append(block)
        return block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def log_scan_result(self, scan_result):
        self.create_block(data=scan_result)
        print("Scan result logged to blockchain.")

    def get_chain(self):
        return self.chain

    def log_threat_intelligence(threat_data):
        """Log threat intelligence data to the blockchain."""
        block_data = {  # Renamed variable to avoid conflict
            'type': 'threat_intelligence',
            'data': threat_data
        }
        # It seems this method should be part of the class or static
        # Assuming it should be a static method or part of an instance
        return BlockchainLogger().create_block(data=block_data)
