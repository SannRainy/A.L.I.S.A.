import logging
import os
import socket
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat_router
from api import admin_router
from api import feature_router
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown logic untuk FastAPI."""
    # STARTUP
    logger.info("🚀 Memulai TVJP API Server...")

    # Cek & Preload LLM (Llama.cpp) jika default provider bukan cloud
    try:
        from services.llm_agent import get_active_model_path, get_llama_model_async
        active_path = await get_active_model_path()
        if not active_path.startswith("hf_cloud:"):
            logger.info("Mengecek dan Preload Llama.cpp (Local LLM)...")
            model_path = settings.UNSLOTH_MODEL_PATH
            if os.path.exists(model_path):
                logger.info(f"✅ Model file ditemukan di '{model_path}'. Melakukan preloading ke VRAM...")
                await get_llama_model_async()
            else:
                logger.warning(f"⚠️ Model file TIDAK ditemukan di '{model_path}'. Cek UNSLOTH_MODEL_PATH di .env!")
        else:
            logger.info("Default provider adalah Cloud (HF). Melewati preloading Local LLM.")
    except Exception as e:
        logger.error(f"❌ Gagal mengecek konfigurasi LLM: {e}")

    # Cek koneksi Neo4j
    logger.info("Mengecek koneksi ke Neo4j...")
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        driver.verify_connectivity()
        driver.close()
        logger.info("✅ API terhubung dengan Neo4j.")
    except Exception as e:
        logger.warning(f"⚠️ Neo4j tidak tersedia. Knowledge Graph dinonaktifkan. Detail: {e}")

    # Cek kredensial Supabase
    logger.info(f"Supabase URL: '{settings.SUPABASE_URL}'")
    if settings.SUPABASE_URL:
        try:
            domain = settings.SUPABASE_URL.replace("https://", "").replace("http://", "").split("/")[0]
            ip = socket.gethostbyname(domain)
            logger.info(f"✅ DNS resolved: {domain} → {ip}")
        except Exception as dns_err:
            logger.error(f"❌ DNS error untuk {settings.SUPABASE_URL}: {dns_err}")

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.warning("⚠️ Kredensial Supabase belum lengkap. Auth & Quest berjalan dalam mode Mock.")

    # Pre-warm Neo4j & LLM di background agar server langsung siap
    try:
        from services.warmup_service import run_warmup
        from api.chat_router import graph as _graph_instance
        asyncio.create_task(run_warmup(_graph_instance))
        logger.info("🔄 Warmup task dijadwalkan di background.")
    except Exception as e:
        logger.warning(f"⚠️ Gagal menjadwalkan warmup task: {e}")

    yield  # Server berjalan

    # SHUTDOWN
    logger.info("👋 Shutting down TVJP API Server...")


app = FastAPI(title="TVJP - Japanese Virtual Tutor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Upgrade", "Connection"],
)

app.include_router(chat_router.router, prefix="/api/v1")
app.include_router(admin_router.router, prefix="/api/v1")
app.include_router(feature_router.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to TVJP API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)