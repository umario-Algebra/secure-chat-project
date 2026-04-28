import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def generate_key() -> bytes:
    return AESGCM.generate_key(bit_length=256)


def encrypt_message(key: bytes, plaintext: str) -> dict:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    return {
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8")
    }


def decrypt_message(key: bytes, nonce_b64: str, ciphertext_b64: str) -> str:
    aesgcm = AESGCM(key)
    nonce = base64.b64decode(nonce_b64.encode("utf-8"))
    ciphertext = base64.b64decode(ciphertext_b64.encode("utf-8"))
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
    
def generate_x25519_keypair():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def public_key_to_base64(public_key) -> str:
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return base64.b64encode(public_bytes).decode("utf-8")


def public_key_from_base64(public_key_b64: str):
    public_bytes = base64.b64decode(public_key_b64.encode("utf-8"))
    return x25519.X25519PublicKey.from_public_bytes(public_bytes)


def derive_shared_key(private_key, peer_public_key) -> bytes:
    shared_secret = private_key.exchange(peer_public_key)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"secure-chat-session-key",
    ).derive(shared_secret)

    return derived_key    