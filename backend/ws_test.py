import asyncio
import json
import time
import websockets

async def main():
    uri = "ws://localhost:8000/api/v1/orchestrator/stream"
    payload = {"user_id":"tester","input_text":"Generate an Instagram post about AI","input_type":"text"}

    # Retry connect for a short window while server starts
    for attempt in range(20):
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps(payload))
                print("Connected and sent payload")
                try:
                    async for message in ws:
                        print("RECV:", message)
                except websockets.exceptions.ConnectionClosedOK:
                    print("Connection closed by server (OK)")
                return
        except Exception as e:
            print(f"Connect attempt {attempt+1} failed: {e}")
            time.sleep(0.5)
    print("Failed to connect after retries")

if __name__ == '__main__':
    asyncio.run(main())
