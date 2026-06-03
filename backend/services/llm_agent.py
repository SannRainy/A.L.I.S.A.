import os
# Force disable HuggingFace Hub offline mode for Cloud Inference API
os.environ.pop("HF_HUB_OFFLINE", None)
os.environ.pop("TRANSFORMERS_OFFLINE", None)
os.environ.pop("HF_DATASETS_OFFLINE", None)


import json
import asyncio
import logging
import re
import base64
from functools import lru_cache
from typing import AsyncGenerator

from llama_cpp import Llama

from core.config import settings
from services.voice_service import VoiceService
from services.supabase_service import SupabaseService
from logic.db_orchestrator import DBOrchestrator

logger = logging.getLogger(__name__)

# ── Local (Llama.cpp) state ───────────────────────────────────────────
_llama_model: Llama | None = None
_active_model_path: str = settings.UNSLOTH_MODEL_PATH
_model_lock = asyncio.Lock()
_init_lock = asyncio.Lock()

# ── Cloud (HuggingFace) state ─────────────────────────────────────────
# Provider: "local" | "hf_cloud"
_active_provider: str = "local"
_hf_token: str = settings.HF_TOKEN
_hf_model_repo: str = settings.HF_MODEL_REPO

HF_CLOUD_MODEL_ID = "hf_cloud:" + settings.HF_MODEL_REPO  # sentinel ID utk UI

async def get_active_model_path() -> str:
    global _active_model_path, _active_provider, _hf_model_repo
    if _active_provider == "hf_cloud":
        return HF_CLOUD_MODEL_ID
    return _active_model_path

async def get_llama_model_async() -> Llama:
    global _llama_model, _active_model_path
    if _llama_model is None:
        async with _init_lock:
            if _llama_model is None:
                logger.info(f"Memuat model dari {_active_model_path}...")
                _llama_model = await asyncio.to_thread(
                    Llama,
                    model_path   = _active_model_path,
                    n_gpu_layers = 32,
                    n_ctx        = 2048,
                    n_batch      = 512,
                    verbose      = False,
                )
                logger.info(f"Model Llama.cpp dimuat dari {_active_model_path}.")
    return _llama_model

async def switch_model_async(model_filename: str) -> None:
    """Ganti model aktif. Jika model_filename == HF_CLOUD_MODEL_ID, switch ke HF Cloud."""
    global _llama_model, _active_model_path, _active_provider

    # ── Switch ke HuggingFace Cloud ──────────────────────────────────
    if model_filename == HF_CLOUD_MODEL_ID or model_filename.startswith("hf_cloud:"):
        async with _init_lock:
            async with _model_lock:
                if _llama_model is not None:
                    logger.info("Unloading local model sebelum beralih ke HF Cloud...")
                    try:
                        if hasattr(_llama_model, "close"):
                            _llama_model.close()
                    except Exception as e:
                        logger.warning(f"Gagal menutup model: {e}")
                    del _llama_model
                    _llama_model = None
                    import gc; gc.collect()
                _active_provider = "hf_cloud"
                logger.info(f"Provider beralih ke HF Cloud: {_hf_model_repo}")
        return

    # ── Switch ke model lokal (.gguf) ────────────────────────────────
    base_name = os.path.basename(model_filename)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate_path = os.path.join(backend_dir, "models", base_name)

    if not os.path.exists(candidate_path):
        candidate_path = os.path.join("models", base_name)
        if not os.path.exists(candidate_path):
            raise FileNotFoundError(f"Model file {base_name} tidak ditemukan di folder models/.")

    logger.info(f"Mengalihkan model ke: {candidate_path}")

    async with _init_lock:
        async with _model_lock:
            if _llama_model is not None:
                logger.info("Menonaktifkan dan mengeluarkan (unloading) model aktif saat ini...")
                try:
                    if hasattr(_llama_model, "close"):
                        _llama_model.close()
                except Exception as e:
                    logger.warning(f"Gagal menutup model: {e}")
                del _llama_model
                _llama_model = None

                import gc
                gc.collect()
                logger.info("Model sebelumnya berhasil dilepas dari memori.")

            _active_provider = "local"
            _active_model_path = candidate_path
            logger.info(f"Memuat model baru ke memori: {_active_model_path}...")

            _llama_model = await asyncio.to_thread(
                Llama,
                model_path   = _active_model_path,
                n_gpu_layers = 32,
                n_ctx        = 2048,
                n_batch      = 512,
                verbose      = False,
            )
            logger.info("Model baru berhasil dimuat.")


async def test_hf_cloud_connection() -> dict:
    """
    Test koneksi ke HuggingFace Inference API.
    Returns dict: {ok: bool, latency_ms: int, model: str, error: str|None}
    """
    import time
    try:
        from huggingface_hub import InferenceClient
        import huggingface_hub.constants
        huggingface_hub.constants.HF_HUB_OFFLINE = False
    except ImportError:
        return {"ok": False, "latency_ms": 0, "model": _hf_model_repo,
                "error": "huggingface_hub tidak ter-install. Jalankan: pip install huggingface_hub"}

    try:
        t0 = time.monotonic()
        client = InferenceClient(model=_hf_model_repo, token=_hf_token)
        # Kirim pesan minimal untuk test latency
        response = await asyncio.to_thread(
            client.chat_completion,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
            stream=False,
        )
        latency_ms = int((time.monotonic() - t0) * 1000)
        reply = response.choices[0].message.content if response.choices else ""
        return {"ok": True, "latency_ms": latency_ms, "model": _hf_model_repo,
                "reply_sample": reply, "error": None}
    except Exception as e:
        return {"ok": False, "latency_ms": 0, "model": _hf_model_repo, "error": str(e)}


async def _stream_hf_cloud(messages: list[dict], max_tokens: int = 512, mode: str = "discovery") -> AsyncGenerator[str, None]:
    """
    Stream response dari HuggingFace Inference API (text-generation via InferenceClient).
    Yield token-token sebagai string secara streaming (low latency).
    Mode 'voice'/'speaking' menggunakan temperature lebih rendah untuk kepatuhan format.
    """
    try:
        from huggingface_hub import InferenceClient
        import huggingface_hub.constants
        huggingface_hub.constants.HF_HUB_OFFLINE = False
    except ImportError:
        yield "[ERROR] huggingface_hub tidak ter-install."
        return

    # Temperature disesuaikan per mode:
    # - voice/speaking: ketat (0.3) agar format JP/ROM/ID terjaga
    # - discovery/quest: sedang (0.5) agar lebih konsisten dari sebelumnya (0.7)
    if mode in ("voice", "speaking"):
        temperature = 0.3
        top_p = 0.85
    else:
        temperature = 0.5
        top_p = 0.9

    try:
        client = InferenceClient(model=_hf_model_repo, token=_hf_token)

        def get_stream():
            return client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                stream=True,
                temperature=temperature,
                top_p=top_p,
            )

        stream = await asyncio.to_thread(get_stream)
        loop = asyncio.get_running_loop()

        def _next():
            try:
                return next(stream)
            except StopIteration:
                return None

        while True:
            chunk = await loop.run_in_executor(None, _next)
            if chunk is None:
                break
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta

    except Exception as e:
        logger.error(f"HF Cloud stream error: {e}")
        yield f"[ERROR] {e}"



