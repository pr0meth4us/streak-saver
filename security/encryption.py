import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureEncryption:
    """Advanced encryption utility for secure data handling."""

    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """Generate a secure encryption key from a password."""
        if not salt:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def encrypt(data: str, key: bytes) -> str:
        """Encrypt data using Fernet symmetric encryption."""
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt(encrypted_data: str, key: bytes) -> str:
        """Decrypt data using Fernet symmetric encryption."""
        f = Fernet(key)
        return f.decrypt(encrypted_data.encode()).decode()
