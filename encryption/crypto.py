from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

def encrypt_password(password: str, key: bytes) -> str:
    """
    Encrypt a password string using AES-GCM.
    Returns a base64-encoded nonce + ciphertext.
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, password.encode(), None)
    return base64.b64encode(nonce + ct).decode()

def decrypt_password(encrypted_data: str, key: bytes) -> str:
    """
    Decrypt a base64-encoded encrypted password using AES-GCM.
    """
    raw = base64.b64decode(encrypted_data)
    nonce = raw[:12]
    ct = raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None).decode()
