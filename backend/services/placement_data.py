"""
Placement Test Data — Adaptive onboarding assessment
30 questions across kanji, vocab, grammar, and listening comprehension.
Questions ordered by difficulty for adaptive early-exit.
"""

PLACEMENT_QUESTIONS = [
    # ── EASY (absolute beginner check) ──────────────────────────────────────
    {
        "id": "pt_1",
        "category": "vocab",
        "difficulty": "easy",
        "type": "mcq",
        "question": "'Ohayou gozaimasu' artinya apa?",
        "options": ["Selamat pagi", "Selamat malam", "Terima kasih", "Permisi"],
        "correct": 0,
    },
    {
        "id": "pt_2",
        "category": "vocab",
        "difficulty": "easy",
        "type": "mcq",
        "question": "Kata 'arigatou' berarti...",
        "options": ["Maaf", "Terima kasih", "Halo", "Selamat tinggal"],
        "correct": 1,
    },
    {
        "id": "pt_3",
        "category": "kanji",
        "difficulty": "easy",
        "type": "mcq",
        "question": "Angka berapa yang ditulis dengan kanji 三?",
        "options": ["1", "2", "3", "4"],
        "correct": 2,
    },
    {
        "id": "pt_4",
        "category": "grammar",
        "difficulty": "easy",
        "type": "mcq",
        "question": "'Watashi wa gakusei desu' berarti...",
        "options": [
            "Saya adalah guru",
            "Saya adalah pelajar",
            "Dia adalah pelajar",
            "Kamu adalah pelajar",
        ],
        "correct": 1,
    },
    {
        "id": "pt_5",
        "category": "vocab",
        "difficulty": "easy",
        "type": "mcq",
        "question": "'Neko' dalam bahasa Indonesia adalah...",
        "options": ["Anjing", "Kucing", "Burung", "Ikan"],
        "correct": 1,
    },
    # ── EASY-MEDIUM ──────────────────────────────────────────────────────────
    {
        "id": "pt_6",
        "category": "grammar",
        "difficulty": "easy",
        "type": "fill",
        "question": "Kore ___ hon desu. (Ini adalah buku) — isi partikel yang tepat",
        "correct": "wa",
    },
    {
        "id": "pt_7",
        "category": "kanji",
        "difficulty": "easy",
        "type": "mcq",
        "question": "Kanji 日 dibaca...",
        "options": ["Tsuki", "Nichi / Hi", "Mizu", "Ka"],
        "correct": 1,
    },
    {
        "id": "pt_8",
        "category": "vocab",
        "difficulty": "easy",
        "type": "mcq",
        "question": "'Tabemasu' artinya...",
        "options": ["Minum", "Makan", "Tidur", "Berjalan"],
        "correct": 1,
    },
    {
        "id": "pt_9",
        "category": "grammar",
        "difficulty": "easy",
        "type": "mcq",
        "question": "Partikel yang menunjukkan objek langsung kata kerja adalah...",
        "options": ["は (wa)", "の (no)", "を (o)", "に (ni)"],
        "correct": 2,
    },
    {
        "id": "pt_10",
        "category": "kanji",
        "difficulty": "easy",
        "type": "mcq",
        "question": "Kanji 水 berarti...",
        "options": ["Api", "Angin", "Air", "Tanah"],
        "correct": 2,
    },
    # ── MEDIUM ──────────────────────────────────────────────────────────────
    {
        "id": "pt_11",
        "category": "grammar",
        "difficulty": "medium",
        "type": "mcq",
        "question": "'Nihon ni ikimasu' — partikel 'ni' menunjukkan...",
        "options": ["Objek", "Waktu", "Tujuan/arah", "Tempat keberadaan"],
        "correct": 2,
    },
    {
        "id": "pt_12",
        "category": "vocab",
        "difficulty": "medium",
        "type": "fill",
        "question": "Lawan kata dari 'ookii' (besar) adalah...",
        "correct": "chiisai",
    },
    {
        "id": "pt_13",
        "category": "grammar",
        "difficulty": "medium",
        "type": "mcq",
        "question": "'Kono heya ni isu ga arimasu' berarti...",
        "options": [
            "Ada orang di kamar ini",
            "Ada kursi di kamar ini",
            "Tidak ada meja di kamar ini",
            "Saya pergi ke kamar ini",
        ],
        "correct": 1,
    },
    {
        "id": "pt_14",
        "category": "kanji",
        "difficulty": "medium",
        "type": "mcq",
        "question": "Kanji 食べる (taberu) mengandung kanji 食 yang berarti...",
        "options": ["Minum", "Makan", "Memasak", "Memotong"],
        "correct": 1,
    },
    {
        "id": "pt_15",
        "category": "grammar",
        "difficulty": "medium",
        "type": "mcq",
        "question": "'Ano eiga wa omoshiroku nakatta desu.' Bentuk ini adalah...",
        "options": [
            "i-adjective present negative",
            "i-adjective past negative",
            "na-adjective present negative",
            "na-adjective past negative",
        ],
        "correct": 1,
    },
    {
        "id": "pt_16",
        "category": "vocab",
        "difficulty": "medium",
        "type": "mcq",
        "question": "'Byouin' dalam bahasa Indonesia berarti...",
        "options": ["Sekolah", "Rumah sakit", "Kantor pos", "Perpustakaan"],
        "correct": 1,
    },
    {
        "id": "pt_17",
        "category": "grammar",
        "difficulty": "medium",
        "type": "fill",
        "question": "Nihongo ___ hanasu koto ga dekimasu. (Bisa berbicara bahasa Jepang) — isi partikel.",
        "correct": "o",
    },
    {
        "id": "pt_18",
        "category": "kanji",
        "difficulty": "medium",
        "type": "mcq",
        "question": "Kanji 学生 dibaca...",
        "options": ["Sensei", "Gakusei", "Seikatsu", "Gakkou"],
        "correct": 1,
    },
    {
        "id": "pt_19",
        "category": "grammar",
        "difficulty": "medium",
        "type": "mcq",
        "question": "'Te-kudasai' digunakan untuk...",
        "options": [
            "Menyatakan keinginan",
            "Meminta tolong / perintah sopan",
            "Menyatakan kemampuan",
            "Menyatakan kebiasaan",
        ],
        "correct": 1,
    },
    {
        "id": "pt_20",
        "category": "vocab",
        "difficulty": "medium",
        "type": "mcq",
        "question": "'Shigoto' berarti...",
        "options": ["Hobi", "Pekerjaan", "Liburan", "Pelajaran"],
        "correct": 1,
    },
    # ── HARD (N5 upper / borderline N4) ──────────────────────────────────
    {
        "id": "pt_21",
        "category": "grammar",
        "difficulty": "hard",
        "type": "mcq",
        "question": "'Nihon ni itta koto ga arimasu' berarti...",
        "options": [
            "Saya ingin pergi ke Jepang",
            "Saya sedang di Jepang",
            "Saya pernah pergi ke Jepang",
            "Saya akan pergi ke Jepang",
        ],
        "correct": 2,
    },
    {
        "id": "pt_22",
        "category": "grammar",
        "difficulty": "hard",
        "type": "mcq",
        "question": "'Ame ga furu mae ni, kasa o kaimashita.' — 'mae ni' berarti...",
        "options": ["Sesudah", "Sebelum", "Sementara", "Karena"],
        "correct": 1,
    },
    {
        "id": "pt_23",
        "category": "grammar",
        "difficulty": "hard",
        "type": "fill",
        "question": "Kono keeki wa amasugiru. (Kue ini terlalu manis.) Pola '~sugiru' menunjukkan...",
        "correct": "terlalu",
    },
    {
        "id": "pt_24",
        "category": "kanji",
        "difficulty": "hard",
        "type": "mcq",
        "question": "Kanji 時間 (jikan) berarti...",
        "options": ["Tempat", "Waktu/jam", "Uang", "Cuaca"],
        "correct": 1,
    },
    {
        "id": "pt_25",
        "category": "grammar",
        "difficulty": "hard",
        "type": "mcq",
        "question": "'Ashita ame ga furu deshou.' — 'deshou' menunjukkan...",
        "options": ["Kepastian", "Dugaan/perkiraan", "Keinginan", "Perintah"],
        "correct": 1,
    },
    {
        "id": "pt_26",
        "category": "grammar",
        "difficulty": "hard",
        "type": "mcq",
        "question": "'Benkyou shinakere ba narimasen' berarti...",
        "options": [
            "Tidak perlu belajar",
            "Harus belajar",
            "Ingin belajar",
            "Sudah belajar",
        ],
        "correct": 1,
    },
    {
        "id": "pt_27",
        "category": "vocab",
        "difficulty": "hard",
        "type": "fill",
        "question": "Lawan kata dari 'hayai' (cepat) adalah...",
        "correct": "osoi",
    },
    {
        "id": "pt_28",
        "category": "grammar",
        "difficulty": "hard",
        "type": "mcq",
        "question": "'Atsui node, mado o akemashita.' — 'node' digunakan untuk...",
        "options": [
            "Menyatakan tujuan",
            "Menyatakan alasan (objektif)",
            "Menyatakan waktu",
            "Menyatakan kontras",
        ],
        "correct": 1,
    },
    {
        "id": "pt_29",
        "category": "kanji",
        "difficulty": "hard",
        "type": "mcq",
        "question": "Kanji 新しい (atarashii) berarti...",
        "options": ["Tua", "Baru", "Mahal", "Murah"],
        "correct": 1,
    },
    {
        "id": "pt_30",
        "category": "grammar",
        "difficulty": "hard",
        "type": "mcq",
        "question": "'Tsumori' dalam 'Nihon ni iku tsumori desu' menunjukkan...",
        "options": [
            "Keharusan",
            "Rencana/niat",
            "Kemampuan",
            "Pengalaman",
        ],
        "correct": 1,
    },
]


