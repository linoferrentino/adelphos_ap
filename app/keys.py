# module that stores the daemon keys

import os
from cryptography.hazmat.primitives import serialization as crypto_serialization
from .logging import gCon

public_key = None
private_key = None


def load_keys(key_file: str):

    global public_key
    global private_key

    if os.path.exists(key_file):
        gCon.log(f"Loading existing private key from {key_file}.")
        with open(key_file, "rb") as f:
            private_key = crypto_serialization.load_pem_private_key(f.read(), password=None)
    else:
        gCon.log(f"No key file found. Generating new private key and saving to {key_file}.")
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PrivateFormat.PKCS8,
                encryption_algorithm=crypto_serialization.NoEncryption()
            ))

    public_key = private_key.public_key().public_bytes(
        encoding=crypto_serialization.Encoding.PEM,
        format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')


