from crypto_utils import generate_key, encrypt_message, decrypt_message


key = generate_key()
plaintext = "Hello secure world"

encrypted = encrypt_message(key, plaintext)
decrypted = decrypt_message(key, encrypted["nonce"], encrypted["ciphertext"])

print("Original:", plaintext)
print("Nonce length:", len(encrypted["nonce"]))
print("Ciphertext length:", len(encrypted["ciphertext"]))
print("Decrypted:", decrypted)
print("Match:", plaintext == decrypted)

tampered = bytearray(encrypted["ciphertext"])
tampered[0] ^= 1

try:
    decrypt_message(key, encrypted["nonce"], bytes(tampered))
    print("Tamper test: FAILED")
except Exception as e:
    print("Tamper test: PASSED")
    print("Tamper error type:", type(e).__name__)