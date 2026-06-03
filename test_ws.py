import asyncio
import websockets
import json
import time

async def test_chat():
    uri = "ws://127.0.0.1:8000/api/v1/ws/chat"
    print(f"Connecting to {uri}...")
    
    start_time = time.time()
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Simulate "hallo" in Voice Mode (speaking)
            payload = {
                "query": "hallo",
                "student_id": "test_user_123",
                "mode": "speaking",
                "history": []
            }
            
            print(f"Sending payload: {payload}")
            await websocket.send(json.dumps(payload))
            
            first_token_time = None
            full_text = ""
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data["type"] == "status":
                    print(f"[{time.time() - start_time:.2f}s] Status: {data['content']}")
                elif data["type"] == "metadata":
                    print(f"[{time.time() - start_time:.2f}s] Metadata received")
                elif data["type"] == "sentence":
                    if first_token_time is None:
                        first_token_time = time.time()
                        print(f"[{first_token_time - start_time:.2f}s] Time-To-First-Token!")
                    
                    content = data.get("content", "")
                    full_text += content
                    audio_present = "YES" if data.get("audio_b64") else "NO"
                    safe_content = content.encode("utf-8", "replace").decode("utf-8")
                    print(f"-> {safe_content} (Audio: {audio_present})".encode("cp1252", errors="replace").decode("cp1252"))
                elif data["type"] == "done":
                    print(f"[{time.time() - start_time:.2f}s] STREAM FINISHED")
                    print("--- FINAL TEXT ---")
                    print(full_text)
                    break
                elif data["type"] == "error":
                    print(f"ERROR: {data['content']}")
                    break
                    
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
