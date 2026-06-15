"""
generate_static_responses.py
─────────────────────────────
Generate file WAV statis dari Style-Bert-VITS2 untuk response yang
sudah diketahui teksnya (mis. quiz redirect guard).

WAV disimpan di backend/temp/ dengan nama khusus `static_*.wav` agar
tidak ikut terhapus oleh cleanup rutinitas VoiceService.

Cara pakai:
    python backend/utils/generate_static_responses.py

Atau dipanggil otomatis oleh warmup_service.run_warmup() saat startup.
"""

import os
import sys
import time
import httpx
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Tentukan path output ───────────────────────────────────────────────────
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))   # backend/utils/
_BACKEND_DIR = os.path.dirname(_SCRIPT_DIR)                  # backend/
_TEMP_DIR    = os.path.join(_BACKEND_DIR, "temp")
_TTS_URL     = "http://127.0.0.1:5050/voice"

# ── Definisi static responses ─────────────────────────────────────────────
# Format: { "filename": "static_xxx.wav", "jp_text": "Teks Jepang untuk TTS" }
# Teks JP dipilih agar natural diucapkan Alisa (hindari emoji, markdown, dll.)
STATIC_RESPONSES = [
    {
        "name": "quiz_redirect",
        "filename": "static_quiz_redirect.wav",
        "jp_text": (
            "あ、クイズがやりたいんですね！"
            "クイズや練習問題はQuestモードでできますよ。"
            "こちらのDiscoveryモードでは、語彙や漢字、文法を一緒に勉強しましょう。"
            "何を勉強したいですか？"
        ),
    },
]

# ── Parameter TTS (sama persis dengan voice_service.py) ──────────────────
_TTS_PARAMS_BASE = {
    "model_id":       0,
    "speaker_id":     0,
    "sdp_ratio":      0.4,
    "noise":          0.6,
    "noisew":         0.9,
    "length":         1.1,
    "language":       "JP",
    "auto_split":     "true",
    "split_interval": 0.5,
    "style":          "Neutral",
    "style_weight":   0.5,
}


def generate_wav(jp_text: str, out_path: str, timeout: float = 90.0) -> bool:
    """Kirim teks ke TTS server dan simpan hasilnya sebagai WAV. Return True jika berhasil."""
    params = {**_TTS_PARAMS_BASE, "text": jp_text}
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(_TTS_URL, params=params)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(resp.content)
            size_kb = len(resp.content) // 1024
            logger.info(f"✅ WAV generated: {os.path.basename(out_path)} ({size_kb} KB)")
            return True
        else:
            logger.error(f"❌ TTS server error {resp.status_code} untuk: {jp_text[:40]}...")
            return False
    except Exception as e:
        logger.error(f"❌ Gagal hubungi TTS server ({_TTS_URL}): {type(e).__name__}: {e}")
        logger.error("   Pastikan Style-Bert-VITS2 sudah berjalan di port 5050.")
        return False


def main(force: bool = False) -> dict[str, bool]:
    """
    Generate semua static WAV. Lewati file yang sudah ada kecuali force=True.
    Return dict: { name: success_bool }
    """
    os.makedirs(_TEMP_DIR, exist_ok=True)
    results = {}

    for resp in STATIC_RESPONSES:
        out_path = os.path.join(_TEMP_DIR, resp["filename"])
        name     = resp["name"]

        if not force and os.path.exists(out_path):
            size_kb = os.path.getsize(out_path) // 1024
            logger.info(f"⏭️  Skip '{name}' — sudah ada ({size_kb} KB): {resp['filename']}")
            results[name] = True
            continue

        logger.info(f"🎙️  Generating '{name}': {resp['jp_text'][:50]}...")
        t0 = time.monotonic()
        ok = generate_wav(resp["jp_text"], out_path)
        ms = int((time.monotonic() - t0) * 1000)

        if ok:
            logger.info(f"   ⏱️  Selesai dalam {ms} ms")
        results[name] = ok

    return results


if __name__ == "__main__":
    force = "--force" in sys.argv
    if force:
        logger.info("🔁 Mode --force: semua WAV akan di-generate ulang.")

    results = main(force=force)

    ok_count   = sum(1 for v in results.values() if v)
    fail_count = sum(1 for v in results.values() if not v)

    logger.info(f"\n{'='*50}")
    logger.info(f"Selesai: {ok_count} berhasil, {fail_count} gagal.")
    if fail_count:
        logger.warning("Jalankan ulang setelah Style-Bert-VITS2 server menyala.")
        sys.exit(1)
