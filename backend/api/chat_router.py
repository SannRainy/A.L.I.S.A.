from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Any
from services.llm_agent import LLMAgent
from services.voice_service import VoiceService
from services.quest_data import QUEST_LEVELS
from services.supabase_service import SupabaseService
from core.supabase_client import supabase
from core.config import settings
import httpx
import os
import shutil
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# ---------------------------------------------------------------------------
# Try to initialize GraphEngine; if Neo4j is unavailable run without it
# ---------------------------------------------------------------------------
graph = None
try:
    from services.graph_engine import GraphEngine
    graph = GraphEngine()
    logger.info("✅ GraphEngine (Neo4j) initialized successfully.")
except Exception as e:
    logger.warning(f"⚠️ GraphEngine not available, running without Knowledge Graph: {e}")

llm_agent = LLMAgent(graph=graph)
voice_service = VoiceService()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    student_id: Optional[str] = "default"
    history: Optional[List[ChatMessage]] = None  # Fixed: mutable default → None
    mode: Optional[str] = "discovery"

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = "User Baru"
    age: Optional[int] = None
    gender: Optional[str] = "prefer_not_to_say"
    country: Optional[str] = "Indonesia"
    study_purpose: Optional[str] = None
    japanese_level: Optional[str] = "beginner"

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    study_purpose: Optional[str] = None
    japanese_level: Optional[str] = None

class KanjiMasteryRequest(BaseModel):
    student_id: str
    set_id: str
    kanji_ids: List[str]
    score: int
    total: int

class QuestSubmitRequest(BaseModel):
    user_id: str
    level_id: str
    score: int

class VocabCard(BaseModel):
    id: Optional[str] = None
    label: Optional[str] = None
    kana: Optional[str] = None
    romaji: Optional[str] = None
    meaning_en: Optional[str] = None
    meaning_id: Optional[str] = None


class GrammarCard(BaseModel):
    id: Optional[str] = None
    pattern: Optional[str] = None
    structure: Optional[str] = None
    meaning_en: Optional[str] = None
    meaning_id: Optional[str] = None
    usage: Optional[str] = None
    example: Optional[str] = None


class TutorResponse(BaseModel):
    answer: str
    thinking: Optional[str] = None
    vocab: List[Any] = []
    grammar: List[Any] = []
    suggestions: List[str] = []


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("/chat")
async def chat_with_tutor(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong.")

    # Handle None history (fixed mutable default)
    history_data = request.history or []

    return StreamingResponse(
        llm_agent.stream_response(
            query=request.query,
            student_id=request.student_id or "default",
            history=[{"role": m.role, "content": m.content} for m in history_data],
            mode=request.mode or "discovery"
        ),
        media_type="text/event-stream"
    )

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), mode: str = Form(None)):
    """ STT (Whisper) -> Text """
    temp_input_path = voice_service.temp_dir / f"input_{audio.filename}"
    try:
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        logger.info(f"Transcribing audio... (mode={mode})")
        user_text = await voice_service.transcribe_audio(str(temp_input_path), mode=mode)
        if not user_text:
            return {"error": "Maaf, suara tidak terdengar jelas."}
        return {"text": user_text}
    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)


@router.get("/get-audio/{filename}")
async def get_audio_file(filename: str):
    file_path = voice_service.temp_dir / filename
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio file not found")


