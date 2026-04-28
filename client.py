import asyncio
import json
import sys
import websockets

from crypto_utils import (
    generate_x25519_keypair,
    public_key_to_base64,
)


async def main():
    uri = "ws://localhost:8765"

    if len(sys.argv) < 4:
        print("Usage: python client.py <register|login> <username> <password>")
        return

    action = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

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

        reply = await websocket.recv()
        print(f"Reply from server: {reply}")

        print(f"{username} keeping connection open for 10 seconds...")
        await asyncio.sleep(10)

        print(f"Client {username} closing connection")


if __name__ == "__main__":
    asyncio.run(main())