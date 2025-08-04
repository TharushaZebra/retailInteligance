import asyncio
import websockets
import json
from datetime import datetime

PASSWORD = "zebra2025"  # Set your password here

# Load your events
with open('events.json') as f:
    events = json.load(f)

LOG_FILE = "client_logs.txt"

def log_event(message: str):
    timestamp = datetime.utcnow().isoformat() + "Z"
    with open(LOG_FILE, "a") as logf:
        logf.write(f"[{timestamp}] {message}\n")

async def stream_events(websocket):
    client = websocket.remote_address
    log_event(f"Client connected: {client}")
    # Wait for the client to send the password as the first message
    received = await websocket.recv()
    if received != PASSWORD:
        log_event(f"Client {client} failed authentication.")
        await websocket.send(json.dumps({"error": "Invalid password"}))
        await websocket.close()
        return

    log_event(f"Client {client} authenticated successfully.")
    # If password is correct, start streaming events
    for event in events:
        await websocket.send(json.dumps(event))
        log_event(f"Sent event to {client}: {json.dumps(event)}")
        try:
            prediction = await asyncio.wait_for(websocket.recv(), timeout=10)
            log_event(f"Received prediction from {client}: {prediction}")
        except asyncio.TimeoutError:
            log_event(f"No prediction received from {client} for event: {json.dumps(event)} (timeout)")
            await websocket.close()
            return
        await asyncio.sleep(1)
    log_event(f"Finished streaming to {client}. Closing connection.")
    await websocket.close()

async def main():
    async with websockets.serve(stream_events, "0.0.0.0", 8765):
        print("WebSocket server started on ws://localhost:8765 (password protected)")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())