# ---------------------------------------------------------------------------
# WebSocket chat — low-latency streaming pipeline
# ---------------------------------------------------------------------------
@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming TTS pipeline.

    Client sends JSON:
        {"query": str, "student_id": str, "mode": str, "history": [...]}

    Server sends JSON frames:
        {"type": "status",   "content": str}
        {"type": "metadata", "vocab": [...], "grammar": [...]}
        {"type": "sentence", "content": str, "audio_b64": str|null}
        {"type": "done"}
        {"type": "error",    "content": str}
    """
    await websocket.accept()
    logger.info("[WS] Client connected")
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({"type": "error", "content": "Invalid JSON payload"})
                )
                continue

            query      = payload.get("query", "").strip()
            student_id = payload.get("student_id", "default_user")
            mode       = payload.get("mode", "discovery")
            history    = payload.get("history", [])

            if not query:
                await websocket.send_text(
                    json.dumps({"type": "error", "content": "Query kosong."})
                )
                continue

            logger.info(f"[WS] Query from {student_id}: {query[:80]}")

            try:
                async for event in llm_agent.stream_response_ws(
                    query=query,
                    student_id=student_id,
                    history=history,
                    mode=mode,
                ):
                    await websocket.send_text(json.dumps(event))
            except Exception as e:
                logger.error(f"[WS] Pipeline error: {e}")
                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "content": "⚠️ Alisa sedang pusing, coba lagi sebentar ya! 🙏",
                    })
                )

    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected")
    except Exception as e:
        logger.error(f"[WS] Unexpected error: {e}")

@router.post("/generate-quest")
async def generate_quest(request: ChatRequest):
    """
    LEGACY: Tetap ada agar tidak break, tapi disarankan pakai sistem Level.
    """
    logger.info("Generating AI Quest (Legacy)...")
    data = await llm_agent.generate_quest_json(
        student_id=request.student_id or "default",
        level="N5"
    )
    return data

@router.get("/quest/levels")
async def get_quest_levels():
    """Ambil daftar level quest yang tersedia."""
    # Sembunyikan data questions di level list agar tidak berat
    levels_summary = []
    for lvl in QUEST_LEVELS:
        levels_summary.append({
            "id": lvl["id"],
            "title": lvl["title"],
            "description": lvl["description"],
            "icon": lvl["icon"]
        })
    return levels_summary

@router.get("/quest/data/{level_id}")
async def get_quest_data(level_id: str):
    """Ambil detail soal untuk level tertentu."""
    for lvl in QUEST_LEVELS:
        if lvl["id"] == level_id:
            return lvl
    raise HTTPException(status_code=404, detail="Level tidak ditemukan")

class AiCorrectionRequest(BaseModel):
    student_id: Optional[str] = "default"
    question: str
    user_answer: str
    correct_answer: str
    node_id: Optional[str] = None
    grammar_focus: Optional[str] = None
    question_type: Optional[str] = None
    hint: Optional[str] = None
    options: Optional[List[str]] = None


# Mapping frontend node_id to Neo4j database node IDs
FRONTEND_TO_NEO4J_MAP = {
    # Level 1
    "grammar_wa": "は",
    "grammar_desu": "Akhiran です、 だ",
    "grammar_no": "Partikel  の",
    "grammar_mo": "も",
    "grammar_ka": "か",
    "grammar_dewa_nai": "じゃない",
    "grammar_kore_sore_are": "Akhiran です、 だ",
    "grammar_dare": "Akhiran です、 だ",
    "grammar_hai_iie": "Akhiran です、 だ",
    # Level 2
    "grammar_ga_arimasu": "があります",
    "grammar_ga_imasu": "がいます",
    "grammar_ni_location": "に",
    "grammar_doko": "に",
    "grammar_kono_sono_ano": "Partikel  の",
    "grammar_ni_e_destination": "に",
    "grammar_de_place": "で",
    "grammar_to": "と",
    "grammar_nani": "か",
    # Level 3
    "grammar_ji": "時 【とき】",
    "grammar_fun_pun": "時 【とき】",
    "grammar_kara_made": "から",
    "grammar_han": "時 【とき】",
    "grammar_goro": "時 【とき】",
    "grammar_ikutsu_ikura": "か",
    "grammar_itsu": "時 【とき】",
    # Level 4
    "grammar_i_adj": "い-adjectives",
    "grammar_na_adj": "な-adjectives",  # Fixed: was ASCII 'na', now Hiragana 'な'
    "grammar_i_adj_neg": "い-adjectives",
    "grammar_totemo": "とても",
    "grammar_amari_neg": "い-adjectives",
    "grammar_donna": "どんな",
    "grammar_na_adj_noun": "な-adjectives",  # Fixed: was ASCII 'na', now Hiragana 'な'
    "grammar_ii_yoku": "い-adjectives",
    "grammar_ga_but": "が",
    # Level 5
    "grammar_o_particle": "を",
    "grammar_shimasu": "Kata Kerja Bentuk Sopan (masu-kei)",
    "grammar_ni_iku": "に⾏く 【にいく】",
    "grammar_issho_ni": "⼀緒に「いっしょに」",
    "grammar_masen_ka": "ませんか",
    "grammar_mashou": "ましょう",
    "grammar_doushite": "どうして",
    "grammar_kara_reason": "から",
    "grammar_frequency": "いつも",
    # Level 6
    "grammar_tai": "たい",
    "grammar_ga_hoshii": "がほしい",
    "grammar_no_ga_suki": "のが好き 【のがすきです】",
    "grammar_jouzu_heta": "のが上⼿",
    "grammar_ichiban": "⼀番 「いちばん」",
    "grammar_yori": "より〜ほうが",
    "grammar_hou_ga_ii": "⽅がいい",
    "grammar_dou_desu_ka": "はどうですか",
    # Level 7
    "grammar_te_kudasai": "てください",
    "grammar_te_mo_ii": "てもいい",
    "grammar_te_wa_ikenai": "てはいけない",
    "grammar_te_iru": "ている",
    "grammar_te_iru_state": "ている",
    "grammar_te_kara": "てから",
    "grammar_tari_tari": "たり〜たり",
    # Level 8
    "grammar_ta_koto_ga_aru": "たことがある",
    "grammar_mae_ni": "前に 【まえに】",
    "grammar_naru": "になる・くなる",
    "grammar_ndesu": "んです",
    "grammar_toki": "時 【とき】",
    "grammar_sugiru": "すぎる",
    "grammar_deshou": "でしょう",
    # Level 9
    "grammar_nakereba_naranai": "なくてはいけない",
    "grammar_naide_kudasai": "ないで",
    "grammar_tsumori": "つもり",
    "grammar_naku_temo_ii": "なくてもいい",
    "grammar_node": "ので",
    "grammar_shikashi": "Namun",
    "grammar_ne_yo": "ね",  # Added: was missing, used in Level 9 q_9_9 (Neo4j has ね and よ as separate nodes)
}

@router.post("/quest/submit")
async def submit_quest(request: QuestSubmitRequest):
    """Submit hasil kuis dan simpan ke Supabase."""
    await SupabaseService.update_quest_score(
        user_id=request.user_id,
        score=request.score,
        level_id=request.level_id
    )
    return {"status": "success", "message": f"Skor {request.score} disimpan!"}

@router.post("/quest/ai-correction")
async def ai_correction(request: AiCorrectionRequest):
    """Meminta AI untuk mengoreksi jawaban yang salah dan update node ke STRUGGLING."""
    # 1. Update status Neo4j ke STRUGGLING
    if graph and request.node_id and request.student_id != "default":
        try:
            neo4j_node_id = FRONTEND_TO_NEO4J_MAP.get(request.node_id, request.node_id)
            graph.update_node_status(request.student_id, neo4j_node_id, "STRUGGLING")
            logger.info(f"Marked node {neo4j_node_id} as STRUGGLING for user {request.student_id}")
        except Exception as e:
            logger.error(f"Failed to update Neo4j status: {e}")

    # 2. Minta feedback dari LLM (Qwen) - Versi Cepat (Non-streaming)
    try:
        data = await llm_agent.get_correction_feedback(
            question=request.question,
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            grammar_focus=request.grammar_focus,
            question_type=request.question_type,
            hint=request.hint,
            options=request.options,
            node_id=request.node_id
        )
        feedback = data.get("feedback")
        audio_url = data.get("audio_url")
    except Exception as e:
        logger.error(f"Error getting AI correction: {e}")
        feedback = f"Aduh, maaf ya Alisa lagi pusing. Pokoknya jawaban yang bener itu '{request.correct_answer}'. Semangat terus ya!"
        audio_url = None

    return {"feedback": feedback, "audio_url": audio_url}

class NodeStatusRequest(BaseModel):
    student_id: str
    node_id: str
    status: str # LEARNED, MASTERED, STRUGGLING

# KanjiMasteryRequest sudah didefinisikan di atas (baris 66-71), tidak perlu duplikasi.

class QuestSessionStatsRequest(BaseModel):
    student_id: str
    level_id: str
    stats: dict # format: { node_id: { correct: int, wrong: int, hint: int } }

@router.get("/mastery/{student_id}")
async def get_mastered_nodes(student_id: str):
    """
    Mengambil daftar node yang telah dipelajari/dikuasai (MASTERED/LEARNED) oleh student
    dari Neo4j, lalu dipetakan ke ID frontend untuk checkLocalPrerequisites.
    """
    logger.info(f"get_mastered_nodes called for: {student_id}")
    mastered_nodes = []
    if graph:
        try:
            path = graph.get_student_mastery_path(student_id)
            logger.info(f"Raw mastery path from Neo4j for {student_id}: {path}")
            for node in path:
                if node.get("status") in ("MASTERED", "LEARNED"):
                    node_id = node.get("id")
                    node_type = str(node.get("type", "")).lower()
                    if node_type == "grammar":
                        # Map back to frontend IDs
                        for frontend_id, neo4j_id in FRONTEND_TO_NEO4J_MAP.items():
                            if neo4j_id == node_id and frontend_id not in mastered_nodes:
                                mastered_nodes.append(frontend_id)
                    elif node_type in ("kanji", "vocab"):
                        if node_id not in mastered_nodes:
                            mastered_nodes.append(node_id)
            logger.info(f"Mapped mastered_nodes for frontend: {mastered_nodes}")
        except Exception as e:
            logger.error(f"Failed to fetch mastery from Neo4j: {e}")
    
    return {"student_id": student_id, "mastered_nodes": mastered_nodes, "kg_available": graph is not None}

@router.post("/quest/session-stats")
async def log_quest_session_stats(request: QuestSessionStatsRequest):
    """
    Memproses statistik sesi kuis di akhir level dan memperbarui status node di Neo4j.
    - Jika correct > 0 dan wrong == 0 dan hint == 0 -> MASTERED
    - Jika correct > 0 -> LEARNED
    - Jika wrong > correct -> STRUGGLING
    """
    logger.info(f"log_quest_session_stats called with student_id={request.student_id}, level_id={request.level_id}, stats={request.stats}")
    if not graph:
        return {"status": "error", "message": "Graph engine tidak tersedia."}
    
    try:
        # Agregasi statistik kuis berdasarkan neo4j_node_id agar tidak saling menimpa
        aggregated_stats = {}
        for frontend_node_id, stat in request.stats.items():
            neo4j_node_id = FRONTEND_TO_NEO4J_MAP.get(frontend_node_id, frontend_node_id)
            if neo4j_node_id not in aggregated_stats:
                aggregated_stats[neo4j_node_id] = {"correct": 0, "wrong": 0, "hint": 0}
            
            aggregated_stats[neo4j_node_id]["correct"] += stat.get("correct", 0)
            aggregated_stats[neo4j_node_id]["wrong"] += stat.get("wrong", 0)
            aggregated_stats[neo4j_node_id]["hint"] += stat.get("hint", 0)
            
        updated_count = 0
        for neo4j_node_id, stat in aggregated_stats.items():
            correct = stat["correct"]
            wrong = stat["wrong"]
            hint = stat["hint"]
            
            status = "LEARNED"
            if correct > 0 and wrong == 0 and hint == 0:
                status = "MASTERED"
            elif wrong > correct:
                status = "STRUGGLING"
            elif correct == 0 and wrong > 0:
                status = "STRUGGLING"
            
            graph.update_node_status(request.student_id, neo4j_node_id, status)
            updated_count += 1
            
        logger.info(f"Successfully processed quest session stats for student {request.student_id}. Updated {updated_count} nodes.")
        return {"status": "success", "message": f"{updated_count} status node berhasil diperbarui."}
    except Exception as e:
        logger.error(f"Failed to log quest session stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log-mastery")
async def log_node_status(request: NodeStatusRequest):
    """Update status node di Knowledge Graph."""
    logger.info(f"log_node_status called with: student_id={request.student_id}, node_id={request.node_id}, status={request.status}")
    if graph:
        try:
            neo4j_node_id = FRONTEND_TO_NEO4J_MAP.get(request.node_id, request.node_id)
            graph.update_node_status(request.student_id, neo4j_node_id, request.status)
            logger.info(f"Successfully updated status for node {neo4j_node_id} (mapped from {request.node_id}) to {request.status}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error in log_node_status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    return {"status": "error", "message": "Graph engine not available"}

@router.post("/kanji/mastery")
async def log_kanji_mastery(request: KanjiMasteryRequest):
    """
    Update status semua kanji yang dipelajari di set ini ke MASTERED di Neo4j.
    Juga MERGE-create node Kanji jika belum ada di graph (agar tidak silent no-op).
    """
    logger.info(f"log_kanji_mastery: student={request.student_id}, set={request.set_id}, kanji={request.kanji_ids}, score={request.score}/{request.total}")
    if not graph:
        logger.warning("log_kanji_mastery: Graph engine tidak tersedia, data hanya disimpan di localStorage.")
        return {"status": "error", "message": "Graph engine tidak tersedia."}

    try:
        # Pastikan tiap node Kanji ada di Neo4j terlebih dahulu, lalu tandai MASTERED
        graph.ensure_and_master_kanji(request.student_id, request.kanji_ids)

        # Award XP: 10 XP per kanji yang dijawab benar
        xp_gain = request.score * 10
        await SupabaseService.update_user_stats(request.student_id, "KANJI_DOJO_COMPLETED", custom_xp=xp_gain)
        logger.info(f"Kanji mastery OK: {len(request.kanji_ids)} kanji MASTERED, +{xp_gain} XP untuk {request.student_id}")
        return {
            "status": "success",
            "message": f"{len(request.kanji_ids)} kanji ditandai MASTERED. Mendapatkan {xp_gain} XP!"
        }
    except Exception as e:
        logger.error(f"Error in log_kanji_mastery: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

class KanjiBulkSyncRequest(BaseModel):
    student_id: str
    kanji_ids: List[str]  # semua kanji dari semua set yang sudah mastered

@router.post("/kanji/mastery/bulk-sync")
async def bulk_sync_kanji_mastery(request: KanjiBulkSyncRequest):
    """
    Re-sync semua kanji yang sudah mastered dari localStorage ke Neo4j.
    Dipanggil sekali saat login untuk memastikan Neo4j sinkron dengan localStorage.
    """
    logger.info(f"bulk_sync_kanji_mastery: student={request.student_id}, {len(request.kanji_ids)} kanji")
    if not graph:
        return {"status": "error", "message": "Graph engine tidak tersedia."}

    try:
        graph.ensure_and_master_kanji(request.student_id, request.kanji_ids)
        logger.info(f"bulk_sync OK: {len(request.kanji_ids)} kanji di-MASTERED untuk {request.student_id}")
        return {"status": "success", "synced": len(request.kanji_ids)}
    except Exception as e:
        logger.error(f"Error in bulk_sync_kanji_mastery: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/register")
async def register_user(request: RegisterRequest):
    """
    Registrasi user baru langsung via httpx (http2=False) untuk fix bug Windows+httpx+Supabase SDK.
    Sekarang menyertakan metadata demographics (age, gender, country, dll).
    """
    try:
        supabase_url = settings.SUPABASE_URL.strip()
        supabase_key = settings.SUPABASE_KEY.strip()

        if not supabase_url or not supabase_key:
            raise Exception("Kredensial Supabase belum dikonfigurasi di server.")

        # Build user metadata for demographics
        user_metadata = {
            "full_name": request.full_name or "User Baru",
            "username": request.email.split("@")[0] if request.email else "user",
        }
        if request.age is not None:
            user_metadata["age"] = str(request.age)
        if request.gender:
            user_metadata["gender"] = request.gender
        if request.country:
            user_metadata["country"] = request.country
        if request.study_purpose:
            user_metadata["study_purpose"] = request.study_purpose
        if request.japanese_level:
            user_metadata["japanese_level"] = request.japanese_level

        async with httpx.AsyncClient(http2=False, timeout=15.0) as client:
            res = await client.post(
                f"{supabase_url}/auth/v1/signup",
                json={
                    "email": request.email,
                    "password": request.password,
                    "data": user_metadata,
                },
                headers={
                    "apikey": supabase_key,
                    "Content-Type": "application/json"
                }
            )

        data = res.json()
        logger.info(f"Supabase signup response: {res.status_code}")

        if res.status_code not in (200, 201):
            raise Exception(data.get("msg") or data.get("message") or f"Supabase error: {res.status_code}")

        # Parsing user_id dengan lebih robust
        user_id = None
        if "user" in data and data["user"]:
            user_id = data["user"].get("id")
        elif "id" in data:
            user_id = data.get("id")

        if not user_id:
            logger.error(f"Supabase Response JSON structure unknown: {data}")
            raise Exception("Registrasi berhasil tapi User ID tidak ditemukan.")

        # Fallback: langsung buat profile dengan demographics jika trigger belum jalan
        try:
            await SupabaseService.ensure_profile_exists(
                user_id,
                email=request.email,
                full_name=request.full_name,
                age=request.age,
                gender=request.gender,
                country=request.country,
                study_purpose=request.study_purpose,
                japanese_level=request.japanese_level,
            )
        except Exception as profile_err:
            logger.info(f"Profile Fallback: {profile_err}")

        return {"status": "success", "message": "User berhasil terdaftar!"}
    except Exception as e:
        logger.error(f"Backend Registration Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/profile/{user_id}")
async def get_profile(user_id: str):
    """Ambil data profil user (XP, Level, etc) dan statistik Neo4j."""
    profile = await SupabaseService.get_user_profile(user_id)
    if not profile:
        # OTOMATIS BUAT JIKA TIDAK ADA (Lazy Initialization)
        logger.info(f"Lazy profile initialization for {user_id}")
        await SupabaseService.ensure_profile_exists(user_id)
        profile = await SupabaseService.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profil tidak ditemukan setelah inisialisasi")
    
    # Tambahkan statistik dari Neo4j jika GraphEngine tersedia
    neo4j_stats = {
        "kanji_mastered": 0, "kanji_total": 103,
        "vocab_learned": 0, "vocab_total": 800,
        "grammar_learned": 0, "grammar_total": 100,
        "assimilation_rate": 0
    }
    mastery_path = []
    if graph:
        # Kita bisa menghitung dari get_student_mastery_path
        mastery_path = graph.get_student_mastery_path(user_id)
        kanji_c = sum(1 for n in mastery_path if str(n.get("type", "")).lower() == "kanji")
        vocab_c = sum(1 for n in mastery_path if str(n.get("type", "")).lower() == "vocab")
        grammar_c = sum(1 for n in mastery_path if str(n.get("type", "")).lower() == "grammar")
        
        neo4j_stats["kanji_mastered"] = kanji_c
        neo4j_stats["vocab_learned"] = vocab_c
        neo4j_stats["grammar_learned"] = grammar_c
        
        total_learned = kanji_c + vocab_c + grammar_c
        total_available = neo4j_stats["kanji_total"] + neo4j_stats["vocab_total"] + neo4j_stats["grammar_total"]
        neo4j_stats["assimilation_rate"] = round((total_learned / total_available) * 100, 1) if total_available > 0 else 0

    profile["stats"] = neo4j_stats
    profile["mastery_path"] = mastery_path
    profile["daily_missions"] = graph.get_daily_missions(user_id) if graph else []
    return profile


@router.put("/user/profile/{user_id}")
async def update_profile(user_id: str, request: ProfileUpdateRequest):
    """Update data profil user (demographics)."""
    payload = {}
    if request.full_name is not None:
        payload["full_name"] = request.full_name
    if request.age is not None:
        payload["age"] = request.age
    if request.gender is not None:
        payload["gender"] = request.gender
    if request.country is not None:
        payload["country"] = request.country
    if request.study_purpose is not None:
        payload["study_purpose"] = request.study_purpose
    if request.japanese_level is not None:
        payload["japanese_level"] = request.japanese_level

    if not payload:
        return {"status": "success", "message": "Tidak ada data yang diubah."}

    try:
        await SupabaseService.update_user_profile(user_id, payload)
        return {"status": "success", "message": "Profil berhasil diperbarui!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/achievements/{user_id}")
async def get_achievements(user_id: str):
    """Ambil daftar pencapaian/quest yang sudah diselesaikan user."""
    achievements = await SupabaseService.get_user_achievements(user_id)
    return {"user_id": user_id, "completed_quests": achievements}

# Route /kanji/mastery sudah didefinisikan di atas (satu route saja).
# Duplikat ini dihapus untuk mencegah FastAPI mengabaikannya secara diam-diam.


@router.get("/speaking/topic")
async def get_speaking_topic(student_id: str = "default"):
    """
    Ambil topik percakapan yang di-ground ke KG untuk seed awal Speaking Practice.
    Frontend memanggil ini saat mode Speaking dibuka.
    """
    topic = await llm_agent.get_speaking_topic(student_id)
    return topic




# ---------------------------------------------------------------------------
# Utility: Background task untuk cleanup temp files
# ---------------------------------------------------------------------------
from starlette.background import BackgroundTask

def _cleanup_temp_file(path: str):
    """Hapus file sementara setelah response terkirim."""
    def _do_cleanup():
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Cleaned up temp file: {path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {path}: {e}")
    return BackgroundTask(_do_cleanup)
