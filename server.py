import asyncio
import json
import websockets

from auth import hash_password, verify_password
from storage import add_user, get_user

connected_users = {}


async def handler(websocket):
    username = None
    print("New connection opened")

    try:
        raw_message = await websocket.recv()
        data = json.loads(raw_message)

        msg_type = data.get("type")
        username = data.get("username")
        password = data.get("password")

        if msg_type not in ("register", "login") or not username or not password:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "First message must be register/login with username and password"
            }))
            return

        if msg_type == "register":
            try:
                password_hash = hash_password(password)
                add_user(username, password_hash)
            except ValueError as e:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
                return

            print(f"User registered: {username}")

        elif msg_type == "login":
            user = get_user(username)

            if not user:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "User does not exist"
                }))
                return

            if not verify_password(password, user["password_hash"]):
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid password"
                }))
                return

            print(f"User logged in: {username}")

        if username in connected_users:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "User already connected"
            }))
            return

        connected_users[username] = {
            "websocket": websocket,
            "public_key": None
        }

        await websocket.send(json.dumps({
            "type": f"{msg_type}_ok",
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