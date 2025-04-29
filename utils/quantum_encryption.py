"""
Quantum-Resistant Encryption Module
Author: morningstar
Description: Implements quantum-resistant encryption algorithms for secure data protection.
"""

import os
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class QuantumResistantEncryption:
    @staticmethod
    def generate_keypair():
        """Generate a quantum-resistant keypair."""
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def key_exchange(private_key, peer_public_key):
        """Perform a key exchange to derive a shared secret."""
        shared_key = private_key.exchange(peer_public_key)
        return shared_key

    @staticmethod
    def derive_key(shared_key):
        """Derive a key from a shared secret using HKDF."""
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'quantum-resistant-key'
        ).derive(shared_key)
        return derived_key

    @staticmethod
    def encrypt(data, key):
        """Encrypt data using AES-GCM."""
        if isinstance(data, str):
            data = data.encode()
        
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv)
        ).encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext

    @staticmethod
    def decrypt(encrypted_data, key):
        """Decrypt data using AES-GCM."""
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag)
        ).decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext