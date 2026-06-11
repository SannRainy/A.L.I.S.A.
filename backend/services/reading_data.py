"""
Reading Material Data — Leveled Japanese texts for reading comprehension module.
Each passage has text, vocabulary annotations, and comprehension questions.
"""

READING_PASSAGES = [
    # ── Level 1: Beginner ────────────────────────────────────────────────
    {
        "id": "read_1",
        "level": "beginner",
        "title": "じこしょうかい (Perkenalan Diri)",
        "text": "私はクリスです。学生です。日本語の文化が好きです。毎日日本語を練習します。すみません、あなたも学生ですか。",
        "translation": "Saya adalah Chris. Saya pelajar. Saya suka budaya Jepang. Setiap hari melatih bahasa Jepang. Permisi, apakah Anda juga seorang pelajar?",
        "vocab_annotations": [
            {"word": "私", "reading": "watashi", "meaning": "saya"},
            {"word": "学生", "reading": "gakusei", "meaning": "pelajar"},
            {"word": "日本語", "reading": "nihongo", "meaning": "bahasa Jepang"},
            {"word": "文化", "reading": "bunka", "meaning": "budaya"},
            {"word": "好き", "reading": "suki", "meaning": "suka"},
            {"word": "毎日", "reading": "mainichi", "meaning": "setiap hari"},
            {"word": "練習", "reading": "renshuu", "meaning": "latihan / melatih"},
        ],
        "questions": [
            {
                "id": "rq_1_1",
                "question": "クリスさんは何が好きですか。",
                "question_id": "Apa yang disukai oleh Chris?",
                "options": ["スポーツ", "文化", "野菜", "お酒"],
                "correct": 1,
            },
            {
                "id": "rq_1_2",
                "question": "クリスさんは毎日何をしますか。",
                "question_id": "Apa yang dilakukan Chris setiap hari?",
                "options": ["サッカー", "映画", "練習", "料理"],
                "correct": 2,
            },
        ],
    },
    # ── Level 2: Beginner ────────────────────────────────────────────────
    {
        "id": "read_2",
        "level": "beginner",
        "title": "お昼ご飯を食べませんか (Makan Siang Bersama)",
        "text": "A: 私と一緒に お昼ご飯を 食べませんか。\nB: いいですね。駅の 近くの レストランで 食べましょう。\nA: 私は 魚が 好きですが、肉も 好きです。\nB: じゃあ、駅で 会いましょうね。お茶か コーヒーも 飲みましょう。",
        "translation": "A: Maukah Anda makan siang bersama saya? B: Bagus ya. Mari makan di restoran dekat stasiun. A: Saya suka ikan, tapi saya juga suka daging. B: Kalau begitu, mari bertemu di stasiun ya. Mari minum teh atau kopi juga.",
        "vocab_annotations": [
            {"word": "お昼ご飯", "reading": "ohiru gohan", "meaning": "makan siang"},
            {"word": "一緒に", "reading": "issho ni", "meaning": "bersama-sama"},
            {"word": "駅", "reading": "eki", "meaning": "stasiun"},
            {"word": "近く", "reading": "chikaku", "meaning": "dekat"},
            {"word": "魚", "reading": "sakana", "meaning": "ikan"},
            {"word": "肉", "reading": "niku", "meaning": "daging"},
            {"word": "お茶", "reading": "ocha", "meaning": "teh"},
            {"word": "コーヒー", "reading": "koohii", "meaning": "kopi"},
        ],
        "questions": [
            {
                "id": "rq_2_1",
                "question": "二人はどこで会いますか。",
                "question_id": "Di mana mereka berdua akan bertemu?",
                "options": ["学校", "レストラン", "駅", "公園"],
                "correct": 2,
            },
            {
                "id": "rq_2_2",
                "question": "二人は何を飲みますか。",
                "question_id": "Apa yang akan mereka minum?",
                "options": ["水かお酒", "お茶かコーヒー", "ジュース", "牛乳"],
                "correct": 1,
            },
        ],
    },
    # ── Level 3: Intermediate ──────────────────────────────────────────
    {
        "id": "read_3",
        "level": "intermediate",
        "title": "ケーキの作り方とお箸 (Cara Membuat Kue dan Sumpit)",
        "text": "私は ケーキを 作るのが 好きです。あなたは ケーキの 作り方を 知っていますか。とても 簡単ですよ。\n\n\nでも、私は おはしの 使い方が 下手です。おはしの 使い方が 上手になりたいです。教えてください。",
        "translation": "Saya suka membuat kue. Apakah Anda tahu cara membuat kue? Sangat mudah lho. Tapi, saya payah dalam menggunakan sumpit. Saya ingin menjadi mahir dalam menggunakan sumpit. Tolong ajari saya.",
        "vocab_annotations": [
            {"word": "作り方", "reading": "tsukurikata", "meaning": "cara membuat"},
            {"word": "知っています", "reading": "shitteimasu", "meaning": "tahu/mengetahui"},
            {"word": "簡単", "reading": "kantan", "meaning": "mudah"},
            {"word": "おはし", "reading": "ohashi", "meaning": "sumpit"},
            {"word": "使い方", "reading": "tsukaikata", "meaning": "cara menggunakan"},
            {"word": "下手", "reading": "heta", "meaning": "payah/tidak mahir"},
            {"word": "上手", "reading": "jouzu", "meaning": "mahir/pandai"},
        ],
        "questions": [
            {
                "id": "rq_3_1",
                "question": "私は何を作るのが好きですか。",
                "question_id": "Saya suka membuat apa?",
                "options": ["おはし", "料理", "ケーキ", "ごはん"],
                "correct": 2,
            },
            {
                "id": "rq_3_2",
                "question": "私は何が下手ですか。",
                "question_id": "Saya payah dalam hal apa?",
                "options": ["おはしの使い方", "ケーキの作り方", "日本語の勉強", "お茶を飲むこと"],
                "correct": 0,
            },
        ],
    },
    # ── Level 4: Intermediate ──────────────────────────────────────────
    {
        "id": "read_4",
        "level": "intermediate",
        "title": "日曜日の予定と趣味 (Rencana Hari Minggu dan Hobi)",
        "text": "日曜日は 買い物したり、映画を 見たりしました。自転車が こわれたから、新しい 自転車を 買いに 行きました。\n日本語を もっと 勉強したいですから、日本語の 本も 買いました。将来は 日本の 会社で 働きたいです。",
        "translation": "Pada hari Minggu saya pergi belanja dan menonton film. Karena sepeda saya rusak, saya pergi membeli sepeda baru. Karena saya ingin belajar bahasa Jepang lebih banyak, saya juga membeli buku bahasa Jepang. Di masa depan, saya ingin bekerja di perusahaan Jepang.",
        "vocab_annotations": [
            {"word": "買い物", "reading": "kaimono", "meaning": "belanja"},
            {"word": "映画", "reading": "eiga", "meaning": "film"},
            {"word": "自転車", "reading": "jitensha", "meaning": "sepeda"},
            {"word": "こわれた", "reading": "kowareta", "meaning": "rusak"},
            {"word": "新しい", "reading": "atarashii", "meaning": "baru"},
            {"word": "勉強したい", "reading": "benkyou shitai", "meaning": "ingin belajar"},
            {"word": "将来", "reading": "shourai", "meaning": "masa depan"},
            {"word": "会社", "reading": "kaisha", "meaning": "perusahaan"},
            {"word": "働きたい", "reading": "hatarakitai", "meaning": "ingin bekerja"},
        ],
        "questions": [
            {
                "id": "rq_4_1",
                "question": "日曜日に何をしましたか。",
                "question_id": "Apa yang dilakukan di hari Minggu?",
                "options": ["運動したり本を読んだりした", "買い物したり映画を見たりした", "仕事をしたり掃除をしたりした", "旅行したり歌ったりした"],
                "correct": 1,
            },
            {
                "id": "rq_4_2",
                "question": "なぜ日本語の本を買いましたか。",
                "question_id": "Mengapa membeli buku bahasa Jepang?",
                "options": ["日本語をもっと勉強したいから", "自転車がこわれたから", "友達にあげるから", "安かったから"],
                "correct": 0,
            },
            {
                "id": "rq_4_3",
                "question": "将来はどこで働きたいですか。",
                "question_id": "Di mana ingin bekerja di masa depan?",
                "options": ["アメリカの会社", "日本の会社", "学校", "デパート"],
                "correct": 1,
            },
        ],
    },
    # ── Level 5: Advanced ─────────────────────────────────────────────
    {
        "id": "read_5",
        "level": "advanced",
        "title": "準備と美味しい料理 (Persiapan dan Masakan Lezat)",
        "text": "今日の お昼ご飯は 食堂が とても 混んでいます。でも、私の 家には 料理が 作ってありますから、家で 食べます。\nお母さんは 「肉だけじゃなくて、野菜も 食べたほうが いいですよ」と言いました。寝る前には スマホを 見ては いけません。早く 寝たほうが いいです。",
        "translation": "Makan siang hari ini kafetaria sangat ramai. Tapi, karena masakan sudah dibuat (tersedia) di rumah saya, saya makan di rumah. Ibu berkata 'Jangan hanya makan daging saja, lebih baik makan sayur juga'. Sebelum tidur, tidak boleh melihat HP. Lebih baik tidur awal.",
        "vocab_annotations": [
            {"word": "食堂", "reading": "shokudou", "meaning": "kafetaria/tempat makan"},
            {"word": "混んでいます", "reading": "kondeimasu", "meaning": "ramai/padat"},
            {"word": "料理", "reading": "ryouri", "meaning": "masakan/makanan"},
            {"word": "作ってあります", "reading": "tsukutte arimasu", "meaning": "sudah dibuat/disediakan"},
            {"word": "野菜", "reading": "yasai", "meaning": "sayuran"},
            {"word": "寝る前", "reading": "neru mae", "meaning": "sebelum tidur"},
            {"word": "早く", "reading": "hayaku", "meaning": "awal/cepat"},
        ],
        "questions": [
            {
                "id": "rq_5_1",
                "question": "なぜ今日は家でお昼ごはんを食べますか。",
                "question_id": "Berdasarkan teks, mengapa makan siang di rumah hari ini?",
                "options": ["食堂が休みだから", "お金がないから", "料理が作ってあるから", "友達が来るから"],
                "correct": 2,
            },
            {
                "id": "rq_5_2",
                "question": "お母さんは何を食べたほうがいいと言いましたか。",
                "question_id": "Ibu menyarankan untuk makan apa?",
                "options": ["肉だけ", "魚だけ", "野菜も", "甘いもの"],
                "correct": 2,
            },
            {
                "id": "rq_5_3",
                "question": "寝る前に何をしてはいけませんか。",
                "question_id": "Apa yang tidak boleh dilakukan sebelum tidur?",
                "options": ["スマホを見ること", "お茶を飲むこと", "歯を磨くこと", "本を読むこと"],
                "correct": 0,
            },
        ],
    },
]


def get_reading_passages(level: str = None) -> list[dict]:
    """Get reading passages, optionally filtered by level."""
    if level:
        return [p for p in READING_PASSAGES if p["level"] == level]
    return READING_PASSAGES


def get_passage_by_id(passage_id: str) -> dict | None:
    """Get a specific passage by ID."""
    for p in READING_PASSAGES:
        if p["id"] == passage_id:
            return p
    return None
