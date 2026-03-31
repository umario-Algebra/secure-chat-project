import asyncio
import json
import sys
import websockets


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

            chat_message = {
                "type": "chat",
                "to": "ana",
                "message": "Hello Ana, this is Mario"
            }

            await websocket.send(json.dumps(chat_message))
            print("Chat message sent to ana")

        print(f"{username} is waiting for messages for 20 seconds...")

        try:
            while True:
                incoming = await asyncio.wait_for(websocket.recv(), timeout=20)
                print(f"{username} received: {incoming}")
        except asyncio.TimeoutError:
            print(f"{username} timed out waiting for messages")

        print(f"Client {username} closing connection")


if __name__ == "__main__":
    asyncio.run(main())