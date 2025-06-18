import os
import hashlib
import base64

def hash_master_password(password: str, salt: bytes = None) -> tuple:
    """
    Hashes the master password using PBKDF2-HMAC-SHA256 with a random salt.

    Parameters:
        password (str): The master password to hash.
        salt (bytes, optional): Salt to use. If None, generates a new 16-byte salt.

    Returns:
        tuple: Base64-encoded (salt, hashed key) as strings.
    """
    if salt is None:
        salt = os.urandom(16)
    
    # Derive a secure hash using PBKDF2 with SHA-256
    key = hashlib.pbkdf2_hmac(
        'sha256',           # Hash function
        password.encode(),  # Convert password to bytes
        salt,               # Use the salt
        100_000             # Number of iterations
    )

    # Return salt and derived key as base64 strings for safe storage
    return base64.b64encode(salt).decode(), base64.b64encode(key).decode()


def verify_password(password: str, stored_salt: str, stored_hash: str) -> bool:
    """
    Verifies if the provided password matches the stored hashed password.

    Parameters:
        password (str): Password entered by the user.
        stored_salt (str): Base64-encoded salt used during hashing.
        stored_hash (str): Base64-encoded correct hashed password.

    Returns:
        bool: True if password matches, False otherwise.
    """
    salt = base64.b64decode(stored_salt)  # Decode stored salt
    # Re-derive the hash using the provided password and stored salt
    hash_attempt = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    # Compare the new hash with the stored one
    return base64.b64encode(hash_attempt).decode() == stored_hash
