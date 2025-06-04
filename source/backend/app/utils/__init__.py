# Utils package
import hashlib

# Helper function to hash passwords
def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()
