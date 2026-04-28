# Secure Chat Project

A secure real-time chat application with user authentication and end-to-end encrypted messaging, developed as a project for the Applied Cryptography course.

## Features

- User registration and login
- Password hashing using scrypt with random salt
- Real-time messaging over WebSockets
- End-to-end encryption using X25519 key exchange and AES-GCM
- Public key exchange through the server
- Replay attack detection using message counters
- Server forwards encrypted payloads and does not decrypt message contents

## Cryptographic design

### Authentication
- User passwords are not stored in plaintext
- Passwords are hashed using `hashlib.scrypt`
- Stored password format: `salt:hash` (Base64-encoded)

### Key exchange
- Each client generates an ephemeral X25519 key pair on startup
- Public keys are shared through the server
- Clients derive a shared session key using X25519 + HKDF-SHA256

### Message encryption
- Messages are encrypted with AES-GCM
- A fresh random 12-byte nonce is generated for each message
- The encrypted payload includes:
  - sender public key
  - message counter
  - nonce
  - ciphertext

### Replay protection
- Each received message contains a counter
- The recipient tracks the last seen counter per sender
- Replayed or old messages are rejected

## Project structure

- `server.py` - WebSocket server and protocol handling
- `client.py` - chat client
- `crypto_utils.py` - key exchange and encryption helpers
- `auth.py` - password hashing and verification
- `storage.py` - local user storage
- `test_crypto.py` - AES-GCM encryption/decryption test
- `test_key_exchange.py` - X25519 shared key derivation test
- `test_auth.py` - password hash/verify test
- `test_storage.py` - user storage test
- `data/` - runtime storage directory
- `docs/` - documentation assets
- `tests/` - reserved for future tests

## Requirements

- Python 3.13+
- `websockets`
- `cryptography`

Install dependencies:

```bash
pip install -r requirements.txt