from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import os

# Generate a symmetric key for AES
def generate_aes_key(length=32):  # 32 bytes = 256 bits
    return os.urandom(length)


# Generate an RSA private key
def generate_rsa_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


aes_key = generate_aes_key()
print("Generated AES Key:", aes_key.hex())