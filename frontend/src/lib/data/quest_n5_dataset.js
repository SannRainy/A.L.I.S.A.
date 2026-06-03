// src/lib/data/quest_n5_dataset.js
/**
 * Dataset Quest JLPT N5
 * Berdasarkan: JLPT N5 Grammar Master by JLPTsensei.com (80 Grammar Lessons)
 *
 * Struktur:
 * - 9 Level, masing-masing 10 soal
 * - Kesulitan meningkat setiap 3 level (difficulty_tier: 1, 2, 3)
 * - Prerequisite antar level untuk mendukung "Pembelajaran Terstruktur"
 * - Tipe soal: 'mcq' (pilihan ganda), 'fill' (isian), 'translate' (terjemah → produksi aktif)
 *
 * Field per Level:
 *   id, title, icon, description, difficulty_tier, prerequisites (array node_id)
 *
 * Field per Soal:
 *   id, type, node_id, grammar_focus, question, [options/correct/acceptedAnswers], hint
 */

export const questLevels = [
    // ══════════════════════════════════════════════════════════════
    // TIER 1 — BEGINNER (Level 1–3)
    // ══════════════════════════════════════════════════════════════
    {
        id: "lvl_1",
        title: "Pondasi Dasar",
        icon: "🌱",
        difficulty_tier: 1,
        description: "Memperkenalkan diri dan menggunakan partikel dasar (wa, mo, no, desu).",
        prerequisites: [], // Level pertama, tidak ada prerequisite
        questions: [
            {
                id: "q_1_1",
                type: "mcq",
                node_id: "grammar_wa",
                grammar_focus: "Partikel は (wa) — Penanda topik",
                question: "Partikel apa yang digunakan untuk menandai topik utama kalimat?",
                options: ["を (o)", "は (wa)", "に (ni)", "へ (e)"],
                correctIndex: 1,
                hint: "Contoh: Watashi ___ Tanaka desu. (Saya [adalah] Tanaka.)"
            },
            {
                id: "q_1_2",
                type: "fill",
                node_id: "grammar_desu",
                grammar_focus: "だ・です (da/desu) — To be",
                question: "Lengkapi kalimat: Watashi wa gakusei ___. (Saya adalah siswa.)",
                correct: ["desu", "です", "da", "だ"],
                hint: "Kata bantu penutup kalimat sopan. Bentuk kasualnya adalah 'da'."
            },
            {
                id: "q_1_3",
                type: "mcq",
                node_id: "grammar_no",
                grammar_focus: "の (no) — Partikel kepemilikan",
                question: "Apa fungsi utama dari partikel 'no' (の)?",
                options: ["Menunjukkan kepemilikan / hubungan antar kata benda", "Menunjukkan tujuan", "Menunjukkan waktu", "Menunjukkan objek"],
                correctIndex: 0,
                hint: "Contoh: Watashi ___ hon = Buku saya. Ini seperti apostrophe-s dalam bahasa Inggris."
            },
            {
                id: "q_1_4",
                type: "fill",
                node_id: "grammar_mo",
                grammar_focus: "も (mo) — Juga / Pula",
                question: "Partikel yang berarti 'juga / pula' adalah ___.",
                correct: ["mo", "も"],
                hint: "Watashi ___ gakusei desu. (Saya juga seorang siswa.)"
            },
            {
                id: "q_1_5",
                type: "mcq",
                node_id: "grammar_ka",
                grammar_focus: "か (ka) — Partikel tanya",
                question: "Partikel apa yang diletakkan di akhir kalimat untuk membuat pertanyaan?",
                options: ["ね (ne)", "よ (yo)", "か (ka)", "な (na)"],
                correctIndex: 2,
                hint: "Diletakkan tepat setelah 'desu'. Contoh: Gakusei desu ___?"
            },
            {
                id: "q_1_6",
                type: "mcq",
                node_id: "grammar_dewa_nai",
                grammar_focus: "じゃない・ではない (janai/dewa nai) — Bentuk negatif to be",
                question: "Mana yang merupakan bentuk negatif dari 'desu' (bukan/tidak)?",
                options: ["dewa arimasen / ではありません", "desu nai", "dewa masu", "nai desu"],
                correctIndex: 0,
                hint: "Bentuk formal: 'dewa arimasen'. Bentuk kasual: 'janai' atau 'dewa nai'."
            },
            {
                id: "q_1_7",
                type: "mcq",
                node_id: "grammar_kore_sore_are",
                grammar_focus: "こ・そ・あ・ど系 (Ko-So-A-Do) — Kata penunjuk",
                question: "Kata untuk menunjukkan benda yang dekat dengan PEMBICARA adalah?",
                options: ["Sore (それ)", "Are (あれ)", "Kore (これ)", "Dore (どれ)"],
                correctIndex: 2,
                hint: "Ko = dekat pembicara, So = dekat pendengar, A = jauh dari keduanya, Do = tanya."
            },
            {
                id: "q_1_8",
                type: "fill",
                node_id: "grammar_dare",
                grammar_focus: "誰 (dare) — Kata tanya 'Siapa'",
                question: "Kata tanya untuk 'Siapa' dalam bahasa Jepang adalah ___.",
                correct: ["dare", "だれ", "donata", "どなた"],
                hint: "Onamae wa nan desu ka? vs ___ desu ka? (Siapa?)"
            },
            {
                id: "q_1_9",
                type: "translate",
                node_id: "grammar_desu",
                grammar_focus: "だ・です (da/desu) — Produksi kalimat dasar",
                question: "Terjemahkan: 'Nama saya adalah Alisa.' (Gunakan: namae / Arisa / desu / wa / watashi no)",
                acceptedAnswers: [
                    "watashi no namae wa arisa desu",
                    "watashi no namae wa arisa desu.",
                    "arisa desu",
                    "watashino namae wa arisa desu"
                ],
                hint: "Polanya: [Topik] wa [Subjek/Info] desu. 'Nama saya' = Watashi no namae."
            },
            {
                id: "q_1_10",
                type: "fill",
                node_id: "grammar_hai_iie",
                grammar_focus: "はい・いいえ (hai/iie) — Ya / Tidak",
                question: "Bahasa Jepang dari 'Ya' (setuju) adalah ___, dan 'Tidak' adalah ___.",
                correct: ["hai iie", "はい いいえ", "hai, iie"],
                hint: "Keduanya dipisah spasi. はい = hai, いいえ = iie."
            }
        ]
    },
    {
        id: "lvl_2",
        title: "Benda & Lokasi",
        icon: "🏠",
        difficulty_tier: 1,
        description: "Menunjukkan benda, tempat, dan keberadaan (arimasu/imasu).",
        prerequisites: ["grammar_wa", "grammar_desu", "grammar_no"],
        questions: [
            {
                id: "q_2_1",
                type: "mcq",
                node_id: "grammar_ga_arimasu",
                grammar_focus: "があります (ga arimasu) — Ada (benda mati)",
                question: "Kalimat mana yang benar untuk 'Ada buku di sini'?",
                options: ["Hon ga imasu", "Hon ga arimasu", "Hon o arimasu", "Hon ni imasu"],
                correctIndex: 1,
                hint: "Arimasu untuk benda mati/tidak bergerak. Imasu untuk makhluk hidup."
            },
            {
                id: "q_2_2",
                type: "fill",
                node_id: "grammar_ga_imasu",
                grammar_focus: "がいます (ga imasu) — Ada (makhluk hidup)",
                question: "Lengkapi: Neko ga ___ (Ada kucing).",
                correct: ["imasu", "います"],
                hint: "Imasu digunakan untuk makhluk hidup: manusia, hewan."
            },
            {
                id: "q_2_3",
                type: "mcq",
                node_id: "grammar_ni_location",
                grammar_focus: "に (ni) — Partikel lokasi keberadaan",
                question: "Partikel untuk menunjukkan letak/keberadaan benda ('di...') adalah?",
                options: ["を (o)", "で (de)", "に (ni)", "へ (e)"],
                correctIndex: 2,
                hint: "Tsukue ___ ue ni hon ga arimasu. (Di atas meja ada buku.)"
            },
            {
                id: "q_2_4",
                type: "fill",
                node_id: "grammar_doko",
                grammar_focus: "どこ (doko) — Kata tanya 'Di mana'",
                question: "Kata tanya untuk 'Di mana' adalah ___.",
                correct: ["doko", "どこ"],
                hint: "Toire wa ___ desu ka? (Di mana toiletnya?)"
            },
            {
                id: "q_2_5",
                type: "mcq",
                node_id: "grammar_kono_sono_ano",
                grammar_focus: "この・その・あの (kono/sono/ano) — Kata penunjuk + kata benda",
                question: "Apa perbedaan utama antara 'Kore' (これ) dan 'Kono' (この)?",
                options: ["Tidak ada bedanya", "'Kono' harus diikuti kata benda langsung", "'Kore' harus diikuti kata benda langsung", "'Kono' digunakan untuk orang"],
                correctIndex: 1,
                hint: "Kono hon (buku ini), tapi Kore wa hon desu (Ini adalah buku)."
            },
            {
                id: "q_2_6",
                type: "mcq",
                node_id: "grammar_ni_e_destination",
                grammar_focus: "に/へ (ni/e) — Partikel tujuan",
                question: "Partikel apa yang bisa digunakan untuk menunjukkan tujuan perjalanan? (Pilih semua yang benar)",
                options: ["Hanya に (ni)", "Hanya へ (e)", "Keduanya に (ni) dan へ (e) bisa", "で (de)"],
                correctIndex: 2,
                hint: "Gakkou ___ ikimasu. Keduanya boleh, tapi に lebih umum untuk tujuan spesifik."
            },
            {
                id: "q_2_7",
                type: "mcq",
                node_id: "grammar_de_place",
                grammar_focus: "で (de) — Partikel tempat aktivitas",
                question: "Partikel 'De' (で) digunakan untuk menunjukkan?",
                options: ["Tujuan perjalanan", "Tempat terjadinya suatu aktivitas/aksi", "Kepemilikan", "Waktu mulai"],
                correctIndex: 1,
                hint: "Resutoran ___ gohan o tabemasu. (Makan di restoran.) Aktivitas terjadi di sana."
            },
            {
                id: "q_2_8",
                type: "fill",
                node_id: "grammar_to",
                grammar_focus: "と (to) — Dan / Bersama",
                question: "Partikel 'to' (と) digunakan untuk menghubungkan dua kata benda, berarti ___.",
                correct: ["dan", "and", "bersama", "dan juga", "to"],
                hint: "Pen ___ enpitsu (Pena dan pensil). Berbeda dengan 'ya' yang berarti 'dan (tidak lengkap)'."
            },
            {
                id: "q_2_9",
                type: "fill",
                node_id: "grammar_nani",
                grammar_focus: "何 (nani/nan) — Kata tanya 'Apa'",
                question: "Kata tanya untuk 'Apa' adalah ___ (atau ___ sebelum konsonan tertentu).",
                correct: ["nani", "nan", "なに", "なん"],
                hint: "Sore wa ___ desu ka? (Apa itu?) / ___ desu ka? (Apa?)"
            },
            {
                id: "q_2_10",
                type: "translate",
                node_id: "grammar_ga_arimasu",
                grammar_focus: "があります (ga arimasu) — Produksi kalimat keberadaan",
                question: "Terjemahkan: 'Di atas meja ada kucing.' (Gunakan: ue ni / tsukue / neko / ga / imasu / no)",
                acceptedAnswers: [
                    "tsukue no ue ni neko ga imasu",
                    "tsukue no ue ni neko ga imasu.",
                    "neko ga tsukue no ue ni imasu"
                ],
                hint: "Lokasi + ni + Subjek + ga + imasu/arimasu. Kucing = makhluk hidup → imasu."
            }
        ]
    },
    {
        id: "lvl_3",
        title: "Waktu & Jumlah",
        icon: "⏰",
        difficulty_tier: 1,
        description: "Menyatakan jam, hari, dan menghitung benda sederhana.",
        prerequisites: ["grammar_ni_location", "grammar_ga_arimasu", "grammar_ga_imasu"],
        questions: [
            {
                id: "q_3_1",
                type: "mcq",
                node_id: "grammar_ji",
                grammar_focus: "時 (ji) — Penghitung jam",
                question: "Bahasa Jepang dari 'Jam 3' adalah?",
                options: ["San-ji (三時)", "San-ka", "San-ni", "San-go"],
                correctIndex: 0,
                hint: "Angka + Ji. Ichi-ji (1), Ni-ji (2), San-ji (3)..."
            },
            {
                id: "q_3_2",
                type: "fill",
                node_id: "grammar_fun_pun",
                grammar_focus: "分 (fun/pun) — Penghitung menit",
                question: "Satuan untuk 'menit' dalam bahasa Jepang adalah ___ atau ___ (tergantung angka sebelumnya).",
                correct: ["fun", "pun", "ふん", "ぷん"],
                hint: "Ichi-fun, ni-fun, san-pun, yon-fun, go-fun, roppun, nana-fun, happun..."
            },
            {
                id: "q_3_3",
                type: "mcq",
                node_id: "grammar_kara_made",
                grammar_focus: "から〜まで (kara~made) — Dari ~ Sampai",
                question: "Untuk menyatakan 'Dari jam 1 sampai jam 3', pola yang tepat adalah?",
                options: ["ichi-ji to san-ji", "ichi-ji kara san-ji made", "ichi-ji de san-ji made", "ichi-ji kara san-ji ni"],
                correctIndex: 1,
                hint: "Kara = dari (titik mulai), Made = sampai (titik akhir)."
            },
            {
                id: "q_3_4",
                type: "fill",
                node_id: "grammar_han",
                grammar_focus: "半 (han) — Setengah jam",
                question: "Jam 2 lewat 30 menit (jam setengah 3) diucapkan: Ni-ji ___.",
                correct: ["han", "はん", "半"],
                hint: "Han berarti 'setengah'. Ni-ji han = 2:30."
            },
            {
                id: "q_3_5",
                type: "mcq",
                node_id: "grammar_mai",
                grammar_focus: "枚 (mai) — Penghitung benda tipis/flat",
                question: "Kata bantu bilangan (counter) untuk benda tipis dan flat seperti kertas, baju, dan piring adalah?",
                options: ["Hon (本) — benda panjang", "Mai (枚) — benda tipis/flat", "Satsu (冊) — buku/majalah", "Ko (個) — benda kecil"],
                correctIndex: 1,
                hint: "Ichi-mai (1 lembar), ni-mai (2 lembar). Contoh: kami ichi-mai (1 lembar kertas)."
            },
            {
                id: "q_3_6",
                type: "fill",
                node_id: "grammar_hitori_futari",
                grammar_focus: "一人・二人 (hitori/futari) — Counter orang (khusus)",
                question: "Satu orang disebut ___, dua orang disebut ___.",
                correct: ["hitori futari", "ひとり ふたり", "hitori, futari"],
                hint: "Ini adalah bentuk KHUSUS, bukan ichi-nin / ni-nin. Tiga ke atas: san-nin, yo-nin, dst."
            },
            {
                id: "q_3_7",
                type: "mcq",
                node_id: "grammar_goro",
                grammar_focus: "ごろ (goro) — Kira-kira (waktu)",
                question: "Untuk menyatakan perkiraan waktu 'Sekitar jam 3', digunakan kata?",
                options: ["dake (だけ)", "goro (ごろ)", "made (まで)", "kara (から)"],
                correctIndex: 1,
                hint: "San-ji ___ ni kimasu. (Akan datang sekitar jam 3.)"
            },
            {
                id: "q_3_8",
                type: "mcq",
                node_id: "grammar_ikutsu_ikura",
                grammar_focus: "いくつ・いくら (ikutsu/ikura) — Berapa banyak / Berapa harga",
                question: "Apa perbedaan antara 'Ikutsu' (いくつ) dan 'Ikura' (いくら)?",
                options: [
                    "Tidak ada beda",
                    "Ikutsu = berapa jumlah/usia benda, Ikura = berapa harga",
                    "Ikura = berapa jumlah, Ikutsu = berapa harga",
                    "Keduanya hanya untuk menanyakan usia"
                ],
                correctIndex: 1,
                hint: "Kore wa ikura desu ka? (Berapa harganya?) vs Ringo wa ikutsu arimasu ka? (Berapa jumlah apelnya?)"
            },
            {
                id: "q_3_9",
                type: "fill",
                node_id: "grammar_itsu",
                grammar_focus: "いつ (itsu) — Kapan",
                question: "Kata tanya untuk 'Kapan' adalah ___.",
                correct: ["itsu", "いつ"],
                hint: "___ Nihon e ikimasu ka? (Kapan pergi ke Jepang?)"
            },
            {
                id: "q_3_10",
                type: "translate",
                node_id: "grammar_kara_made",
                grammar_focus: "から〜まで — Produksi kalimat waktu",
                question: "Terjemahkan: 'Toko buka dari jam 9 sampai jam 6.' (Gunakan: ku-ji / roku-ji / kara / made / aku / mise / wa / desu)",
                acceptedAnswers: [
                    "mise wa ku-ji kara roku-ji made desu",
                    "mise wa kuji kara rokuji made desu",
                    "mise wa ku ji kara roku ji made desu",
                    "mise wa 9-ji kara 6-ji made desu"
                ],
                hint: "Mise (toko), ku-ji (jam 9), roku-ji (jam 6). Pola: [Topik] wa [Awal] kara [Akhir] made desu."
            }
        ]
    },

    // ══════════════════════════════════════════════════════════════
    // TIER 2 — ELEMENTARY (Level 4–6)
    // ══════════════════════════════════════════════════════════════
    {
        id: "lvl_4",
        title: "Kata Sifat & Deskripsi",
        icon: "🎨",
        difficulty_tier: 2,
        description: "Menggunakan kata sifat -i dan -na untuk mendeskripsikan sesuatu.",
        prerequisites: ["grammar_desu", "grammar_wa", "grammar_dewa_nai"],
        questions: [
            {
                id: "q_4_1",
                type: "mcq",
                node_id: "grammar_i_adj",
                grammar_focus: "い-adjectives — Kata sifat berakhiran -i",
                question: "Mana yang merupakan kata sifat-i (i-adjective) sejati?",
                options: ["Kirei (きれい)", "Shizuka (しずか)", "Takai (たかい)", "Genki (げんき)"],
                correctIndex: 2,
                hint: "Kirei dan Genki terlihat berakhiran -i tapi mereka na-adjective (pengecualian penting!)."
            },
            {
                id: "q_4_2",
                type: "mcq",
                node_id: "grammar_na_adj",
                grammar_focus: "な-adjectives — Kata sifat yang butuh 'na'",
                question: "'Kirei' (きれい) dan 'Genki' (げんき) termasuk jenis kata sifat apa, meskipun terlihat berakhiran -i?",
                options: ["i-adjective karena berakhiran i", "na-adjective (pengecualian penting!)", "Kata benda biasa", "Kata kerja"],
                correctIndex: 1,
                hint: "Ini pengecualian penting! Kirei-NA hana (bunga yang cantik). Bukan kirei-i hana."
            },
            {
                id: "q_4_3",
                type: "mcq",
                node_id: "grammar_i_adj_neg",
                grammar_focus: "い-adjective negatif: -kunai",
                question: "Bentuk negatif dari 'Atsui' (あつい — Panas) adalah?",
                options: ["Atsui janai", "Atsuku nai (あつくない)", "Atsu dewa nai", "Atsunai"],
                correctIndex: 1,
                hint: "Rumus i-adjective negatif: Hapus -i, tambah -ku nai. Atsui → atsuku nai."
            },
            {
                id: "q_4_4",
                type: "fill",
                node_id: "grammar_totemo",
                grammar_focus: "とても (totemo) — Sangat",
                question: "Kata keterangan untuk 'Sangat' adalah ___.",
                correct: ["totemo", "とても"],
                hint: "___ oishii desu ne! (Sangat enak ya!)"
            },
            {
                id: "q_4_5",
                type: "mcq",
                node_id: "grammar_amari_neg",
                grammar_focus: "あまり〜ない (amari~nai) — Tidak terlalu",
                question: "Kata 'Amari' (あまり — tidak terlalu) harus diikuti kalimat bentuk apa?",
                options: ["Positif", "Tanya", "Negatif (~nai)", "Lampau"],
                correctIndex: 2,
                hint: "Amari atsuku NAI desu. (Tidak terlalu panas.) Selalu butuh bentuk negatif!"
            },
            {
                id: "q_4_6",
                type: "fill",
                node_id: "grammar_donna",
                grammar_focus: "どんな (donna) — Seperti apa / yang bagaimana",
                question: "Untuk menanyakan 'Seperti apa?' digunakan kata ___.",
                correct: ["donna", "どんな"],
                hint: "___ hito ga suki desu ka? (Kamu suka orang seperti apa?)"
            },
            {
                id: "q_4_7",
                type: "mcq",
                node_id: "grammar_na_adj_noun",
                grammar_focus: "な-adjective + Kata benda",
                question: "Cara menggabungkan kata sifat-na (na-adjective) dengan kata benda yang benar?",
                options: ["Langsung digabung tanpa apa-apa", "Tambah partikel 'no' di antara keduanya", "Tambah 'na' di antara keduanya", "Tambah 'i' di antara keduanya"],
                correctIndex: 2,
                hint: "Shizuka ___ machi (Kota yang tenang). Na-adjective + NA + Kata benda."
            },
            {
                id: "q_4_8",
                type: "mcq",
                node_id: "grammar_ii_yoku",
                grammar_focus: "いい/よい (ii/yoi) — Bagus (kata sifat tidak beraturan)",
                question: "'Ii' (いい — Bagus) adalah kata sifat tidak beraturan. Bentuk negatifnya adalah?",
                options: ["Ii janai", "Yoku nai (よくない)", "I nai", "Ii kunai"],
                correctIndex: 1,
                hint: "Perubahan tidak beraturan: ii → YOKU (bukan ii-ku). Yoku nai = tidak bagus."
            },
            {
                id: "q_4_9",
                type: "fill",
                node_id: "grammar_ga_but",
                grammar_focus: "が (ga) — Namun / Tetapi (konjungsi)",
                question: "Partikel 'ga' (が) di tengah kalimat dapat berfungsi sebagai kata hubung yang berarti ___.",
                correct: ["tetapi", "namun", "tapi", "but", "however", "ga"],
                hint: "Takai desu ___ oishii desu. (Mahal, tapi enak.)"
            },
            {
                id: "q_4_10",
                type: "translate",
                node_id: "grammar_i_adj",
                grammar_focus: "い-adjective — Produksi kalimat deskripsi",
                question: "Terjemahkan: 'Cuaca hari ini sangat panas.' (Gunakan: kyou / tenki / atsui / totemo / wa / desu)",
                acceptedAnswers: [
                    "kyou wa totemo atsui desu",
                    "kyou no tenki wa totemo atsui desu",
                    "kyou wa totemo atsui",
                    "kyou no tenki wa atsui desu"
                ],
                hint: "Tenki = cuaca, kyou = hari ini, totemo = sangat, atsui = panas."
            }
        ]
    },
    {
        id: "lvl_5",
        title: "Aktivitas & Partikel Objek",
        icon: "🍱",
        difficulty_tier: 2,
        description: "Menyatakan tindakan sehari-hari dan menggunakan partikel 'o'.",
        prerequisites: ["grammar_wa", "grammar_ni_e_destination", "grammar_de_place"],
        questions: [
            {
                id: "q_5_1",
                type: "mcq",
                node_id: "grammar_o_particle",
                grammar_focus: "を (o/wo) — Partikel objek",
                question: "Partikel apa yang digunakan untuk menandai objek penderita (yang dikenai tindakan)?",
                options: ["は (wa)", "に (ni)", "を (o/wo)", "で (de)"],
                correctIndex: 2,
                hint: "Ringo ___ tabemasu. (Makan apel.) Apel adalah yang dimakan, jadi objek penderita."
            },
            {
                id: "q_5_2",
                type: "fill",
                node_id: "grammar_shimasu",
                grammar_focus: "します (shimasu) — Melakukan",
                question: "Lengkapi: Sakkā o ___ (Bermain sepak bola / Melakukan sepak bola).",
                correct: ["shimasu", "します", "suru", "する"],
                hint: "Shimasu adalah kata kerja 'melakukan'. Bisa disambung dengan kata benda olahraga/aktivitas."
            },
            {
                id: "q_5_3",
                type: "mcq",
                node_id: "grammar_ni_iku",
                grammar_focus: "に行く (ni iku) — Pergi untuk melakukan",
                question: "Pola untuk menyatakan 'Pergi untuk melakukan sesuatu' adalah?",
                options: ["V-masu (stem) + ni ikimasu", "V-te + ikimasu", "V-dictionary + ni ikimasu", "V-nai + ni ikimasu"],
                correctIndex: 0,
                hint: "Tabe-masu → tabe + ni ikimasu = Pergi untuk makan. Gunakan V-masu stem (bentuk masu tanpa masu)."
            },
            {
                id: "q_5_4",
                type: "fill",
                node_id: "grammar_issho_ni",
                grammar_focus: "一緒に (issho ni) — Bersama-sama",
                question: "Kata untuk 'Bersama-sama' adalah ___.",
                correct: ["issho ni", "いっしょに", "一緒に"],
                hint: "___ tabemashou! (Ayo makan bersama!)"
            },
            {
                id: "q_5_5",
                type: "mcq",
                node_id: "grammar_masen_ka",
                grammar_focus: "〜ませんか (masen ka) — Ajakan sopan",
                question: "Cara mengajak seseorang dengan sopan (Maukah kamu...?) adalah?",
                options: ["~mashou (ましょう)", "~masen ka (ませんか)", "~masu ka (ますか)", "~tai desu (たいです)"],
                correctIndex: 1,
                hint: "Tabemashou = Ayo kita makan (inisiatif pembicara). Tabemasen ka = Mau makan tidak? (ajak orang lain)."
            },
            {
                id: "q_5_6",
                type: "fill",
                node_id: "grammar_mashou",
                grammar_focus: "〜ましょう (mashou) — Ayo kita lakukan",
                question: "Akhiran kata kerja untuk mengajak 'Ayo...!' adalah ___.",
                correct: ["mashou", "ましょう"],
                hint: "Ikimashou! (Ayo pergi!) Tabemamashou! (Ayo makan!)"
            },
            {
                id: "q_5_7",
                type: "mcq",
                node_id: "grammar_doushite",
                grammar_focus: "どうして・なぜ (doushite/naze) — Kenapa",
                question: "Kata tanya untuk 'Kenapa / Mengapa' dalam bahasa Jepang adalah?",
                options: ["Hanya Naze (なぜ)", "Hanya Doushite (どうして)", "Hanya Nan de (なんで)", "Ketiganya benar (Naze, Doushite, Nan de)"],
                correctIndex: 3,
                hint: "Ada beberapa variasi: Naze (formal/tulisan), Doushite (umum), Nan de (kasual)."
            },
            {
                id: "q_5_8",
                type: "fill",
                node_id: "grammar_kara_reason",
                grammar_focus: "から (kara) — Karena (alasan)",
                question: "Untuk menyatakan alasan 'Karena...', kata ___ diletakkan setelah kalimat alasan.",
                correct: ["kara", "から"],
                hint: "Atsui ___ mizu o nomimasu. (Karena panas, minum air.) Bandingkan: kara juga bisa berarti 'dari'."
            },
            {
                id: "q_5_9",
                type: "mcq",
                node_id: "grammar_frequency",
                grammar_focus: "Kata keterangan frekuensi: いつも・よく・ときどき・あまり",
                question: "Urutkan kata-kata ini dari frekuensi PALING SERING ke PALING JARANG:",
                options: [
                    "Itsumo > yoku > tokidoki > amari (nai)",
                    "Yoku > itsumo > amari (nai) > tokidoki",
                    "Tokidoki > itsumo > yoku > amari (nai)",
                    "Itsumo > tokidoki > yoku > amari (nai)"
                ],
                correctIndex: 0,
                hint: "Itsumo (selalu) > yoku (sering) > tokidoki (kadang-kadang) > amari ~nai (tidak terlalu sering)."
            },
            {
                id: "q_5_10",
                type: "translate",
                node_id: "grammar_o_particle",
                grammar_focus: "を (o) — Produksi kalimat dengan objek",
                question: "Terjemahkan: 'Setiap hari saya minum kopi.' (Gunakan: mainichi / watashi wa / koohii / o / nomimasu)",
                acceptedAnswers: [
                    "watashi wa mainichi koohii o nomimasu",
                    "mainichi koohii o nomimasu",
                    "watashi wa mainichi kohii o nomimasu",
                    "mainichi kohii o nomimasu"
                ],
                hint: "Pola: Topik wa + Keterangan waktu + Objek o + Kata kerja. Mainichi = setiap hari."
            }
        ]
    },
    {
        id: "lvl_6",
        title: "Keinginan & Kemampuan",
        icon: "🌟",
        difficulty_tier: 2,
        description: "Menyatakan hobi, keinginan, dan kemahiran.",
        prerequisites: ["grammar_o_particle", "grammar_shimasu", "grammar_i_adj"],
        questions: [
            {
                id: "q_6_1",
                type: "mcq",
                node_id: "grammar_tai",
                grammar_focus: "〜たい (tai) — Ingin melakukan (subjek sendiri)",
                question: "Cara menyatakan 'Ingin melakukan sesuatu' (untuk diri sendiri) adalah?",
                options: ["V-masu (stem) + tai desu", "V-te + tai desu", "V-dictionary + tai desu", "V-masu + hoshii"],
                correctIndex: 0,
                hint: "Nomi-masu → nomi + tai desu = Ingin minum. Perlu V-masu stem (bukan bentuk lengkapnya)."
            },
            {
                id: "q_6_2",
                type: "fill",
                node_id: "grammar_ga_hoshii",
                grammar_focus: "がほしい (ga hoshii) — Ingin (benda)",
                question: "Untuk menyatakan keinginan terhadap BENDA, pola yang dipakai adalah: [Benda] ga ___.",
                correct: ["hoshii", "ほしい", "欲しい"],
                hint: "Kuruma ga ___ (Saya ingin mobil). Berbeda dengan -tai yang untuk kata kerja."
            },
            {
                id: "q_6_3",
                type: "mcq",
                node_id: "grammar_no_ga_suki",
                grammar_focus: "のが好き (no ga suki) — Suka melakukan",
                question: "Untuk menyatakan 'Suka MELAKUKAN sesuatu', pola yang dipakai adalah: V-dictionary + ___ ga suki desu.",
                options: ["koto (こと)", "no (の)", "mono (もの)", "naka (なか)"],
                correctIndex: 1,
                hint: "Taberu ___ ga suki desu. (Suka makan.) のが好き = N5 standard. こと punya nuansa lebih formal."
            },
            {
                id: "q_6_4",
                type: "fill",
                node_id: "grammar_jouzu_heta",
                grammar_focus: "上手・下手 (jouzu/heta) — Pandai / Tidak pandai",
                question: "Kata untuk 'Pandai/Mahir' adalah ___, lawan katanya 'Tidak pandai/Payah' adalah ___.",
                correct: ["jouzu heta", "じょうず へた", "jōzu heta", "jouzu, heta"],
                hint: "Nihongo ga jouzu desu ne! (Bahasa Jepangmu bagus!) vs uta ga heta desu. (Tidak pandai menyanyi.)"
            },
            {
                id: "q_6_5",
                type: "fill",
                node_id: "grammar_wakaru",
                grammar_focus: "わかる (wakaru) — Mengerti / Paham",
                question: "Kata kerja 'Mengerti / Paham' dalam bentuk sopan adalah ___.",
                correct: ["wakarimasu", "わかります", "wakaru", "わかる"],
                hint: "Nihongo ga ___ ka? (Apakah mengerti bahasa Jepang?)"
            },
            {
                id: "q_6_6",
                type: "mcq",
                node_id: "grammar_ichiban",
                grammar_focus: "一番 (ichiban) — Paling / Nomor satu",
                question: "Kata untuk menyatakan 'Paling' atau 'Nomor Satu' (superlatif) adalah?",
                options: ["Motto (もっと — lebih lagi)", "Zutto (ずっと — sejauh ini/terus)", "Ichiban (一番 — paling)", "Dake (だけ — hanya)"],
                correctIndex: 2,
                hint: "___ suki na tabemono wa nan desu ka? (Makanan yang paling kamu suka apa?)"
            },
            {
                id: "q_6_7",
                type: "fill",
                node_id: "grammar_yori",
                grammar_focus: "より (yori) — Daripada (perbandingan)",
                question: "Untuk perbandingan 'A lebih ... daripada B': A wa B ___ ... desu.",
                correct: ["yori", "より"],
                hint: "Neko wa inu ___ chiisai desu. (Kucing lebih kecil daripada anjing.)"
            },
            {
                id: "q_6_8",
                type: "mcq",
                node_id: "grammar_hou_ga_ii",
                grammar_focus: "ほうがいい (hou ga ii) — Lebih baik / Sebaiknya",
                question: "Pola untuk memberikan saran 'Lebih baik melakukan...' adalah?",
                options: ["Hanya V-ta + hou ga ii (sudah melakukan)", "Hanya V-nai + hou ga ii (jangan melakukan)", "Keduanya bisa: V-ta hou ga ii (positif) dan V-nai hou ga ii (negatif)", "Hanya V-masu + hou ga ii"],
                correctIndex: 2,
                hint: "Neta hou ga ii (Lebih baik tidur). vs Tabenai hou ga ii (Lebih baik tidak makan)."
            },
            {
                id: "q_6_9",
                type: "fill",
                node_id: "grammar_dou_desu_ka",
                grammar_focus: "はどうですか (wa dou desu ka) — Bagaimana / Bagaimana kalau",
                question: "Untuk menanyakan 'Bagaimana pendapatmu?' atau menawarkan sesuatu, digunakan ___.",
                correct: ["dou desu ka", "どうですか", "wa dou desu ka"],
                hint: "Koohii ___ ? (Bagaimana kalau kopi? / Mau kopi?)"
            },
            {
                id: "q_6_10",
                type: "translate",
                node_id: "grammar_tai",
                grammar_focus: "〜たい — Produksi kalimat keinginan",
                question: "Terjemahkan: 'Saya ingin pergi ke Jepang suatu saat nanti.' (Gunakan: nihon / ni / itsu ka / ikitai desu / watashi wa)",
                acceptedAnswers: [
                    "watashi wa itsu ka nihon ni ikitai desu",
                    "itsu ka nihon ni ikitai desu",
                    "nihon ni ikitai desu",
                    "watashi wa nihon ni ikitai desu"
                ],
                hint: "Ikimasu → iki + tai desu = ingin pergi. Itsu ka = suatu saat nanti."
            }
        ]
    },

    // ══════════════════════════════════════════════════════════════
    // TIER 3 — PRE-INTERMEDIATE (Level 7–9)
    // ══════════════════════════════════════════════════════════════
    {
        id: "lvl_7",
        title: "Perintah & Izin (Te-Form)",
        icon: "📜",
        difficulty_tier: 3,
        description: "Menguasai perubahan bentuk Te dan penggunaannya.",
        prerequisites: ["grammar_shimasu", "grammar_masen_ka", "grammar_mashou"],
        questions: [
            {
                id: "q_7_1",
                type: "mcq",
                node_id: "grammar_te_kudasai",
                grammar_focus: "てください (te kudasai) — Tolong lakukan",
                question: "Cara meminta tolong dengan sopan 'Tolong lakukan...' adalah?",
                options: ["V-te kudasai", "V-masu kudasai", "V-nai kudasai", "V-dictionary kudasai"],
                correctIndex: 0,
                hint: "Mite kudasai (Tolong lihat). Kite kudasai (Tolong datang). Selalu pakai bentuk -te."
            },
            {
                id: "q_7_2",
                type: "fill",
                node_id: "grammar_te_mo_ii",
                grammar_focus: "てもいいです (temo ii desu) — Boleh / Diizinkan",
                question: "Meminta atau memberi izin 'Boleh melakukan...': V-te ___ desu.",
                correct: ["mo ii", "もいい", "mo ii desu"],
                hint: "Tabete ___ desu ka? (Bolehkah makan?) → Hai, tabete mo ii desu. (Ya, boleh makan.)"
            },
            {
                id: "q_7_3",
                type: "mcq",
                node_id: "grammar_te_wa_ikenai",
                grammar_focus: "てはいけない (te wa ikenai) — Tidak boleh / Larangan",
                question: "Untuk menyatakan larangan 'Tidak boleh...', pola yang digunakan adalah V-te ___.",
                options: ["wa ikemasen (は行けません) — formal", "wa dame desu (はだめです) — standar", "wa ikenai (はいけない) — kasual", "Semua benar, berbeda tingkat kesopanan"],
                correctIndex: 3,
                hint: "Ketiganya bermakna sama (dilarang), tapi beda tingkat formalitas. Ikemasen paling sopan."
            },
            {
                id: "q_7_4",
                type: "fill",
                node_id: "grammar_te_iru",
                grammar_focus: "ている (te iru) — Sedang melakukan / Keadaan menetap",
                question: "Untuk menyatakan aksi yang 'sedang berlangsung': V-te ___.",
                correct: ["imasu", "iru", "います", "いる"],
                hint: "Benkyou shite ___ (Sedang belajar). Kekkon shite ___ (Sudah menikah — keadaan menetap)."
            },
            {
                id: "q_7_5",
                type: "mcq",
                node_id: "grammar_te_iru_state",
                grammar_focus: "ている — Keadaan menetap (meaning ke-2)",
                question: "Selain menyatakan aksi 'sedang berlangsung', pola Te-imasu juga bisa menyatakan?",
                options: ["Keinginan", "Keadaan/kondisi yang menetap sebagai hasil dari aksi", "Masa lalu", "Kemungkinan"],
                correctIndex: 1,
                hint: "Kekkon shite imasu (Saya sudah menikah — menikah adalah hasilnya, statusnya menetap)."
            },
            {
                id: "q_7_6",
                type: "fill",
                node_id: "grammar_te_kara",
                grammar_focus: "てから (te kara) — Setelah melakukan",
                question: "Untuk menyatakan 'Setelah melakukan A, baru B': V-te ___.",
                correct: ["kara", "から"],
                hint: "Tabete ___ benkyou shimasu. (Setelah makan, baru belajar.) Urutannya jelas: A dulu, baru B."
            },
            {
                id: "q_7_7",
                type: "mcq",
                node_id: "grammar_te_ageru_morau_kureru",
                grammar_focus: "てあげる・てもらう・てくれる — Memberi / Menerima jasa",
                question: "Manakah yang berarti 'Melakukan sesuatu untuk orang lain (memberi jasa)'?",
                options: ["~te morau (もらう) — menerima jasa dari orang lain", "~te kureru (くれる) — orang lain berbuat untuk saya", "~te ageru (あげる) — saya berbuat untuk orang lain", "~te iku (いく) — melakukan sambil pergi"],
                correctIndex: 2,
                hint: "Ageru = memberi (dari perspektif pembicara keluar). Morau = menerima. Kureru = orang lain memberi ke saya."
            },
            {
                id: "q_7_8",
                type: "fill",
                node_id: "grammar_tari_tari",
                grammar_focus: "たり〜たりする (tari~tari suru) — Melakukan berbagai hal",
                question: "Untuk menyebutkan beberapa aktivitas secara sampel/tidak lengkap, pola yang dipakai adalah V-___, V-___ shimasu.",
                correct: ["tari tari", "たり たり", "tari, tari"],
                hint: "Tabe-TARI, nomi-TARI shimasu. (Melakukan hal-hal seperti makan dan minum.) Bukan daftar lengkap."
            },
            {
                id: "q_7_9",
                type: "fill",
                node_id: "grammar_te_miru",
                grammar_focus: "てみる (te miru) — Mencoba melakukan",
                question: "Untuk menyatakan 'Mencoba melakukan sesuatu (dan lihat hasilnya)': V-te ___.",
                correct: ["mimasu", "miru", "みます", "みる"],
                hint: "Tabete ___ (Coba makan deh). Kite ___ (Coba pakai/datang). Implisit: ingin tahu hasilnya."
            },
            {
                id: "q_7_10",
                type: "translate",
                node_id: "grammar_te_kudasai",
                grammar_focus: "てください — Produksi kalimat permintaan",
                question: "Terjemahkan: 'Tolong tulis namamu di sini.' (Gunakan: koko ni / namae / kaite / o / kudasai / anata no)",
                acceptedAnswers: [
                    "koko ni namae o kaite kudasai",
                    "koko ni anata no namae o kaite kudasai",
                    "namae o koko ni kaite kudasai"
                ],
                hint: "Kakimasu → kaite. Pola: [Tempat] ni [Objek] o kaite kudasai."
            }
        ]
    },
    {
        id: "lvl_8",
        title: "Kondisi & Pengalaman",
        icon: "🌊",
        difficulty_tier: 3,
        description: "Menyatakan pengalaman (pernah) dan urutan kejadian.",
        prerequisites: ["grammar_te_iru", "grammar_te_kara", "grammar_tai"],
        questions: [
            {
                id: "q_8_1",
                type: "mcq",
                node_id: "grammar_ta_koto_ga_aru",
                grammar_focus: "たことがある (ta koto ga aru) — Pernah melakukan",
                question: "Cara menyatakan pengalaman 'Pernah melakukan sesuatu (setidaknya sekali)' adalah?",
                options: ["V-ta koto ga arimasu", "V-te koto ga arimasu", "V-dictionary koto ga arimasu", "V-nai koto ga arimasu"],
                correctIndex: 0,
                hint: "Nihon e itta koto ga arimasu. (Pernah pergi ke Jepang.) V-ta = past tense verb."
            },
            {
                id: "q_8_2",
                type: "fill",
                node_id: "grammar_mae_ni",
                grammar_focus: "前に (mae ni) — Sebelum",
                question: "Untuk menyatakan 'Sebelum melakukan sesuatu': V-dictionary ___.",
                correct: ["mae ni", "まえに", "前に"],
                hint: "Neru ___ ha o migakimasu. (Sebelum tidur, gosok gigi.) V-dictionary + mae ni."
            },
            {
                id: "q_8_3",
                type: "mcq",
                node_id: "grammar_nagara",
                grammar_focus: "ながら (nagara) — Sambil (melakukan dua hal bersamaan)",
                question: "Untuk menyatakan 'Melakukan dua hal bersamaan (sambil...)', pola yang digunakan adalah?",
                options: ["V-te", "V-masu (stem) + nagara", "V-dictionary + nagara", "V-ta + nagara"],
                correctIndex: 1,
                hint: "Ongaku o kiki-NAGARA tabemasu. (Makan sambil mendengar musik.) Gunakan V-masu stem + nagara."
            },
            {
                id: "q_8_4",
                type: "mcq",
                node_id: "grammar_mou_mada",
                grammar_focus: "もう・まだ (mou/mada) — Sudah / Belum",
                question: "Pasangan kata yang tepat: 'Sudah' = ___, 'Belum' = ___.",
                options: ["Mou (もう) / Mada (まだ)", "Mada (まだ) / Mou (もう)", "Yoku (よく) / Mada (まだ)", "Mou (もう) / Amari (あまり)"],
                correctIndex: 0,
                hint: "Mou tabemashita (Sudah makan). Mada tabete imasen (Belum makan). Perhatikan: mada butuh bentuk ~te imasen!"
            },
            {
                id: "q_8_5",
                type: "fill",
                node_id: "grammar_naru",
                grammar_focus: "なる (naru) — Menjadi",
                question: "Kata kerja 'Menjadi (become)' dalam bentuk sopan adalah ___.",
                correct: ["narimasu", "なります", "naru", "なる"],
                hint: "Atsuku ___ (Menjadi panas). Sensei ni ___ (Menjadi guru)."
            },
            {
                id: "q_8_6",
                type: "mcq",
                node_id: "grammar_ndesu",
                grammar_focus: "んです・のです (ndesu/no desu) — Penjelasan / Penekanan",
                question: "Fungsi utama dari akhiran '~ndesu' (んです) atau '~no desu' (のです) adalah?",
                options: ["Memberi perintah", "Memberikan penjelasan atau alasan dari suatu situasi", "Menanyakan waktu", "Menyatakan hobi"],
                correctIndex: 1,
                hint: "Doushite okureta no? - Densha ga okureta n desu. (Mengapa terlambat? - Karena keretanya terlambat.)"
            },
            {
                id: "q_8_7",
                type: "fill",
                node_id: "grammar_toki",
                grammar_focus: "とき (toki) — Ketika / Saat",
                question: "Kata untuk menyatakan 'Ketika / Saat' adalah ___.",
                correct: ["toki", "とき", "時"],
                hint: "Kodomo no ___ (Ketika masih anak-anak). Nihon ni ita ___ (Ketika di Jepang)."
            },
            {
                id: "q_8_8",
                type: "mcq",
                node_id: "grammar_sugiru",
                grammar_focus: "すぎる (sugiru) — Terlalu / Berlebihan",
                question: "Untuk menyatakan 'Terlalu / Berlebihan (sampai bermasalah)', pola yang dipakai adalah?",
                options: ["~sugiru (すぎる)", "~totemo (とても)", "~motto (もっと)", "~dake (だけ)"],
                correctIndex: 0,
                hint: "Tabe-SUGIRU (Terlalu banyak makan). Nomi-sugiru (Terlalu banyak minum). i-adj: hatsu-sugiru → atsusugiru."
            },
            {
                id: "q_8_9",
                type: "fill",
                node_id: "grammar_deshou",
                grammar_focus: "でしょう (deshou) — Sepertinya / Mungkin (sopan)",
                question: "Bentuk sopan dari 'darou (だろう)' yang menyatakan perkiraan/kemungkinan adalah ___.",
                correct: ["deshou", "でしょう"],
                hint: "Ashita wa ame ga ___ (Sepertinya besok hujan). Lebih sopan dari 'darou'."
            },
            {
                id: "q_8_10",
                type: "translate",
                node_id: "grammar_ta_koto_ga_aru",
                grammar_focus: "たことがある — Produksi kalimat pengalaman",
                question: "Terjemahkan: 'Apakah kamu pernah makan sushi?' (Gunakan: sushi o / koto ga / tabeta / arimasu ka / anata wa)",
                acceptedAnswers: [
                    "anata wa sushi o tabeta koto ga arimasu ka",
                    "sushi o tabeta koto ga arimasu ka",
                    "sushi wo tabeta koto ga arimasu ka"
                ],
                hint: "Tabemasu → tabeta (past). Pola: [Objek] o V-ta koto ga arimasu ka?"
            }
        ]
    },
    {
        id: "lvl_9",
        title: "Kewajiban & Aturan",
        icon: "⚔️",
        difficulty_tier: 3,
        description: "Menyatakan keharusan, larangan, rencana, dan kemampuan.",
        prerequisites: ["grammar_te_wa_ikenai", "grammar_te_mo_ii", "grammar_ta_koto_ga_aru"],
        questions: [
            {
                id: "q_9_1",
                type: "mcq",
                node_id: "grammar_nakereba_naranai",
                grammar_focus: "なければならない・なくてはいけない (nakereba naranai) — Harus",
                question: "Cara menyatakan 'Harus melakukan sesuatu' dalam bahasa Jepang adalah?",
                options: ["Hanya V-nakereba narimasen", "Hanya V-nai to ikenai", "Hanya V-nakucha", "Semua benar — ada banyak cara dalam bahasa Jepang"],
                correctIndex: 3,
                hint: "Nakereba narimasen (formal), nai to ikenai (standar), nakucha (sangat kasual) — semua bermakna 'harus'."
            },
            {
                id: "q_9_2",
                type: "fill",
                node_id: "grammar_naide_kudasai",
                grammar_focus: "ないでください (naide kudasai) — Tolong jangan",
                question: "Untuk meminta seseorang TIDAK melakukan sesuatu: V-nai ___.",
                correct: ["de kudasai", "でください"],
                hint: "Wasurenai ___ (Tolong jangan lupa). Berbeda dengan te wa ikenai yang lebih kuat."
            },
            {
                id: "q_9_3",
                type: "mcq",
                node_id: "grammar_tsumori",
                grammar_focus: "つもり (tsumori) — Berencana / Berniat",
                question: "Cara menyatakan rencana/niat 'Berencana untuk...', menggunakan pola mana?",
                options: ["Hanya V-dictionary + tsumori desu (rencana positif)", "Hanya V-nai + tsumori desu (rencana tidak melakukan)", "Keduanya: V-dic tsumori desu ATAU V-nai tsumori desu", "V-ta + tsumori desu"],
                correctIndex: 2,
                hint: "Nihon e iku tsumori desu (Berencana pergi ke Jepang). Tabenai tsumori desu (Tidak berencana makan)."
            },
            {
                id: "q_9_4",
                type: "fill",
                node_id: "grammar_naku_temo_ii",
                grammar_focus: "なくてもいい (naku temo ii) — Tidak harus / Boleh tidak",
                question: "Untuk menyatakan 'Tidak harus melakukan / Boleh tidak melakukan': V-nai ___ desu.",
                correct: ["ku temo ii", "くてもいい", "naku temo ii", "なくてもいい"],
                hint: "Isoganakute mo ii desu. (Tidak perlu buru-buru.) Isogu → isoganai → isogana-KU-TE MO II."
            },
            {
                id: "q_9_5",
                type: "mcq",
                node_id: "grammar_koto_ga_dekiru",
                grammar_focus: "ことができる (koto ga dekiru) — Bisa / Mampu melakukan",
                question: "Cara menyatakan kemampuan 'Bisa melakukan sesuatu' menggunakan pola?",
                options: ["V-dictionary + koto ga dekimasu", "V-masu + dekimasu", "V-te + dekimasu", "V-nai + dekimasu"],
                correctIndex: 0,
                hint: "Yomu koto ga dekimasu. (Bisa membaca.) = V-dictionary + koto ga dekimasu."
            },
            {
                id: "q_9_6",
                type: "mcq",
                node_id: "grammar_cha_ikenai",
                grammar_focus: "ちゃいけない / じゃいけない (cha ikenai / ja ikenai) — Tidak boleh (kasual)",
                question: "Dalam bahasa Jepang kasual (spoken), 'ちゃいけない (cha ikenai)' digunakan ketika bentuk -te dari kata kerjanya berakhiran ___.",
                options: [
                    "て (te) → ちゃ (cha)",
                    "で (de) → ちゃ (cha)",
                    "で (de) → じゃ (ja)",
                    "A dan C benar: て→ちゃ, で→じゃ"
                ],
                correctIndex: 3,
                hint: "Taberu → tabete → tabeCHA ikenai. Nomu → nonde → nonJA ikenai. Ini lebih kasual dari te wa ikenai."
            },
            {
                id: "q_9_7",
                type: "mcq",
                node_id: "grammar_node",
                grammar_focus: "ので (node) — Karena (objektif/sopan)",
                question: "Apa perbedaan utama antara 'Kara (から)' dan 'Node (ので)' sebagai kata 'karena'?",
                options: ["Tidak ada perbedaan", "Node terdengar lebih objektif dan sopan; Kara lebih subjektif/kasual", "Kara lebih sopan dari Node", "Node hanya untuk kalimat cuaca"],
                correctIndex: 1,
                hint: "Ame nano de, ie ni imasu (Karena hujan, di rumah) — Node terasa objektif. Ame da kara, ie ni iru — lebih kasual/subjektif."
            },
            {
                id: "q_9_8",
                type: "fill",
                node_id: "grammar_shikashi",
                grammar_focus: "しかし (shikashi) — Namun / Tetapi (formal)",
                question: "Kata hubung FORMAL untuk 'Namun / Tetapi' (setara dengan 'however' dalam tulisan) adalah ___.",
                correct: ["shikashi", "しかし"],
                hint: "Demo (でも) dipakai dalam percakapan. Shikashi dipakai dalam tulisan formal/resmi."
            },
            {
                id: "q_9_9",
                type: "mcq",
                node_id: "grammar_ne_yo",
                grammar_focus: "ね・よ (ne/yo) — Partikel akhir kalimat",
                question: "Apa perbedaan partikel akhir 'ね (ne)' dan 'よ (yo)'?",
                options: [
                    "Tidak ada beda",
                    "Ne = meminta konfirmasi/persetujuan dari pendengar; Yo = memberikan informasi baru/meyakinkan",
                    "Yo = meminta konfirmasi; Ne = memberikan informasi baru",
                    "Keduanya hanya untuk pertanyaan"
                ],
                correctIndex: 1,
                hint: "Oishii desu NE! (Enak ya? — kita berdua rasakan.) vs Oishii desu YO! (Ini enak lho! — kamu mungkin belum tahu.)"
            },
            {
                id: "q_9_10",
                type: "translate",
                node_id: "grammar_nakereba_naranai",
                grammar_focus: "なければならない — Produksi kalimat kewajiban",
                question: "Terjemahkan: 'Besok saya harus bangun jam 6.' (Gunakan: ashita / wa / roku-ji ni / okina kereba / narimasen / watashi)",
                acceptedAnswers: [
                    "watashi wa ashita roku-ji ni okinakereba narimasen",
                    "ashita roku-ji ni okinakereba narimasen",
                    "watashi wa ashita rokuji ni okinakereba narimasen",
                    "ashita rokuji ni okinakereba narimasen"
                ],
                hint: "Okiru (bangun) → okinai → okinakereba narimasen. Roku-ji ni = pada jam 6."
            }
        ]
    }
];

/**
 * Ambil semua prerequisite node_id untuk sebuah level.
 * Digunakan untuk pengecekan "Pembelajaran Terstruktur".
 * @param {string} levelId 
 * @returns {string[]} Array of prerequisite node_ids
 */
export function getPrerequisites(levelId) {
    const level = questLevels.find(l => l.id === levelId);
    return level ? level.prerequisites : [];
}

/**
 * Cek apakah level bisa dibuka berdasarkan daftar node yang sudah dikuasai.
 * Fallback lokal jika backend KG tidak tersedia.
 * @param {string} levelId 
 * @param {string[]} masteredNodeIds - Daftar node_id yang sudah MASTERED
 * @returns {{ unlocked: boolean, missingNodes: string[] }}
 */
export function checkLocalPrerequisites(levelId, masteredNodeIds = []) {
    const prerequisites = getPrerequisites(levelId);
    if (prerequisites.length === 0) return { unlocked: true, missingNodes: [] };

    const missingNodes = prerequisites.filter(req => !masteredNodeIds.includes(req));
    return {
        unlocked: missingNodes.length === 0,
        missingNodes
    };
}
