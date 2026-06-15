"""
warmup_service.py
─────────────────
Startup warm-up otomatis untuk menghilangkan cold-start latency:

  1. Neo4j warm-up  — query dummy sederhana agar connection pool aktif
                      dan Neo4j JIT (query plan cache) sudah siap.

  2. LLM warm-up    — kirim prompt 1-token ke model (local Llama.cpp atau
                      HF Cloud) agar:
                        • Bobot sudah di-load ke VRAM (local)
                        • KV-cache alokasi pertama sudah selesai
                        • HTTP connection ke HF API sudah established (cloud)

Dipanggil sebagai asyncio background task dari lifespan() di main.py
sehingga server langsung siap menerima request — warmup berjalan paralel.
"""

import asyncio
import logging
import time

logger = logging.getLogger(__name__)

# ── Pesan dummy untuk LLM warm-up ─────────────────────────────────────────
_WARMUP_SYSTEM = "Kamu adalah Alisa, tutor Bahasa Jepang."
_WARMUP_USER   = "Halo"   # prompt minimal, 1 kata
_WARMUP_TTS_TEXT = "こんにちは"


async def _warmup_tts() -> None:
    """
    Warm-up Style-Bert-VITS2 TTS server (proses eksternal di port 5050).

    Server SBVITS2 lazy-load model ke VRAM saat request pertama tiba.
    Dengan mengirim request dummy sini, model sudah di VRAM sebelum
    user pertama pakai Voice/Speaking mode.
    """
    try:
        import httpx
        t0 = time.monotonic()

        params = {
            "text":         _WARMUP_TTS_TEXT,
            "model_id":     0,
            "speaker_id":   0,
            "sdp_ratio":    0.4,
            "noise":        0.6,
            "noisew":       0.9,
            "length":       1.1,
            "language":     "JP",
            "auto_split":   "true",
            "split_interval": 0.5,
            "style":        "Neutral",
            "style_weight": 0.5,
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post("http://127.0.0.1:5050/voice", params=params)

        ms = int((time.monotonic() - t0) * 1000)
        if response.status_code == 200:
            logger.info(f"🔥 [Warmup] TTS (Style-Bert-VITS2) OK — {ms} ms")
        else:
            logger.warning(f"⚠️ [Warmup] TTS server response {response.status_code} — {ms} ms")
    except Exception as e:
        # TTS server mungkin belum nyala (optional feature) — bukan fatal error
        logger.warning(f"⚠️ [Warmup] TTS tidak tersedia (Style-Bert-VITS2 belum jalan?): {type(e).__name__}")


async def _warmup_whisper() -> None:
    """
    Pre-load Kotoba-Whisper model ke GPU VRAM dari path LOKAL.

    Hanya berjalan jika model sudah didownload ke models/kotoba-whisper-v1.0-faster/.
    Jika belum, skip warmup dan tampilkan instruksi download.
    Ini mencegah warmup memicu download HF Hub yang bisa sangat lama.
    """
    try:
        import os
        from core.config import settings

        # Tentukan path lokal model
        backend_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )  # backend/services/ → backend/
        local_path = os.path.join(backend_dir, settings.WHISPER_MODEL_PATH)

        # Skip jika model lokal belum ada — jangan trigger HF download saat warmup
        if not os.path.isdir(local_path) or not any(
            f.endswith((".bin", ".ggml", "config.json"))
            for f in os.listdir(local_path)
            if os.path.isdir(local_path)
        ):
            logger.warning(
                f"⚠️ [Warmup] Whisper SKIP — model lokal belum ada di '{local_path}'. "
                f"Download dulu dengan: python backend/utils/download_whisper.py"
            )
            return

        from services.voice_service import VoiceService

        t0 = time.monotonic()
        vs = VoiceService()
        await asyncio.to_thread(vs._load_whisper)
        ms = int((time.monotonic() - t0) * 1000)
        logger.info(f"🔥 [Warmup] Whisper STT loaded dari lokal ke GPU — {ms} ms")
    except Exception as e:
        logger.warning(f"⚠️ [Warmup] Whisper gagal di-load: {e}")



async def _warmup_neo4j(graph) -> None:
    """
    Jalankan beberapa query ringan ke Neo4j agar:
      - Connection pool terpakai (tidak lazy-init saat user pertama)
      - Query plan cache Neo4j sudah ter-compile untuk pola umum
    """
    t0 = time.monotonic()
    try:
        # Query 1: ambil 1 vocab acak (query paling sering dipakai RAG)
        await asyncio.to_thread(graph.get_random_vocab, "N5", 1)

        # Query 2: ambil 1 grammar acak (query kedua paling sering)
        await asyncio.to_thread(graph.get_random_grammar, "N5", 1)

        # Query 3: get_full_context dengan token dummy agar pipeline RAG
        #          (exact match → fuzzy search) ter-warm
        await graph.get_full_context(["食べる", "です"], student_id="__warmup__")

        ms = int((time.monotonic() - t0) * 1000)
        logger.info(f"🔥 [Warmup] Neo4j OK — {ms} ms")
    except Exception as e:
        logger.warning(f"⚠️ [Warmup] Neo4j gagal (akan retry oleh driver): {e}")


