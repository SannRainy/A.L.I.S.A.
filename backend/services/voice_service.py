import os
import time
import logging
import httpx
import asyncio
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

# Timeout for TTS requests. Model inference can be slow, especially on first GPU load.
_TTS_TIMEOUT_SECONDS = 120.0
# Number of retries if TTS server is still warming up
_TTS_MAX_RETRIES = 3
_TTS_RETRY_DELAY = 3.0

# Maksimal umur file temp (dalam detik) sebelum dianggap expired
_TEMP_MAX_AGE_SECONDS = 3600  # 1 jam


class VoiceService:
    def __init__(self):
        # FIX: OpenMP duplicate runtime initialization on Windows
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

        # FIX: Whisper membutuhkan ffmpeg di system PATH. 
        # Kita inject executable dari imageio_ffmpeg ke system PATH secara dinamis.
        try:
            import imageio_ffmpeg
            ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
            if ffmpeg_dir not in os.environ["PATH"]:
                os.environ["PATH"] += os.pathsep + ffmpeg_dir
                logger.info(f"Injecting embedded ffmpeg path: {ffmpeg_dir}")
        except ImportError:
            logger.warning("imageio-ffmpeg tidak ada. Jika gagal jalan, pastikan ffmpeg terinstall di OS.")

        self.whisper_model = None
        # Lazy load whisper behavior can be implemented if it takes too much memory during startup
        self.temp_dir = Path(os.getcwd()) / "backend" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.tts_url = "http://127.0.0.1:5050/voice" # Diperbarui ke 5050 sesuai config.yml Style-Bert-VITS2

        # Bersihkan sisa file temp lama dari session sebelumnya saat startup
        self._cleanup_stale_files()

    def _cleanup_stale_files(self):
        """Hapus file .wav yang sudah terlalu lama di temp dir saat startup."""
        now = time.time()
        cleaned = 0
        try:
            for f in self.temp_dir.glob("response_*.wav"):
                if (now - f.stat().st_mtime) > _TEMP_MAX_AGE_SECONDS:
                    f.unlink(missing_ok=True)
                    cleaned += 1
            if cleaned:
                logger.info(f"[VoiceService] Cleaned up {cleaned} stale temp files.")
        except Exception as e:
            logger.warning(f"[VoiceService] Error during temp cleanup: {e}")

    def _load_whisper(self):
        if self.whisper_model is None:
            from faster_whisper import WhisperModel
            logger.info("Membuka model Kotoba-Whisper v1.0 (faster) pada GPU dengan compute_type='float16'...")
            # Load Kotoba-Whisper model on GPU with float16 compute_type for better precision
            self.whisper_model = WhisperModel(
                "kotoba-tech/kotoba-whisper-v1.0-faster",
                device="cuda",
                compute_type="float16"
            )
        return self.whisper_model

    async def transcribe_audio(self, file_path: str, mode: str = None) -> str:
        """Mengubah audio dari user menjadi teks (STT) menggunakan Kotoba-Whisper."""
        try:
            # Gunakan asyncio.to_thread karena model load bersifat blocking
            model = await asyncio.to_thread(self._load_whisper)

            # FIX: Selalu paksa bahasa Jepang dan berikan initial_prompt tanpa bergantung pada nilai `mode`
            transcribe_opts = {
                "language": "ja",
                "beam_size": 5, # Meningkatkan akurasi pencarian token kata Jepang
                "initial_prompt": (
                    "日本語の会話です。ひらがな、カタカナ、漢字。"
                    "こんにちは、お元気ですか、ありがとうございます、すみません、天気がいいですね。"
                )
            }
            logger.info(f"[Whisper STT] Transcribing file with strict Japanese settings (mode passed: {mode})")

            # Jalankan transkripsi dan iterasi segmen di thread terpisah agar tidak memblock event loop
            def run_transcription():
                segments, info = model.transcribe(
                    file_path, 
                    **transcribe_opts,
                    vad_filter=True, # Aktifkan VAD bawaan faster-whisper untuk membuang keheningan/noise
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                return list(segments), info

            segments_list, info = await asyncio.to_thread(run_transcription)
            text = "".join([segment.text for segment in segments_list]).strip()
            detected_lang = info.language
            logger.info(f"[Whisper STT] Input dikenali (mode={mode}, lang={detected_lang}): {text}")
            return text
        except Exception as e:
            logger.error(f"[Whisper STT] Gagal transcribe: {e}")
            return ""

    async def translate_to_jp(self, text: str) -> str:
        """Menerjemahkan balasan AI (Bhs Indonesia) ke Jepang untuk diucapkan TTS."""
        # Jika teks sudah bahasa Jepang (AI membalas romaji/kana), kita bisa skip penerjemahan
        # Tapi asumsi mode Voice AI membalas B. Indonesia campuran, kita perbaiki dgn deep-translator
        try:
            from deep_translator import GoogleTranslator
            # Kita hanya terjemahkan jika perlu. Jika LLM sudah diajar dengan strict untuk reply JP,
            # mungkin tidak perlu translator (langsung feed ke TTS).
            # Sesuai blueprint: Deep Translation mengubah respon AI menjadi JP natural untuk TTS.
            translator = GoogleTranslator(source='id', target='ja')
            jp_text = await asyncio.to_thread(translator.translate, text)
            logger.info(f"[Translate] Hasil terjemahan untuk TTS: {jp_text}")
            return jp_text
        except Exception as e:
            logger.error(f"[Translate] Gagal translate: {e}")
            return text # fallback

    async def translate_and_romaji_user(self, query: str) -> dict:
        """
        Manually translates user query and converts it to romaji.
        Returns a dict: {"jp": str, "rom": str, "id": str}
        """
        if not query or not query.strip():
            return {"jp": "", "rom": "", "id": ""}

        import re
        is_jp = bool(re.search(r'[\u3040-\u30ff\u4e00-\u9fff\u3400-\u4dbf]', query))
        
        from deep_translator import GoogleTranslator
        
        jp_text = ""
        id_text = ""
        
        try:
            if is_jp:
                jp_text = query
                translator = GoogleTranslator(source='ja', target='id')
                id_text = await asyncio.to_thread(translator.translate, query)
            else:
                id_text = query
                translator = GoogleTranslator(source='id', target='ja')
                jp_text = await asyncio.to_thread(translator.translate, query)
        except Exception as e:
            logger.error(f"[ManualTranslate] Failed to translate: {e}")
            jp_text = jp_text or query
            id_text = id_text or query

        # Convert JP to Romaji using pykakasi
        romaji_text = ""
        try:
            import pykakasi
            kks = pykakasi.kakasi()
            result = kks.convert(jp_text)
            romaji_text = " ".join([item['hepburn'] for item in result]).capitalize().strip()
            romaji_text = re.sub(r'\s+([.,!?;:])', r'\1', romaji_text)
        except Exception as e:
            logger.error(f"[ManualTranslate] Kakasi romaji conversion failed: {e}")
            romaji_text = jp_text

        return {
            "jp": jp_text.strip(),
            "rom": romaji_text.strip(),
            "id": id_text.strip()
        }

    async def synthesize_speech(self, text: str) -> str | None:
        """Mengirim teks JP ke Style-Bert-VITS2 dan mengembalikan path file audio."""
        if not text or not text.strip():
            return None

        # Check if the text contains Japanese characters (Hiragana, Katakana, Kanji)
        # to avoid sending English/Indonesian/abbreviations to Style-Bert-VITS2 which crashes it.
        import re
        if not re.search(r'[\u3040-\u30ff\u4e00-\u9fff\u3400-\u4dbf]', text):
            logger.warning(f"[TTS] Skip synthesis: text has no Japanese characters: {text!r}")
            return None

        # Parameter TTS sesuai spesifikasi Style-Bert-VITS2 untuk model Alisa_Voice
        params = {
            "text": text,
            "model_id": 0,
            "speaker_id": 0,
            "sdp_ratio": 0.4,
            "noise": 0.6,
            "noisew": 0.9,
            "length": 1.1,
            "language": "JP",
            "auto_split": "true",
            "split_interval": 0.5,
            "style": "Neutral",
            "style_weight": 0.5
        }

        last_error: Exception | None = None
        for attempt in range(1, _TTS_MAX_RETRIES + 1):
            try:
                # Timeout diperbesar ke 120s karena GPU inference bisa lambat di percobaan pertama
                # khususnya saat model baru saja di-load ke VRAM.
                async with httpx.AsyncClient(timeout=_TTS_TIMEOUT_SECONDS) as client:
                    response = await client.post(self.tts_url, params=params)

                if response.status_code == 200:
                    unique_id = uuid.uuid4().hex[:8]
                    output_filename = f"response_{int(time.time())}_{unique_id}.wav"
                    output_path = self.temp_dir / output_filename
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"[TTS] Audio berhasil disintesis: {output_filename}")
                    return str(output_path)
                else:
                    logger.error(f"[TTS] Gagal synthesis. Status: {response.status_code}")
                    return None

            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadError) as e:
                last_error = e
                logger.warning(
                    f"[TTS] Attempt {attempt}/{_TTS_MAX_RETRIES} gagal ({type(e).__name__}). "
                    f"{'Retrying...' if attempt < _TTS_MAX_RETRIES else 'Menyerah — TTS tidak tersedia.'}"
                )
                if attempt < _TTS_MAX_RETRIES:
                    await asyncio.sleep(_TTS_RETRY_DELAY)

            except Exception as e:
                logger.warning(f"[TTS] Error tak terduga: {type(e).__name__}: {e}")
                return None

        logger.error(f"[TTS] Semua {_TTS_MAX_RETRIES} percobaan gagal. Error terakhir: {last_error}")
        return None
