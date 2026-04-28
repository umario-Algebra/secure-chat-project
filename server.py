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

        connected_users[username] = {
            "websocket": websocket,
            "public_key": None
        }

        print(f"User registered: {username}")

        await websocket.send(json.dumps({
            "type": "register_ok",
            "message": f"Welcome, {username}"
        }))

        async for raw_message in websocket:
            print(f"From {username}: {raw_message}")
            data = json.loads(raw_message)

            if data.get("type") == "public_key":
                connected_users[username]["public_key"] = data.get("key")
                print(f"Stored public key for {username}")

                await websocket.send(json.dumps({
                    "type": "public_key_ok",
                    "message": f"Public key stored for {username}"
                }))

            elif data.get("type") == "get_public_key":
                target_user = data.get("username")

                if target_user not in connected_users:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"User {target_user} is not connected"
                    }))
                    continue

                target_public_key = connected_users[target_user]["public_key"]

                if not target_public_key:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"User {target_user} has not uploaded a public key"
                    }))
                    continue

                await websocket.send(json.dumps({
                    "type": "public_key_result",
                    "username": target_user,
                    "key": target_public_key
                }))

            elif data.get("type") == "chat":
                recipient = data.get("to")
                payload = data.get("payload")

                if recipient not in connected_users:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Recipient {recipient} is not connected"
                    }))
                    continue

                await connected_users[recipient]["websocket"].send(json.dumps({
                    "type": "chat",
                    "from": username,
                    "payload": payload
                }))

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed: {username}")
    finally:
        if username and username in connected_users:
            del connected_users[username]
            print(f"User removed: {username}")


async def main():
    print("Starting server on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())