_JP_RE      = re.compile(r"[\u3000-\u9FFF\uFF00-\uFFEF]+")
_NUMBER_RE  = re.compile(r"\b(\d+)\b")
_WORD_RE    = re.compile(r"[^\s\-「」。、？！,.!?\"'()「」【】（）]+")
_PHRASE_END = re.compile(r'([,.!?。！？、]|\n)\s*$')
_DATA_BLOCK = re.compile(r'\|\|\|DATA(.*?)DATA\|\|\|', re.DOTALL)

_LISTING_PATTERNS = [
    (re.compile(r"(sebutkan|berikan|kasih|tampilkan|list|tunjukkan|minta|ajari|ajarkan|jelaskan|mau|ingin).{0,30}(kanji|huruf|karakter|漢字)", re.I), "list_kanji"),
    (re.compile(r"(sebutkan|berikan|kasih|tampilkan|list|tunjukkan|minta|ajari|ajarkan|jelaskan|mau|ingin).{0,30}(kosakata|vocab|kata|kotoba|言葉)", re.I), "list_vocab"),
    (re.compile(r"(sebutkan|berikan|kasih|tampilkan|list|tunjukkan|minta|ajari|ajarkan|jelaskan|mau|ingin).{0,30}(tata\s*bahasa|grammar|bunpou|文法|pola\s*kalimat)", re.I), "list_grammar"),
    (re.compile(r"(contoh|daftar|belajar).{0,30}(kanji|huruf|karakter|漢字)", re.I), "list_kanji"),
    (re.compile(r"(contoh|daftar|belajar).{0,30}(kosakata|vocab|kata|kotoba|言葉)", re.I), "list_vocab"),
    (re.compile(r"(contoh|daftar|belajar).{0,30}(tata\s*bahasa|grammar|bunpou|文法|pola\s*kalimat)", re.I), "list_grammar"),
    (re.compile(r"^(kanji|huruf|karakter)$", re.I), "list_kanji"),
    (re.compile(r"^(kosakata|vocab|kata)$", re.I), "list_vocab"),
    (re.compile(r"^(tata\s*bahasa|grammar|bunpou)$", re.I), "list_grammar"),
]

def _detect_listing_intent(query: str, history: list) -> dict | None:
    for pat, intent in _LISTING_PATTERNS:
        if pat.search(query):
            nums = _NUMBER_RE.findall(query)
            return {"intent": intent, "limit": min(int(nums[0]) if nums else 3, 10)}

    if re.search(r"\b(lagi|lainnya|tambah|lanjut|berikutnya)\b", query, re.I) and history:
        for h in reversed(history):
            if h.get("role") == "user":
                for pat, intent in _LISTING_PATTERNS:
                    if pat.search(h.get("content", "")):
                        nums = _NUMBER_RE.findall(query) or _NUMBER_RE.findall(h.get("content", ""))
                        return {"intent": intent, "limit": min(int(nums[0]) if nums else 3, 10)}
                break
    return None

@lru_cache(maxsize=1)
def _get_kw_model():
    try:
        from keybert import KeyBERT
        from sentence_transformers import SentenceTransformer
        return KeyBERT(model=SentenceTransformer("paraphrase-MiniLM-L3-v2"))
    except Exception:
        return None

def _tokenize(text: str) -> list[str]:
    jp_tokens = [m.group().strip() for m in _JP_RE.finditer(text) if m.group().strip()]
    latin_text = _JP_RE.sub(" ", text).strip()
    latin_tokens: list[str] = []
    kw = _get_kw_model()
    if kw and latin_text:
        try:
            kws = kw.extract_keywords(latin_text, top_n=5, keyphrase_ngram_range=(1, 2), stop_words=None, use_mmr=True, diversity=0.5)
            latin_tokens = [k for k, s in kws if s >= 0.2]
        except Exception:
            pass
    if not latin_tokens and latin_text:
        seen: set = set()
        for m in _WORD_RE.finditer(latin_text):
            w = m.group().strip()
            if len(w) >= 2 and not w.isdigit() and w not in seen:
                seen.add(w)
                latin_tokens.append(w)

    seen2: set = set()
    result = []
    for t in latin_tokens + jp_tokens:
        if t not in seen2:
            seen2.add(t)
            result.append(t)
    return result

_MAX_KG_CHARS   = 1800
_MAX_HIST_CHARS = 200

_SYSTEM_BASE = """\
Kamu adalah Alisa, tutor Bahasa Jepang virtual yang hangat dan suportif bergaya Onee-san.
Gunakan bahasa Indonesia santai (aku/kamu), natural, dan to-the-point.

ATURAN:
1. Jawab dalam bahasa Indonesia. Sisipkan istilah Jepang hanya saat menjelaskan materi.
2. Gunakan HANYA data dari [KONTEKS WIKI NEO4J]. Jika materi tidak ada di konteks, jawab: "Maaf ya, materi itu belum ada di database-ku 🙏"
3. Jawab singkat, maksimal 2 paragraf pendek.
4. Untuk Kanji, jelaskan On'yomi dan Kun'yomi jika tersedia di konteks.
5. Respons harus alami seperti tutor sungguhan, bukan mesin.
6. Untuk contoh kalimat, gunakan format ini (maks 2 contoh):

**Contoh Kalimat:**
「日本語の文」
Romaji: nihongo no bun
Arti: Kalimat bahasa Jepang


"""

_QUEST_FEEDBACK_PROMPT = """\
Kamu adalah Alisa. Evaluasi jawaban siswa dengan gaya Onee-san yang suportif tapi tegas.
Aturan:
1. Sangat ringkas (Maksimal 2 kalimat).
2. Langsung sebutkan letak kesalahan dan berikan jawaban benarnya.
3. Tanpa basa-basi, tanpa blok DATA, tanpa JSON.
"""

