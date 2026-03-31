# Secure Chat Project

A secure real-time chat application with end-to-end encryption and authentication, developed as a project for the Applied Cryptography course.

## Project goals

- User authentication
- End-to-end encrypted messaging
- Secure session key establishment
- Message integrity protection
- Basic replay attack protection
- Clean and reproducible project structure

## Planned architecture

- Python-based server
- Python-based client
- WebSocket communication
- Cryptographic key exchange between clients
- AEAD encryption for messages
- Server forwards ciphertext but does not read plaintext

## Project structure

- `server.py` - chat server
- `client.py` - chat client
- `auth.py` - user authentication logic
- `crypto_utils.py` - cryptographic helper functions
- `protocol.py` - message formats and protocol handling
- `storage.py` - local storage / user persistence
- `tests/` - test files
- `docs/` - report and screenshots

## Status

Project initialization completed. Implementation in progress.