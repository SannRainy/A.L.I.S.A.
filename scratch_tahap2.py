import os

target = r"c:\Users\satya\OneDrive\Desktop\TVJP\Feature.md"

tahap2_content = """

---

## Tahap 2: Pemetaan Arsitektur Backend (FastAPI & Logika Inti)

Struktur *backend* berbasis FastAPI membagi tanggung jawabnya ke dalam dua lapisan utama: **API Routers** (gerbang komunikasi klien) dan **Services** (otak algoritma logika). 

### 1. Daftar *Service* (Logika Sistem & Algoritma Akar)
Service merupakan modul independen di `backend/services/` yang memproses komputasi berat di belakang layar:
1. **`bkt_engine.py` (Bayesian Knowledge Tracing):** Algoritma statistik tersembunyi yang terus-menerus memperbarui probabilitas penguasaan (*Mastery Probability*) materi pengguna setiap kali kuis (*Quest*) dijawab.
2. **`srs_service.py` (Spaced Repetition System):** Algoritma penjadwalan interval berbasis modifikasi SM-2 untuk mengatur kapan *flashcard* harus dimunculkan kembali (`easiness_factor`, `interval_days`).
3. **`graph_engine.py` (Topological Sorter):** Mesin perutean graf yang berkomunikasi dengan Neo4j. Bertugas mencari jalur terpendek (*shortest path*) materi belajar dan melakukan *seed prerequisites* agar materi tidak melompat.
4. **`llm_agent.py`:** Pipeline instruksi (*Prompt Engineering*) yang menggerakkan model *Large Language Model* lokal (seperti Qwen) untuk merespons percakapan, mengoreksi tata bahasa (*AI Correction*), dan menghasilkan pertanyaan kuis secara dinamis.
5. **`voice_service.py`:** Penghubung modul *Speech-to-Text* (Transkripsi Audio) dan *Text-to-Speech* (Audio Output) yang menjadi nyawa sinkronisasi bibir (*lip-sync*) model 3D VRM.
6. **`streak_service.py`:** Logika gamifikasi yang memvalidasi *login* harian, menghitung akumulasi *Experience Points* (XP), dan mendeteksi pencapaian.

### 2. Daftar API Endpoints (*Routers*)

#### A. `feature_router.py` (Modul Pembelajaran Kognitif)
*Router* ini menangani seluruh *core features* belajar pengguna:
- **SRS & Penjadwalan:** `GET /srs/due/{user_id}`, `POST /srs/review`, `GET /srs/forecast/{user_id}`
- **Alur Graf Pembelajaran:** `GET /learning-path/{user_id}`, `GET /kg/shortest-path/...`
- **Tes Penempatan:** `GET /placement/questions`, `POST /placement/submit`
- **Evaluasi Teks Terstruktur:**
  - `POST /grammar/check` (Umpan balik tata bahasa)
  - `POST /reading/submit` (Penilaian membaca teks)
  - `POST /writing/submit` (Penilaian kreatif menulis)
- **Gamifikasi & Target:** `GET /streak/calendar`, `PUT /daily-goals`

#### B. `chat_router.py` (Modul Interaksi LLM & Sinkronisasi BKT)
*Router* ini mengintegrasikan agen AI dengan UI klien:
- **Percakapan & Suara:** `POST /chat`, `POST /transcribe`, `GET /get-audio/{filename}` (Streaming audio ke SvelteKit untuk VRM).
- **Mekanisme Quest (BKT):** `POST /generate-quest`, `POST /quest/submit`, `POST /quest/ai-correction` (Memicu BKT Engine).
- **Sinkronisasi Graf:** `POST /kanji/mastery/bulk-sync` (Mengunci status MASTERED dari SvelteKit ke Supabase dan Neo4j).
- **Profil User:** `POST /auth/register`, `PUT /user/profile/{user_id}`.

#### C. `admin_router.py` (Modul Operasional & Riset Tertutup)
*Router* ini dilindungi oleh fungsi otorisasi `get_admin_user` khusus untuk peran Peneliti/Dosen:
- **Pengawasan User:** `GET /users`, `GET /users/{user_id}/detail` (Pemantauan kemajuan belajar spesifik untuk riset BKT).
- **Manajemen Pipeline CSV:** `GET /csv-files`, `GET /csv/{filename}` (Untuk mengedit *nodes* Neo4j langsung dari tabel *browser* tanpa *rebuild* aplikasi).
"""

with open(target, 'a', encoding='utf-8') as f:
    f.write(tahap2_content)

print("Tahap 2 berhasil ditambahkan!")
