import asyncio
import json
import sys
import websockets

from crypto_utils import encrypt_message, decrypt_message


# Temporary shared demo key for both clients
DEMO_KEY = bytes.fromhex(
    "00112233445566778899aabbccddeeff"
    "00112233445566778899aabbccddeeff"
)


async def main():
    uri = "ws://localhost:8765"

    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        return

    username = sys.argv[1]

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

        if username == "mario":
            await asyncio.sleep(2)

            encrypted_payload = encrypt_message(DEMO_KEY, "Hello Ana, this is Mario")

            chat_message = {
                "type": "chat",
                "to": "ana",
                "payload": encrypted_payload
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
                    plaintext = decrypt_message(
                        DEMO_KEY,
                        payload["nonce"],
                        payload["ciphertext"]
                    )
                    print(f"{username} decrypted message: {plaintext}")
        except asyncio.TimeoutError:
            print(f"{username} timed out waiting for messages")

        print(f"Client {username} closing connection")


if __name__ == "__main__":
    asyncio.run(main())