_MODE_QUEST     = "\n[MODE: QUEST] Umpan balik instan, koreksi langsung, tanpa penjelasan panjang.\n"
_MODE_VOICE     = "\n[MODE: VOICE] Respon lisan. Super singkat, maksimal 1 kalimat. Abaikan markdown.\n"
_MODE_DISCOVERY = """
[MODE: DISCOVERY]
Beri penjelasan terstruktur sesuai konteks. Langsung ke inti, tanpa basa-basi.
Setiap contoh kalimat harus ada: teks Jepang, romaji, dan artinya (masing-masing baris baru).
Berikan maksimal 2 contoh kalimat.
Pastikan romaji akurat sesuai cara baca huruf Jepang yang benar.
Jika ada baris "Contoh:" di dalam [KONTEKS WIKI NEO4J], WAJIB gunakan kalimat itu — jangan buat contoh sendiri.
Jika tidak ada contoh sama sekali di konteks, tulis: "(Contoh kalimat belum tersedia di database)"
"""

_MODE_SPEAKING = """
[MODE: SPEAKING PRACTICE — Latihan Percakapan Kasual]
Kamu adalah Alisa, teman ngobrol ramah yang membantu user berlatih berbicara bahasa Jepang secara kasual.

BALAS SELALU dalam format PERSIS berikut ini (jangan ubah urutan, jangan tambah teks lain di luar format):
JP: [balasan Alisa dalam bahasa Jepang kasual, 1-2 kalimat pendek]
ROM: [romaji dari JP]
ID: [terjemahan JP dalam bahasa Indonesia]

Aturan tambahan:
- Selalu kasual dan hangat, seperti teman ngobrol
- Balasan singkat (1-2 kalimat)
- Tanpa markdown, tanpa penjelasan materi, tanpa basa-basi
- Jika user bicara bahasa Indonesia, tetap isi USER_JP dengan terjemahan JP-nya
"""


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[dipotong]"


# ──────────────────────────────────────────────────────────────────────────
# KG Accuracy Validation (Hybrid Structured — Method 3)
# ──────────────────────────────────────────────────────────────────────────
_JP_CHAR_RE = re.compile(r'[\u3040-\u9FFF]+')
_GREETING_RE = re.compile(
    r'^\s*(halo|hai|hello|hi|hey|konnichiwa|ohayou|konbanwa|'
    r'selamat\s*(pagi|siang|sore|malam)|apa\s*kabar|genki)',
    re.IGNORECASE
)

def validate_response(ai_text: str, vocab_data: list, grammar_data: list, query: str = "", kanji_data: list = None) -> dict:
    """
    Validate AI response against structured KG data.

    Returns dict with:
      pct          — accuracy percentage (0-100)
      label        — human-readable label
      verified     — # of facts confirmed correct in the response
      total        — total # of facts checked
      category     — 'grounded' | 'casual' | 'no_data'
      facts_detail — list of per-fact verification results for UI popup & debug
    """
    kanji_data = kanji_data or []

    # ── Edge case: casual greeting / chit-chat ──
    if _GREETING_RE.search(query) and not vocab_data and not grammar_data and not kanji_data:
        return {"pct": -1, "label": "💬 Casual Chat", "verified": 0, "total": 0, "category": "casual", "facts_detail": []}

    # ── Edge case: no KG data retrieved ──
    if not vocab_data and not grammar_data and not kanji_data:
        return {"pct": -1, "label": "📭 Data Tidak Tersedia", "verified": 0, "total": 0, "category": "no_data", "facts_detail": []}

    ai_lower = ai_text.lower()
    ai_text_norm = ai_text  # preserve original casing for JP checks

    facts: list[tuple] = []  # (type, subject, *props)

    # ── Extract facts from vocab ──
    for v in vocab_data:
        vid = v.get("id", "")
        romaji = v.get("romaji", "")
        meaning = v.get("indonesian_meaning", "")
        if vid:
            facts.append(("vocab", vid, romaji, meaning))
        # Kanji sub-facts dari vocab
        for k in v.get("kanji", []):
            kid = k.get("id", "")
            if kid:
                facts.append(("kanji", kid, k.get("onyomi", ""), k.get("kunyomi", ""), k.get("arti", "")))

    # ── Extract facts from grammar ──
    for g in grammar_data:
        gname = g.get("name", g.get("id", ""))
        if gname:
            rules = [r for r in g.get("rules", []) if r]
            facts.append(("grammar", gname, g.get("level", ""), "|".join(rules[:2])))

    # ── Extract facts from kanji_data (listing mode) ──
    for k in kanji_data:
        kid = k.get("id", "")
        if kid:
            facts.append(("kanji", kid, k.get("onyomi", ""), k.get("kunyomi", ""), k.get("arti", "")))

    if not facts:
        return {"pct": -1, "label": "💬 Casual Chat", "verified": 0, "total": 0, "category": "casual", "facts_detail": []}

    verified = 0
    mentioned = 0
    facts_detail: list[dict] = []

    for fact in facts:
        ftype   = fact[0]
        subject = fact[1]

        # Cek apakah subjek disebut dalam respons
        subject_found = subject in ai_text_norm or subject.lower() in ai_lower
        if not subject_found:
            continue

        mentioned += 1
        raw_props = [p for p in fact[2:] if p and p.strip()]

        # Flatten prop (ada yg compound "rule1|rule2")
        readable_props: list[str] = []
        for prop in raw_props:
            for sp in (prop.split("|") if "|" in prop else [prop]):
                sp = sp.strip()
                if sp and sp not in readable_props:
                    readable_props.append(sp)

        if not readable_props:
            # Subjek disebut, tidak ada properti → anggap benar
            verified += 1
            facts_detail.append({"type": ftype, "subject": subject, "props": [], "matched_prop": None, "match": True})
            continue

        # Cek konsistensi properti — cari properti pertama yang cocok
        matched_prop: str | None = None
        for prop in raw_props:
            sub_props = prop.split("|") if "|" in prop else [prop]
            for sp in sub_props:
                sp = sp.strip()
                if sp and (sp in ai_text_norm or sp.lower() in ai_lower):
                    matched_prop = sp
                    break
            if matched_prop:
                break

        is_match = matched_prop is not None
        if is_match:
            verified += 1

        facts_detail.append({
            "type":         ftype,
            "subject":      subject,
            "props":        readable_props[:4],   # max 4 prop untuk UI
            "matched_prop": matched_prop,
            "match":        is_match,
        })

    # ── Hitung akurasi ──
    if mentioned == 0:
        return {"pct": -1, "label": "💬 Casual Chat", "verified": 0, "total": 0, "category": "casual", "facts_detail": []}

    pct = round((verified / mentioned) * 100)

    if pct >= 90:
        label = "✅ Sangat Akurat"
    elif pct >= 70:
        label = "🟡 Cukup Akurat"
    elif pct >= 50:
        label = "🟠 Perlu Verifikasi"
    else:
        label = "🔴 Akurasi Rendah"

    return {"pct": pct, "label": label, "verified": verified, "total": mentioned, "category": "grounded", "facts_detail": facts_detail}


