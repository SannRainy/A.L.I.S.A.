import asyncio
import sys
import os
sys.path.append(os.getcwd())

from core.config import settings
from services.graph_engine import GraphEngine
from services.llm_agent import LLMAgent

async def main():
    try:
        g = GraphEngine()
        agent = LLMAgent(g)
        print("Starting stream...")
        
        # Override _tts_bytes to skip actual TTS synthesis for fast testing
        async def dummy_tts(text):
            return b"dummy_audio"
        agent._tts_bytes = dummy_tts

        async for event in agent.stream_response_ws("bisa ajarin aku bahasa jepangnya laut ?", "test"):
            if event and event.get("type") == "sentence":
                print(f"SENTENCE: {event.get('content')}")
        
        g.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
