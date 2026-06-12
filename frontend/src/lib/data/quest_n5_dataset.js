// src/lib/data/quest_n5_dataset.js
/**
 * Dataset Quest JLPT N5
 * Berdasarkan: JLPT N5 Grammar Master by JLPTsensei.com (80 Grammar Lessons)
 * 
 * Struktur:
 * - 9 Level, masing-masing 10 soal
 * - Kesulitan meningkat setiap 3 level (difficulty_tier: 1, 2, 3)
 * - Tipe soal: 'mcq' (pilihan ganda), 'fill' (isian), 'translate' (terjemah)
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
        prerequisites: [],
        questions: [
            {
                id: "q_1_1",
                type: "mcq",
                node_id: "grammar_wa",
                grammar_focus: "Partikel は (wa) — Penanda Topik",
                question: "Lengkapi kalimat: わたし ___ クリスです。 (Saya adalah Chris.)",
                options: ["を (o)", "は (wa)", "に (ni)", "も (mo)"],
                correctIndex: 1,
                hint: "Topik utama kalimat ditandai dengan partikel 'wa' (ditulis hiragana 'ha')."
            },
            {
                id: "q_1_2",
                type: "fill",
                node_id: "grammar_desu",
                grammar_focus: "だ・です (da/desu) — To Be (Sopan)",
                question: "Lengkapi kalimat penutup sopan berikut: かれはわたしの<ruby>友<rt>とも</rt></ruby>だち ___。 (He is my friend.)",
                correct: ["desu", "です"],
                hint: "Kopula penutup kalimat sopan untuk kata benda."
            },
            {
                id: "q_1_3",
                type: "mcq",
                node_id: "grammar_no",
                grammar_focus: "の (no) — Partikel Kepemilikan",
                question: "Lengkapi kalimat: わたしの<ruby>名前<rt>なまえ</rt></ruby> ___ クリスです。 (Nama saya adalah Chris.)",
                options: ["は (wa)", "の (no)", "が (ga)", "を (o)"],
                correctIndex: 1,
                hint: "Partikel 'no' digunakan untuk menghubungkan dua kata benda (kepemilikan/hubungan)."
            },
            {
                id: "q_1_4",
                type: "fill",
                node_id: "grammar_mo",
                grammar_focus: "も (mo) — Juga / Pula",
                question: "Lengkapi kalimat: わたし ___ インドネシア<ruby>人<rt>じん</rt></ruby>です。 (Saya juga orang Indonesia.)",
                correct: ["mo", "も"],
                hint: "Partikel yang berarti 'juga' atau 'pula'."
            },
            {
                id: "q_1_5",
                type: "mcq",
                node_id: "grammar_ka",
                grammar_focus: "か (ka) — Partikel Tanya",
                question: "Lengkapi kalimat tanya: あれはなんですか ___。 (Apakah itu?)",
                options: ["ね (ne)", "よ (yo)", "か (ka)", "な (na)"],
                correctIndex: 2,
                hint: "Partikel akhir yang menandai pertanyaan."
            },
            {
                id: "q_1_6",
                type: "mcq",
                node_id: "grammar_dewa_nai",
                grammar_focus: "じゃない・ではない (dewa nai) — Negatif To Be",
                question: "Pilihlah bentuk negatif sopan (bukan/tidak) yang tepat: わたしは<ruby>先生<rt>せんせい</rt></ruby> ___。 (Saya bukan guru.)",
                options: ["ではありません (dewa arimasen)", "じゃないでした (janai deshita)", "ですない (desu nai)", "ではあります (dewa arimasu)"],
                correctIndex: 0,
                hint: "Bentuk negatif formal dari desu adalah dewa arimasen."
            },
            {
                id: "q_1_7",
                type: "mcq",
                node_id: "grammar_kore_sore_are",
                grammar_focus: "これ・それ・あれ (Ko-So-A-Do) — Kata Penunjuk Benda",
                question: "Pilihlah kata penunjuk yang tepat: ほしいものは ___ だけです。 (Barang yang saya inginkan hanya ini [dekat pembicara].)",
                options: ["それ (sore)", "あれ (are)", "これ (kore)", "どれ (dore)"],
                correctIndex: 2,
                hint: "Ko-so-a-do: 'kore' digunakan untuk menunjuk benda yang dekat dengan pembicara."
            },
            {
                id: "q_1_8",
                type: "fill",
                node_id: "grammar_dare",
                grammar_focus: "誰 (dare) — Kata Tanya 'Siapa'",
                question: "Lengkapi kalimat tanya: あそこにいる<ruby>人<rt>ひと</rt></ruby>は ___ ですか。 (Siapa orang yang ada di sana?)",
                correct: ["dare", "だれ", "donata", "どなた"],
                hint: "Kata tanya untuk menanyakan orang ('siapa')."
            },
            {
                id: "q_1_9",
                type: "translate",
                node_id: "grammar_desu",
                grammar_focus: "だ・です (da/desu) — Penerapan Struktur Kalimat",
                question: "Terjemahkan ke bahasa Jepang: 'Nama saya adalah Chris.' (Tulis dalam Romaji huruf kecil)",
                acceptedAnswers: [
                    "watashi no namae wa kurisu desu",
                    "watashi no namae wa kurisu desu.",
                    "watashino namae wa kurisu desu"
                ],
                hint: "Gunakan partikel 'no', 'wa', dan diakhiri dengan 'desu'."
            },
            {
                id: "q_1_10",
                type: "fill",
                node_id: "grammar_hai_iie",
                grammar_focus: "はい・いいえ (hai/iie) — Ya / Tidak",
                question: "Lengkapi percakapan: A: Tanaka-san wa gakusei desu ka? B: ___, gakusei desu. (Ya, siswa.)",
                correct: ["hai", "はい"],
                hint: "Kata persetujuan 'Ya'."
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
                grammar_focus: "があります (ga arimasu) — Ada (Benda Mati)",
                question: "Pilihlah kalimat yang tepat untuk menyatakan 'Ada buku':",
                options: ["<ruby>本<rt>ほん</rt></ruby>がいます (hon ga imasu)", "<ruby>本<rt>ほん</rt></ruby>があります (hon ga arimasu)", "<ruby>本<rt>ほん</rt></ruby>をあります (hon o arimasu)", "<ruby>本<rt>ほん</rt></ruby>にあります (hon ni arimasu)"],
                correctIndex: 1,
                hint: "Buku adalah benda mati. Gunakan partikel 'ga' + 'arimasu'."
            },
            {
                id: "q_2_2",
                type: "fill",
                node_id: "grammar_ga_imasu",
                grammar_focus: "がいます (ga imasu) — Ada (Makhluk Hidup)",
                question: "Lengkapi kalimat: あそこに<ruby>猫<rt>ねこ</rt></ruby>が ___。 (Ada kucing di sana.)",
                correct: ["imasu", "います"],
                hint: "Kucing adalah makhluk hidup, gunakan kata kerja keberadaan 'imasu'."
            },
            {
                id: "q_2_3",
                type: "mcq",
                node_id: "grammar_ni_location",
                grammar_focus: "に (ni) — Partikel Lokasi Keberadaan",
                question: "Lengkapi kalimat: <ruby>机<rt>つくえ</rt></ruby>の<ruby>上<rt>うえ</rt></ruby> ___ <ruby>本<rt>ほん</rt></ruby>があります。 (Di atas meja ada buku.)",
                options: ["で (de)", "を (o)", "に (ni)", "が (ga)"],
                correctIndex: 2,
                hint: "Partikel 'ni' menandai lokasi keberadaan benda/makhluk hidup."
            },
            {
                id: "q_2_4",
                type: "fill",
                node_id: "grammar_doko",
                grammar_focus: "どこ (doko) — Kata Tanya 'Di mana'",
                question: "Lengkapi kalimat tanya: トイレは ___ ですか。 (Toiletnya di mana?)",
                correct: ["doko", "どこ"],
                hint: "Kata tanya tempat ('di mana')."
            },
            {
                id: "q_2_5",
                type: "mcq",
                node_id: "grammar_kono_sono_ano",
                grammar_focus: "この・その・あの — Kata Penunjuk Benda + Kata Benda",
                question: "Lengkapi kalimat: ___ <ruby>本<rt>ほん</rt></ruby>はわたしのです。 (Buku ini adalah milik saya.)",
                options: ["これ (kore)", "この (kono)", "あそこ (asoko)", "それ (sore)"],
                correctIndex: 1,
                hint: "Kata penunjuk yang harus diikuti langsung oleh kata benda (hon = buku)."
            },
            {
                id: "q_2_6",
                type: "mcq",
                node_id: "grammar_ni_e_destination",
                grammar_focus: "へ (e) — Partikel Arah/Tujuan",
                question: "Lengkapi kalimat: <ruby>日本<rt>にほん</rt></ruby> ___ <ruby>行<rt>い</rt></ruby>きます。 (Pergi ke Jepang.)",
                options: ["で (de)", "を (o)", "へ (e)", "が (ga)"],
                correctIndex: 2,
                hint: "Partikel 'he' (ditulis 'he' tapi dibaca 'e') menunjukkan arah/tujuan perjalanan."
            },
            {
                id: "q_2_7",
                type: "mcq",
                node_id: "grammar_de_place",
                grammar_focus: "で (de) — Partikel Tempat Aktivitas",
                question: "Lengkapi kalimat: レストラン ___ ごはんを<ruby>食<rt>た</rt></ruby>べます。 (Makan nasi di restoran.)",
                options: ["に (ni)", "で (de)", "を (o)", "へ (e)"],
                correctIndex: 1,
                hint: "Partikel 'de' digunakan untuk menandai tempat terjadinya suatu tindakan/aktivitas."
            },
            {
                id: "q_2_8",
                type: "fill",
                node_id: "grammar_to",
                grammar_focus: "と (to) — Partikel Penghubung 'Dan'",
                question: "Lengkapi kalimat: ペン ___ えんぴつがあります。 (Ada pena dan pensil.)",
                correct: ["to", "と"],
                hint: "Partikel untuk menghubungkan dua kata benda sejajar yang berarti 'dan'."
            },
            {
                id: "q_2_9",
                type: "fill",
                node_id: "grammar_nani",
                grammar_focus: "何 (nani/nan) — Kata Tanya 'Apa'",
                question: "Lengkapi kalimat tanya: それは ___ ですか。 (Apakah itu?)",
                correct: ["nan", "nani", "なん", "なに"],
                hint: "Kata tanya 'apa'. Sebelum 'desu ka', lafalnya berubah menjadi 'nan'."
            },
            {
                id: "q_2_10",
                type: "translate",
                node_id: "grammar_ga_arimasu",
                grammar_focus: "があります (ga arimasu) — Struktur Keberadaan",
                question: "Terjemahkan ke bahasa Jepang: 'Di atas meja ada kucing.' (Tulis dalam Romaji)",
                acceptedAnswers: [
                    "tsukue no ue ni neko ga imasu",
                    "tsukue no ue ni neko ga imasu.",
                    "tsukue no ue niwa neko ga imasu"
                ],
                hint: "Meja = tsukue, atas = ue, kucing = neko (makhluk hidup -> imasu)."
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
                grammar_focus: "時 (ji) — Akhiran Penghitung Jam",
                question: "Pilihlah bahasa Jepang yang tepat untuk 'Jam 3':",
                options: ["さんじ (san-ji)", "みっじ (mit-ji)", "さんじかん (san-jikan)", "さんふん (san-fun)"],
                correctIndex: 0,
                hint: "Angka 3 (san) diikuti dengan akhiran jam (ji)."
            },
            {
                id: "q_3_2",
                type: "fill",
                node_id: "grammar_fun_pun",
                grammar_focus: "分 (fun/pun) — Akhiran Menit",
                question: "Lengkapi kalimat: 今は<ruby>二時十分<rt>にじじゅっぷん</rt></ruby> ___ です。 (Sekarang jam 2 lewat 10 menit.)",
                correct: ["pun", "ぷん"],
                hint: "Untuk angka 10 (juu), akhiran menit dilafalkan 'pun'."
            },
            {
                id: "q_3_3",
                type: "mcq",
                node_id: "grammar_kara_made",
                grammar_focus: "から〜まで (kara~made) — Dari ~ Sampai",
                question: "Lengkapi kalimat: <ruby>一時<rt>いちじ</rt></ruby> ___ <ruby>八時<rt>はちじ</rt></ruby> ___ です。 (Dari jam 1 sampai jam 8.)",
                options: ["kara ... made", "de ... ni", "to ... made", "kara ... ni"],
                correctIndex: 0,
                hint: "Pola untuk menyatakan rentang waktu 'dari ~ sampai'."
            },
            {
                id: "q_3_4",
                type: "fill",
                node_id: "grammar_han",
                grammar_focus: "半 (han) — Setengah Jam",
                question: "Lengkapi kalimat: 今は<ruby>七時<rt>しちじ</rt></ruby> ___ です。 (Sekarang jam 7 lewat 30 menit / setengah 8.)",
                correct: ["han", "はん", "半"],
                hint: "Kata untuk 'setengah' jam dalam penunjukan waktu."
            },
            {
                id: "q_3_5",
                type: "mcq",
                node_id: "grammar_mai",
                grammar_focus: "枚 (mai) — Penghitung Benda Tipis/Flat",
                question: "Lengkapi kalimat: シャツを<ruby>二<rt>に</rt></ruby> ___ <ruby>買<rt>か</rt></ruby>いました。 (Saya membeli dua helai kemeja.)",
                options: ["本 (hon)", "冊 (satsu)", "枚 (mai)", "個 (ko)"],
                correctIndex: 2,
                hint: "Kemeja adalah benda tipis/datar. Gunakan satuan bilangan 'mai'."
            },
            {
                id: "q_3_6",
                type: "fill",
                node_id: "grammar_hitori_futari",
                grammar_focus: "一人・二人 — Counter Orang Khusus",
                question: "<ruby>教室<rt>きょうしつ</rt></ruby>に<ruby>学生<rt>がくせい</rt></ruby>が<ruby>二<rt>に</rt></ruby> ___ います。 (Ada dua orang siswa di kelas.)",
                correct: ["futari", "ふたり", "二人"],
                hint: "Hitungan khusus untuk 'dua orang'."
            },
            {
                id: "q_3_7",
                type: "mcq",
                node_id: "grammar_goro",
                grammar_focus: "ごろ (goro) — Perkiraan Waktu",
                question: "<ruby>三時<rt>さんじ</rt></ruby> ___ に<ruby>行<rt>い</rt></ruby>きます。 (Pergi sekitar jam 3.)",
                options: ["ごろ (goro)", "ぐらい (gurai)", "だけ (dake)", "まで (made)"],
                correctIndex: 0,
                hint: "Gunakan 'goro' untuk titik perkiraan waktu (jam/hari/tahun). 'Gurai' untuk durasi."
            },
            {
                id: "q_3_8",
                type: "mcq",
                node_id: "grammar_ikutsu_ikura",
                grammar_focus: "いくら (ikura) — Menanyakan Harga",
                question: "このりんごは ___ ですか。 (Berapa harga apel ini?)",
                options: ["いくつ (ikutsu)", "いくら (ikura)", "どんな (donna)", "だれ (dare)"],
                correctIndex: 1,
                hint: "Kata tanya untuk menanyakan harga barang adalah 'ikura'."
            },
            {
                id: "q_3_9",
                type: "fill",
                node_id: "grammar_itsu",
                grammar_focus: "いつ (itsu) — Kata Tanya 'Kapan'",
                question: "<ruby>日本<rt>にほん</rt></ruby>へ ___ <ruby>行<rt>い</rt></ruby>きますか。 (Kapan kamu pergi ke Jepang?)",
                correct: ["itsu", "いつ"],
                hint: "Kata tanya waktu ('kapan')."
            },
            {
                id: "q_3_10",
                type: "translate",
                node_id: "grammar_kara_made",
                grammar_focus: "から〜まで — Terjemahan Waktu",
                question: "Terjemahkan ke bahasa Jepang: 'Toko buka dari jam 9 sampai jam 6.' (Toko = mise)",
                acceptedAnswers: [
                    "mise wa ku-ji kara roku-ji made desu",
                    "mise wa kuji kara rokuji made desu",
                    "mise wa 9-ji kara 6-ji made desu"
                ],
                hint: "Toko = mise, jam 9 = ku-ji, jam 6 = roku-ji."
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
                grammar_focus: "い-adjectives — Kata Sifat berakhiran -i",
                question: "Pilihlah kata sifat-i (i-adjective) yang tepat di bawah ini:",
                options: ["きれい (kirei)", "しずか (shizuka)", "たかい (takai)", "genki (genki)"],
                correctIndex: 2,
                hint: "Takai (mahal/tinggi) adalah i-adjective asli. Kirei dan shizuka adalah na-adjective."
            },
            {
                id: "q_4_2",
                type: "mcq",
                node_id: "grammar_na_adj",
                grammar_focus: "な-adjectives — Kata Sifat-na",
                question: "Pilihlah kalimat yang menggunakan kata sifat-na secara benar untuk mendeskripsikan kota yang tenang:",
                options: ["しずか<ruby>町<rt>まち</rt></ruby> (shizuka machi)", "しずかい<ruby>町<rt>まち</rt></ruby> (shizukai machi)", "しずかな<ruby>町<rt>まち</rt></ruby> (shizuka na machi)", "しずかの<ruby>町<rt>まち</rt></ruby> (shizuka no machi)"],
                correctIndex: 2,
                hint: "Kata sifat-na memerlukan partikel 'na' ketika memodifikasi kata benda (machi)."
            },
            {
                id: "q_4_3",
                type: "mcq",
                node_id: "grammar_i_adj_neg",
                grammar_focus: "い-adjective Negatif: -kunai",
                question: "Bentuk negatif dari 'あつい' (atsui - panas) yang tepat adalah:",
                options: ["あついじゃない (atsui janai)", "あつくない (atsuku nai)", "あつない (atsunai)", "あつじゃない (atsu janai)"],
                correctIndex: 1,
                hint: "Ubah akhiran -i menjadi -kunai. Atsui -> atsuku nai."
            },
            {
                id: "q_4_4",
                type: "fill",
                node_id: "grammar_totemo",
                grammar_focus: "とても (totemo) — Sangat",
                question: "Lengkapi kalimat: このラーメンは ___ おいしいです。 (Ramen ini sangat enak.)",
                correct: ["totemo", "とても"],
                hint: "Kata keterangan penguat yang berarti 'sangat' (totemo)."
            },
            {
                id: "q_4_5",
                type: "mcq",
                node_id: "grammar_amari_neg",
                grammar_focus: "あまり〜ない (amari~nai) — Tidak Terlalu",
                question: "Lengkapi kalimat: この<ruby>肉<rt>にく</rt></ruby>はあまり ___。 (Daging ini tidak begitu enak.)",
                options: ["おいしいです (oishii desu)", "おいしくないです (oishikunai desu)", "おいしいじゃない (oishii janai)", "おいしかったです (oishikatta desu)"],
                correctIndex: 1,
                hint: "Kata keterangan 'amari' (tidak terlalu) wajib diikuti oleh bentuk kalimat negatif."
            },
            {
                id: "q_4_6",
                type: "fill",
                node_id: "grammar_donna",
                grammar_focus: "どんな (donna) — Kata Tanya Karakteristik",
                question: "Lengkapi kalimat tanya: ___ <ruby>人<rt>ひと</rt></ruby>が好きですか。 (Kamu menyukai orang yang seperti apa?)",
                correct: ["donna", "どんな"],
                hint: "Kata tanya untuk menanyakan karakteristik ('yang bagaimana / seperti apa')."
            },
            {
                id: "q_4_7",
                type: "mcq",
                node_id: "grammar_na_adj_noun",
                grammar_focus: "な-adjective + Kata Benda",
                question: "Pilihlah bentuk deskripsi yang tepat untuk menyatakan 'Bunga yang cantik' (hana = bunga):",
                options: ["きれいな<ruby>花<rt>はな</rt></ruby> (kireina hana)", "きれいい<ruby>花<rt>はな</rt></ruby> (kireii hana)", "きれい<ruby>花<rt>はな</rt></ruby> (kirei hana)", "きれいの<ruby>花<rt>はな</rt></ruby> (kirei no hana)"],
                correctIndex: 0,
                hint: "Kirei adalah na-adjective pengecualian (meski berakhiran -i). Maka gunakan 'kireina hana'."
            },
            {
                id: "q_4_8",
                type: "mcq",
                node_id: "grammar_ii_yoku",
                grammar_focus: "いい/よい (ii/yoi) — Bagus (Bentuk Irregular)",
                question: "Bentuk negatif dari kata sifat 'いい' (ii - bagus) adalah:",
                options: ["いいくない (iikunai)", "よくない (yoku nai)", "いくない (ikunai)", "いいじゃない (ii janai)"],
                correctIndex: 1,
                hint: "Kata 'ii' berasal dari 'yoi', perubahannya tidak beraturan: ii -> yoku nai."
            },
            {
                id: "q_4_9",
                type: "fill",
                node_id: "grammar_ga_but",
                grammar_focus: "が (ga) — Tetapi / Namun (Konjungsi)",
                question: "Lengkapi kalimat hubung: このカメラは<ruby>高<rt>たか</rt></ruby>いです ___、とてもいいです。 (Kamera ini mahal, tetapi sangat bagus.)",
                correct: ["ga", "が"],
                hint: "Partikel di tengah kalimat yang berarti 'tetapi/namun' (ga)."
            },
            {
                id: "q_4_10",
                type: "translate",
                node_id: "grammar_i_adj",
                grammar_focus: "い-adjective — Terjemahan Deskripsi",
                question: "Terjemahkan ke bahasa Jepang: 'Hari ini sangat panas.' (Hari ini = kyou, panas = atsui)",
                acceptedAnswers: [
                    "kyou wa totemo atsui desu",
                    "kyou wa totemo atsui desu.",
                    "kyou wa totemo atsui"
                ],
                hint: "Hari ini = kyou, sangat = totemo, panas = atsui."
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
                grammar_focus: "を (o/wo) — Partikel Objek",
                question: "Lengkapi kalimat: <ruby>毎日<rt>まいにち</rt></ruby>、コーヒー ___ <ruby>飲<rt>の</rt></ruby>んでいます。 (Setiap hari, saya minum kopi.)",
                options: ["が (ga)", "を (o/wo)", "に (ni)", "で (de)"],
                correctIndex: 1,
                hint: "Kopi adalah objek penderita dari kata kerja 'nomimasu' (minum). Gunakan partikel o."
            },
            {
                id: "q_5_2",
                type: "fill",
                node_id: "grammar_shimasu",
                grammar_focus: "します (shimasu) — Melakukan",
                question: "Lengkapi kalimat: <ruby>毎週土曜日<rt>まいしゅうどようび</rt></ruby>にサッカーを ___。 (Setiap hari Sabtu, saya bermain sepak bola.)",
                correct: ["shimasu", "します"],
                hint: "Kata kerja untuk menyatakan 'melakukan' olahraga atau hobi."
            },
            {
                id: "q_5_3",
                type: "mcq",
                node_id: "grammar_ni_iku",
                grammar_focus: "に行く (ni iku) — Pergi Untuk Melakukan",
                question: "Pilihlah bentuk yang tepat untuk menyatakan 'Pergi untuk makan':",
                options: ["<ruby>食<rt>た</rt></ruby>べに<ruby>行<rt>い</rt></ruby>きます (tabe ni ikimasu)", "<ruby>食<rt>た</rt></ruby>べて<ruby>行<rt>い</rt></ruby>きます (tabete ikimasu)", "<ruby>食<rt>た</rt></ruby>べるに<ruby>行<rt>い</rt></ruby>きます (taberu ni ikimasu)", "<ruby>食<rt>た</rt></ruby>べに<ruby>行<rt>い</rt></ruby>き (tabe ni iki)"],
                correctIndex: 0,
                hint: "Kata kerja bentuk stem-masu (tabe) + partikel 'ni' + ikimasu."
            },
            {
                id: "q_5_4",
                type: "fill",
                node_id: "grammar_issho_ni",
                grammar_focus: "一緒に (issho ni) — Bersama-sama",
                question: "Lengkapi ajakan: ___ <ruby>映画<rt>えいが</rt></ruby>を<ruby>見<rt>み</rt></ruby>ませんか。 (Maukah menonton film bersama?)",
                correct: ["issho ni", "いっしょに"],
                hint: "Bahasa Jepang dari 'bersama-sama'."
            },
            {
                id: "q_5_5",
                type: "mcq",
                node_id: "grammar_masen_ka",
                grammar_focus: "〜ませんか (masen ka) — Ajakan Sopan",
                question: "Pilihlah bentuk ajakan sopan 'Maukah kamu minum kopi bersama?':",
                options: ["コーヒーを<ruby>飲<rt>の</rt></ruby>みましょう (koohii o nomimashou)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みませんか (koohii o nomimasen ka)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みますか (koohii o nomimasu ka)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みたいes (koohii o nomitai desu)"],
                correctIndex: 1,
                hint: "Nomimasen ka (maukah minum) adalah bentuk ajakan paling sopan karena memberikan pilihan bagi lawan bicara."
            },
            {
                id: "q_5_6",
                type: "fill",
                node_id: "grammar_mashou",
                grammar_focus: "〜ましょう (mashou) — Ayo Melakukan",
                question: "Lengkapi ajakan penegasan 'Ayo pergi!': <ruby>行<rt>い</rt></ruby>き___！",
                correct: ["mashou", "ましょう"],
                hint: "Akhiran bentuk -mashou digunakan untuk menyatakan 'Ayo kita lakukan!'."
            },
            {
                id: "q_5_7",
                type: "mcq",
                node_id: "grammar_doushite",
                grammar_focus: "どうして (doushite) — Kenapa / Mengapa",
                question: "Lengkapi kalimat tanya: ___ <ruby>学校<rt>がっこう</rt></ruby>を<ruby>休<rt>やす</rt></ruby>みましたか。 (Kenapa kamu libur sekolah?)",
                options: ["だれ (dare)", "どうして (doushite)", "いつ (itsu)", "いくら (ikura)"],
                correctIndex: 1,
                hint: "Kata tanya untuk menanyakan sebab/alasan ('mengapa/kenapa')."
            },
            {
                id: "q_5_8",
                type: "fill",
                node_id: "grammar_kara_reason",
                grammar_focus: "から (kara) — Karena (Alasan)",
                question: "Lengkapi kalimat: 今日は<ruby>雨<rt>あめ</rt></ruby>が<ruby>降<rt>ふ</rt></ruby>りました ___、<ruby>学校<rt>がっこう</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きませんでした。 (Karena hari ini turun hujan, saya tidak pergi ke sekolah.)",
                correct: ["kara", "から"],
                hint: "Partikel yang diletakkan setelah klausa alasan/sebab ('karena')."
            },
            {
                id: "q_5_9",
                type: "mcq",
                node_id: "grammar_frequency",
                grammar_focus: "Keterangan Frekuensi (Itsumo)",
                question: "Pilihlah kata keterangan frekuensi yang bermakna 'selalu / biasanya':",
                options: ["ときどき (tokidoki)", "よく (yoku)", "いつも (itsumo)", "あまり (amari)"],
                correctIndex: 2,
                hint: "Itsumo berarti 'selalu/biasanya'. Tokidoki = kadang-kadang, yoku = sering."
            },
            {
                id: "q_5_10",
                type: "translate",
                node_id: "grammar_o_particle",
                grammar_focus: "を (o) — Terjemahan Aktivitas",
                question: "Terjemahkan ke bahasa Jepang: 'Setiap hari saya makan apel.' (Setiap hari = mainichi, apel = ringo)",
                acceptedAnswers: [
                    "mainichi ringo o tabemasu",
                    "mainichi ringo o tabemasu.",
                    "watashi wa mainichi ringo o tabemasu",
                    "mainichi ringo wo tabemasu"
                ],
                hint: "Setiap hari = mainichi, apel = ringo, makan = tabemasu."
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
                grammar_focus: "〜たい (tai) — Ingin Melakukan",
                question: "Pilihlah kalimat yang benar untuk menyatakan 'Saya ingin minum teh':",
                options: ["<ruby>お茶<rt>おちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>みたいです (ocha o nomitai desu)", "<ruby>お茶<rt>おちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>みていです (ocha o nomitei desu)", "<ruby>お茶<rt>おちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>mu たいです (ocha o nomutai desu)", "<ruby>お茶<rt>おちゃ</rt></ruby>が<ruby>飲<rt>の</rt></ruby>みます (ocha ga nomimasu)"],
                correctIndex: 0,
                hint: "Kata kerja stem-masu (nomi) + tai desu."
            },
            {
                id: "q_6_2",
                type: "fill",
                node_id: "grammar_ga_hoshii",
                grammar_focus: "がほしい (ga hoshii) — Ingin (Benda)",
                question: "Lengkapi kalimat keinginan: <ruby>新<rt>あたら</rt></ruby>しい<ruby>車<rt>くるま</rt></ruby>が ___ です。 (Saya ingin mobil baru.)",
                correct: ["hoshii", "ほしい", "欲しい"],
                hint: "Gunakan kata sifat 'hoshii' untuk menyatakan keinginan terhadap suatu benda."
            },
            {
                id: "q_6_3",
                type: "mcq",
                node_id: "grammar_no_ga_suki",
                grammar_focus: "のが好き (no ga suki) — Suka Melakukan",
                question: "Lengkapi kalimat: 私は<ruby>音楽<rt>おんがく</rt></ruby>を<ruby>聞<rt>き</rt></ruby>く ___ が好きです。 (Saya suka mendengarkan musik.)",
                options: ["こと (koto)", "の (no)", "もの (mono)", "と (to)"],
                correctIndex: 1,
                hint: "V-dictionary (kiku) + partikel 'no' + ga suki desu untuk merujuk pada kesukaan aktivitas."
            },
            {
                id: "q_6_4",
                type: "fill",
                node_id: "grammar_jouzu_heta",
                grammar_focus: "のが下手 (no ga heta) — Tidak Pandai",
                question: "Lengkapi kalimat: 私は<ruby>歌<rt>うた</rt></ruby>が ___ です。 (Saya tidak pandai bernyanyi.)",
                correct: ["heta", "へた", "下手"],
                hint: "Lawan kata dari 'jouzu' (pandai) adalah 'heta' (tidak pandai/payah)."
            },
            {
                id: "q_6_5",
                type: "fill",
                node_id: "grammar_wakaru",
                grammar_focus: "わかる (wakaru) — Mengerti / Paham",
                question: "Lengkapi kalimat: 私は<ruby>英語<rt>えいご</rt></ruby>がよく ___。 (Saya sangat paham bahasa Inggris.)",
                correct: ["wakarimasu", "わかります", "wakaru", "わかる"],
                hint: "Kata kerja 'mengerti/paham' dalam bentuk sopan desu/masu."
            },
            {
                id: "q_6_6",
                type: "mcq",
                node_id: "grammar_ichiban",
                grammar_focus: "一番 (ichiban) — Paling / Nomor Satu",
                question: "Lengkapi kalimat: くだものの中で、りんごが ___ 好きです。 (Di antara buah-buahan, saya paling suka apel.)",
                options: ["もっと (motto)", "一番 (ichiban)", "ずっと (zutto)", "とても (totemo)"],
                correctIndex: 1,
                hint: "Kata 'ichiban' digunakan untuk menyatakan predikat superlatif ('paling/nomor satu')."
            },
            {
                id: "q_6_7",
                type: "fill",
                node_id: "grammar_yori",
                grammar_focus: "より (yori) — Daripada (Perbandingan)",
                question: "Lengkapi kalimat perbandingan: <ruby>猫<rt>ねこ</rt></ruby>は<ruby>犬<rt>いぬ</rt></ruby> ___ <ruby>小<rt>ちい</rt></ruby>さいです。 (Kucing lebih kecil daripada anjing.)",
                correct: ["yori", "より"],
                hint: "Partikel 'yori' ditempelkan pada benda pembanding yang berarti 'daripada'."
            },
            {
                id: "q_6_8",
                type: "mcq",
                node_id: "grammar_hou_ga_ii",
                grammar_focus: "ほうがいい (hou ga ii) — Lebih Baik / Saran",
                question: "Lengkapi kalimat: <ruby>風邪<rt>かぜ</rt></ruby>ですね。早く ___ ほうがいいですよ。 (Kamu sedang flu ya. Sebaiknya tidur cepat.)",
                options: ["<ruby>寝<rt>ね</rt></ruby>る (neru)", "<ruby>寝<rt>ね</rt></ruby>て (nete)", "<ruby>寝<rt>ね</rt></ruby>た (neta)", "<ruby>寝<rt>ね</rt></ruby>ない (nenai)"],
                correctIndex: 2,
                hint: "Pola 'hou ga ii' (sebaiknya) untuk saran positif berpasangan dengan kata kerja bentuk lampau kasual (~ta)."
            },
            {
                id: "q_6_9",
                type: "fill",
                node_id: "grammar_dou_desu_ka",
                grammar_focus: "はどうですか (wa dou desu ka) — Bagaimana Kalau",
                question: "Lengkapi penawaran berikut: <ruby>温<rt>あたた</rt></ruby>かいお<ruby>茶<rt>おちゃ</rt></ruby>は ___ ですか。 (Bagaimana kalau minum teh hangat?)",
                correct: ["dou", "どう"],
                hint: "Kata tanya 'dou desu ka' digunakan untuk menanyakan keadaan atau menawarkan sesuatu."
            },
            {
                id: "q_6_10",
                type: "translate",
                node_id: "grammar_tai",
                grammar_focus: "〜たい — Terjemahan Keinginan",
                question: "Terjemahkan ke bahasa Jepang: 'Saya ingin pergi ke Jepang.' (Jepang = nihon, pergi = ikimasu)",
                acceptedAnswers: [
                    "nihon ni ikitai desu",
                    "nihon ni ikitai desu.",
                    "nihon e ikitai desu",
                    "watashi wa nihon ni ikitai desu"
                ],
                hint: "Jepang = nihon, pergi = ikimasu -> ikitai desu."
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
                grammar_focus: "てください (te kudasai) — Tolong Lakukan",
                question: "Lengkapi kalimat: <ruby>名前<rt>なまえ</rt></ruby>をここに ___ ください。 (Tolong tulis namamu di sini.)",
                options: ["<ruby>書<rt>か</rt></ruby>く (kaku)", "<ruby>書<rt>か</rt></ruby>いて (kaite)", "<ruby>書<rt>か</rt></ruby>きます (kakimasu)", "<ruby>書<rt>か</rt></ruby>かない (kakanai)"],
                correctIndex: 1,
                hint: "Pola permintaan sopan 'tolong lakukan' dibentuk dari Kata Kerja bentuk -te + kudasai."
            },
            {
                id: "q_7_2",
                type: "fill",
                node_id: "grammar_te_mo_ii",
                grammar_focus: "てもいいです (temo ii desu) — Boleh / Izin",
                question: "Lengkapi izin berikut: <ruby>写真<rt>しゃしん</rt></ruby>を<ruby>撮<rt>と</rt></ruby>っても ___ ですか。 (Bolehkah saya mengambil foto?)",
                correct: ["ii", "いい"],
                hint: "Pola izin: V-te + mo ii desu ka?"
            },
            {
                id: "q_7_3",
                type: "mcq",
                node_id: "grammar_te_wa_ikenai",
                grammar_focus: "てはいけない (te wa ikenai) — Larangan",
                question: "Lengkapi kalimat: ここは<ruby>危<rt>あぶ</rt></ruby>ないから、<ruby>入<rt>はい</rt></ruby>って ___。 (Karena di sini bahaya, kamu tidak boleh masuk.)",
                options: ["はいいです (wa ii desu)", "はいけません (wa ikemasen)", "はだめ (wa dame)", "はいいですか (wa ii desu ka)"],
                correctIndex: 1,
                hint: "Pola larangan formal: V-te + wa ikemasen (tidak boleh)."
            },
            {
                id: "q_7_4",
                type: "fill",
                node_id: "grammar_te_iru",
                grammar_focus: "ている (te iru) — Sedang Berlangsung",
                question: "Lengkapi kalimat: 彼は今、日本語を勉強して ___。 (Dia sekarang sedang belajar bahasa Jepang.)",
                correct: ["imasu", "います", "iru", "いる"],
                hint: "Pola sedang berlangsung: V-te + imasu."
            },
            {
                id: "q_7_5",
                type: "mcq",
                node_id: "grammar_te_iru_state",
                grammar_focus: "ている — Keadaan Menetap",
                question: "Pilihlah bentuk yang tepat untuk menyatakan 'Saya sudah menikah' (status saat ini):",
                options: ["<ruby>結婚<rt>けっこん</rt></ruby>します (kekkon shimasu)", "<ruby>結婚<rt>けっこん</rt></ruby>しています (kekkon shite imasu)", "<ruby>結婚<rt>けっこん</rt></ruby>しました (kekkon shimashita)", "<ruby>結婚<rt>けっこん</rt></ruby>してありました (kekkon shite arimashita)"],
                correctIndex: 1,
                hint: "Gunakan bentuk 'V-te imasu' untuk menunjukkan kondisi/status yang bertahan dari suatu aksi lampau."
            },
            {
                id: "q_7_6",
                type: "fill",
                node_id: "grammar_te_kara",
                grammar_focus: "てから (te kara) — Setelah Melakukan",
                question: "Lengkapi kalimat: <ruby>手<rt>て</rt></ruby>を<ruby>洗<rt>あら</rt></ruby>t て ___ 、<ruby>ご飯<rt>ごはん</rt></ruby>を食べます。 (Setelah mencuci tangan, baru saya makan nasi.)",
                correct: ["kara", "から"],
                hint: "Pola V-te + kara berarti 'setelah melakukan [A], baru melakukan [B]'."
            },
            {
                id: "q_7_7",
                type: "mcq",
                node_id: "grammar_te_ageru_morau_kureru",
                grammar_focus: "てあげる・てもらう・てくれる — Jasa/Bantuan",
                question: "Pilihlah kalimat yang tepat untuk menyatakan 'Teman saya membacakan buku untuk saya':",
                options: ["<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んであげました", "<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んでくれました", "<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んでいいました", "<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んでいきました"],
                correctIndex: 1,
                hint: "Kureru digunakan ketika orang lain memberikan/melakukan sesuatu yang menguntungkan pembicara."
            },
            {
                id: "q_7_8",
                type: "fill",
                node_id: "grammar_tari_tari",
                grammar_focus: "たり〜たり (tari~tari) — Daftar Aktivitas Acak",
                question: "Lengkapi kalimat: <ruby>休<rt>やす</rt></ruby>みの<ruby>日<rt>ひ</rt></ruby>は<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>ん ___ 、<ruby>音楽<rt>おんがく</rt></ruby>を<ruby>聞<rt>き</rt></ruby>いたりします。 (Pada hari libur, saya membaca buku, mendengar musik, dll.)",
                correct: ["dari", "だり"],
                hint: "Pola tari~tari untuk daftar acak kata kerja. Karena form 'yonde' berakhiran 'de', maka 'tari' berubah menjadi 'dari'."
            },
            {
                id: "q_7_9",
                type: "fill",
                node_id: "grammar_te_miru",
                grammar_focus: "てみる (te miru) — Mencoba Melakukan",
                question: "Lengkapi kalimat: おいしそうですね。食べて ___ ます。 (Kelihatannya enak ya. Saya akan coba memakannya.)",
                correct: ["mi", "み"],
                hint: "Pola 'mencoba melakukan sesuatu' dibentuk dari V-te + mimasu."
            },
            {
                id: "q_7_10",
                type: "translate",
                node_id: "grammar_te_kudasai",
                grammar_focus: "てください — Terjemahan Permintaan",
                question: "Terjemahkan ke bahasa Jepang: 'Tolong tunggu sebentar.' (Tunggu = machimasu -> matte)",
                acceptedAnswers: [
                    "chotto matte kudasai",
                    "chotto matte kudasai.",
                    "sukoshi matte kudasai"
                ],
                hint: "Sebentar = chotto, menunggu = machimasu -> matte."
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
                grammar_focus: "たことがある (ta koto ga aru) — Pernah",
                question: "Pilihlah kalimat yang tepat untuk menyatakan 'Saya pernah pergi ke Jepang':",
                options: ["<ruby>日本<rt>にほん</rt></ruby>に<ruby>行<rt>い</rt></ruby>きことがあります", "<ruby>日本<rt>にほん</rt></ruby>に<ruby>行<rt>い</rt></ruby>ったことがあります", "<ruby>日本<rt>にほん</rt></ruby>に<ruby>行<rt>い</rt></ruby>てことがあります", "<ruby>日本<rt>にほん</rt></ruby>に<ruby>行<rt>い</rt></ruby>くことがあります"],
                correctIndex: 1,
                hint: "Pola menyatakan pengalaman 'pernah': V-ta (bentuk lampau kasual) + koto ga arimasu."
            },
            {
                id: "q_8_2",
                type: "fill",
                node_id: "grammar_mae_ni",
                grammar_focus: "前に (mae ni) — Sebelum Melakukan",
                question: "<ruby>寝<rt>ね</rt></ruby>る ___ スマホを<ruby>見<rt>み</rt></ruby>ちゃダメよ。 (Kamu tidak boleh melihat HP sebelum tidur.)",
                correct: ["mae ni", "まえに", "前に"],
                hint: "Pola V-dictionary (neru) + 'mae ni' berarti 'sebelum melakukan'."
            },
            {
                id: "q_8_3",
                type: "mcq",
                node_id: "grammar_nagara",
                grammar_focus: "ながら (nagara) — Sambil Melakukan",
                question: "<ruby>音楽<rt>おんがく</rt></ruby>を ___ <ruby>ご飯<rt>ごはん</rt></ruby>を食べます。 (Makan nasi sambil mendengarkan musik.)",
                options: ["<ruby>聞<rt>き</rt></ruby>くながら", "<ruby>聞<rt>き</rt></ruby>いてながら", "<ruby>聞<rt>き</rt></ruby>きながら", "<ruby>聞<rt>き</rt></ruby>かながら"],
                correctIndex: 2,
                hint: "Pola 'sambil': V-masu stem (kiki) + nagara."
            },
            {
                id: "q_8_4",
                type: "mcq",
                node_id: "grammar_mou_mada",
                grammar_focus: "まだ (mada) — Belum",
                question: "Lengkapi tanya-jawab ini: A: Mou gohan o tabemashita ka? B: Iie, ___ tabete imasen. (Belum makan.)",
                options: ["mou", "mada", "itsumo", "totemo"],
                correctIndex: 1,
                hint: "Mada (belum) digunakan bersama dengan bentuk negatif sedang berlangsung (~te imasen)."
            },
            {
                id: "q_8_5",
                type: "fill",
                node_id: "grammar_naru",
                grammar_focus: "なる (naru) — Menjadi",
                question: "<ruby>暖<rt>あたた</rt></ruby>かく ___ ましたね。 (Sudah menjadi hangat ya.)",
                correct: ["nari", "なり"],
                hint: "Kata kerja 'naru' (menjadi) dalam bentuk sopan lampau 'narimashita'."
            },
            {
                id: "q_8_6",
                type: "mcq",
                node_id: "grammar_ndesu",
                grammar_focus: "んです (ndesu) — Penjelasan / Penekanan",
                question: "Pilihlah ungkapan penjelasan/alasan yang tepat untuk menjawab 'Kenapa terlambat?':",
                options: ["<ruby>電車<rt>でんしゃ</rt></ruby>が<ruby>遅<rt>おく</rt></ruby>れました", "<ruby>電車<rt>でんしゃ</rt></ruby>が<ruby>遅<rt>おく</rt></ruby>れたのです", "<ruby>電車<rt>でんしゃ</rt></ruby>が<ruby>遅<rt>おく</rt></ruby>れたんです", "Semua di atas benar tergantung nuansa kesopanan"],
                correctIndex: 3,
                hint: "Akhiran ndesu (dan no desu) digunakan untuk memberi penjelasan. Bentuk polosnya juga benar tapi tanpa penekanan."
            },
            {
                id: "q_8_7",
                type: "fill",
                node_id: "grammar_toki",
                grammar_focus: "とき (toki) — Ketika / Saat",
                question: "<ruby>子<rt>こ</rt></ruby>どもの ___ 、甘いものが好きでした。 (Ketika anak-anak, saya suka makanan manis.)",
                correct: ["toki", "とき", "時"],
                hint: "Kata benda (kodomo) + 'no' + 'toki' berarti 'ketika/saat'."
            },
            {
                id: "q_8_8",
                type: "mcq",
                node_id: "grammar_sugiru",
                grammar_focus: "すぎる (sugiru) — Terlalu / Berlebihan",
                question: "昨日はお<ruby>酒<rt>さけ</rt></ruby>を ___ すぎました。 (Kemarin saya terlalu banyak minum alkohol.)",
                options: ["<ruby>飲<rt>の</rt></ruby>む (nomu)", "<ruby>飲<rt>の</rt></ruby>み (nomi)", "<ruby>飲<rt>の</rt></ruby>んで (nonde)", "<ruby>飲<rt>の</rt></ruby>んだ (nonda)"],
                correctIndex: 1,
                hint: "Kata kerja stem-masu (nomi) + sugiru berarti 'terlalu berlebihan melakukan'."
            },
            {
                id: "q_8_9",
                type: "fill",
                node_id: "grammar_deshou",
                grammar_focus: "でしょう (deshou) — Sepertinya / Kemungkinan",
                question: "<ruby>明日<rt>あした</rt></ruby>は<ruby>雨<rt>あめ</rt></ruby>が<ruby>降<rt>ふ</rt></ruby>る ___。 (Sepertinya besok akan turun hujan.)",
                correct: ["deshou", "でしょう"],
                hint: "Deshou digunakan untuk memperkirakan sesuatu secara sopan."
            },
            {
                id: "q_8_10",
                type: "translate",
                node_id: "grammar_ta_koto_ga_aru",
                grammar_focus: "たことがある — Terjemahan Pengalaman",
                question: "Terjemahkan ke bahasa Jepang: 'Apakah kamu pernah makan sushi?' (Sushi = sushi, makan = tabemasu)",
                acceptedAnswers: [
                    "sushi o tabeta koto ga arimasu ka",
                    "sushi o tabeta koto ga arimasu ka.",
                    "sushi wo tabeta koto ga arimasu ka",
                    "watashi wa sushi o tabeta koto ga arimasu ka"
                ],
                hint: "Sushi = sushi, makan = tabemasu -> tabeta, pernah = koto ga arimasu ka."
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
                grammar_focus: "なくてはいけない (nakute wa ikenai) — Harus",
                question: "<ruby>時間<rt>じかん</rt></ruby>がありませんから、早く ___。",
                options: ["<ruby>起<rt>お</rt></ruby>きなければなりません (okinakereba narimasen)", "<ruby>起<rt>お</rt></ruby>きてはいけません (okite wa ikemasen)", "<ruby>起<rt>お</rt></ruby>きてもいいです (okite mo ii desu)", "<ruby>起<rt>お</rt></ruby>きないでください (okinaide kudasai)"],
                correctIndex: 0,
                hint: "Pola menyatakan kewajiban/keharusan: V-nai (tanpa -i) + kereba narimasen."
            },
            {
                id: "q_9_2",
                type: "fill",
                node_id: "grammar_naide_kudasai",
                grammar_focus: "ないdeください (naide kudasai) — Tolong Jangan",
                question: "<ruby>写真<rt>しゃしん</rt></ruby>を<ruby>撮<rt>と</rt></ruby>ら ___ ください。 (Tolong jangan ambil foto.)",
                correct: ["naide", "ないで"],
                hint: "Pola permintaan jangan melakukan: V-nai + de kudasai."
            },
            {
                id: "q_9_3",
                type: "mcq",
                node_id: "grammar_tsumori",
                grammar_focus: "つもり (tsumori) — Berencana / Berniat",
                question: "<ruby>来年<rt>らいねん</rt></ruby>、<ruby>日本<rt>にほん</rt></ruby>へ<ruby>行<rt>い</rt></ruby>く ___ です. (Tahun depan, saya berencana pergi ke Jepang.)",
                options: ["つもり (tsumori)", "よてい (yotei)", "から (kara)", "こと (koto)"],
                correctIndex: 0,
                hint: "Pola niat/rencana personal: V-dictionary + tsumori desu."
            },
            {
                id: "q_9_4",
                type: "fill",
                node_id: "grammar_naku_temo_ii",
                grammar_focus: "なくてもいい (naku temo ii) — Tidak Harus",
                question: "<ruby>急<rt>いそ</rt></ruby>がなくても ___ ですよ。 (Kamu tidak harus terburu-buru lho.)",
                correct: ["ii", "いい"],
                hint: "Pola tidak harus: V-nakutemo ii desu."
            },
            {
                id: "q_9_5",
                type: "mcq",
                node_id: "grammar_koto_ga_dekiru",
                grammar_focus: "ことができる (koto ga dekiru) — Bisa / Mampu",
                question: "私は日本語を話すこと ___ できます。 (Saya bisa berbicara bahasa Jepang.)",
                options: ["を (o)", "が (ga)", "に (ni)", "は (wa)"],
                correctIndex: 1,
                hint: "Pola kemampuan: V-dictionary + koto ga dekimasu."
            },
            {
                id: "q_9_6",
                type: "mcq",
                node_id: "grammar_cha_ikenai",
                grammar_focus: "ちゃいけない — Larangan Kasual (Spoken)",
                question: "Pilihlah bentuk kasual lisan yang tepat untuk 'Jangan minum kopi itu' (dari nonde wa ikenai):",
                options: ["コーヒーを<ruby>飲<rt>の</rt></ruby>んじゃダメ (koohii o nonja dame)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みちゃダメ (koohii o nomicha dame)", "コーヒーを<ruby>飲<rt>の</rt></ruby>んだダメ (koohii o nonda dame)", "コーヒーを<ruby>飲<rt>の</rt></ruby>むちゃダメ (koohii o nomucha dame)"],
                correctIndex: 0,
                hint: "Dalam bahasa percakapan, bentuk V-te wa ikenai berubah menjadi cha/ja dame. Nomu -> nonde -> nonja dame."
            },
            {
                id: "q_9_7",
                type: "mcq",
                node_id: "grammar_node",
                grammar_focus: "ので (node) — Karena (Objektif)",
                question: "ここは<ruby>危険<rt>きけん</rt></ruby>な ___、<ruby>入<rt>はい</rt></ruby>っちゃダメだよ。 (Karena tempat ini berbahaya, kamu dilarang masuk.)",
                options: ["ので (node)", "から (kara)", "ため (tame)", "と (to)"],
                correctIndex: 0,
                hint: "Kata sifat-na (kikenna) + node untuk menyatakan alasan objektif/sopan."
            },
            {
                id: "q_9_8",
                type: "fill",
                node_id: "grammar_shikashi",
                grammar_focus: "しかし (shikashi) — Namun / Tetapi (Formal)",
                question: "Lengkapi kalimat formal: <ruby>日本<rt>にほん</rt></ruby>の<ruby>生活<rt>せいかつ</rt></ruby>は<ruby>大変<rt>たいへん</rt></ruby>es. ___、<ruby>面白<rt>おもしろ</rt></ruby>いです。 (Kehidupan di Jepang berat. Namun, menarik.)",
                correct: ["shikashi", "しかし"],
                hint: "Kata hubung tertulis formal yang berarti 'namun / tetapi' (shikashi)."
            },
            {
                id: "q_9_9",
                type: "mcq",
                node_id: "grammar_ne_yo",
                grammar_focus: "よ (yo) — Partikel Penegas Akhir",
                question: "Lengkapi kalimat: A: Kono keeki wa oishii desu ka? B: Hai, totemo oishii desu ___! (Ya, sangat enak lho!)",
                options: ["ね (ne)", "よ (yo)", "か (ka)", "な (na)"],
                correctIndex: 1,
                hint: "Partikel 'yo' digunakan untuk memberikan informasi baru atau meyakinkan pendengar."
            },
            {
                id: "q_9_10",
                type: "translate",
                node_id: "grammar_nakereba_naranai",
                grammar_focus: "なければならない — Terjemahan Keharusan",
                question: "Terjemahkan ke bahasa Jepang: 'Besok saya harus bangun jam 6.' (Besok = ashita, bangun = okiru)",
                acceptedAnswers: [
                    "ashita roku-ji ni okinakereba narimasen",
                    "watashi wa ashita roku-ji ni okinakereba narimasen",
                    "ashita rokuji ni okinakereba narimasen",
                    "watashi wa ashita rokuji ni okinakereba narimasen"
                ],
                hint: "Besok = ashita, jam 6 = roku-ji ni, harus bangun = okinakereba narimasen."
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
