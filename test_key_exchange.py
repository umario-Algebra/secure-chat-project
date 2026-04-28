from crypto_utils import (
    generate_x25519_keypair,
    public_key_to_base64,
    public_key_from_base64,
    derive_shared_key,
)


alice_private, alice_public = generate_x25519_keypair()
bob_private, bob_public = generate_x25519_keypair()

alice_public_b64 = public_key_to_base64(alice_public)
bob_public_b64 = public_key_to_base64(bob_public)

alice_received_bob_public = public_key_from_base64(bob_public_b64)
bob_received_alice_public = public_key_from_base64(alice_public_b64)

alice_key = derive_shared_key(alice_private, alice_received_bob_public)
bob_key = derive_shared_key(bob_private, bob_received_alice_public)

print("Alice public key (base64):", alice_public_b64)
print("Bob public key (base64):", bob_public_b64)
print("Alice derived key length:", len(alice_key))
print("Bob derived key length:", len(bob_key))
print("Keys match:", alice_key == bob_key)