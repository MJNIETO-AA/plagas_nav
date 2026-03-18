import hashlib
import os

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"), salt, 120_000)
    return salt.hex() + ":" + dk.hex()

def verify_password(password: str, store: str) -> bool:
    """Verify a stored password against one provided by user."""
    salt_hex, dk_hex = store.split(':')
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"), salt, 120_000)
    return dk.hex() == dk_hex