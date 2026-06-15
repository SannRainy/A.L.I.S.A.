"""
download_whisper.py
───────────────────
Script satu kali untuk men-download model Kotoba-Whisper v1.0 (faster-whisper)
ke folder lokal `backend/models/kotoba-whisper-v1.0-faster/`.

Setelah dijalankan, VoiceService akan load dari path lokal — tidak butuh
internet/HF Hub saat startup atau warmup.

Cara pakai (dari root project TVJP/):
    python backend/utils/download_whisper.py

Atau dari dalam folder backend/:
    python utils/download_whisper.py
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    # ── Tentukan path tujuan download ──────────────────────────────────────
    script_dir   = os.path.dirname(os.path.abspath(__file__))   # backend/utils/
    backend_dir  = os.path.dirname(script_dir)                   # backend/
    models_dir   = os.path.join(backend_dir, "models")
    target_path  = os.path.join(models_dir, "kotoba-whisper-v1.0-faster")
    hf_model_id  = "kotoba-tech/kotoba-whisper-v1.0-faster"

    os.makedirs(target_path, exist_ok=True)

    # ── Cek apakah sudah didownload ────────────────────────────────────────
    # faster-whisper menyimpan model sebagai file .bin / .ggml + config.json
    existing = os.listdir(target_path)
    if any(f.endswith((".bin", ".ggml", "config.json")) for f in existing):
        logger.info(f"✅ Model sudah ada di '{target_path}'. Tidak perlu download ulang.")
        logger.info(f"   File: {existing}")
        return

    logger.info(f"📥 Men-download '{hf_model_id}' ke '{target_path}'...")
    logger.info("   Ukuran: ~1.5 GB (float16). Pastikan koneksi stabil.")

    # ── Download via huggingface_hub snapshot_download ──────────────────────
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        logger.error("❌ huggingface_hub tidak terinstall. Jalankan: pip install huggingface_hub")
        sys.exit(1)

    try:
        # Cek apakah perlu token HF
        hf_token = os.environ.get("HF_TOKEN") or _try_get_token_from_env()

        downloaded_path = snapshot_download(
            repo_id        = hf_model_id,
            repo_type      = "model",
            local_dir      = target_path,
            token          = hf_token or None,
            ignore_patterns= ["*.msgpack", "*.h5", "flax_model*", "tf_model*"],
        )
        logger.info(f"✅ Download selesai! Model tersimpan di: {downloaded_path}")
        logger.info("")
        logger.info("💡 Sekarang VoiceService akan otomatis load dari path lokal saat startup.")
        logger.info(f"   Path: {target_path}")

    except Exception as e:
        logger.error(f"❌ Gagal download: {e}")
        logger.error("   Coba manual: huggingface-cli download kotoba-tech/kotoba-whisper-v1.0-faster")
        sys.exit(1)


def _try_get_token_from_env() -> str:
    """Coba baca HF_TOKEN dari .env file backend jika tersedia."""
    try:
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
        )
        if not os.path.exists(env_path):
            return ""
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("HF_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if token:
                        logger.info("🔑 Menggunakan HF_TOKEN dari .env")
                    return token
    except Exception:
        pass
    return ""


if __name__ == "__main__":
    main()
