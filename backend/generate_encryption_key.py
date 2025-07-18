#!/usr/bin/env python3
"""
Generate a secure encryption key for the Flask application.
Run this script and set the output as the ENCRYPTION_KEY environment variable.
"""

from cryptography.fernet import Fernet

def generate_encryption_key():
    """Generate a new encryption key for Fernet encryption."""
    key = Fernet.generate_key()
    return key.decode()

if __name__ == "__main__":
    key = generate_encryption_key()
    print("Generated encryption key:")
    print(key)
    print("\nTo use this key, set it as an environment variable:")
    print(f"export ENCRYPTION_KEY='{key}'")
    print("\nOr add it to your .env file:")
    print(f"ENCRYPTION_KEY={key}")