async def _warmup_llm_local() -> None:
    """Warm-up Llama.cpp local — force first inference agar KV-cache siap."""
    try:
        from services.llm_agent import get_llama_model_async, _model_lock

        t0 = time.monotonic()
        model = await get_llama_model_async()

        messages = [
            {"role": "system",  "content": _WARMUP_SYSTEM},
            {"role": "user",    "content": _WARMUP_USER},
        ]

        async with _model_lock:
            await asyncio.to_thread(
                model.create_chat_completion,
                messages    = messages,
                max_tokens  = 1,      # hanya butuh 1 token — minimise waktu
                temperature = 0.1,
                stream      = False,
            )

        ms = int((time.monotonic() - t0) * 1000)
        logger.info(f"🔥 [Warmup] LLM Local OK — {ms} ms (first-token latency reference)")
    except Exception as e:
        logger.warning(f"⚠️ [Warmup] LLM Local gagal: {e}")


async def _warmup_llm_cloud() -> None:
    """Warm-up HuggingFace Inference API — establish HTTP connection + first-token."""
    try:
        from services.llm_agent import _hf_model_repo, _hf_token
        from huggingface_hub import InferenceClient
        import huggingface_hub.constants
        huggingface_hub.constants.HF_HUB_OFFLINE = False

        t0 = time.monotonic()
        client = InferenceClient(model=_hf_model_repo, token=_hf_token)

        messages = [
            {"role": "system", "content": _WARMUP_SYSTEM},
            {"role": "user",   "content": _WARMUP_USER},
        ]

        kwargs: dict = {
            "messages":   messages,
            "max_tokens": 1,
            "stream":     False,
            "temperature": 0.1,
        }

        # Matikan thinking mode untuk Qwen3 agar warmup cepat
        if "qwen3" in _hf_model_repo.lower():
            kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}

        await asyncio.to_thread(client.chat_completion, **kwargs)

        ms = int((time.monotonic() - t0) * 1000)
        logger.info(f"🔥 [Warmup] LLM HF Cloud OK — {ms} ms")
    except Exception as e:
        logger.warning(f"⚠️ [Warmup] LLM HF Cloud gagal: {e}")


async def _warmup_llm() -> None:
    """Pilih warmup LLM berdasarkan provider yang aktif."""
    try:
        from services.llm_agent import _active_provider
        if _active_provider == "hf_cloud":
            await _warmup_llm_cloud()
        else:
            await _warmup_llm_local()
    except Exception as e:
        logger.warning(f"⚠️ [Warmup] LLM provider check gagal: {e}")


async def _generate_static_wavs() -> None:
    """Generate static WAV files using generate_static_responses module."""
    try:
        from utils import generate_static_responses
        t0 = time.monotonic()
        results = await asyncio.to_thread(generate_static_responses.main, False)
        ms = int((time.monotonic() - t0) * 1000)
        ok_count = sum(1 for v in results.values() if v)
        fail_count = sum(1 for v in results.values() if not v)
        if fail_count > 0:
            logger.warning(f"⚠️ [Warmup] Generate static responses selesai dengan {fail_count} kegagalan — {ms} ms")
        else:
            logger.info(f"🔥 [Warmup] Generate static responses OK ({ok_count} file) — {ms} ms")
    except Exception as e:
        logger.warning(f"⚠️ [Warmup] Gagal generate static responses: {e}")


async def run_warmup(graph=None) -> None:
    """
    Entry point utama dipanggil dari lifespan() di main.py.

    Urutan warmup (semua paralel):
      ┌─ Neo4j   ─ query dummy → connection pool + query plan JIT
      ├─ LLM     ─ 1-token inference → KV-cache alloc + GPU init
      ├─ TTS     ─ HTTP こんにちは → Style-Bert-VITS2 load model ke VRAM
      ├─ Whisper ─ model load ke GPU VRAM (tanpa audio dummy)
      └─ Static  ─ generate static WAV responses (seperti quiz_redirect)

    Total waktu = max(t_neo4j, t_llm, t_tts, t_whisper, t_static) bukan jumlahnya.
    """
    logger.info("🔄 [Warmup] Memulai pre-warm Neo4j, LLM, TTS, Whisper & Static WAV di background...")
    t_start = time.monotonic()

    tasks = []
    if graph is not None:
        tasks.append(_warmup_neo4j(graph))
    tasks.append(_warmup_llm())
    tasks.append(_warmup_tts())
    tasks.append(_warmup_whisper())
    tasks.append(_generate_static_wavs())

    # Jalankan semua paralel — exception per task sudah di-handle di dalam masing-masing
    await asyncio.gather(*tasks, return_exceptions=True)

    total_ms = int((time.monotonic() - t_start) * 1000)
    logger.info(
        f"✅ [Warmup] Selesai dalam {total_ms} ms. "
        f"Response pertama user tidak akan kena cold-start! 🚀"
    )