def validate_grammar_correction(ai_text: str, grammar_data: list, query: str = "") -> dict:
    """
    Validate the AI-generated grammar correction (KOREKSI: line) against KG grammar data.
    Returns a grammar_check dict:
      category    — 'correct' | 'corrected' | 'kg_verified' | 'kg_unverified'
      correction  — the correction text extracted
      kg_match    — grammar pattern name from KG that matched (or None)
      label       — human-readable label
    """
    # Extract KOREKSI: line
    corr_match = re.search(r'KOREKSI:\s*(.+?)(?:\n|$)', ai_text, re.IGNORECASE)
    correction_text = corr_match.group(1).strip() if corr_match else ""

    # No correction needed
    if not correction_text or correction_text.lower() in ('tidak ada', 'none', '-', 'tidak ada.', 'benar'):
        return {
            "category": "correct",
            "correction": "",
            "kg_match": None,
            "label": "✅ Tata Bahasa Tepat",
        }

    # Has correction — try to match against KG grammar patterns
    corr_lower = correction_text.lower()
    ai_lower   = ai_text.lower()
    kg_match   = None

    for g in grammar_data:
        name = g.get("name", g.get("id", ""))
        if not name:
            continue
        # Check if grammar pattern name or its rules appear in the correction or full AI response
        if name.lower() in corr_lower or name.lower() in ai_lower:
            kg_match = name
            break
        # Check rules
        for rule in g.get("rules", []):
            if rule and len(rule) > 1 and rule.lower() in corr_lower:
                kg_match = name
                break
        if kg_match:
            break

    if kg_match:
        return {
            "category": "kg_verified",
            "correction": correction_text,
            "kg_match": kg_match,
            "label": f"🛡️ Koreksi Terverifikasi KG",
        }
    else:
        return {
            "category": "corrected",
            "correction": correction_text,
            "kg_match": None,
            "label": "✏️ Ada Koreksi Grammar",
        }

