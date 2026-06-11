import logging
import os
import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat_router
from api import admin_router
from api import feature_router
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Lifespan: menggantikan @app.on_event("startup") yang deprecated ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown logic untuk FastAPI."""
    # ── STARTUP ──────────────────────────────────────────────────────────
    logger.info("🚀 Memulai TVJP API Server...")

    # Cek & Preload LLM (Llama.cpp)
    logger.info("Mengecek dan Preload Llama.cpp (Local LLM)...")
    try:
        from services.llm_agent import get_llama_model_async
        model_path = settings.UNSLOTH_MODEL_PATH
        if os.path.exists(model_path):
            logger.info(f"✅ Model file ditemukan di '{model_path}'. Melakukan preloading ke VRAM...")
            await get_llama_model_async()  # Memaksa model diload saat startup
        else:
            logger.warning(f"⚠️ WARNING: Model file TIDAK ditemukan di '{model_path}'. Cek UNSLOTH_MODEL_PATH di .env atau config.py!")
    except Exception as e:
        logger.error(f"❌ ERROR: Gagal mengecek konfigurasi LLM! Detail: {e}")

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
        logger.info("✅ SUCCESS: API terhubung dengan Neo4j!")
    except Exception as e:
        logger.warning(f"⚠️ WARNING: Neo4j tidak tersedia. Knowledge Graph akan dinonaktifkan. Detail: {e}")

    # Cek kredensial Supabase
    logger.info(f"DEBUG: SUPABASE_URL diatur ke: '{settings.SUPABASE_URL}'")
    
    # DNS Check untuk Supabase URL
    if settings.SUPABASE_URL:
        try:
            domain = settings.SUPABASE_URL.replace("https://", "").replace("http://", "").split("/")[0]
            ip = socket.gethostbyname(domain)
            logger.info(f"✅ DNS SUCCESS: {domain} terurai ke {ip}")
        except Exception as dns_err:
            logger.error(f"❌ DNS ERROR: Gagal mengurai {settings.SUPABASE_URL}. Detail: {dns_err}")
            logger.warning("Saran: Jalankan 'ipconfig /flushdns' atau ganti DNS ke 8.8.8.8")

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.warning("⚠️ WARNING: Kredensial Supabase belum lengkap. Fitur Auth & Quest akan berjalan dalam mode Simulasi (Mock).")
    
    yield  # Server berjalan

    # ── SHUTDOWN ─────────────────────────────────────────────────────────
    logger.info("👋 Shutting down TVJP API Server...")


app = FastAPI(title="TVJP - Japanese Virtual Tutor API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
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
    # Menjalankan server FastAPI (Pastikan reload=False agar VRAM aman)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)