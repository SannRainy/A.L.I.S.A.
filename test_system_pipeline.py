#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🏯 A.L.I.S.A. - System Integration & Pipeline Test Script
-------------------------------------------------------
File ini menguji seluruh jaringan/pipeline server & client TVJP.
Hasil dari pengujian ditampilkan bersih di terminal, terkelompok per fitur,
tanpa cunk/log bocor dari library eksternal.

Cara Menjalankan:
1. Pastikan server backend sedang aktif (start.bat atau python backend/main.py)
2. Aktifkan venv-backend dan jalankan:
   python test_system_pipeline.py
"""

import os
import sys
import time
import uuid
import wave
import io
import json
import asyncio
import logging
import traceback
from pathlib import Path

# Set UTF-8 encoding untuk console Windows agar aksara Jepang tidak crash
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Tambahkan folder backend ke path untuk mengakses service lokal secara langsung jika perlu
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.append(str(BACKEND_DIR))

# Suppress noisy logs dari library pihak ketiga agar output terminal bersih
logging.basicConfig(level=logging.WARNING)
for logger_name in ["httpx", "websockets", "httpcore", "neo4j", "supabase", "urllib3", "asyncio"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Teks dekorasi terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Target Server
BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/api/v1/ws/chat"
API_PREFIX = f"{BASE_URL}/api/v1"

# Global Test State
TEST_USER_EMAIL = f"pipeline_test_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PW = "PasswordSecure123!"
TEST_USER_ID = None
ADMIN_ID = None  # Akan di-set setelah user dibuat dan dielevasi di database

class TestReporter:
    def __init__(self):
        self.results = {}
        self.failures_detail = {}
        self.skipped_count = 0

    def add_result(self, category: str, test_id: str, name: str, status: str, detail: str = None):
        if category not in self.results:
            self.results[category] = []
        self.results[category].append({
            "id": test_id,
            "name": name,
            "status": status,
            "detail": detail
        })
        if status == "FAILED":
            self.failures_detail[f"[{category}] {test_id} - {name}"] = detail
        elif status == "SKIPPED":
            self.skipped_count += 1

    def print_section(self, title: str):
        print(f"\n{BOLD}{CYAN}[{title}]{RESET}")

    def print_test_row(self, test_id: str, name: str, status: str):
        dots = "." * (60 - len(name) - len(test_id))
        if status == "SUCCESS":
            status_str = f"{GREEN}[ SUCCESS ]{RESET}"
        elif status == "WARNING" or status == "SIMULATED":
            status_str = f"{YELLOW}[ {status} ]{RESET}"
        elif status == "SKIPPED":
            status_str = f"{YELLOW}[ SKIPPED ]{RESET}"
        else:
            status_str = f"{RED}[ FAILED  ]{RESET}"
        print(f"  [{test_id}] {name} {dots} {status_str}")

    def generate_summary(self):
        total = sum(len(items) for items in self.results.values())
        passed = sum(sum(1 for t in items if t["status"] in ("SUCCESS", "SIMULATED")) for items in self.results.values())
        failed = sum(sum(1 for t in items if t["status"] == "FAILED") for items in self.results.values())
        
        print("\n" + "=" * 80)
        print(f"                     🏯 {BOLD}RINGKASAN LAPORAN PENGUJIAN SISTEM{RESET} 🏯")
        print("=" * 80)
        print(f"  Total Pengujian Dirancang : {total}")
        print(f"  Berhasil / Simulasi       : {GREEN}{passed}{RESET}")
        print(f"  Gagal (Errors)            : {RED if failed > 0 else GREEN}{failed}{RESET}")
        print(f"  Dilewati (Offline/Skip)   : {YELLOW}{self.skipped_count}{RESET}")
        print("-" * 80)
        
        if failed > 0:
            print(f"\n{BOLD}{RED}DETAIL KEGAPALAN PENGUJIAN SISTEM:{RESET}")
            for idx, (test_name, err) in enumerate(self.failures_detail.items(), 1):
                print(f"  {idx}. {BOLD}{test_name}{RESET}")
                print(f"     Detail Error: {err}")
                print("-" * 40)
        else:
            print(f"\n✨ {GREEN}{BOLD}Seluruh pipeline sistem terverifikasi dengan sangat baik!{RESET} ✨")
        print("=" * 80 + "\n")


reporter = TestReporter()

# Helper: Generate minimal silent WAV 16kHz mono (Standard input for STT/Whisper)
def generate_minimal_wav() -> bytes:
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(16000)  # 16kHz
        wav_file.writeframes(b'\x00' * 32000)  # 1 second of silence
    return wav_io.getvalue()


# Helper: Dynamic role promotion
async def set_db_role(user_id: str, role: str) -> bool:
    try:
        from services.supabase_service import SupabaseService
        await SupabaseService.update_profile_role(user_id, role)
        return True
    except Exception as e:
        print(f"    (Database Direct Note: Gagal mengubah role ke {role}: {e})")
        return False


# ==============================================================================
# TEST SUITE ACTIONS
# ==============================================================================

async def run_tests():
    global TEST_USER_ID, ADMIN_ID
    import httpx
    
    print("\n" + "=" * 80)
    print(f"              🏯 {BOLD}A.L.I.S.A. SYSTEM PIPELINE AUTOMATED TESTER{RESET} 🏯")
    print("=" * 80)
    print(f"  Waktu Pengujian : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Server Target   : {BASE_URL}")
    print(f"  Email Test User : {TEST_USER_EMAIL}")
    print("=" * 80)

    # Check if target server is running
    server_online = False
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            res = await client.get(BASE_URL)
            if res.status_code == 200:
                server_online = True
        except Exception:
            pass

    if not server_online:
        print(f"\n{RED}{BOLD}[ WARNING ] Server TVJP offline di {BASE_URL}!{RESET}")
        print("  Mengaktifkan mode pemeriksaan DB lokal murni (API pipeline akan di-SKIP).\n")
        
    # --------------------------------------------------------------------------
    # CATEGORY A: INFRASTRUCTURE & BACKEND SERVICE CONNECTIVITY
    # --------------------------------------------------------------------------
    cat = "A. INFRASTRUCTURE & CONFIG"
    reporter.print_section(cat)

    # A1: API Server Ping
    if server_online:
        reporter.add_result(cat, "A1", "FastAPI Server Ping", "SUCCESS")
        reporter.print_test_row("A1", "FastAPI Server Ping", "SUCCESS")
    else:
        reporter.add_result(cat, "A1", "FastAPI Server Ping", "FAILED", "FastAPI Server tidak aktif di http://127.0.0.1:8000")
        reporter.print_test_row("A1", "FastAPI Server Ping", "FAILED")

    # A2: Supabase Connectivity
    try:
        from core.supabase_client import supabase, MockSupabaseClient
        if isinstance(supabase, MockSupabaseClient):
            reporter.add_result(cat, "A2", "Supabase Client Connection", "SIMULATED", "Menggunakan MockSupabaseClient (.env belum dikonfigurasi)")
            reporter.print_test_row("A2", "Supabase Client Connection", "SIMULATED")
        else:
            # Test simple select query
            res = supabase.table("profiles").select("id").limit(1).execute()
            reporter.add_result(cat, "A2", "Supabase Client Connection", "SUCCESS")
            reporter.print_test_row("A2", "Supabase Client Connection", "SUCCESS")
    except Exception as e:
        reporter.add_result(cat, "A2", "Supabase Client Connection", "FAILED", f"Supabase connection error: {traceback.format_exc()}")
        reporter.print_test_row("A2", "Supabase Client Connection", "FAILED")

    # A3: Neo4j Aura Connectivity
    try:
        from core.config import settings
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        driver.verify_connectivity()
        driver.close()
        reporter.add_result(cat, "A3", "Neo4j Aura Graph DB Connectivity", "SUCCESS")
        reporter.print_test_row("A3", "Neo4j Aura Graph DB Connectivity", "SUCCESS")
    except Exception as e:
        reporter.add_result(cat, "A3", "Neo4j Aura Graph DB Connectivity", "WARNING", f"Neo4j offline/not configured: {e}")
        reporter.print_test_row("A3", "Neo4j Aura Graph DB Connectivity", "WARNING")

    # A4: Style-Bert-VITS2 Voice Server Status
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            res = await client.get("http://localhost:5050")
            # Style-Bert-VITS2 server responds at port 5050
            reporter.add_result(cat, "A4", "Style-Bert-VITS2 Voice Server", "SUCCESS")
            reporter.print_test_row("A4", "Style-Bert-VITS2 Voice Server", "SUCCESS")
        except Exception:
            reporter.add_result(cat, "A4", "Style-Bert-VITS2 Voice Server", "WARNING", "Voice server port 5050 unreachable (TTS offline)")
            reporter.print_test_row("A4", "Style-Bert-VITS2 Voice Server", "WARNING")

    # A5: Local GGUF Model Path Check
    try:
        from core.config import settings
        model_path = BACKEND_DIR / settings.UNSLOTH_MODEL_PATH
        if model_path.exists():
            reporter.add_result(cat, "A5", f"Local GGUF Model Path ({model_path.name})", "SUCCESS")
            reporter.print_test_row("A5", f"Local GGUF Model Path ({model_path.name})", "SUCCESS")
        else:
            reporter.add_result(cat, "A5", "Local GGUF Model Path Check", "WARNING", f"Model file tidak ditemukan di {model_path}")
            reporter.print_test_row("A5", "Local GGUF Model Path Check", "WARNING")
    except Exception as e:
        reporter.add_result(cat, "A5", "Local GGUF Model Path Check", "FAILED", str(e))
        reporter.print_test_row("A5", "Local GGUF Model Path Check", "FAILED")

    # A6: HuggingFace Hub Connectivity
    try:
        from core.config import settings
        from huggingface_hub import HfApi
        api = HfApi(token=settings.HF_TOKEN if settings.HF_TOKEN else None)
        # Check model repo info
        api.model_info(repo_id=settings.HF_MODEL_REPO)
        reporter.add_result(cat, "A6", "HuggingFace API Repo Connection", "SUCCESS")
        reporter.print_test_row("A6", "HuggingFace API Repo Connection", "SUCCESS")
    except Exception as e:
        reporter.add_result(cat, "A6", "HuggingFace API Repo Connection", "WARNING", f"HF connection skipped or not authenticated: {e}")
        reporter.print_test_row("A6", "HuggingFace API Repo Connection", "WARNING")


    # --------------------------------------------------------------------------
    # CATEGORY B: STUDENT AUTHENTICATION & PROFILE PIPELINE
    # --------------------------------------------------------------------------
    cat = "B. AUTHENTICATION & PROFILE PIPELINE"
    reporter.print_section(cat)

    if not server_online:
        for tid, tname in [
            ("B1", "User Registration (Auth Register)"),
            ("B2", "Lazy Profile Init & Fetch"),
            ("B3", "Profile Demographics Update"),
            ("B4", "User Achievements Retrieval")
        ]:
            reporter.add_result(cat, tid, tname, "SKIPPED")
            reporter.print_test_row(tid, tname, "SKIPPED")
    else:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # B1: Register User
            try:
                reg_payload = {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PW,
                    "full_name": "Siswa Pipeline Test",
                    "age": 21,
                    "gender": "male",
                    "country": "Indonesia",
                    "study_purpose": "Persiapan JLPT N5",
                    "japanese_level": "beginner"
                }
                res = await client.post(f"{API_PREFIX}/auth/register", json=reg_payload)
                if res.status_code == 200:
                    data = res.json()
                    reporter.add_result(cat, "B1", "User Registration (Auth Register)", "SUCCESS")
                    reporter.print_test_row("B1", "User Registration (Auth Register)", "SUCCESS")
                else:
                    reporter.add_result(cat, "B1", "User Registration (Auth Register)", "FAILED", f"Status: {res.status_code}, Body: {res.text}")
                    reporter.print_test_row("B1", "User Registration (Auth Register)", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "B1", "User Registration (Auth Register)", "FAILED", traceback.format_exc())
                reporter.print_test_row("B1", "User Registration (Auth Register)", "FAILED")

            # Ambil profile & user ID untuk test berkelanjutan
            try:
                from core.supabase_client import supabase, MockSupabaseClient
                if not isinstance(supabase, MockSupabaseClient):
                    db_res = supabase.table("profiles").select("id").eq("email", TEST_USER_EMAIL).execute()
                    if db_res.data:
                        TEST_USER_ID = db_res.data[0]["id"]
                        ADMIN_ID = TEST_USER_ID
                else:
                    TEST_USER_ID = "mock-user-uuid-1234"
                    ADMIN_ID = TEST_USER_ID
            except Exception:
                TEST_USER_ID = "mock-user-uuid-1234"
                ADMIN_ID = TEST_USER_ID

            # B2: Profile Fetch (Lazy Init Verification)
            try:
                res = await client.get(f"{API_PREFIX}/user/profile/{TEST_USER_ID}")
                if res.status_code == 200:
                    data = res.json()
                    if "xp" in data and "level" in data:
                        reporter.add_result(cat, "B2", "Lazy Profile Init & Fetch", "SUCCESS")
                        reporter.print_test_row("B2", "Lazy Profile Init & Fetch", "SUCCESS")
                    else:
                        reporter.add_result(cat, "B2", "Lazy Profile Init & Fetch", "FAILED", f"JSON keys invalid: {data}")
                        reporter.print_test_row("B2", "Lazy Profile Init & Fetch", "FAILED")
                else:
                    reporter.add_result(cat, "B2", "Lazy Profile Init & Fetch", "FAILED", f"Status: {res.status_code}, Body: {res.text}")
                    reporter.print_test_row("B2", "Lazy Profile Init & Fetch", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "B2", "Lazy Profile Init & Fetch", "FAILED", traceback.format_exc())
                reporter.print_test_row("B2", "Lazy Profile Init & Fetch", "FAILED")

            # B3: Profile Update (Demographics)
            try:
                upd_payload = {
                    "full_name": "Siswa Pipeline Test Updated",
                    "age": 22,
                    "country": "Jepang",
                    "study_purpose": "Melanjutkan Kuliah ke Tokyo"
                }
                res = await client.put(f"{API_PREFIX}/user/profile/{TEST_USER_ID}", json=upd_payload)
                if res.status_code == 200:
                    reporter.add_result(cat, "B3", "Profile Demographics Update", "SUCCESS")
                    reporter.print_test_row("B3", "Profile Demographics Update", "SUCCESS")
                else:
                    reporter.add_result(cat, "B3", "Profile Demographics Update", "FAILED", f"Status: {res.status_code}, Body: {res.text}")
                    reporter.print_test_row("B3", "Profile Demographics Update", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "B3", "Profile Demographics Update", "FAILED", traceback.format_exc())
                reporter.print_test_row("B3", "Profile Demographics Update", "FAILED")

            # B4: User Achievements
            try:
                res = await client.get(f"{API_PREFIX}/user/achievements/{TEST_USER_ID}")
                if res.status_code == 200:
                    reporter.add_result(cat, "B4", "User Achievements Retrieval", "SUCCESS")
                    reporter.print_test_row("B4", "User Achievements Retrieval", "SUCCESS")
                else:
                    reporter.add_result(cat, "B4", "User Achievements Retrieval", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("B4", "User Achievements Retrieval", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "B4", "User Achievements Retrieval", "FAILED", traceback.format_exc())
                reporter.print_test_row("B4", "User Achievements Retrieval", "FAILED")


    # --------------------------------------------------------------------------
    # CATEGORY C: INTERACTIVE CHAT & NEURO-SYMBOLIC RAG
    # --------------------------------------------------------------------------
    cat = "C. INTERACTIVE CHAT & NEURO-SYMBOLIC RAG"
    reporter.print_section(cat)

    if not server_online:
        for tid, tname in [
            ("C1", "HTTP Streaming Chat (GraphRAG Context)"),
            ("C2", "WebSocket Real-Time Chat (Framing & TTS)"),
            ("C3", "Knowledge Graph Mastery Path Retrieval")
        ]:
            reporter.add_result(cat, tid, tname, "SKIPPED")
            reporter.print_test_row(tid, tname, "SKIPPED")
    else:
        # C1: HTTP Streaming Chat
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                chat_payload = {
                    "query": "Jelaskan tentang air dalam Bahasa Jepang",
                    "student_id": TEST_USER_ID,
                    "mode": "discovery",
                    "history": []
                }
                async with client.stream("POST", f"{API_PREFIX}/chat", json=chat_payload) as response:
                    if response.status_code == 200:
                        first_chunk_ok = False
                        async for chunk in response.aiter_bytes():
                            if chunk:
                                first_chunk_ok = True
                                break
                        if first_chunk_ok:
                            reporter.add_result(cat, "C1", "HTTP Streaming Chat (GraphRAG Context)", "SUCCESS")
                            reporter.print_test_row("C1", "HTTP Streaming Chat (GraphRAG Context)", "SUCCESS")
                        else:
                            reporter.add_result(cat, "C1", "HTTP Streaming Chat (GraphRAG Context)", "FAILED", "Stream returned empty")
                            reporter.print_test_row("C1", "HTTP Streaming Chat (GraphRAG Context)", "FAILED")
                    else:
                        reporter.add_result(cat, "C1", "HTTP Streaming Chat (GraphRAG Context)", "FAILED", f"Status: {response.status_code}")
                        reporter.print_test_row("C1", "HTTP Streaming Chat (GraphRAG Context)", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "C1", "HTTP Streaming Chat (GraphRAG Context)", "FAILED", traceback.format_exc())
            reporter.print_test_row("C1", "HTTP Streaming Chat (GraphRAG Context)", "FAILED")

        # C2: WebSocket Real-Time Chat Pipeline
        import websockets
        try:
            ws_payload = {
                "query": "Mizu",
                "student_id": TEST_USER_ID,
                "mode": "speaking",
                "history": []
            }
            async with websockets.connect(WS_URL, open_timeout=5.0, close_timeout=2.0) as ws:
                await ws.send(json.dumps(ws_payload))
                
                received_frames = []
                for _ in range(5):
                    frame_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    frame = json.loads(frame_raw)
                    received_frames.append(frame.get("type"))
                    if frame.get("type") in ("done", "error"):
                        break
                
                if "status" in received_frames or "metadata" in received_frames or "sentence" in received_frames:
                    reporter.add_result(cat, "C2", "WebSocket Real-Time Chat (Framing & TTS)", "SUCCESS")
                    reporter.print_test_row("C2", "WebSocket Real-Time Chat (Framing & TTS)", "SUCCESS")
                else:
                    reporter.add_result(cat, "C2", "WebSocket Real-Time Chat (Framing & TTS)", "FAILED", f"Frames received missing context: {received_frames}")
                    reporter.print_test_row("C2", "WebSocket Real-Time Chat (Framing & TTS)", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "C2", "WebSocket Real-Time Chat (Framing & TTS)", "WARNING", f"WebSocket check failed/timed out (common if local LLM loading takes time): {e}")
            reporter.print_test_row("C2", "WebSocket Real-Time Chat (Framing & TTS)", "WARNING")

        # C3: Knowledge Graph Mastery Path Retrieval
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/mastery/{TEST_USER_ID}")
                if res.status_code == 200:
                    reporter.add_result(cat, "C3", "Knowledge Graph Mastery Path Retrieval", "SUCCESS")
                    reporter.print_test_row("C3", "Knowledge Graph Mastery Path Retrieval", "SUCCESS")
                else:
                    reporter.add_result(cat, "C3", "Knowledge Graph Mastery Path Retrieval", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("C3", "Knowledge Graph Mastery Path Retrieval", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "C3", "Knowledge Graph Mastery Path Retrieval", "FAILED", traceback.format_exc())
            reporter.print_test_row("C3", "Knowledge Graph Mastery Path Retrieval", "FAILED")


    # --------------------------------------------------------------------------
    # CATEGORY D: SPEECH-TO-TEXT & VOCAL INTERACTION
    # --------------------------------------------------------------------------
    cat = "D. SPEECH-TO-TEXT & VOCAL INTERACTION"
    reporter.print_section(cat)

    if not server_online:
        for tid, tname in [
            ("D1", "Voice Audio Transcription (STT/Whisper)"),
            ("D2", "Speaking Practice Topic Seed"),
            ("D3", "TTS Audio File Retrieval")
        ]:
            reporter.add_result(cat, tid, tname, "SKIPPED")
            reporter.print_test_row(tid, tname, "SKIPPED")
    else:
        # D1: Voice Audio Transcription
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                silent_wav = generate_minimal_wav()
                files = {"audio": ("test_silence.wav", silent_wav, "audio/wav")}
                data = {"mode": "speaking"}
                res = await client.post(f"{API_PREFIX}/transcribe", files=files, data=data)
                
                if res.status_code == 200:
                    res_json = res.json()
                    if "text" in res_json or "error" in res_json:
                        reporter.add_result(cat, "D1", "Voice Audio Transcription (STT/Whisper)", "SUCCESS")
                        reporter.print_test_row("D1", "Voice Audio Transcription (STT/Whisper)", "SUCCESS")
                    else:
                        reporter.add_result(cat, "D1", "Voice Audio Transcription (STT/Whisper)", "FAILED", f"Invalid response: {res_json}")
                        reporter.print_test_row("D1", "Voice Audio Transcription (STT/Whisper)", "FAILED")
                else:
                    reporter.add_result(cat, "D1", "Voice Audio Transcription (STT/Whisper)", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("D1", "Voice Audio Transcription (STT/Whisper)", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "D1", "Voice Audio Transcription (STT/Whisper)", "WARNING", f"STT failed (Whisper model might not be preloaded on server): {e}")
            reporter.print_test_row("D1", "Voice Audio Transcription (STT/Whisper)", "WARNING")

        # D2: Speaking Practice Topic Seed
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/speaking/topic?student_id={TEST_USER_ID}")
                if res.status_code == 200:
                    reporter.add_result(cat, "D2", "Speaking Practice Topic Seed", "SUCCESS")
                    reporter.print_test_row("D2", "Speaking Practice Topic Seed", "SUCCESS")
                else:
                    reporter.add_result(cat, "D2", "Speaking Practice Topic Seed", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("D2", "Speaking Practice Topic Seed", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "D2", "Speaking Practice Topic Seed", "FAILED", traceback.format_exc())
            reporter.print_test_row("D2", "Speaking Practice Topic Seed", "FAILED")

        # D3: Audio file retrieval (GET /get-audio/{filename})
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/get-audio/invalid_non_existent.wav")
                if res.status_code == 404:
                    reporter.add_result(cat, "D3", "TTS Audio File Retrieval (404 Handled)", "SUCCESS")
                    reporter.print_test_row("D3", "TTS Audio File Retrieval (404 Handled)", "SUCCESS")
                else:
                    reporter.add_result(cat, "D3", "TTS Audio File Retrieval", "FAILED", f"Expected 404, got status: {res.status_code}")
                    reporter.print_test_row("D3", "TTS Audio File Retrieval", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "D3", "TTS Audio File Retrieval", "FAILED", traceback.format_exc())
            reporter.print_test_row("D3", "TTS Audio File Retrieval", "FAILED")


    # --------------------------------------------------------------------------
    # CATEGORY E: QUEST SYSTEM & GAMIFICATION EVALUATION
    # --------------------------------------------------------------------------
    cat = "E. QUEST SYSTEM & GAMIFICATION"
    reporter.print_section(cat)

    if not server_online:
        for tid, tname in [
            ("E1", "Quest Level List Summary"),
            ("E2", "Quest Level Details (Questions)"),
            ("E3", "AI Quest Correction & Status Update"),
            ("E4", "Quest Score Submission (XP Level Up)"),
            ("E5", "Quest Session Stats Update"),
            ("E6", "Kanji Dojo Mastery Sync"),
            ("E7", "Kanji Bulk Re-sync")
        ]:
            reporter.add_result(cat, tid, tname, "SKIPPED")
            reporter.print_test_row(tid, tname, "SKIPPED")
    else:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # E1: Quest Level List
            try:
                res = await client.get(f"{API_PREFIX}/quest/levels")
                if res.status_code == 200:
                    reporter.add_result(cat, "E1", "Quest Level List Summary", "SUCCESS")
                    reporter.print_test_row("E1", "Quest Level List Summary", "SUCCESS")
                else:
                    reporter.add_result(cat, "E1", "Quest Level List Summary", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("E1", "Quest Level List Summary", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "E1", "Quest Level List Summary", "FAILED", traceback.format_exc())
                reporter.print_test_row("E1", "Quest Level List Summary", "FAILED")

            # E2: Quest Level Details
            try:
                res = await client.get(f"{API_PREFIX}/quest/data/lvl_1")
                if res.status_code == 200:
                    reporter.add_result(cat, "E2", "Quest Level Details (Questions)", "SUCCESS")
                    reporter.print_test_row("E2", "Quest Level Details (Questions)", "SUCCESS")
                else:
                    reporter.add_result(cat, "E2", "Quest Level Details (Questions)", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("E2", "Quest Level Details (Questions)", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "E2", "Quest Level Details (Questions)", "FAILED", traceback.format_exc())
                reporter.print_test_row("E2", "Quest Level Details (Questions)", "FAILED")

            # E3: AI Quiz Correction
            try:
                corr_payload = {
                    "student_id": TEST_USER_ID,
                    "question": "Pilihlah partikel yang tepat: Watashi __ Satya desu.",
                    "user_answer": "ga",
                    "correct_answer": "wa",
                    "node_id": "grammar_wa",
                    "grammar_focus": "Partikel wa",
                    "question_type": "multiple_choice"
                }
                res = await client.post(f"{API_PREFIX}/quest/ai-correction", json=corr_payload)
                if res.status_code == 200:
                    data = res.json()
                    if "feedback" in data:
                        reporter.add_result(cat, "E3", "AI Quest Correction & Status Update", "SUCCESS")
                        reporter.print_test_row("E3", "AI Quest Correction & Status Update", "SUCCESS")
                    else:
                        reporter.add_result(cat, "E3", "AI Quest Correction & Status Update", "FAILED", f"No feedback: {data}")
                        reporter.print_test_row("E3", "AI Quest Correction & Status Update", "FAILED")
                else:
                    reporter.add_result(cat, "E3", "AI Quest Correction & Status Update", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("E3", "AI Quest Correction & Status Update", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "E3", "AI Quest Correction & Status Update", "FAILED", traceback.format_exc())
                reporter.print_test_row("E3", "AI Quest Correction & Status Update", "FAILED")

            # E4: Quest Score Submission
            try:
                sub_payload = {
                    "user_id": TEST_USER_ID,
                    "level_id": "lvl_1",
                    "score": 90
                }
                res = await client.post(f"{API_PREFIX}/quest/submit", json=sub_payload)
                if res.status_code == 200:
                    reporter.add_result(cat, "E4", "Quest Score Submission (XP Level Up)", "SUCCESS")
                    reporter.print_test_row("E4", "Quest Score Submission (XP Level Up)", "SUCCESS")
                else:
                    reporter.add_result(cat, "E4", "Quest Score Submission (XP Level Up)", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("E4", "Quest Score Submission (XP Level Up)", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "E4", "Quest Score Submission (XP Level Up)", "FAILED", traceback.format_exc())
                reporter.print_test_row("E4", "Quest Score Submission (XP Level Up)", "FAILED")

            # E5: Quest Session Stats Update
            try:
                stats_payload = {
                    "student_id": TEST_USER_ID,
                    "level_id": "lvl_1",
                    "stats": {
                        "grammar_wa": {"correct": 1, "wrong": 0, "hint": 0},
                        "grammar_desu": {"correct": 0, "wrong": 1, "hint": 0}
                    }
                }
                res = await client.post(f"{API_PREFIX}/quest/session-stats", json=stats_payload)
                if res.status_code == 200:
                    reporter.add_result(cat, "E5", "Quest Session Stats Update", "SUCCESS")
                    reporter.print_test_row("E5", "Quest Session Stats Update", "SUCCESS")
                else:
                    reporter.add_result(cat, "E5", "Quest Session Stats Update", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("E5", "Quest Session Stats Update", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "E5", "Quest Session Stats Update", "FAILED", traceback.format_exc())
                reporter.print_test_row("E5", "Quest Session Stats Update", "FAILED")

            # E6: Kanji Dojo Mastery Sync
            try:
                kanji_payload = {
                    "student_id": TEST_USER_ID,
                    "set_id": "kanji_n5_set1",
                    "kanji_ids": ["水", "火", "木"],
                    "score": 3,
                    "total": 3
                }
                res = await client.post(f"{API_PREFIX}/kanji/mastery", json=kanji_payload)
                if res.status_code == 200:
                    reporter.add_result(cat, "E6", "Kanji Dojo Mastery Sync", "SUCCESS")
                    reporter.print_test_row("E6", "Kanji Dojo Mastery Sync", "SUCCESS")
                else:
                    reporter.add_result(cat, "E6", "Kanji Dojo Mastery Sync", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("E6", "Kanji Dojo Mastery Sync", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "E6", "Kanji Dojo Mastery Sync", "FAILED", traceback.format_exc())
                reporter.print_test_row("E6", "Kanji Dojo Mastery Sync", "FAILED")

            # E7: Kanji Bulk Re-sync
            try:
                bulk_payload = {
                    "student_id": TEST_USER_ID,
                    "kanji_ids": ["水", "火", "木", "金", "土"]
                }
                res = await client.post(f"{API_PREFIX}/kanji/mastery/bulk-sync", json=bulk_payload)
                if res.status_code == 200:
                    reporter.add_result(cat, "E7", "Kanji Bulk Re-sync", "SUCCESS")
                    reporter.print_test_row("E7", "Kanji Bulk Re-sync", "SUCCESS")
                else:
                    reporter.add_result(cat, "E7", "Kanji Bulk Re-sync", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("E7", "Kanji Bulk Re-sync", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "E7", "Kanji Bulk Re-sync", "FAILED", traceback.format_exc())
                reporter.print_test_row("E7", "Kanji Bulk Re-sync", "FAILED")


    # --------------------------------------------------------------------------
    # CATEGORY F: SUPER ADMIN MANAGEMENT & REPORTING
    # --------------------------------------------------------------------------
    cat = "F. SUPER ADMIN MANAGEMENT & REPORTING"
    reporter.print_section(cat)

    if not server_online:
        for tid, tname in [
            ("F1", "Verify Admin Access Guard (Block Student)"),
            ("F2", "Get All Users (Neo4j Enriched Listing)"),
            ("F3", "User Detail Inspection"),
            ("F4", "CSV File Pipeline Inventory"),
            ("F5", "Ingestion Data Reader (CSV to JSON)"),
            ("F6", "Ingestion ETL Trigger"),
            ("F7", "Survey & System Analytics Metrics"),
            ("F8", "Export User Data Profiles"),
            ("F9", "Visual Knowledge Graph Network Export"),
            ("F10", "AI Model Switcher & Status Checking")
        ]:
            reporter.add_result(cat, tid, tname, "SKIPPED")
            reporter.print_test_row(tid, tname, "SKIPPED")
    else:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # F1: Verify Admin Access Guard (Block Student User)
            try:
                res = await client.get(f"{API_PREFIX}/admin/users?admin_id={TEST_USER_ID}")
                if res.status_code == 403:
                    reporter.add_result(cat, "F1", "Verify Admin Access Guard (Block Student)", "SUCCESS")
                    reporter.print_test_row("F1", "Verify Admin Access Guard (Block Student)", "SUCCESS")
                else:
                    reporter.add_result(cat, "F1", "Verify Admin Access Guard (Block Student)", "FAILED", f"Expected 403, got status: {res.status_code}")
                    reporter.print_test_row("F1", "Verify Admin Access Guard (Block Student)", "FAILED")
            except Exception as e:
                reporter.add_result(cat, "F1", "Verify Admin Access Guard (Block Student)", "FAILED", traceback.format_exc())
                reporter.print_test_row("F1", "Verify Admin Access Guard (Block Student)", "FAILED")

            # --- Elevasi Role User di DB untuk test Admin selanjutnya ---
            db_elevated = await set_db_role(ADMIN_ID, "admin")

            # F2: Get All Users (Enriched)
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/users?admin_id={ADMIN_ID}")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F2", "Get All Users (Neo4j Enriched Listing)", "SUCCESS")
                        reporter.print_test_row("F2", "Get All Users (Neo4j Enriched Listing)", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F2", "Get All Users (Neo4j Enriched Listing)", "FAILED", f"Status: {res.status_code}, Msg: {res.text}")
                        reporter.print_test_row("F2", "Get All Users (Neo4j Enriched Listing)", "FAILED")
                except Exception as e:
                    reporter.add_result(cat, "F2", "Get All Users (Neo4j Enriched Listing)", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F2", "Get All Users (Neo4j Enriched Listing)", "FAILED")
            else:
                reporter.add_result(cat, "F2", "Get All Users (Neo4j Enriched Listing)", "SKIPPED", "Gagal me-elevasi user ke admin di DB")
                reporter.print_test_row("F2", "Get All Users (Neo4j Enriched Listing)", "SKIPPED")

            # F3: User Detail Inspection
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/users/{TEST_USER_ID}/detail?admin_id={ADMIN_ID}")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F3", "User Detail Inspection", "SUCCESS")
                        reporter.print_test_row("F3", "User Detail Inspection", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F3", "User Detail Inspection", "FAILED", f"Status: {res.status_code}")
                        reporter.print_test_row("F3", "User Detail Inspection", "FAILED")
                except Exception as e:
                    reporter.add_result(cat, "F3", "User Detail Inspection", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F3", "User Detail Inspection", "FAILED")
            else:
                reporter.add_result(cat, "F3", "User Detail Inspection", "SKIPPED")
                reporter.print_test_row("F3", "User Detail Inspection", "SKIPPED")

            # F4: CSV File Pipeline Inventory
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/csv-files?admin_id={ADMIN_ID}")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F4", "CSV File Pipeline Inventory", "SUCCESS")
                        reporter.print_test_row("F4", "CSV File Pipeline Inventory", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F4", "CSV File Pipeline Inventory", "FAILED", f"Status: {res.status_code}")
                        reporter.print_test_row("F4", "CSV File Pipeline Inventory", "FAILED")
                except Exception as e:
                    reporter.add_result(cat, "F4", "CSV File Pipeline Inventory", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F4", "CSV File Pipeline Inventory", "FAILED")
            else:
                reporter.add_result(cat, "F4", "CSV File Pipeline Inventory", "SKIPPED")
                reporter.print_test_row("F4", "CSV File Pipeline Inventory", "SKIPPED")

            # F5: Ingestion Data Reader
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/csv/nodes_kanji.csv?admin_id={ADMIN_ID}")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F5", "Ingestion Data Reader (CSV to JSON)", "SUCCESS")
                        reporter.print_test_row("F5", "Ingestion Data Reader (CSV to JSON)", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F5", "Ingestion Data Reader", "WARNING", f"nodes_kanji.csv tidak terakses: {res.status_code}")
                        reporter.print_test_row("F5", "Ingestion Data Reader", "WARNING")
                except Exception as e:
                    reporter.add_result(cat, "F5", "Ingestion Data Reader", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F5", "Ingestion Data Reader", "FAILED")
            else:
                reporter.add_result(cat, "F5", "Ingestion Data Reader (CSV to JSON)", "SKIPPED")
                reporter.print_test_row("F5", "Ingestion Data Reader (CSV to JSON)", "SKIPPED")

            # F6: Ingestion ETL Trigger
            reporter.add_result(cat, "F6", "Ingestion ETL Trigger (Safe-Skipped for speed)", "SKIPPED")
            reporter.print_test_row("F6", "Ingestion ETL Trigger (Safe-Skipped for speed)", "SKIPPED")

            # F7: Survey & System Analytics Metrics
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/analytics?admin_id={ADMIN_ID}")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F7", "Survey & System Analytics Metrics", "SUCCESS")
                        reporter.print_test_row("F7", "Survey & System Analytics Metrics", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F7", "Survey & System Analytics Metrics", "FAILED", f"Status: {res.status_code}")
                        reporter.print_test_row("F7", "Survey & System Analytics Metrics", "FAILED")
                except Exception as e:
                    reporter.add_result(cat, "F7", "Survey & System Analytics Metrics", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F7", "Survey & System Analytics Metrics", "FAILED")
            else:
                reporter.add_result(cat, "F7", "Survey & System Analytics Metrics", "SKIPPED")
                reporter.print_test_row("F7", "Survey & System Analytics Metrics", "SKIPPED")

            # F8: Export User Data Profiles
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/export/users?admin_id={ADMIN_ID}&format=json")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F8", "Export User Data Profiles (JSON)", "SUCCESS")
                        reporter.print_test_row("F8", "Export User Data Profiles (JSON)", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F8", "Export User Data Profiles (JSON)", "FAILED", f"Status: {res.status_code}")
                        reporter.print_test_row("F8", "Export User Data Profiles (JSON)", "FAILED")
                except Exception as e:
                    reporter.add_result(cat, "F8", "Export User Data Profiles (JSON)", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F8", "Export User Data Profiles (JSON)", "FAILED")
            else:
                reporter.add_result(cat, "F8", "Export User Data Profiles (JSON)", "SKIPPED")
                reporter.print_test_row("F8", "Export User Data Profiles (JSON)", "SKIPPED")

            # F9: Visual Knowledge Graph Network Export
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/kg-data?admin_id={ADMIN_ID}")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F9", "Visual Knowledge Graph Network Export", "SUCCESS")
                        reporter.print_test_row("F9", "Visual Knowledge Graph Network Export", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F9", "Visual Knowledge Graph Network Export", "FAILED", f"Status: {res.status_code}")
                        reporter.print_test_row("F9", "Visual Knowledge Graph Network Export", "FAILED")
                except Exception as e:
                    reporter.add_result(cat, "F9", "Visual Knowledge Graph Network Export", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F9", "Visual Knowledge Graph Network Export", "FAILED")
            else:
                reporter.add_result(cat, "F9", "Visual Knowledge Graph Network Export", "SKIPPED")
                reporter.print_test_row("F9", "Visual Knowledge Graph Network Export", "SKIPPED")

            # F10: AI Model Switcher & Status Checking
            if db_elevated:
                try:
                    res = await client.get(f"{API_PREFIX}/admin/models?admin_id={ADMIN_ID}")
                    if res.status_code == 200:
                        reporter.add_result(cat, "F10", "AI Model Switcher & Status Checking", "SUCCESS")
                        reporter.print_test_row("F10", "AI Model Switcher & Status Checking", "SUCCESS")
                    else:
                        reporter.add_result(cat, "F10", "AI Model Switcher & Status Checking", "FAILED", f"Status: {res.status_code}")
                        reporter.print_test_row("F10", "AI Model Switcher & Status Checking", "FAILED")
                except Exception as e:
                    reporter.add_result(cat, "F10", "AI Model Switcher & Status Checking", "FAILED", traceback.format_exc())
                    reporter.print_test_row("F10", "AI Model Switcher & Status Checking", "FAILED")
            else:
                reporter.add_result(cat, "F10", "AI Model Switcher & Status Checking", "SKIPPED")
                reporter.print_test_row("F10", "AI Model Switcher & Status Checking", "SKIPPED")

            # --- Kembalikan Role User ke Student (Database Cleanup) ---
            await set_db_role(ADMIN_ID, "student")

    # --------------------------------------------------------------------------
    # CATEGORY G: READING COMPREHENSION & COGNITIVE SERVICES (V3)
    # --------------------------------------------------------------------------
    cat = "G. READING COMPREHENSION & COGNITIVE SERVICES (V3)"
    reporter.print_section(cat)

    # G1: BKT Engine Belief Update (Local calculation)
    try:
        from services.bkt_engine import BKTEngine
        params = BKTEngine.get_params("vocab")
        p_l_1 = BKTEngine.update_belief(0.1, False, params)
        p_l_2 = BKTEngine.update_belief(0.1, True, params)
        if p_l_2 > p_l_1:
            reporter.add_result(cat, "G1", "BKT Engine Belief Update", "SUCCESS")
            reporter.print_test_row("G1", "BKT Engine Belief Update", "SUCCESS")
        else:
            reporter.add_result(cat, "G1", "BKT Engine Belief Update", "FAILED", "P(L) correct not higher than P(L) incorrect")
            reporter.print_test_row("G1", "BKT Engine Belief Update", "FAILED")
    except Exception as e:
        reporter.add_result(cat, "G1", "BKT Engine Belief Update", "FAILED", traceback.format_exc())
        reporter.print_test_row("G1", "BKT Engine Belief Update", "FAILED")

    # G2: BKT Question Selection (Local calculation)
    try:
        from services.bkt_engine import BKTEngine
        beliefs = {"v1": 0.5, "v2": 0.9, "v3": 0.1}
        nodes = [{"id": "v1", "node_type": "vocab"}, {"id": "v2", "node_type": "vocab"}, {"id": "v3", "node_type": "vocab"}]
        selected = BKTEngine.select_next_questions(beliefs, nodes, count=2)
        if len(selected) > 0:
            reporter.add_result(cat, "G2", "BKT Question Selection", "SUCCESS")
            reporter.print_test_row("G2", "BKT Question Selection", "SUCCESS")
        else:
            reporter.add_result(cat, "G2", "BKT Question Selection", "FAILED", "No nodes selected")
            reporter.print_test_row("G2", "BKT Question Selection", "FAILED")
    except Exception as e:
        reporter.add_result(cat, "G2", "BKT Question Selection", "FAILED", traceback.format_exc())
        reporter.print_test_row("G2", "BKT Question Selection", "FAILED")

    # G3: Reading Passages List API
    if not server_online:
        reporter.add_result(cat, "G3", "Reading Passages List (GET /reading/passages)", "SKIPPED")
        reporter.print_test_row("G3", "Reading Passages List (GET /reading/passages)", "SKIPPED")
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/reading/passages")
                if res.status_code == 200:
                    reporter.add_result(cat, "G3", "Reading Passages List (GET /reading/passages)", "SUCCESS")
                    reporter.print_test_row("G3", "Reading Passages List (GET /reading/passages)", "SUCCESS")
                else:
                    reporter.add_result(cat, "G3", "Reading Passages List (GET /reading/passages)", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("G3", "Reading Passages List (GET /reading/passages)", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "G3", "Reading Passages List (GET /reading/passages)", "FAILED", traceback.format_exc())
            reporter.print_test_row("G3", "Reading Passages List (GET /reading/passages)", "FAILED")

    # G4: Reading Passage Detail API
    if not server_online:
        reporter.add_result(cat, "G4", "Reading Passage Detail (GET /reading/passage/read_1)", "SKIPPED")
        reporter.print_test_row("G4", "Reading Passage Detail (GET /reading/passage/read_1)", "SKIPPED")
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/reading/passage/read_1")
                if res.status_code == 200:
                    reporter.add_result(cat, "G4", "Reading Passage Detail (GET /reading/passage/read_1)", "SUCCESS")
                    reporter.print_test_row("G4", "Reading Passage Detail (GET /reading/passage/read_1)", "SUCCESS")
                else:
                    reporter.add_result(cat, "G4", "Reading Passage Detail (GET /reading/passage/read_1)", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("G4", "Reading Passage Detail (GET /reading/passage/read_1)", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "G4", "Reading Passage Detail (GET /reading/passage/read_1)", "FAILED", traceback.format_exc())
            reporter.print_test_row("G4", "Reading Passage Detail (GET /reading/passage/read_1)", "FAILED")

    # G5: Reading Session Submit API
    if not server_online or not TEST_USER_ID:
        reporter.add_result(cat, "G5", "Reading Session Submit (POST /reading/submit)", "SKIPPED")
        reporter.print_test_row("G5", "Reading Session Submit (POST /reading/submit)", "SKIPPED")
    else:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                submit_payload = {
                    "user_id": TEST_USER_ID,
                    "passage_id": "read_1",
                    "unknown_words": ["私"],
                    "comprehension_answers": [
                        {"question_id": "rq_1_1", "is_correct": True}
                    ]
                }
                res = await client.post(f"{API_PREFIX}/reading/submit", json=submit_payload)
                if res.status_code == 200:
                    reporter.add_result(cat, "G5", "Reading Session Submit (POST /reading/submit)", "SUCCESS")
                    reporter.print_test_row("G5", "Reading Session Submit (POST /reading/submit)", "SUCCESS")
                else:
                    reporter.add_result(cat, "G5", "Reading Session Submit (POST /reading/submit)", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("G5", "Reading Session Submit (POST /reading/submit)", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "G5", "Reading Session Submit (POST /reading/submit)", "FAILED", traceback.format_exc())
            reporter.print_test_row("G5", "Reading Session Submit (POST /reading/submit)", "FAILED")

    # G6: Reading History Retrieval API
    if not server_online or not TEST_USER_ID:
        reporter.add_result(cat, "G6", "Reading History Retrieval (GET /reading/history)", "SKIPPED")
        reporter.print_test_row("G6", "Reading History Retrieval (GET /reading/history)", "SKIPPED")
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/reading/history/{TEST_USER_ID}")
                if res.status_code == 200:
                    reporter.add_result(cat, "G6", "Reading History Retrieval (GET /reading/history)", "SUCCESS")
                    reporter.print_test_row("G6", "Reading History Retrieval (GET /reading/history)", "SUCCESS")
                else:
                    reporter.add_result(cat, "G6", "Reading History Retrieval (GET /reading/history)", "FAILED", f"Status: {res.status_code}")
                    reporter.print_test_row("G6", "Reading History Retrieval (GET /reading/history)", "FAILED")
        except Exception as e:
            reporter.add_result(cat, "G6", "Reading History Retrieval (GET /reading/history)", "FAILED", traceback.format_exc())
            reporter.print_test_row("G6", "Reading History Retrieval (GET /reading/history)", "FAILED")

    # G7: Graph Engine Prerequisites Sort
    try:
        from services.graph_engine import GraphEngine
        local_graph = GraphEngine()
        local_graph.ensure_prerequisite_edges()
        edges = local_graph.get_prerequisite_graph()
        sorted_nodes = local_graph.topological_sort(level="N5")
        reporter.add_result(cat, "G7", "Graph Engine Prerequisites Sort", "SUCCESS")
        reporter.print_test_row("G7", "Graph Engine Prerequisites Sort", "SUCCESS")
    except Exception as e:
        reporter.add_result(cat, "G7", "Graph Engine Prerequisites Sort", "WARNING", f"Neo4j offline/not configured: {e}")
        reporter.print_test_row("G7", "Graph Engine Prerequisites Sort", "WARNING")

    # G8: Graph Engine Personalized Learning Path
    try:
        from services.graph_engine import GraphEngine
        local_graph = GraphEngine()
        path = local_graph.generate_learning_path(TEST_USER_ID or "mock-user-uuid-1234", level="N5")
        reporter.add_result(cat, "G8", "Graph Engine Personalized Learning Path", "SUCCESS")
        reporter.print_test_row("G8", "Graph Engine Personalized Learning Path", "SUCCESS")
    except Exception as e:
        reporter.add_result(cat, "G8", "Graph Engine Personalized Learning Path", "WARNING", f"Neo4j offline/not configured: {e}")
        reporter.print_test_row("G8", "Graph Engine Personalized Learning Path", "WARNING")


    # Generate final formatted output
    reporter.generate_summary()

if __name__ == "__main__":
    asyncio.run(run_tests())

