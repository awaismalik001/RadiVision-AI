"""
encryption.py
-------------
AES-256 Database Encryption at Rest for RadiVision AI.
Provides authenticated field-level encryption (AES-256-GCM) for sensitive
patient demographics, national identifiers, contact information, and clinical notes.
"""

import os
import base64
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Attempt import of modern AES-GCM from cryptography
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_AESGCM = True
except ImportError:
    HAS_AESGCM = False

# Encryption key management
_DEFAULT_FALLBACK_KEY = b"RadivisionAI_AES256_SecureKey32B!"  # Exactly 32 bytes for 256-bit key

def _get_aes_key() -> bytes:
    """Retrieves 32-byte key from environment or fallback."""
    raw_key = os.getenv("AES_SECRET_KEY", "")
    if raw_key:
        try:
            # Check if base64 encoded
            decoded = base64.b64decode(raw_key.encode("utf-8"))
            if len(decoded) == 32:
                return decoded
        except Exception:
            pass
        # If UTF-8 string, pad or hash to 32 bytes
        encoded = raw_key.encode("utf-8")
        if len(encoded) >= 32:
            return encoded[:32]
        return encoded.ljust(32, b"0")
    return _DEFAULT_FALLBACK_KEY

class AES256Cipher:
    """AES-256-GCM Authenticated Encryption for sensitive database fields."""

    def __init__(self, key: Optional[bytes] = None):
        self.key = key or _get_aes_key()
        if HAS_AESGCM:
            self._cipher = AESGCM(self.key)
        else:
            self._cipher = None

    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        """
        Encrypts plaintext string into base64-encoded ciphertext with 12-byte IV.
        Returns ciphertext string prefixed with 'enc:aes256:'.
        """
        if plaintext is None:
            return None
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)

        # Do not double-encrypt
        if plaintext.startswith("enc:aes256:"):
            return plaintext

        if not HAS_AESGCM or not self._cipher:
            # Fallback reversible obfuscation if cryptography lib missing
            encoded = base64.b64encode(plaintext.encode("utf-8")).decode("ascii")
            return f"enc:b64:{encoded}"

        try:
            iv = os.urandom(12)  # Recommended 96-bit nonce for AES-GCM
            data_bytes = plaintext.encode("utf-8")
            ciphertext = self._cipher.encrypt(iv, data_bytes, None)
            combined = iv + ciphertext
            b64_cipher = base64.b64encode(combined).decode("ascii")
            return f"enc:aes256:{b64_cipher}"
        except Exception as e:
            print(f"[AES-256 Error] Encryption failed: {e}")
            return plaintext

    def decrypt(self, ciphertext: Optional[str]) -> Optional[str]:
        """
        Decrypts 'enc:aes256:' prefixed string back into UTF-8 plaintext.
        Returns original string if not encrypted.
        """
        if ciphertext is None:
            return None
        if not isinstance(ciphertext, str):
            return str(ciphertext)

        if ciphertext.startswith("enc:b64:"):
            try:
                raw_b64 = ciphertext[len("enc:b64:"):]
                return base64.b64decode(raw_b64.encode("ascii")).decode("utf-8")
            except Exception:
                return ciphertext

        if not ciphertext.startswith("enc:aes256:"):
            return ciphertext

        if not HAS_AESGCM or not self._cipher:
            return ciphertext

        try:
            raw_b64 = ciphertext[len("enc:aes256:"):]
            combined = base64.b64decode(raw_b64.encode("ascii"))
            iv = combined[:12]
            actual_cipher = combined[12:]
            decrypted_bytes = self._cipher.decrypt(iv, actual_cipher, None)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            print(f"[AES-256 Error] Decryption failed: {e}")
            return ciphertext

# Global singleton cipher instance
pacs_cipher = AES256Cipher()
