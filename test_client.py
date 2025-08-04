
import asyncio
import websockets

async def test_client():
    uri = "ws://192.168.8.144:8765"
    password = input("Enter password: ")
    async with websockets.connect(uri) as websocket:
        await websocket.send(password)
        try:
            while True:
                message = await websocket.recv()
                print("Received:", message)
                # Send a dummy prediction back (replace with model output as needed)
                prediction = "decode"  # or "no-decode" or your model's output
                await websocket.send(prediction)
        except websockets.ConnectionClosed:
            print("Connection closed.")

asyncio.run(test_client())