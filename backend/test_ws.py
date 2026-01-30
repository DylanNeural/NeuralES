import asyncio, json
import websockets

async def main():
    uri = "ws://127.0.0.1:8000/eeg/stream"
    async with websockets.connect(uri) as ws:
        msg = await ws.recv()
        data = json.loads(msg)
        print("OK keys:", list(data.keys()))
        print("channels:", data.get("channels"))
        print("fatigue:", data.get("fatigue"))
        print("chunk shape:", len(data["samples"]), "x", len(data["samples"][0]))

asyncio.run(main())
