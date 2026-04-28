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

    if len(sys.argv) < 4:
        print("Usage: python client.py <register|login> <username> <password> [recipient] [message]")
        return

    action = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    recipient = sys.argv[4] if len(sys.argv) >= 5 else None
    message_text = sys.argv[5] if len(sys.argv) >= 6 else None

    last_seen_counters = {}

    private_key, public_key = generate_x25519_keypair()
    public_key_b64 = public_key_to_base64(public_key)

    print(f"Connecting to {uri} as {username}")

    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        first_message = {
            "type": action,
            "username": username,
            "password": password
        }

        await websocket.send(json.dumps(first_message))
        print(f"{action.capitalize()} message sent")

        reply_raw = await websocket.recv()
        print(f"Reply from server: {reply_raw}")

        reply = json.loads(reply_raw)
        if reply.get("type") not in ("register_ok", "login_ok"):
            print(f"{action.capitalize()} failed")
            return

        public_key_message = {
            "type": "public_key",
            "key": public_key_b64
        }

        await websocket.send(json.dumps(public_key_message))
        print("Public key message sent")

        reply_raw = await websocket.recv()
        print(f"Reply from server: {reply_raw}")

        if recipient and message_text:
            await asyncio.sleep(2)

            get_key_message = {
                "type": "get_public_key",
                "username": recipient
            }

            await websocket.send(json.dumps(get_key_message))
            print(f"Requested public key for {recipient}")

            reply_raw = await websocket.recv()
            print(f"Reply from server: {reply_raw}")

            reply = json.loads(reply_raw)

            if reply.get("type") == "public_key_result":
                recipient_public_key_b64 = reply["key"]
                recipient_public_key = public_key_from_base64(recipient_public_key_b64)
                shared_key = derive_shared_key(private_key, recipient_public_key)

                print(f"Derived shared key length: {len(shared_key)}")

                encrypted_payload = encrypt_message(shared_key, message_text)

                chat_message = {
                    "type": "chat",
                    "to": recipient,
                    "payload": {
                        "sender_public_key": public_key_b64,
                        "counter": 1,
                        "nonce": encrypted_payload["nonce"],
                        "ciphertext": encrypted_payload["ciphertext"]
                    }
                }

                await websocket.send(json.dumps(chat_message))
                print(f"Encrypted chat message with counter=1 sent to {recipient}")

        print(f"{username} is waiting for messages for 20 seconds...")

        try:
            while True:
                incoming_raw = await asyncio.wait_for(websocket.recv(), timeout=20)
                print(f"{username} received raw: {incoming_raw}")

                incoming = json.loads(incoming_raw)

                if incoming.get("type") == "chat":
                    sender = incoming.get("from")
                    payload = incoming.get("payload", {})

                    counter = payload["counter"]
                    last_seen = last_seen_counters.get(sender, 0)

                    if counter <= last_seen:
                        print(
                            f"{username} detected replay attack from {sender}: "
                            f"counter={counter}, last_seen={last_seen}"
                        )
                        continue

                    last_seen_counters[sender] = counter

                    sender_public_key_b64 = payload["sender_public_key"]
                    sender_public_key = public_key_from_base64(sender_public_key_b64)

                    shared_key = derive_shared_key(private_key, sender_public_key)
                    plaintext = decrypt_message(
                        shared_key,
                        payload["nonce"],
                        payload["ciphertext"]
                    )

                    print(f"{username} accepted counter {counter} from {sender}")
                    print(f"{username} decrypted message: {plaintext}")

        except asyncio.TimeoutError:
            print(f"{username} timed out waiting for messages")

        print(f"Client {username} closing connection")


if __name__ == "__main__":
    asyncio.run(main())