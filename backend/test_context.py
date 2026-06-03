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
        print("Graph initialized")
        ctx = await g.get_full_context(["laut", "jepang", "bahasa"], "test")
        
        agent = LLMAgent(g)
        rag_text, _, _ = await agent._build_kg_context("bisa ajarin aku bahasa jepang laut?", "test", [])
        
        print("--- RAG TEXT ---")
        print(rag_text)
        print(f"--- RAG TEXT LENGTH: {len(rag_text)} ---")
        
        g.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