class LLMAgent:
    def __init__(self, graph=None):
        self.graph = graph
        self.voice_service = VoiceService()
        _get_kw_model()

    async def _tts(self, text: str) -> str | None:
        try:
            clean = re.sub(r'[*_`#|]', '', text).strip()
            if not clean:
                return None
            clean_upper = clean.upper()
            # Skip non-speech lines — only speak JP: (Alisa's reply)
            if clean_upper.startswith((
                "ROM:", "ROM：", "ID:", "ID：",
                "KOREKSI:", "KOREKSI：",
                "USER_JP:", "USER_ROM:", "USER_ID:"
            )):
                return None
            if clean_upper.startswith(("JP:", "JP：")):
                clean = re.sub(r'^(?i)(JP:|JP：)\s*', '', clean)
            jp_ratio = len("".join(_JP_RE.findall(clean)))
            jp_text  = clean if jp_ratio > len(clean) // 3 else await self.voice_service.translate_to_jp(clean)
            audio    = await self.voice_service.synthesize_speech(jp_text)
            return os.path.basename(audio) if audio else None
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

    async def _tts_bytes(self, text: str) -> bytes | None:
        try:
            clean = re.sub(r'[*_`#|]', '', text).strip()
            if not clean:
                return None
            clean_upper = clean.upper()
            # Skip non-speech lines — only speak JP: (Alisa's reply)
            if clean_upper.startswith((
                "ROM:", "ROM：", "ID:", "ID：",
                "KOREKSI:", "KOREKSI：",
                "USER_JP:", "USER_ROM:", "USER_ID:"
            )):
                return None
            if clean_upper.startswith(("JP:", "JP：")):
                clean = re.sub(r'^(?i)(JP:|JP：)\s*', '', clean)
            jp_ratio = len("".join(_JP_RE.findall(clean)))
            jp_text  = clean if jp_ratio > len(clean) // 3 else await self.voice_service.translate_to_jp(clean)
            audio_path = await self.voice_service.synthesize_speech(jp_text)
            if not audio_path:
                return None
            with open(audio_path, "rb") as f:
                data = f.read()
            try:
                os.remove(audio_path)
            except OSError:
                pass
            return data
        except Exception as e:
            logger.error(f"TTS bytes error: {e}")
            return None

    async def _stream_tokens(self, messages: list[dict], max_tokens: int = 2048, mode: str = "discovery") -> AsyncGenerator[str, None]:
        if _active_provider == "hf_cloud" or mode in ("voice", "speaking"):
            async for token in _stream_hf_cloud(messages, max_tokens=max_tokens, mode=mode):
                yield token
        else:
            model = await get_llama_model_async()
            async with _model_lock:
                stream = await asyncio.to_thread(
                    model.create_chat_completion,
                    messages       = messages,
                    max_tokens     = max_tokens,
                    temperature    = 0.4,
                    top_p          = 0.85,
                    top_k          = 30,
                    repeat_penalty = 1.3,
                    stop           = ["<|im_end|>", "<|eot_id|>"],
                    stream         = True,
                )
                loop = asyncio.get_running_loop()

                def _next():
                    try:
                        return next(stream)
                    except StopIteration:
                        return None

                while True:
                    chunk = await loop.run_in_executor(None, _next)
                    if chunk is None:
                        break
                    text_chunk = chunk["choices"][0].get("delta", {}).get("content", "")
                    if text_chunk:
                        yield text_chunk

    async def _handle_listing(self, intent: str, limit: int) -> tuple[str, list, list, list]:
        vocab_data: list = []
        grammar_data: list = []
        kanji_data: list = []
        try:
            if intent == "list_kanji":
                results = await asyncio.to_thread(self.graph.get_random_kanji, "N5", limit)
                if results:
                    lines = []
                    for r in results:
                        line = f"• **{r.get('id','-')}** | On: {r.get('onyomi','-')} | Kun: {r.get('kunyomi','-')} | Arti: {r.get('arti','-')}"
                        exs = [e for e in r.get("examples", []) if e.get("text")]
                        if exs:
                            line += " | Contoh: " + " / ".join(f"{e['text']} ({e.get('meaning','')})" for e in exs[:2])
                        lines.append(line)
                        kanji_data.append(r)  # ← kumpulkan untuk validasi akurasi
                    return f"[KONTEKS NEO4J — {limit} Kanji N5]\n" + "\n".join(lines), vocab_data, grammar_data, kanji_data
                return "[KONTEKS NEO4J] Data kanji tidak ditemukan.", vocab_data, grammar_data, kanji_data

            if intent == "list_vocab":
                results = await asyncio.to_thread(self.graph.get_random_vocab, "N5", limit)
                if results:
                    lines = []
                    for r in results:
                        line = f"• **{r.get('id','-')}** ({r.get('romaji','-')}) → {r.get('indonesian_meaning','-')}"
                        exs = [e for e in r.get("examples", []) if e.get("text")]
                        if exs:
                            line += " | Contoh: " + " / ".join(e['text'] for e in exs[:2])
                        lines.append(line)
                        vocab_data.append(r)
                    return f"[KONTEKS NEO4J — {limit} Kosakata N5]\n" + "\n".join(lines), vocab_data, grammar_data, kanji_data
                return "[KONTEKS NEO4J] Data kosakata tidak ditemukan.", vocab_data, grammar_data, kanji_data

            if intent == "list_grammar":
                results = await asyncio.to_thread(self.graph.get_random_grammar, "N5", limit)
                if results:
                    lines = []
                    for r in results:
                        rules = " | ".join(r.get("rules", [])) or "Lihat contoh"
                        line = f"• **{r.get('name', r.get('id','-'))}** → {rules}"
                        exs = [e for e in r.get("examples", []) if e.get("text")]
                        if exs:
                            line += " | Contoh: " + " / ".join(e['text'] for e in exs[:2])
                        lines.append(line)
                        grammar_data.append(r)
                    return f"[KONTEKS NEO4J — {limit} Grammar N5]\n" + "\n".join(lines), vocab_data, grammar_data, kanji_data
                return "[KONTEKS NEO4J] Data grammar tidak ditemukan.", vocab_data, grammar_data, kanji_data

        except Exception as e:
            logger.warning(f"[LISTING] gagal: {e}")
        return "[KONTEKS NEO4J] Gagal mengambil data.", vocab_data, grammar_data, kanji_data

    @staticmethod
    def _fmt_vocab(v: dict) -> str:
        head = f"• [{v.get('level','-')}] **{v.get('id','')}**"
        if v.get('romaji'):
            head += f" ({v['romaji']})"
        head += f" → {v.get('indonesian_meaning', '-')}"
        pos_list = [p for p in v.get('pos', []) if p]
        if pos_list:
            head += f" [{', '.join(pos_list)}]"
        lines = [head]
        for k in v.get('kanji', [])[:1]:
            if not k.get('id'):
                continue
            kline = f"  Kanji: **{k['id']}**"
            parts = []
            if k.get('onyomi'):  parts.append(f"On: {k['onyomi']}")
            if k.get('kunyomi'): parts.append(f"Kun: {k['kunyomi']}")
            if k.get('arti'):    parts.append(f"Arti: {k['arti']}")
            if parts:
                kline += " | " + " | ".join(parts)
            lines.append(kline)
        exs = [e for e in v.get('examples', []) if e.get('text')]
        for e in exs[:1]:
            lines.append(f"  → {e['text']} ＝ {e.get('meaning', '')}")
        return "\n".join(lines)

    @staticmethod
    def _fmt_grammar(g: dict) -> str:
        head = f"• [{g.get('level','-')}] **{g.get('name', g.get('id',''))}**"
        lines = [head]
        rules = [r for r in g.get('rules', []) if r]
        if rules:
            lines.append("  Aturan: " + " | ".join(rules[:2]))
        exs = [e for e in g.get('examples', []) if e.get('text')]
        for e in exs[:1]:
            lines.append(f"  → {e['text']} ＝ {e.get('meaning', '')}")
        return "\n".join(lines)

    @staticmethod
    def _fmt_kanji(k: dict) -> str:
        head = f"• [{k.get('level','-')}] **{k.get('id','')}**"
        parts = []
        if k.get('onyomi'):  parts.append(f"On: {k['onyomi']}")
        if k.get('kunyomi'): parts.append(f"Kun: {k['kunyomi']}")
        if k.get('arti'):    parts.append(f"Arti: {k['arti']}")
        if parts:
            head += " | " + " | ".join(parts)
        lines = [head]
        exs = [e for e in k.get('examples', []) if e.get('text')]
        for e in exs[:1]:
            lines.append(f"  → {e['text']} ＝ {e.get('meaning', '')}")
        return "\n".join(lines)

    async def _handle_rag(self, query: str, student_id: str, mode: str = "discovery") -> tuple[str, list, list, list]:
        vocab_data: list = []
        grammar_data: list = []
        kanji_data: list = []
        try:
            tokens = await asyncio.to_thread(_tokenize, query)
            ctx = await self.graph.get_full_context(tokens, student_id)
            
            student_progress = await asyncio.to_thread(self.graph.get_student_progress, student_id)
            mastered_count = student_progress.get("mastered_count", 0) if student_progress else 0

            vocab_data   = ctx.get("vocab", [])
            grammar_data = ctx.get("grammar", [])
            kanji_data   = ctx.get("kanji", [])
            topic        = ctx.get("topic")

            sections: list[str] = [
                f"**Profil Siswa:** Mastered={mastered_count} item",
            ]

            if vocab_data:
                vocab_lines = [self._fmt_vocab(v) for v in vocab_data[:3]]
                sections.append("## Kosakata:\n" + "\n".join(vocab_lines))

            if grammar_data:
                gram_lines = [self._fmt_grammar(g) for g in grammar_data[:2]]
                sections.append("## Grammar:\n" + "\n".join(gram_lines))

            if kanji_data:
                kanji_lines = [self._fmt_kanji(k) for k in kanji_data[:2]]
                sections.append("## Kanji:\n" + "\n".join(kanji_lines))

            if topic:
                sections.append(f"## Topik: {topic.get('name','')} ({topic.get('category','')})")

            if len(sections) > 1:
                raw_ctx = "[KONTEKS WIKI NEO4J]\n" + "\n\n".join(sections)
                return _truncate(raw_ctx, _MAX_KG_CHARS), vocab_data, grammar_data, kanji_data

            if mode in ("speaking", "voice"):
                return "[KONTEKS WIKI NEO4J] KOSONG. Gunakan kosakata N5 dasar.", vocab_data, grammar_data, kanji_data

            return "[KONTEKS WIKI NEO4J] Tidak ada data materi spesifik. Jika user hanya menyapa atau ngobrol santai, balas secara natural dan ramah. Jika user bertanya tentang materi Jepang spesifik (kanji/kosakata/grammar), baru sampaikan bahwa materinya belum ada di database.", vocab_data, grammar_data, kanji_data

        except Exception as e:
            logger.warning(f"[RAG] KG lookup gagal: {e}")
            if mode in ("speaking", "voice"):
                return "[KONTEKS WIKI NEO4J] KOSONG. Gunakan kosakata N5 dasar.", vocab_data, grammar_data, kanji_data
            return "[KONTEKS WIKI NEO4J] Tidak ada data materi spesifik. Jika user hanya menyapa atau ngobrol santai, balas secara natural dan ramah. Jika user bertanya tentang materi Jepang spesifik (kanji/kosakata/grammar), baru sampaikan bahwa materinya belum ada di database.", vocab_data, grammar_data, kanji_data

    async def _build_kg_context(self, query: str, student_id: str, history: list, mode: str = "discovery") -> tuple[str, list, list, list]:
        if not self.graph:
            if mode in ("speaking", "voice"):
                return "[KONTEKS NEO4J] KOSONG. Gunakan kosakata N5 dasar.", [], [], []
            return "[KONTEKS NEO4J] Tidak ada data materi spesifik. Jika user hanya menyapa atau ngobrol santai, balas secara natural dan ramah. Jika user bertanya tentang materi Jepang spesifik (kanji/kosakata/grammar), baru sampaikan bahwa materinya belum ada di database.", [], [], []

        listing = _detect_listing_intent(query, history)
        if listing:
            return await self._handle_listing(listing["intent"], listing["limit"])
        return await self._handle_rag(query, student_id, mode)

    def _build_messages(self, kg_context: str, history: list, query: str, mode: str) -> list[dict]:
        if mode == "quest":
            system_content = _SYSTEM_BASE + _MODE_QUEST
        elif mode == "voice":
            system_content = _MODE_VOICE
        elif mode == "speaking":
            system_content = _MODE_SPEAKING
        else:
            system_content = _SYSTEM_BASE + _MODE_DISCOVERY

        messages: list[dict] = [{"role": "system", "content": system_content}]

        if kg_context:
            messages.append({"role": "system", "content": kg_context})

        # Speaking mode needs more history for conversational context (6 turns)
        hist_limit = 6 if mode == "speaking" else 3
        for h in history[-hist_limit:]:
            role = "assistant" if h.get("role") in ("tutor", "assistant") else "user"
            messages.append({"role": role, "content": h.get("content", "")[:_MAX_HIST_CHARS]})

        messages.append({"role": "user", "content": query[:500]})
        return messages

    async def get_speaking_topic(self, student_id: str) -> dict:
        """Ambil topik percakapan dari KG yang sesuai level user untuk seed awal."""
        topic_suggestions = [
            {"topic": "Perkenalan Diri",    "starter_id": "はじめまして。わたしはアリサです。あなたのなまえはなんですか？",
             "starter_rom": "Hajimemashite. Watashi wa Arisa desu. Anata no namae wa nan desu ka?",
             "starter_id_": "Senang bertemu. Saya Alisa. Siapa namamu?",
             "vocab_hint": ["namae", "watashi", "hajimemashite"]},
            {"topic": "Kegiatan Sehari-hari", "starter_id": "まいにち なにを しますか？",
             "starter_rom": "Mainichi nani o shimasu ka?",
             "starter_id_": "Setiap hari kamu ngapain?",
             "vocab_hint": ["mainichi", "shimasu", "nani"]},
            {"topic": "Makanan & Minuman",  "starter_id": "すきなたべものはなんですか？",
             "starter_rom": "Suki na tabemono wa nan desu ka?",
             "starter_id_": "Makanan kesukaanmu apa?",
             "vocab_hint": ["tabemono", "suki", "nani"]},
            {"topic": "Waktu & Jadwal",     "starter_id": "いまなんじですか？",
             "starter_rom": "Ima nan-ji desu ka?",
             "starter_id_": "Sekarang jam berapa?",
             "vocab_hint": ["ima", "nan-ji", "desu"]},
            {"topic": "Tempat & Arah",      "starter_id": "えきはどこですか？",
             "starter_rom": "Eki wa doko desu ka?",
             "starter_id_": "Di mana stasiunnya?",
             "vocab_hint": ["eki", "doko", "wa"]},
        ]
        import random
        return random.choice(topic_suggestions)


    async def stream_response(
        self,
        query: str,
        student_id: str = "default_user",
        history: list[dict] = None,
        mode: str = "discovery",
    ) -> AsyncGenerator[str, None]:

        if not history and student_id != "default_user":
            history = await SupabaseService.get_chat_history(student_id)
        if history is None:
            history = []

        if student_id != "default_user":
            asyncio.create_task(SupabaseService.save_chat_log(student_id, "user", query, mode))

        if mode == "speaking":
            kg_context, vocab_data, grammar_data, kanji_data = "", [], [], []
        else:
            kg_context, vocab_data, grammar_data, kanji_data = await self._build_kg_context(query, student_id, history, mode)

        yield f"data: {json.dumps({'type': 'status', 'content': 'Alisa sedang menganalisis materi...'})}\n\n"
        yield f"data: {json.dumps({'type': 'metadata', 'vocab': vocab_data, 'grammar': grammar_data, 'suggestions': []})}\n\n"

        messages = self._build_messages(kg_context, history, query, mode)

        full_content = ""
        sentence_buf = ""

        try:
            emitted_text = ""

            async for text_chunk in self._stream_tokens(messages, max_tokens=2048, mode=mode):
                if not text_chunk:
                    continue

                full_content += text_chunk

                visible_content = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL)
                visible_content = re.sub(r'<think>.*', '', visible_content, flags=re.DOTALL)
                visible_content = re.sub(r'\|\|\|DATA.*', '', visible_content, flags=re.DOTALL)

                new_text = visible_content[len(emitted_text):]

                if new_text:
                    sentence_buf += new_text
                    emitted_text += new_text

                    stripped_buf = sentence_buf.strip()
                    should_flush = (
                        _PHRASE_END.search(sentence_buf)
                        or ("\n" in sentence_buf)
                        or (len(stripped_buf) >= 30)
                    )
                    if should_flush:
                        af = await self._tts(sentence_buf)
                        yield f"data: {json.dumps({'type': 'sentence', 'content': sentence_buf, 'audio': af})}\n\n"
                        sentence_buf = ""

            if sentence_buf:
                af = await self._tts(sentence_buf)
                yield f"data: {json.dumps({'type': 'sentence', 'content': sentence_buf, 'audio': af})}\n\n"

            m = _DATA_BLOCK.search(full_content)
            if m:
                asyncio.create_task(self._process_db_updates(student_id, m.group(1).strip()))

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'chunk', 'content': '⚠️ Alisa sedang pusing merapikan Wiki, coba lagi sebentar ya! 🙏'})}\n\n"

        if student_id != "default_user" and full_content:
            visible_final = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()
            visible_final = re.sub(r'\|\|\|DATA.*?DATA\|\|\|', '', visible_final, flags=re.DOTALL).strip()
            await SupabaseService.save_chat_log(student_id, "assistant", visible_final, mode)

        accuracy = validate_response(full_content, vocab_data, grammar_data, query, kanji_data)
        yield f"data: {json.dumps({'type': 'done', 'accuracy': accuracy})}\n\n"

    async def stream_response_ws(
        self,
        query: str,
        student_id: str = "default_user",
        history: list[dict] = None,
        mode: str = "discovery",
    ) -> AsyncGenerator[dict, None]:
        if not history and student_id != "default_user":
            history = await SupabaseService.get_chat_history(student_id)
        if history is None:
            history = []

        if student_id != "default_user":
            asyncio.create_task(
                SupabaseService.save_chat_log(student_id, "user", query, mode)
            )

        if mode == "speaking":
            # For speaking mode: fetch grammar context from KG so correction can be validated
            if self.graph:
                try:
                    tokens = await asyncio.to_thread(_tokenize, query)
                    ctx = await self.graph.get_full_context(tokens, student_id)
                    grammar_data = ctx.get("grammar", [])
                    vocab_data   = ctx.get("vocab", [])
                    kanji_data   = ctx.get("kanji", [])
                except Exception as e:
                    logger.debug(f"[Speaking KG lookup] {e}")
                    grammar_data, vocab_data, kanji_data = [], [], []
            else:
                grammar_data, vocab_data, kanji_data = [], [], []
            kg_context = ""  # Still don't inject KG context into prompt — keep conversation natural

            try:
                user_trans = await self.voice_service.translate_and_romaji_user(query)
            except Exception as e:
                logger.error(f"[Speaking Manual Translate] failed: {e}")
                user_trans = {"jp": query, "rom": "", "id": query}
        else:
            kg_context, vocab_data, grammar_data, kanji_data = await self._build_kg_context(
                query, student_id, history, mode
            )
            user_trans = None

        yield {"type": "status", "content": "Alisa sedang menganalisis materi..."}
        yield {"type": "metadata", "vocab": vocab_data, "grammar": grammar_data, "suggestions": []}

        if user_trans:
            yield {
                "type": "user_translation",
                "jp": user_trans["jp"],
                "rom": user_trans["rom"],
                "id": user_trans["id"]
            }

        query_for_llm = user_trans["jp"] if (mode == "speaking" and user_trans) else query
        messages = self._build_messages(kg_context, history, query_for_llm, mode)

        audio_tasks_queue: asyncio.Queue[asyncio.Task | None] = asyncio.Queue(maxsize=20)
        output_queue: asyncio.Queue[dict | None] = asyncio.Queue()

        full_content = ""

        async def _tts_worker(sentence: str):
            audio_bytes = await self._tts_bytes(sentence)
            audio_b64 = base64.b64encode(audio_bytes).decode() if audio_bytes else None
            return {
                "type": "sentence",
                "content": sentence,
                "audio_b64": audio_b64,
            }

        async def _order_consumer():
            while True:
                task = await audio_tasks_queue.get()
                if task is None:
                    await output_queue.put(None)
                    break
                result = await task
                await output_queue.put(result)

        async def _llm_producer():
            nonlocal full_content
            sentence_buf = ""
            emitted_text = ""
            try:
                async for text_chunk in self._stream_tokens(messages, max_tokens=2048, mode=mode):
                    if not text_chunk:
                        continue

                    full_content += text_chunk

                    visible = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL)
                    visible = re.sub(r'<think>.*', '', visible, flags=re.DOTALL)
                    visible = re.sub(r'\|\|\|DATA.*', '', visible, flags=re.DOTALL)

                    new_text = visible[len(emitted_text):]
                    if not new_text:
                        continue

                    sentence_buf += new_text
                    emitted_text += new_text

                    while '\n' in sentence_buf:
                        line, sentence_buf = sentence_buf.split('\n', 1)
                        line_with_nl = line + '\n'
                        task = asyncio.create_task(_tts_worker(line_with_nl))
                        await audio_tasks_queue.put(task)

                    stripped = sentence_buf.strip()
                    should_flush = (
                        _PHRASE_END.search(sentence_buf)
                        or (len(stripped) >= 60 and ' ' in stripped)
                    )
                    if should_flush:
                        # Potong di batas kata terakhir agar tidak terpotong di tengah kata
                        if len(stripped) >= 60 and ' ' in stripped and not _PHRASE_END.search(sentence_buf):
                            last_space = sentence_buf.rfind(' ')
                            if last_space > 0:
                                to_flush = sentence_buf[:last_space + 1]
                                sentence_buf = sentence_buf[last_space + 1:]
                            else:
                                to_flush = sentence_buf
                                sentence_buf = ""
                        else:
                            to_flush = sentence_buf
                            sentence_buf = ""
                        task = asyncio.create_task(_tts_worker(to_flush))
                        await audio_tasks_queue.put(task)

                if sentence_buf:
                    task = asyncio.create_task(_tts_worker(sentence_buf))
                    await audio_tasks_queue.put(task)

            except Exception as e:
                logger.error(f"[WS] LLM producer error: {e}")
            finally:
                await audio_tasks_queue.put(None)

        producer_task = asyncio.create_task(_llm_producer())
        consumer_task = asyncio.create_task(_order_consumer())

        while True:
            event = await output_queue.get()
            if event is None:
                break
            yield event

        await asyncio.gather(producer_task, consumer_task)

        m = _DATA_BLOCK.search(full_content)
        if m:
            asyncio.create_task(
                self._process_db_updates(student_id, m.group(1).strip())
            )

        if student_id != "default_user" and full_content:
            visible_final = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()
            visible_final = re.sub(r'\|\|\|DATA.*?DATA\|\|\|', '', visible_final, flags=re.DOTALL).strip()
            await SupabaseService.save_chat_log(student_id, "assistant", visible_final, mode)

        if mode == "speaking":
            grammar_check = validate_grammar_correction(full_content, grammar_data, query)
            yield {"type": "done", "grammar_check": grammar_check}
        else:
            accuracy = validate_response(full_content, vocab_data, grammar_data, query, kanji_data)
            yield {"type": "done", "accuracy": accuracy}

    async def _process_db_updates(self, student_id: str, data_str: str):
        try:
            await asyncio.sleep(0.5)
            updates = json.loads(data_str).get("database_updates", {})
            await DBOrchestrator(self.graph).process_sync_event(student_id, updates)
            logger.info(f"DB update ok for {student_id}")
        except Exception as e:
            logger.error(f"DB update gagal: {e} | raw: {data_str}")

    async def generate_quest_json(self, student_id: str, level: str = "N5") -> dict:
        prompt = (
            f"Buat 10 soal Bahasa Jepang level {level} dalam JSON murni.\n"
            "Format:\n"
            "{\"questions\":[{\"id\":1,\"type\":\"mcq\",\"question\":\"...\",\"options\":[\"A\",\"B\",\"C\",\"D\"],\"correct\":0,\"explanation\":\"...\"}]}\n"
            "Soal 1-6 tipe mcq, soal 7-10 tipe fill (tanpa options, tambahkan \"correct\":\"<jawaban>\").\n"
            "HANYA cetak JSON, tanpa teks lain."
        )
        try:
            model = await get_llama_model_async()
            async with _model_lock:
                resp  = await asyncio.to_thread(
                    model.create_chat_completion,
                    messages    = [{"role": "user", "content": prompt}],
                    max_tokens  = 1024,
                    temperature = 0.3,
                    stop        = ["<|im_end|>", "<|eot_id|>"],
                )
            content = resp["choices"][0]["message"]["content"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Quest gen error: {e}")

        return {"questions": [
            {"id": 1, "type": "mcq", "question": "Kanji untuk 'Api'?", "options": ["水","火","木","金"], "correct": 1, "explanation": "火 (hi) = Api"},
            {"id": 2, "type": "mcq", "question": "Arti 'Arigatou'?", "options": ["Selamat tinggal","Maaf","Terima kasih","Permisi"], "correct": 2, "explanation": "Arigatou = Terima kasih"},
            {"id": 3, "type": "mcq", "question": "Partikel penanda subjek?", "options": ["を","に","は","で"], "correct": 2, "explanation": "は (wa) = penanda topik/subjek"},
            {"id": 4, "type": "mcq", "question": "Angka 3 dalam bahasa Jepang?", "options": ["Ichi","Ni","San","Yon"], "correct": 2, "explanation": "San (三) = 3"},
            {"id": 5, "type": "mcq", "question": "Arti 'Sensei'?", "options": ["Murid","Sekolah","Guru","Kelas"], "correct": 2, "explanation": "先生 = Guru"},
            {"id": 6, "type": "mcq", "question": "Kanji untuk 'Air'?", "options": ["火","木","水","金"], "correct": 2, "explanation": "水 (mizu) = Air"},
            {"id": 7, "type": "fill", "question": "Romaji dari 'か'?", "correct": "ka", "explanation": "か = ka"},
            {"id": 8, "type": "fill", "question": "Partikel tempat: Gakkou ___ benkyou shimasu.", "correct": "de", "explanation": "で = partikel tempat aktivitas"},
            {"id": 9, "type": "fill", "question": "Romaji dari 'す'?", "correct": "su", "explanation": "す = su"},
            {"id": 10, "type": "fill", "question": "'Saya' dalam bahasa Jepang (romaji)?", "correct": "watashi", "explanation": "私 = watashi"},
        ]}

    async def get_correction_feedback(self, question: str, user_answer: str, correct_answer: str) -> dict:
        prompt = (
            f"Pertanyaan: {question}\n"
            f"Jawaban Siswa: {user_answer}\n"
            f"Jawaban Benar: {correct_answer}\n\n"
            "Tolong jelaskan singkat dan ramah ya!"
        )
        try:
            # ── HuggingFace Cloud provider ────────────────────────────────
            if _active_provider == "hf_cloud":
                from huggingface_hub import InferenceClient
                client = InferenceClient(model=_hf_model_repo, token=_hf_token)
                messages = [
                    {"role": "system", "content": _QUEST_FEEDBACK_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                def run_chat():
                    return client.chat_completion(
                        messages=messages,
                        max_tokens=256,
                    )
                resp = await asyncio.to_thread(run_chat)
                feedback = resp.choices[0].message.content if resp.choices else ""
                return {"feedback": feedback, "audio_url": None}

            # ── Local Llama.cpp provider ──────────────────────────────────
            model = await get_llama_model_async()
            async with _model_lock:
                resp = await asyncio.to_thread(
                    model.create_chat_completion,
                    messages    = [{"role": "system", "content": _QUEST_FEEDBACK_PROMPT}, {"role": "user", "content": prompt}],
                    max_tokens  = 256,
                    temperature = 0.5,
                    stop        = ["<|im_end|>", "<|eot_id|>"],
                )
            feedback = resp["choices"][0]["message"]["content"]
            return {"feedback": feedback, "audio_url": None}
        except Exception as e:
            logger.error(f"Feedback error: {e}")
            return {"feedback": f"Maaf, gagal membuat feedback: {e}", "audio_url": None}

    async def stream_pure_response(
        self,
        query: str,
        history: list[dict] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Pure Chat Completion (CCP Mode) - murni streaming respon model
        tanpa Neo4j RAG, tanpa DB logging, tanpa TTS.
        Mendukung provider: local (Llama.cpp) dan hf_cloud (HuggingFace Inference API).
        """
        messages = [
            {"role": "system", "content": "Kamu adalah Alisa, tutor Bahasa Jepang virtual yang ramah. Jawab pertanyaan user dengan ringkas dan jelas."}
        ]
        if history:
            for h in history:
                role = "assistant" if h.get("role") in ("tutor", "assistant") else "user"
                messages.append({"role": role, "content": h.get("content", "")})
        messages.append({"role": "user", "content": query})

        try:
            async for token in self._stream_tokens(messages, max_tokens=1024):
                if token:
                    yield f"data: {json.dumps({'content': token})}\n\n"
        except Exception as e:
            logger.error(f"Pure stream error: {e}")
            yield f"data: {json.dumps({'content': f'⚠️ Error: {str(e)}'})}\n\n"