import base64
import os
import hashlib
import hmac


def hash_password(password: str) -> str:
    salt = os.urandom(16)

    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )

    return (
        base64.b64encode(salt).decode("utf-8")
        + ":"
        + base64.b64encode(derived_key).decode("utf-8")
    )


def verify_password(password: str, stored_value: str) -> bool:
    salt_b64, hash_b64 = stored_value.split(":")

    salt = base64.b64decode(salt_b64.encode("utf-8"))
    expected_hash = base64.b64decode(hash_b64.encode("utf-8"))

    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )

    return hmac.compare_digest(derived_key, expected_hash)