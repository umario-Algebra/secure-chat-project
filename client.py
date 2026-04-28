import asyncio
import json
import sys
import websockets

from crypto_utils import (
    generate_x25519_keypair,
    public_key_to_base64,
    public_key_from_base64,
    derive_shared_key,
    encrypt_message,
    decrypt_message,
)


async def main():
    uri = "ws://localhost:8765"

    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        return

    username = sys.argv[1]

    private_key, public_key = generate_x25519_keypair()
    public_key_b64 = public_key_to_base64(public_key)

    print(f"Connecting to {uri} as {username}")

    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        register_message = {
            "type": "register",
            "username": username
        }

        await websocket.send(json.dumps(register_message))
        print("Registration message sent")

        reply = await websocket.recv()
        print(f"Reply from server: {reply}")

        public_key_message = {
            "type": "public_key",
            "key": public_key_b64
        }

        await websocket.send(json.dumps(public_key_message))
        print("Public key message sent")

        reply = await websocket.recv()
        print(f"Reply from server: {reply}")

        if username == "mario":
            await asyncio.sleep(2)

            get_key_message = {
                "type": "get_public_key",
                "username": "ana"
            }

            await websocket.send(json.dumps(get_key_message))
            print("Requested public key for ana")

            reply_raw = await websocket.recv()
            print(f"Reply from server: {reply_raw}")

            reply = json.loads(reply_raw)

            if reply.get("type") == "public_key_result":
                ana_public_key_b64 = reply["key"]
                ana_public_key = public_key_from_base64(ana_public_key_b64)
                shared_key = derive_shared_key(private_key, ana_public_key)

                print(f"Derived shared key length: {len(shared_key)}")

                encrypted_payload = encrypt_message(shared_key, "Hello Ana, this is Mario using X25519 + AES-GCM")

                chat_message = {
                    "type": "chat",
                    "to": "ana",
                    "payload": {
                        "sender_public_key": public_key_b64,
                        "nonce": encrypted_payload["nonce"],
                        "ciphertext": encrypted_payload["ciphertext"]
                    }
                }

                await websocket.send(json.dumps(chat_message))
                print("Encrypted chat message sent to ana")

        print(f"{username} is waiting for messages for 20 seconds...")

        try:
            while True:
                incoming_raw = await asyncio.wait_for(websocket.recv(), timeout=20)
                print(f"{username} received raw: {incoming_raw}")

                incoming = json.loads(incoming_raw)

                if incoming.get("type") == "chat":
                    payload = incoming.get("payload", {})
                    sender_public_key_b64 = payload["sender_public_key"]
                    sender_public_key = public_key_from_base64(sender_public_key_b64)

                    shared_key = derive_shared_key(private_key, sender_public_key)
                    plaintext = decrypt_message(
                        shared_key,
                        payload["nonce"],
                        payload["ciphertext"]
                    )

                    print(f"{username} decrypted message: {plaintext}")

        except asyncio.TimeoutError:
            print(f"{username} timed out waiting for messages")

        print(f"Client {username} closing connection")


if __name__ == "__main__":
    asyncio.run(main())