QUEST_LEVELS = [
    {
        "id": "lvl_1",
        "title": "Level 1: Partikel Dasar",
        "description": "Kuasai partikel penanda topik, subjek, dan kepemilikan (Wa, Ga, No).",
        "icon": "⚔️",
        "questions": [
            {
                "id": "q1_1",
                "type": "mcq",
                "node_id": "は",
                "question": "Watashi ___ Alisa desu. (Saya adalah Alisa)",
                "options": ["Wa", "Ga", "No", "O"],
                "correct": 0,
                "explanation": "Partikel Wa (は) digunakan untuk menandai topik utama kalimat."
            },
            {
                "id": "q1_2",
                "type": "mcq",
                "node_id": "の",
                "question": "Watashi ___ namae wa Tanaka desu. (Nama SAYA adalah Tanaka)",
                "options": ["Wa", "Ga", "No", "De"],
                "correct": 2,
                "explanation": "Partikel No (の) menunjukkan kepemilikan (Possessive)."
            },
            {
                "id": "q1_3",
                "type": "mcq",
                "node_id": "を",
                "question": "Gohan ___ tabemasu. (Makan nasi)",
                "options": ["Wa", "Ni", "No", "O"],
                "correct": 3,
                "explanation": "Partikel O (を) menandai objek langsung dari kata kerja."
            },
            {
                "id": "q1_4",
                "type": "fill",
                "node_id": "の",
                "question": "Anata ___ kuruma desu ka? (Apakah ini mobil ANDA?)",
                "correct": "no",
                "explanation": "No digunakan untuk kepemilikan."
            },
            {
                "id": "q1_5",
                "type": "fill",
                "node_id": "に",
                "question": "Sensei ___ hanashimasu. (Berbicara kepada GURU)",
                "correct": "ni",
                "explanation": "Partikel Ni (に) menunjukkan arah atau target tindakan."
            }
        ]
    },
    {
        "id": "lvl_2",
        "title": "Level 2: Desu & Adjective",
        "description": "Belajar pola kalimat dasar 'to-be' dan kata sifat i/na.",
        "icon": "🛡️",
        "questions": [
            {
                "id": "q2_1",
                "type": "mcq",
                "node_id": "Akhiran です、 だ",
                "question": "Kyou wa samui ___ ne. (Hari ini dingin ya)",
                "options": ["Da", "Desu", "Na", "No"],
                "correct": 1,
                "explanation": "Desu adalah bentuk sopan dari kopula 'to-be'."
            },
            {
                "id": "q2_2",
                "type": "mcq",
                "node_id": "い-adjectives",
                "question": "Kono ringo wa ___ desu. (Apel ini MANIS)",
                "options": ["Oishii", "Amai", "Karai", "Nigai"],
                "correct": 1,
                "explanation": "Amai berarti manis."
            },
            {
                "id": "q2_3",
                "type": "mcq",
                "node_id": "na-adjectives",
                "question": "Ano hito wa ___ desu. (Orang itu BAIK HATI - Na Adj)",
                "options": ["Shinsetsu", "Tanoshime", "Atsui", "Samui"],
                "correct": 0,
                "explanation": "Shinsetsu (親切) adalah kata sifat-na yang berarti baik hati."
            },
            {
                "id": "q2_4",
                "type": "fill",
                "node_id": "い-adjectives",
                "question": "Kyou wa totemo ___ desu. (Hari ini sangat PANAS - i-adj)",
                "correct": "atsui",
                "explanation": "Atsui (暑い) berarti panas untuk cuaca."
            },
            {
                "id": "q2_5",
                "type": "fill",
                "node_id": "Akhiran です、 だ",
                "question": "Kinou wa ame ___ . (Kemarin [dulu] hujan)",
                "correct": "deshita",
                "explanation": "Deshita adalah bentuk lampau dari desu."
            }
        ]
    }
]
