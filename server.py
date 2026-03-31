import asyncio
import json
import websockets

connected_users = {}


async def handler(websocket):
    username = None
    print("New connection opened")

    try:
        raw_message = await websocket.recv()
        data = json.loads(raw_message)

        if data.get("type") != "register" or "username" not in data:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "First message must be a register message"
            }))
            return

        username = data["username"]

        if username in connected_users:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Username already connected"
            }))
            return

        connected_users[username] = websocket
        print(f"User registered: {username}")

        await websocket.send(json.dumps({
            "type": "register_ok",
            "message": f"Welcome, {username}"
        }))

        async for raw_message in websocket:
            print(f"From {username}: {raw_message}")

            data = json.loads(raw_message)

            if data.get("type") == "chat":
                recipient = data.get("to")
                payload = data.get("payload")

                if recipient not in connected_users:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Recipient {recipient} is not connected"
                    }))
                    continue

                await connected_users[recipient].send(json.dumps({
                    "type": "chat",
                    "from": username,
                    "payload": payload
                }))

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed: {username}")
    finally:
        if username and connected_users.get(username) is websocket:
            del connected_users[username]
            print(f"User removed: {username}")


async def main():
    print("Starting server on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())