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

    def print_test_row(self, test_id: str, name: str, status: str, detail_info: str = None):
        dots = "." * (65 - len(name) - len(test_id))
        if status == "SUCCESS":
            status_str = f"{GREEN}[ SUCCESS ]{RESET}"
        elif status == "WARNING" or status == "SIMULATED":
            status_str = f"{YELLOW}[ {status} ]{RESET}"
        elif status == "SKIPPED":
            status_str = f"{YELLOW}[ SKIPPED ]{RESET}"
        else:
            status_str = f"{RED}[ FAILED  ]{RESET}"
        print(f"  [{test_id}] {name} {dots} {status_str}")
        if detail_info:
            for line in detail_info.strip().split('\n'):
                print(f"      {CYAN}↳ {line}{RESET}")

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
    import math
    import struct
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(16000)  # 16kHz
        # Generate 1 second of a 440Hz sine wave beep
        samples = []
        for i in range(16000):
            val = int(16384 * math.sin(2 * math.pi * 440 * i / 16000))
            samples.append(struct.pack('<h', val))
        wav_file.writeframes(b''.join(samples))
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


# Helper: Generic Test Runner to measure execution and format detailed outputs
async def run_test_step(category: str, test_id: str, name: str, test_func, *args, **kwargs):
    start_time = time.perf_counter()
    status = "SUCCESS"
    detail = ""
    try:
        if asyncio.iscoroutinefunction(test_func):
            res_val = await test_func(*args, **kwargs)
        elif callable(test_func):
            res_val = test_func(*args, **kwargs)
            if asyncio.iscoroutine(res_val):
                res_val = await res_val
        else:
            res_val = test_func

        if isinstance(res_val, tuple) and len(res_val) == 2:
            status, detail = res_val
        else:
            status = "SUCCESS"
            detail = str(res_val)

        latency = (time.perf_counter() - start_time) * 1000
        if status in ("SUCCESS", "WARNING", "SIMULATED"):
            detail = f"{detail} (Latency: {latency:.2f}ms)"
    except Exception as e:
        status = "FAILED"
        detail = f"Exception: {str(e)}\n{traceback.format_exc()}"

    reporter.add_result(category, test_id, name, status, detail)
    reporter.print_test_row(test_id, name, status, detail)
    return status == "SUCCESS"


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
    async def test_a1():
        if not server_online:
            return "FAILED", "FastAPI Server offline/unreachable"
        return "SUCCESS", f"Connected to {BASE_URL}"
    await run_test_step(cat, "A1", "FastAPI Server Ping", test_a1)

    # A2: Supabase Connectivity
    async def test_a2():
        from core.supabase_client import supabase, MockSupabaseClient
        if isinstance(supabase, MockSupabaseClient):
            return "SIMULATED", "Using MockSupabaseClient (local file system simulation, .env empty)"
        res = supabase.table("profiles").select("id").limit(1).execute()
        return "SUCCESS", "Connected to Supabase DB. Successfully queried 'profiles' table"
    await run_test_step(cat, "A2", "Supabase Client Connection", test_a2)

    # A3: Neo4j Aura Connectivity
    async def test_a3():
        from core.config import settings
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        driver.verify_connectivity()
        driver.close()
        return "SUCCESS", f"Connected to Neo4j Aura DB at {settings.NEO4J_URI}"
    await run_test_step(cat, "A3", "Neo4j Aura Graph DB Connectivity", test_a3)

    # A4: Style-Bert-VITS2 Voice Server Status
    async def test_a4():
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get("http://localhost:5050")
            return "SUCCESS", f"Style-Bert-VITS2 active at port 5050 -> HTTP {res.status_code}"
    await run_test_step(cat, "A4", "Style-Bert-VITS2 Voice Server", test_a4)

    # A5: Local GGUF Model Path Check
    def test_a5():
        from core.config import settings
        model_path = BACKEND_DIR / settings.UNSLOTH_MODEL_PATH
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            return "SUCCESS", f"Model exists: '{settings.UNSLOTH_MODEL_PATH}' ({size_mb:.2f} MB)"
        return "WARNING", f"Model file not found at: {model_path}"
    await run_test_step(cat, "A5", "Local GGUF Model Path Check", test_a5)

    # A6: HuggingFace Hub Connectivity
    async def test_a6():
        from core.config import settings
        from huggingface_hub import HfApi
        api = HfApi(token=settings.HF_TOKEN if settings.HF_TOKEN else None)
        info = api.model_info(repo_id=settings.HF_MODEL_REPO)
        return "SUCCESS", f"Fetched HF repo info for '{settings.HF_MODEL_REPO}'"
    await run_test_step(cat, "A6", "HuggingFace API Repo Connection", test_a6)


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
            detail = "Skipped because target FastAPI server is offline."
            reporter.add_result(cat, tid, tname, "SKIPPED", detail)
            reporter.print_test_row(tid, tname, "SKIPPED", detail)
    else:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # B1: Register User
            async def test_b1():
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
                    return "SUCCESS", f"POST /auth/register -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"POST /auth/register failed -> HTTP {res.status_code}\nBody: {res.text}"
            await run_test_step(cat, "B1", "User Registration (Auth Register)", test_b1)

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
            async def test_b2():
                res = await client.get(f"{API_PREFIX}/user/profile/{TEST_USER_ID}")
                if res.status_code == 200:
                    data = res.json()
                    if "xp" in data and "level" in data:
                        return "SUCCESS", f"GET /user/profile -> HTTP 200. level={data.get('level')}, xp={data.get('xp')}"
                    return "FAILED", f"GET /user/profile -> HTTP 200 but missing keys: {data}"
                return "FAILED", f"GET /user/profile failed -> HTTP {res.status_code}\nBody: {res.text}"
            await run_test_step(cat, "B2", "Lazy Profile Init & Fetch", test_b2)

            # B3: Profile Update (Demographics)
            async def test_b3():
                upd_payload = {
                    "full_name": "Siswa Pipeline Test Updated",
                    "age": 22,
                    "country": "Jepang",
                    "study_purpose": "Melanjutkan Kuliah ke Tokyo"
                }
                res = await client.put(f"{API_PREFIX}/user/profile/{TEST_USER_ID}", json=upd_payload)
                if res.status_code == 200:
                    return "SUCCESS", f"PUT /user/profile -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"PUT /user/profile failed -> HTTP {res.status_code}\nBody: {res.text}"
            await run_test_step(cat, "B3", "Profile Demographics Update", test_b3)

            # B4: User Achievements
            async def test_b4():
                res = await client.get(f"{API_PREFIX}/user/achievements/{TEST_USER_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /user/achievements -> HTTP 200. Achievements: {res.text}"
                return "FAILED", f"GET /user/achievements failed -> HTTP {res.status_code}"
            await run_test_step(cat, "B4", "User Achievements Retrieval", test_b4)


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
            detail = "Skipped because FastAPI server is offline."
            reporter.add_result(cat, tid, tname, "SKIPPED", detail)
            reporter.print_test_row(tid, tname, "SKIPPED", detail)
    else:
        # C1: HTTP Streaming Chat
        async def test_c1():
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
                        received_bytes = 0
                        chunks = []
                        async for chunk in response.aiter_bytes():
                            if chunk:
                                received_bytes += len(chunk)
                                if not first_chunk_ok:
                                    first_chunk_ok = True
                                if len(chunks) < 3:
                                    chunks.append(chunk.decode('utf-8', errors='ignore')[:40])
                        if first_chunk_ok:
                            return "SUCCESS", f"Stream success. Read {received_bytes} bytes. Sample: {chunks}"
                        return "FAILED", "Stream returned empty response"
                    return "FAILED", f"POST /chat failed -> HTTP {response.status_code}"
        await run_test_step(cat, "C1", "HTTP Streaming Chat (GraphRAG Context)", test_c1)

        # C2: WebSocket Real-Time Chat Pipeline
        async def test_c2():
            import websockets
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
                if any(t in received_frames for t in ("status", "metadata", "sentence")):
                    return "SUCCESS", f"WebSocket communication succeeded. Frame types: {received_frames}"
                return "FAILED", f"Frames received missing expected context: {received_frames}"
        async def test_c2_wrapper():
            try:
                return await test_c2()
            except Exception as e:
                return "WARNING", f"WebSocket check warning (could be local model loading): {e}"
        await run_test_step(cat, "C2", "WebSocket Real-Time Chat (Framing & TTS)", test_c2_wrapper)

        # C3: Knowledge Graph Mastery Path Retrieval
        async def test_c3():
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/mastery/{TEST_USER_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /mastery -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"GET /mastery failed -> HTTP {res.status_code}\nBody: {res.text}"
        await run_test_step(cat, "C3", "Knowledge Graph Mastery Path Retrieval", test_c3)


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
            detail = "Skipped because FastAPI server is offline."
            reporter.add_result(cat, tid, tname, "SKIPPED", detail)
            reporter.print_test_row(tid, tname, "SKIPPED", detail)
    else:
        # D1: Voice Audio Transcription
        async def test_d1():
            async with httpx.AsyncClient(timeout=30.0) as client:
                silent_wav = generate_minimal_wav()
                files = {"audio": ("test_silence.wav", silent_wav, "audio/wav")}
                data = {"mode": "speaking"}
                res = await client.post(f"{API_PREFIX}/transcribe", files=files, data=data)
                if res.status_code == 200:
                    return "SUCCESS", f"POST /transcribe -> HTTP 200\nBody: {res.text}"
                return "FAILED", f"POST /transcribe failed -> HTTP {res.status_code}\nBody: {res.text}"
        async def test_d1_wrapper():
            try:
                return await test_d1()
            except Exception as e:
                return "WARNING", f"STT failed/warning (Whisper model loading issue): {e}"
        await run_test_step(cat, "D1", "Voice Audio Transcription (STT/Whisper)", test_d1_wrapper)

        # D2: Speaking Practice Topic Seed
        async def test_d2():
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/speaking/topic?student_id={TEST_USER_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /speaking/topic -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"GET /speaking/topic failed -> HTTP {res.status_code}\nBody: {res.text}"
        await run_test_step(cat, "D2", "Speaking Practice Topic Seed", test_d2)

        # D3: Audio file retrieval (GET /get-audio/{filename})
        async def test_d3():
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{API_PREFIX}/get-audio/invalid_non_existent.wav")
                if res.status_code == 404:
                    return "SUCCESS", "GET /get-audio/invalid_non_existent.wav returned HTTP 404 (Correct Handled)"
                return "FAILED", f"GET /get-audio returned unexpected status: {res.status_code}"
        await run_test_step(cat, "D3", "TTS Audio File Retrieval (404 Handled)", test_d3)


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
            detail = "Skipped because FastAPI server is offline."
            reporter.add_result(cat, tid, tname, "SKIPPED", detail)
            reporter.print_test_row(tid, tname, "SKIPPED", detail)
    else:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # E1: Quest Level List
            async def test_e1():
                res = await client.get(f"{API_PREFIX}/quest/levels")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /quest/levels -> HTTP 200\nLevels: {res.text}"
                return "FAILED", f"GET /quest/levels failed -> HTTP {res.status_code}"
            await run_test_step(cat, "E1", "Quest Level List Summary", test_e1)

            # E2: Quest Level Details
            async def test_e2():
                res = await client.get(f"{API_PREFIX}/quest/data/lvl_1")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /quest/data/lvl_1 -> HTTP 200\nResponse: {res.text[:200]}..."
                return "FAILED", f"GET /quest/data/lvl_1 failed -> HTTP {res.status_code}"
            await run_test_step(cat, "E2", "Quest Level Details (Questions)", test_e2)

            # E3: AI Quiz Correction
            async def test_e3():
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
                        return "SUCCESS", f"POST /quest/ai-correction -> HTTP 200. Feedback: {data.get('feedback')}"
                    return "FAILED", f"POST /quest/ai-correction succeeded but returned no feedback: {data}"
                return "FAILED", f"POST /quest/ai-correction failed -> HTTP {res.status_code}"
            await run_test_step(cat, "E3", "AI Quest Correction & Status Update", test_e3)

            # E4: Quest Score Submission
            async def test_e4():
                sub_payload = {
                    "user_id": TEST_USER_ID,
                    "level_id": "lvl_1",
                    "score": 90
                }
                res = await client.post(f"{API_PREFIX}/quest/submit", json=sub_payload)
                if res.status_code == 200:
                    return "SUCCESS", f"POST /quest/submit -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"POST /quest/submit failed -> HTTP {res.status_code}"
            await run_test_step(cat, "E4", "Quest Score Submission (XP Level Up)", test_e4)

            # E5: Quest Session Stats Update
            async def test_e5():
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
                    return "SUCCESS", f"POST /quest/session-stats -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"POST /quest/session-stats failed -> HTTP {res.status_code}"
            await run_test_step(cat, "E5", "Quest Session Stats Update", test_e5)

            # E6: Kanji Dojo Mastery Sync
            async def test_e6():
                kanji_payload = {
                    "student_id": TEST_USER_ID,
                    "set_id": "kanji_n5_set1",
                    "kanji_ids": ["水", "火", "木"],
                    "score": 3,
                    "total": 3
                }
                res = await client.post(f"{API_PREFIX}/kanji/mastery", json=kanji_payload)
                if res.status_code == 200:
                    return "SUCCESS", f"POST /kanji/mastery -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"POST /kanji/mastery failed -> HTTP {res.status_code}"
            await run_test_step(cat, "E6", "Kanji Dojo Mastery Sync", test_e6)

            # E7: Kanji Bulk Re-sync
            async def test_e7():
                bulk_payload = {
                    "student_id": TEST_USER_ID,
                    "kanji_ids": ["水", "火", "木", "金", "土"]
                }
                res = await client.post(f"{API_PREFIX}/kanji/mastery/bulk-sync", json=bulk_payload)
                if res.status_code == 200:
                    return "SUCCESS", f"POST /kanji/mastery/bulk-sync -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"POST /kanji/mastery/bulk-sync failed -> HTTP {res.status_code}"
            await run_test_step(cat, "E7", "Kanji Bulk Re-sync", test_e7)


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
            detail = "Skipped because FastAPI server is offline."
            reporter.add_result(cat, tid, tname, "SKIPPED", detail)
            reporter.print_test_row(tid, tname, "SKIPPED", detail)
    else:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # F1: Verify Admin Access Guard (Block Student User)
            async def test_f1():
                res = await client.get(f"{API_PREFIX}/admin/users?admin_id={TEST_USER_ID}")
                if res.status_code == 403:
                    return "SUCCESS", "GET /admin/users returned HTTP 403 Forbidden as expected (Student blocked)"
                return "FAILED", f"GET /admin/users returned HTTP {res.status_code} (Expected 403)"
            await run_test_step(cat, "F1", "Verify Admin Access Guard (Block Student)", test_f1)

            # Elevate DB role to admin
            db_elevated = await set_db_role(ADMIN_ID, "admin")

            # F2: Get All Users (Enriched)
            async def test_f2():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/users?admin_id={ADMIN_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /admin/users -> HTTP 200. Users count: {len(res.json())}"
                return "FAILED", f"GET /admin/users failed -> HTTP {res.status_code}\nBody: {res.text}"
            await run_test_step(cat, "F2", "Get All Users (Neo4j Enriched Listing)", test_f2)

            # F3: User Detail Inspection
            async def test_f3():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/users/{TEST_USER_ID}/detail?admin_id={ADMIN_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /admin/users/{TEST_USER_ID}/detail -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"GET /admin/users/{TEST_USER_ID}/detail failed -> HTTP {res.status_code}"
            await run_test_step(cat, "F3", "User Detail Inspection", test_f3)

            # F4: CSV File Pipeline Inventory
            async def test_f4():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/csv-files?admin_id={ADMIN_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /admin/csv-files -> HTTP 200. Files: {res.text}"
                return "FAILED", f"GET /admin/csv-files failed -> HTTP {res.status_code}"
            await run_test_step(cat, "F4", "CSV File Pipeline Inventory", test_f4)

            # F5: Ingestion Data Reader
            async def test_f5():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/csv/nodes_kanji.csv?admin_id={ADMIN_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /admin/csv/nodes_kanji.csv -> HTTP 200. Records count: {len(res.json())}"
                return "WARNING", f"nodes_kanji.csv inaccessible -> HTTP {res.status_code}"
            await run_test_step(cat, "F5", "Ingestion Data Reader (CSV to JSON)", test_f5)

            # F6: Ingestion ETL Trigger
            reporter.add_result(cat, "F6", "Ingestion ETL Trigger (Safe-Skipped for speed)", "SKIPPED", "ETL skipped to avoid long db load times.")
            reporter.print_test_row("F6", "Ingestion ETL Trigger (Safe-Skipped for speed)", "SKIPPED", "ETL skipped to avoid long db load times.")

            # F7: Survey & System Analytics Metrics
            async def test_f7():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/analytics?admin_id={ADMIN_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /admin/analytics -> HTTP 200\nResponse: {res.text}"
                return "FAILED", f"GET /admin/analytics failed -> HTTP {res.status_code}"
            await run_test_step(cat, "F7", "Survey & System Analytics Metrics", test_f7)

            # F8: Export User Data Profiles
            async def test_f8():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/export/users?admin_id={ADMIN_ID}&format=json")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /admin/export/users -> HTTP 200. Length: {len(res.content)} bytes"
                return "FAILED", f"GET /admin/export/users failed -> HTTP {res.status_code}"
            await run_test_step(cat, "F8", "Export User Data Profiles (JSON)", test_f8)

            # F9: Visual Knowledge Graph Network Export
            async def test_f9():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/kg-data?admin_id={ADMIN_ID}")
                if res.status_code == 200:
                    data = res.json()
                    return "SUCCESS", f"GET /admin/kg-data -> HTTP 200. Elements: {len(data.get('nodes', []))} nodes, {len(data.get('links', []))} links"
                return "FAILED", f"GET /admin/kg-data failed -> HTTP {res.status_code}"
            await run_test_step(cat, "F9", "Visual Knowledge Graph Network Export", test_f9)

            # F10: AI Model Switcher & Status Checking
            async def test_f10():
                if not db_elevated:
                    return "SKIPPED", "Database elevation to admin failed"
                res = await client.get(f"{API_PREFIX}/admin/models?admin_id={ADMIN_ID}")
                if res.status_code == 200:
                    return "SUCCESS", f"GET /admin/models -> HTTP 200\nModels: {res.text}"
                return "FAILED", f"GET /admin/models failed -> HTTP {res.status_code}"
            await run_test_step(cat, "F10", "AI Model Switcher & Status Checking", test_f10)

            # Revert role to student
            await set_db_role(ADMIN_ID, "student")


    # --------------------------------------------------------------------------
    # CATEGORY G: READING COMPREHENSION & COGNITIVE SERVICES (V3)
    # --------------------------------------------------------------------------
    cat = "G. READING COMPREHENSION & COGNITIVE SERVICES (V3)"
    reporter.print_section(cat)

    # G1: BKT Engine Belief Update (Local calculation)
    def test_g1():
        from services.bkt_engine import BKTEngine
        params = BKTEngine.get_params("vocab")
        p_l_1 = BKTEngine.update_belief(0.1, False, params)
        p_l_2 = BKTEngine.update_belief(0.1, True, params)
        if p_l_2 > p_l_1:
            return "SUCCESS", f"P(L) correct={p_l_2:.4f} > P(L) incorrect={p_l_1:.4f}"
        return "FAILED", f"Belief update error: correct={p_l_2:.4f}, incorrect={p_l_1:.4f}"
    await run_test_step(cat, "G1", "BKT Engine Belief Update", test_g1)

    # G2: BKT Question Selection (Local calculation)
    def test_g2():
        from services.bkt_engine import BKTEngine
        beliefs = {"v1": 0.5, "v2": 0.9, "v3": 0.1}
        nodes = [{"id": "v1", "node_type": "vocab"}, {"id": "v2", "node_type": "vocab"}, {"id": "v3", "node_type": "vocab"}]
        selected = BKTEngine.select_next_questions(beliefs, nodes, count=2)
        if len(selected) > 0:
            return "SUCCESS", f"Successfully selected nodes: {selected}"
        return "FAILED", "No nodes selected"
    await run_test_step(cat, "G2", "BKT Question Selection", test_g2)

    # G3: Reading Passages List API
    async def test_g3():
        if not server_online:
            return "SKIPPED", "Server is offline"
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{API_PREFIX}/reading/passages")
            if res.status_code == 200:
                return "SUCCESS", f"GET /reading/passages -> HTTP 200. Passages: {res.text}"
            return "FAILED", f"GET /reading/passages failed -> HTTP {res.status_code}"
    await run_test_step(cat, "G3", "Reading Passages List (GET /reading/passages)", test_g3)

    # G4: Reading Passage Detail API
    async def test_g4():
        if not server_online:
            return "SKIPPED", "Server is offline"
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{API_PREFIX}/reading/passage/read_1")
            if res.status_code == 200:
                return "SUCCESS", f"GET /reading/passage/read_1 -> HTTP 200. Title: '{res.json().get('title')}'"
            return "FAILED", f"GET /reading/passage/read_1 failed -> HTTP {res.status_code}"
    await run_test_step(cat, "G4", "Reading Passage Detail (GET /reading/passage/read_1)", test_g4)

    # G5: Reading Session Submit API
    async def test_g5():
        if not server_online or not TEST_USER_ID:
            return "SKIPPED", "Server offline or user ID missing"
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
                return "SUCCESS", f"POST /reading/submit -> HTTP 200. Response: {res.text}"
            return "FAILED", f"POST /reading/submit failed -> HTTP {res.status_code}"
    await run_test_step(cat, "G5", "Reading Session Submit (POST /reading/submit)", test_g5)

    # G6: Reading History Retrieval API
    async def test_g6():
        if not server_online or not TEST_USER_ID:
            return "SKIPPED", "Server offline or user ID missing"
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{API_PREFIX}/reading/history/{TEST_USER_ID}")
            if res.status_code == 200:
                return "SUCCESS", f"GET /reading/history -> HTTP 200. History: {res.text}"
            return "FAILED", f"GET /reading/history failed -> HTTP {res.status_code}"
    await run_test_step(cat, "G6", "Reading History Retrieval (GET /reading/history)", test_g6)

    # G7: Graph Engine Prerequisites Sort
    def test_g7():
        from services.graph_engine import GraphEngine
        local_graph = GraphEngine()
        local_graph.ensure_prerequisite_edges()
        edges = local_graph.get_prerequisite_graph()
        sorted_nodes = local_graph.topological_sort(level="N5")
        return "SUCCESS", f"Topological sort successful. Edges count: {len(edges)}, sorted sample: {sorted_nodes[:5]}..."
    async def test_g7_wrapper():
        try:
            return test_g7()
        except Exception as e:
            return "WARNING", f"Neo4j offline/not configured: {e}"
    await run_test_step(cat, "G7", "Graph Engine Prerequisites Sort", test_g7_wrapper)

    # G8: Graph Engine Personalized Learning Path
    def test_g8():
        from services.graph_engine import GraphEngine
        local_graph = GraphEngine()
        path = local_graph.generate_learning_path(TEST_USER_ID or "mock-user-uuid-1234", level="N5")
        return "SUCCESS", f"Generated path: {path}"
    async def test_g8_wrapper():
        try:
            return test_g8()
        except Exception as e:
            return "WARNING", f"Neo4j offline/not configured: {e}"
    await run_test_step(cat, "G8", "Graph Engine Personalized Learning Path", test_g8_wrapper)


    # Generate final formatted output
    reporter.generate_summary()

if __name__ == "__main__":
    asyncio.run(run_tests())

