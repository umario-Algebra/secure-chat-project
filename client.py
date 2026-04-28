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


async def receive_messages(websocket, private_key, last_seen_counters, username, control_queue):
    while True:
        try:
            incoming_raw = await websocket.recv()
            print(f"\n{username} received raw: {incoming_raw}")

            incoming = json.loads(incoming_raw)
            msg_type = incoming.get("type")

            if msg_type == "chat":
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

            elif msg_type in ("public_key_result", "error", "public_key_ok", "register_ok", "login_ok"):
                await control_queue.put(incoming)

            else:
                print(f"{username} received other message: {incoming}")

        except websockets.exceptions.ConnectionClosed:
            print(f"{username} connection closed while receiving")
            break


async def interactive_sender_loop(
    websocket,
    private_key,
    public_key_b64,
    username,
    control_queue,
):
    send_counters = {}

    print(f"{username} is in interactive mode.")
    print("Commands:")
    print("  /msg <recipient> <message>")
    print("  /quit")

    while True:
        user_input = await asyncio.to_thread(input, f"{username}> ")
        text = user_input.strip()

        if not text:
            continue

        if text.lower() == "/quit":
            print(f"{username} exiting chat")
            break

        if not text.startswith("/msg "):
            print("Invalid command. Use: /msg <recipient> <message>")
            continue

        parts = text.split(" ", 2)
        if len(parts) < 3:
            print("Invalid command. Use: /msg <recipient> <message>")
            continue

        recipient = parts[1].strip()
        message_text = parts[2].strip()

        if not recipient or not message_text:
            print("Recipient and message must not be empty")
            continue

        get_key_message = {
            "type": "get_public_key",
            "username": recipient
        }

        await websocket.send(json.dumps(get_key_message))
        print(f"Requested public key for {recipient}")

        reply = await control_queue.get()
        print(f"{username} control message: {reply}")

        if reply.get("type") != "public_key_result":
            print("Could not get recipient public key")
            continue

        recipient_public_key_b64 = reply["key"]
        recipient_public_key = public_key_from_base64(recipient_public_key_b64)
        shared_key = derive_shared_key(private_key, recipient_public_key)

        counter = send_counters.get(recipient, 0) + 1
        send_counters[recipient] = counter

        encrypted_payload = encrypt_message(shared_key, message_text)

        chat_message = {
            "type": "chat",
            "to": recipient,
            "payload": {
                "sender_public_key": public_key_b64,
                "counter": counter,
                "nonce": encrypted_payload["nonce"],
                "ciphertext": encrypted_payload["ciphertext"]
            }
        }

        await websocket.send(json.dumps(chat_message))
        print(f"Encrypted chat message with counter={counter} sent to {recipient}")


async def main():
    uri = "ws://localhost:8765"

    if len(sys.argv) < 4:
        print("Usage: python client.py <register|login> <username> <password>")
        return

    action = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    last_seen_counters = {}
    control_queue = asyncio.Queue()

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

        receive_task = asyncio.create_task(
            receive_messages(
                websocket,
                private_key,
                last_seen_counters,
                username,
                control_queue
            )
        )

        try:
            await interactive_sender_loop(
                websocket,
                private_key,
                public_key_b64,
                username,
                control_queue,
            )
        finally:
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass

        print(f"Client {username} closing connection")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Client stopped")