def get_placement_questions() -> list[dict]:
    """Return all placement questions."""
    return PLACEMENT_QUESTIONS


def calculate_placement_result(answers: list[dict]) -> dict:
    """
    Calculate placement test result.

    answers: list of {"question_id": str, "user_answer": str|int, "is_correct": bool}

    Returns:
        total_score, estimated_level, category_scores,
        mastered_levels (which quest levels to skip)
    """
    category_scores = {"kanji": 0, "vocab": 0, "grammar": 0}
    category_totals = {"kanji": 0, "vocab": 0, "grammar": 0}
    total_correct = 0

    q_map = {q["id"]: q for q in PLACEMENT_QUESTIONS}

    for ans in answers:
        q = q_map.get(ans.get("question_id"))
        if not q:
            continue
        cat = q.get("category", "vocab")
        category_totals[cat] = category_totals.get(cat, 0) + 1
        if ans.get("is_correct"):
            total_correct += 1
            category_scores[cat] = category_scores.get(cat, 0) + 1

    total_questions = len(answers)
    accuracy = total_correct / max(total_questions, 1)

    # Determine level based on score distribution
    easy_correct = sum(
        1 for a in answers
        if a.get("is_correct") and q_map.get(a["question_id"], {}).get("difficulty") == "easy"
    )
    medium_correct = sum(
        1 for a in answers
        if a.get("is_correct") and q_map.get(a["question_id"], {}).get("difficulty") == "medium"
    )
    hard_correct = sum(
        1 for a in answers
        if a.get("is_correct") and q_map.get(a["question_id"], {}).get("difficulty") == "hard"
    )

    if accuracy >= 0.8 and hard_correct >= 5:
        estimated_level = "N5_high"
    elif accuracy >= 0.6 and medium_correct >= 4:
        estimated_level = "N5_mid"
    elif accuracy >= 0.4 and easy_correct >= 6:
        estimated_level = "N5_low"
    else:
        estimated_level = "absolute_beginner"

    # Map to quest levels that can be skipped
    level_skip_map = {
        "absolute_beginner": [],
        "N5_low": ["lvl_1", "lvl_2"],
        "N5_mid": ["lvl_1", "lvl_2", "lvl_3", "lvl_4", "lvl_5"],
        "N5_high": ["lvl_1", "lvl_2", "lvl_3", "lvl_4", "lvl_5", "lvl_6", "lvl_7"],
    }

    return {
        "total_score": total_correct,
        "total_questions": total_questions,
        "accuracy": round(accuracy * 100, 1),
        "estimated_level": estimated_level,
        "category_scores": category_scores,
        "category_totals": category_totals,
        "mastered_levels": level_skip_map.get(estimated_level, []),
    }
