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
                question: "Lengkapi kalimat: <ruby>私<rt>わたし</rt></ruby> ___ クリスです。 (Saya adalah Chris.)",
                options: ["を (wo)", "は (wa)", "に (ni)", "も (mo)"],
                correctIndex: 1,
                hint: "Topik utama kalimat ditandai dengan partikel 'wa' (ditulis hiragana は, bukan ha)."
            },
            {
                id: "q_1_2",
                type: "fill",
                node_id: "grammar_desu",
                grammar_focus: "だ・です (da/desu) — To Be (Sopan)",
                question: "Lengkapi kalimat penutup sopan berikut: かれは<ruby>私<rt>わたし</rt></ruby>の<ruby>友<rt>とも</rt></ruby>だち ___。 (Dia adalah teman saya.)",
                correct: ["desu", "です"],
                hint: "Kopula penutup kalimat sopan untuk kata benda adalah です."
            },
            {
                id: "q_1_3",
                type: "mcq",
                node_id: "grammar_no",
                grammar_focus: "の (no) — Partikel Kepemilikan",
                question: "Pilihlah partikel yang tepat: <ruby>私<rt>わたし</rt></ruby> ___ <ruby>名前<rt>なまえ</rt></ruby>はクリスです。 (Nama saya adalah Chris.)",
                options: ["は (wa)", "の (no)", "が (ga)", "を (wo)"],
                correctIndex: 1,
                hint: "Partikel の menghubungkan dua kata benda dan menyatakan kepemilikan (nama milik saya)."
            },
            {
                id: "q_1_4",
                type: "fill",
                node_id: "grammar_mo",
                grammar_focus: "も (mo) — Juga / Pula",
                question: "Lengkapi kalimat: <ruby>私<rt>わたし</rt></ruby> ___ インドネシア<ruby>人<rt>じん</rt></ruby>です。 (Saya juga orang Indonesia.)",
                correct: ["mo", "も"],
                hint: "Ganti partikel は dengan も untuk menyatakan 'juga' atau 'pula'."
            },
            {
                id: "q_1_5",
                type: "mcq",
                node_id: "grammar_ka",
                grammar_focus: "か (ka) — Partikel Tanya",
                question: "Partikel apa yang digunakan untuk membuat kalimat tanya? あれはなん ___ 。 (Apakah itu?)",
                options: ["ね (ne)", "よ (yo)", "か (ka)", "な (na)"],
                correctIndex: 2,
                hint: "Partikel か di akhir kalimat mengubah pernyataan menjadi pertanyaan."
            },
            {
                id: "q_1_6",
                type: "mcq",
                node_id: "grammar_dewa_nai",
                grammar_focus: "じゃない・ではない (dewa nai) — Negatif To Be",
                question: "Pilihlah bentuk negatif sopan yang tepat: <ruby>私<rt>わたし</rt></ruby>は<ruby>先生<rt>せんせい</rt></ruby> ___。 (Saya bukan guru.)",
                options: ["ではありません (dewa arimasen)", "じゃないでした (janai deshita)", "ですない (desu nai)", "ではあります (dewa arimasu)"],
                correctIndex: 0,
                hint: "Bentuk negatif formal dari です adalah ではありません (dewa arimasen)."
            },
            {
                id: "q_1_7",
                type: "mcq",
                node_id: "grammar_kore_sore_are",
                grammar_focus: "これ・それ・あれ (Ko-So-A-Do) — Kata Penunjuk Benda",
                question: "Pilihlah kata penunjuk yang tepat untuk benda dekat pembicara: ___ は<ruby>私<rt>わたし</rt></ruby>の<ruby>本<rt>ほん</rt></ruby>です。 (Ini adalah buku saya.)",
                options: ["それ (sore)", "あれ (are)", "これ (kore)", "どれ (dore)"],
                correctIndex: 2,
                hint: "Ko-so-a-do: これ untuk benda dekat pembicara, それ dekat pendengar, あれ jauh dari keduanya."
            },
            {
                id: "q_1_8",
                type: "fill",
                node_id: "grammar_dare",
                grammar_focus: "誰 (dare) — Kata Tanya 'Siapa'",
                question: "Lengkapi kalimat tanya: あそこにいる<ruby>人<rt>ひと</rt></ruby>は ___ ですか。 (Siapa orang yang ada di sana?)",
                correct: ["dare", "だれ", "donata", "どなた"],
                hint: "だれ adalah kata tanya 'siapa'. Bentuk sopannya adalah どなた (donata)."
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
                hint: "Nama saya = watashi no namae, adalah = wa ... desu, Chris = kurisu."
            },
            {
                id: "q_1_10",
                type: "fill",
                node_id: "grammar_hai_iie",
                grammar_focus: "はい・いいえ (hai/iie) — Ya / Tidak",
                question: "Lengkapi percakapan: A: <ruby>田中<rt>たなか</rt></ruby>さんは<ruby>学生<rt>がくせい</rt></ruby>ですか？ B: ___、<ruby>学生<rt>がくせい</rt></ruby>です。 (Ya, saya pelajar.)",
                correct: ["hai", "はい"],
                hint: "はい adalah kata 'Ya' dalam bahasa Jepang. Lawan katanya adalah いいえ (iie = Tidak)."
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
                question: "Pilihlah kalimat yang tepat untuk menyatakan 'Ada buku di sini':",
                options: ["<ruby>本<rt>ほん</rt></ruby>がいます (hon ga imasu)", "<ruby>本<rt>ほん</rt></ruby>があります (hon ga arimasu)", "<ruby>本<rt>ほん</rt></ruby>をあります (hon o arimasu)", "<ruby>本<rt>ほん</rt></ruby>にあります (hon ni arimasu)"],
                correctIndex: 1,
                hint: "Buku adalah benda mati → gunakan があります. Untuk makhluk hidup gunakan がいます."
            },
            {
                id: "q_2_2",
                type: "fill",
                node_id: "grammar_ga_imasu",
                grammar_focus: "がいます (ga imasu) — Ada (Makhluk Hidup)",
                question: "Lengkapi kalimat: あそこに<ruby>猫<rt>ねこ</rt></ruby>が ___。 (Ada kucing di sana.)",
                correct: ["imasu", "います"],
                hint: "Kucing adalah makhluk hidup → gunakan います (imasu), bukan あります."
            },
            {
                id: "q_2_3",
                type: "mcq",
                node_id: "grammar_ni_location",
                grammar_focus: "に (ni) — Partikel Lokasi Keberadaan",
                question: "Lengkapi kalimat: <ruby>机<rt>つくえ</rt></ruby>の<ruby>上<rt>うえ</rt></ruby> ___ <ruby>本<rt>ほん</rt></ruby>があります。 (Di atas meja ada buku.)",
                options: ["で (de)", "を (wo)", "に (ni)", "が (ga)"],
                correctIndex: 2,
                hint: "Partikel に menandai lokasi keberadaan benda (dengan あります/います)."
            },
            {
                id: "q_2_4",
                type: "fill",
                node_id: "grammar_doko",
                grammar_focus: "どこ (doko) — Kata Tanya 'Di mana'",
                question: "Lengkapi kalimat tanya: トイレは ___ ですか。 (Toiletnya di mana?)",
                correct: ["doko", "どこ"],
                hint: "どこ adalah kata tanya untuk menanyakan tempat ('di mana')."
            },
            {
                id: "q_2_5",
                type: "mcq",
                node_id: "grammar_kono_sono_ano",
                grammar_focus: "この・その・あの — Kata Penunjuk + Kata Benda",
                question: "Lengkapi kalimat: ___ <ruby>本<rt>ほん</rt></ruby>は<ruby>私<rt>わたし</rt></ruby>のです。 (Buku ini adalah milik saya.)",
                options: ["これ (kore)", "この (kono)", "あそこ (asoko)", "それ (sore)"],
                correctIndex: 1,
                hint: "この/その/あの harus diikuti langsung oleh kata benda. これ/それ/あれ berdiri sendiri."
            },
            {
                id: "q_2_6",
                type: "mcq",
                node_id: "grammar_ni_e_destination",
                grammar_focus: "へ (e) — Partikel Arah/Tujuan",
                question: "Lengkapi kalimat: <ruby>日本<rt>にほん</rt></ruby> ___ <ruby>行<rt>い</rt></ruby>きます。 (Pergi ke Jepang.)",
                options: ["で (de)", "を (wo)", "へ (e)", "が (ga)"],
                correctIndex: 2,
                hint: "Partikel へ (dibaca 'e') menunjukkan arah atau tujuan perjalanan."
            },
            {
                id: "q_2_7",
                type: "mcq",
                node_id: "grammar_de_place",
                grammar_focus: "で (de) — Partikel Tempat Aktivitas",
                question: "Lengkapi kalimat: レストラン ___ ごはんを<ruby>食<rt>た</rt></ruby>べます。 (Makan di restoran.)",
                options: ["に (ni)", "で (de)", "を (wo)", "へ (e)"],
                correctIndex: 1,
                hint: "で menandai tempat aktivitas/tindakan berlangsung. に menandai keberadaan/tujuan."
            },
            {
                id: "q_2_8",
                type: "fill",
                node_id: "grammar_to",
                grammar_focus: "と (to) — Partikel Penghubung 'Dan'",
                question: "Lengkapi kalimat: ペン ___ えんぴつがあります。 (Ada pena dan pensil.)",
                correct: ["to", "と"],
                hint: "Partikel と menghubungkan kata benda secara lengkap (A dan B dan C). Berbeda dengan や yang berarti 'antara lain'."
            },
            {
                id: "q_2_9",
                type: "fill",
                node_id: "grammar_nani",
                grammar_focus: "何 (nani/nan) — Kata Tanya 'Apa'",
                question: "Lengkapi kalimat tanya: それは ___ ですか。 (Apakah itu?)",
                correct: ["nan", "nani", "なん", "なに"],
                hint: "何 dibaca 'nani', tapi berubah menjadi 'nan' saat diikuti langsung oleh です atau で."
            },
            {
                id: "q_2_10",
                type: "translate",
                node_id: "grammar_ga_arimasu",
                grammar_focus: "があります/がいます — Struktur Keberadaan",
                question: "Terjemahkan ke bahasa Jepang: 'Di atas meja ada kucing.' (Tulis dalam Romaji)",
                acceptedAnswers: [
                    "tsukue no ue ni neko ga imasu",
                    "tsukue no ue ni neko ga imasu.",
                    "tsukue no ue niwa neko ga imasu"
                ],
                hint: "meja = tsukue, atas = ue, di = ni, kucing = neko, ada (makhluk hidup) = imasu."
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
                hint: "Angka 3 = さん (san) + akhiran jam = じ (ji) → さんじ. じかん berarti 'durasi jam'."
            },
            {
                id: "q_3_2",
                type: "fill",
                node_id: "grammar_fun_pun",
                grammar_focus: "分 (fun/pun) — Akhiran Menit",
                question: "Lengkapi: いまは<ruby>二時<rt>にじ</rt></ruby>じゅっ ___ です。 (Sekarang jam 2 lewat 10 menit.)",
                correct: ["pun", "ぷん", "fun", "ふん"],
                hint: "Akhiran menit adalah ふん (fun), tapi setelah angka seperti じゅっ (10) pelafalan berubah menjadi ぷん (pun)."
            },
            {
                id: "q_3_3",
                type: "mcq",
                node_id: "grammar_kara_made",
                grammar_focus: "から〜まで (kara~made) — Dari ~ Sampai",
                question: "Lengkapi kalimat: <ruby>一時<rt>いちじ</rt></ruby> ___ <ruby>八時<rt>はちじ</rt></ruby> ___ しごとです。 (Kerja dari jam 1 sampai jam 8.)",
                options: ["kara ... made", "de ... ni", "to ... made", "kara ... ni"],
                correctIndex: 0,
                hint: "Pola から〜まで untuk menyatakan rentang: dari (kara) ~ sampai (made)."
            },
            {
                id: "q_3_4",
                type: "fill",
                node_id: "grammar_han",
                grammar_focus: "半 (han) — Setengah Jam",
                question: "Lengkapi kalimat: いまは<ruby>七時<rt>しちじ</rt></ruby> ___ です。 (Sekarang jam setengah delapan / jam 7 lebih 30 menit.)",
                correct: ["han", "はん", "半"],
                hint: "半 (はん) berarti 'setengah'. しちじはん = jam 7 setengah."
            },
            {
                id: "q_3_5",
                type: "mcq",
                node_id: "grammar_mai",
                grammar_focus: "枚 (mai) — Penghitung Benda Tipis/Flat",
                question: "Lengkapi kalimat: シャツを<ruby>二<rt>に</rt></ruby> ___ <ruby>買<rt>か</rt></ruby>いました。 (Saya membeli dua helai kemeja.)",
                options: ["本 (hon)", "冊 (satsu)", "枚 (mai)", "個 (ko)"],
                correctIndex: 2,
                hint: "枚 (mai) untuk benda tipis/datar: baju, kertas, piring. 本 untuk benda panjang, 冊 untuk buku."
            },
            {
                id: "q_3_6",
                type: "fill",
                node_id: "grammar_hitori_futari",
                grammar_focus: "一人・二人 — Counter Orang Khusus",
                question: "<ruby>教室<rt>きょうしつ</rt></ruby>に<ruby>学生<rt>がくせい</rt></ruby>が ___ います。 (Ada dua orang siswa di kelas.)",
                correct: ["futari", "ふたり", "二人"],
                hint: "Hitungan orang bersifat khusus: ひとり (1 orang), ふたり (2 orang). Angka 3+ menggunakan ~にん."
            },
            {
                id: "q_3_7",
                type: "mcq",
                node_id: "grammar_goro",
                grammar_focus: "ごろ (goro) — Perkiraan Waktu",
                question: "<ruby>三時<rt>さんじ</rt></ruby> ___ に<ruby>行<rt>い</rt></ruby>きます。 (Pergi sekitar jam 3.)",
                options: ["ごろ (goro)", "ぐらい (gurai)", "だけ (dake)", "まで (made)"],
                correctIndex: 0,
                hint: "ごろ untuk perkiraan titik waktu (jam/tanggal). ぐらい untuk perkiraan durasi atau jumlah."
            },
            {
                id: "q_3_8",
                type: "mcq",
                node_id: "grammar_ikutsu_ikura",
                grammar_focus: "いくら (ikura) — Menanyakan Harga",
                question: "このりんごは ___ ですか。 (Berapa harga apel ini?)",
                options: ["いくつ (ikutsu)", "いくら (ikura)", "どんな (donna)", "だれ (dare)"],
                correctIndex: 1,
                hint: "いくら untuk menanyakan harga. いくつ untuk menanyakan jumlah benda."
            },
            {
                id: "q_3_9",
                type: "fill",
                node_id: "grammar_itsu",
                grammar_focus: "いつ (itsu) — Kata Tanya 'Kapan'",
                question: "<ruby>日本<rt>にほん</rt></ruby>へ ___ <ruby>行<rt>い</rt></ruby>きますか。 (Kapan kamu pergi ke Jepang?)",
                correct: ["itsu", "いつ"],
                hint: "いつ adalah kata tanya waktu yang berarti 'kapan'."
            },
            {
                id: "q_3_10",
                type: "translate",
                node_id: "grammar_kara_made",
                grammar_focus: "から〜まで — Terjemahan Waktu",
                question: "Terjemahkan ke bahasa Jepang: 'Toko buka dari jam 9 sampai jam 6.' (toko = mise, buka = aku)",
                acceptedAnswers: [
                    "mise wa ku-ji kara roku-ji made desu",
                    "mise wa kuji kara rokuji made desu",
                    "mise wa ku-ji kara roku-ji made akimasu",
                    "mise wa kuji kara rokuji made akimasu"
                ],
                hint: "toko = みせ, jam 9 = くじ, dari = から, jam 6 = ろくじ, sampai = まで."
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
                question: "Manakah di bawah ini yang merupakan い-adjektif (i-adjective) asli?",
                options: ["きれい (kirei)", "しずか (shizuka)", "たかい (takai)", "げんき (genki)"],
                correctIndex: 2,
                hint: "たかい berakhiran い dan bisa langsung dikonjugasi (たかくない, たかかった). きれい dan げんき adalah な-adjektif meski terlihat berakhiran い."
            },
            {
                id: "q_4_2",
                type: "mcq",
                node_id: "grammar_na_adj",
                grammar_focus: "な-adjectives — Kata Sifat-na",
                question: "Pilihlah kalimat yang benar untuk menyatakan 'kota yang tenang':",
                options: ["しずか<ruby>町<rt>まち</rt></ruby> (shizuka machi)", "しずかい<ruby>町<rt>まち</rt></ruby> (shizukai machi)", "しずかな<ruby>町<rt>まち</rt></ruby> (shizukana machi)", "しずかの<ruby>町<rt>まち</rt></ruby> (shizuka no machi)"],
                correctIndex: 2,
                hint: "な-adjektif memerlukan partikel な saat memodifikasi kata benda secara langsung."
            },
            {
                id: "q_4_3",
                type: "mcq",
                node_id: "grammar_i_adj_neg",
                grammar_focus: "い-adjective Negatif: -kunai",
                question: "Bentuk negatif dari 'あつい' (panas) yang tepat adalah:",
                options: ["あついじゃない (atsui janai)", "あつくない (atsuku nai)", "あつない (atsunai)", "あつじゃない (atsu janai)"],
                correctIndex: 1,
                hint: "Ubah akhiran い → くない. あつい → あつくない. Pola ini berlaku untuk semua い-adjektif kecuali いい."
            },
            {
                id: "q_4_4",
                type: "fill",
                node_id: "grammar_totemo",
                grammar_focus: "とても (totemo) — Sangat",
                question: "Lengkapi kalimat: このラーメンは ___ おいしいです。 (Ramen ini sangat enak.)",
                correct: ["totemo", "とても"],
                hint: "とても adalah kata keterangan penguat yang berarti 'sangat'. Letakkan sebelum kata sifat."
            },
            {
                id: "q_4_5",
                type: "mcq",
                node_id: "grammar_amari_neg",
                grammar_focus: "あまり〜ない (amari~nai) — Tidak Terlalu",
                question: "Lengkapi kalimat: この<ruby>肉<rt>にく</rt></ruby>はあまり ___。 (Daging ini tidak begitu enak.)",
                options: ["おいしいです (oishii desu)", "おいしくないです (oishikunai desu)", "おいしいじゃない (oishii janai)", "おいしかったです (oishikatta desu)"],
                correctIndex: 1,
                hint: "あまり wajib berpasangan dengan bentuk negatif (〜ない). Tidak boleh diikuti bentuk positif."
            },
            {
                id: "q_4_6",
                type: "fill",
                node_id: "grammar_donna",
                grammar_focus: "どんな (donna) — Kata Tanya Karakteristik",
                question: "Lengkapi kalimat tanya: ___ <ruby>人<rt>ひと</rt></ruby>が好きですか。 (Kamu menyukai orang yang seperti apa?)",
                correct: ["donna", "どんな"],
                hint: "どんな berarti 'seperti apa / yang bagaimana'. Harus diikuti langsung oleh kata benda."
            },
            {
                id: "q_4_7",
                type: "mcq",
                node_id: "grammar_na_adj_noun",
                grammar_focus: "な-adjective + Kata Benda",
                question: "Pilihlah bentuk deskripsi yang tepat untuk 'bunga yang cantik' (hana = bunga):",
                options: ["きれいな<ruby>花<rt>はな</rt></ruby> (kireina hana)", "きれいい<ruby>花<rt>はな</rt></ruby> (kireii hana)", "きれい<ruby>花<rt>はな</rt></ruby> (kirei hana)", "きれいの<ruby>花<rt>はな</rt></ruby> (kirei no hana)"],
                correctIndex: 0,
                hint: "きれい adalah な-adjektif (pengecualian meski berakhiran い), sehingga harus menggunakan きれいな saat memodifikasi kata benda."
            },
            {
                id: "q_4_8",
                type: "mcq",
                node_id: "grammar_ii_yoku",
                grammar_focus: "いい/よい (ii/yoi) — Bagus (Bentuk Irregular)",
                question: "Bentuk negatif dari kata sifat 'いい' (bagus) adalah:",
                options: ["いいくない (iikunai)", "よくない (yoku nai)", "いくない (ikunai)", "いいじゃない (ii janai)"],
                correctIndex: 1,
                hint: "いい berasal dari よい, sehingga konjugasinya mengikuti よい: よくない (negatif), よかった (lampau)."
            },
            {
                id: "q_4_9",
                type: "fill",
                node_id: "grammar_ga_but",
                grammar_focus: "が (ga) — Tetapi / Namun (Konjungsi)",
                question: "Lengkapi kalimat: このカメラは<ruby>高<rt>たか</rt></ruby>いです ___、とてもいいです。 (Kamera ini mahal, tetapi sangat bagus.)",
                correct: ["ga", "が"],
                hint: "が di tengah kalimat (setelah ます/です) berfungsi sebagai kata hubung yang berarti 'tetapi'."
            },
            {
                id: "q_4_10",
                type: "translate",
                node_id: "grammar_i_adj",
                grammar_focus: "い-adjective — Terjemahan Deskripsi",
                question: "Terjemahkan ke bahasa Jepang: 'Hari ini sangat panas.' (hari ini = kyou, panas = atsui)",
                acceptedAnswers: [
                    "kyou wa totemo atsui desu",
                    "kyou wa totemo atsui desu.",
                    "kyou wa totemo atsui"
                ],
                hint: "hari ini = きょう, sangat = とても, panas = あつい, diakhiri dengan です."
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
                grammar_focus: "を (wo) — Partikel Objek",
                question: "Lengkapi kalimat: <ruby>毎日<rt>まいにち</rt></ruby>、コーヒー ___ <ruby>飲<rt>の</rt></ruby>んでいます。 (Setiap hari, saya minum kopi.)",
                options: ["が (ga)", "を (wo)", "に (ni)", "で (de)"],
                correctIndex: 1,
                hint: "を menandai objek langsung dari kata kerja. Kopi adalah objek yang 'diminum'."
            },
            {
                id: "q_5_2",
                type: "fill",
                node_id: "grammar_shimasu",
                grammar_focus: "します (shimasu) — Melakukan",
                question: "Lengkapi kalimat: <ruby>毎週土曜日<rt>まいしゅうどようび</rt></ruby>にサッカーを ___。 (Setiap hari Sabtu, saya bermain sepak bola.)",
                correct: ["shimasu", "します"],
                hint: "します (shimasu) digunakan untuk olahraga dan hobi: サッカーをします = bermain sepak bola."
            },
            {
                id: "q_5_3",
                type: "mcq",
                node_id: "grammar_ni_iku",
                grammar_focus: "に行く (ni iku) — Pergi Untuk Melakukan",
                question: "Pilihlah bentuk yang tepat untuk menyatakan 'Pergi ke restoran untuk makan':",
                options: ["<ruby>食<rt>た</rt></ruby>べに<ruby>行<rt>い</rt></ruby>きます (tabe ni ikimasu)", "<ruby>食<rt>た</rt></ruby>べて<ruby>行<rt>い</rt></ruby>きます (tabete ikimasu)", "<ruby>食<rt>た</rt></ruby>べるに<ruby>行<rt>い</rt></ruby>きます (taberu ni ikimasu)", "<ruby>食<rt>た</rt></ruby>べます<ruby>行<rt>い</rt></ruby>きます (tabemasu ikimasu)"],
                correctIndex: 0,
                hint: "Pola tujuan: kata kerja bentuk masu-stem (tabe) + に + ikimasu. Bukan bentuk kamus atau te-form."
            },
            {
                id: "q_5_4",
                type: "fill",
                node_id: "grammar_issho_ni",
                grammar_focus: "一緒に (issho ni) — Bersama-sama",
                question: "Lengkapi ajakan: ___ <ruby>映画<rt>えいが</rt></ruby>を<ruby>見<rt>み</rt></ruby>ませんか。 (Maukah menonton film bersama?)",
                correct: ["issho ni", "いっしょに"],
                hint: "いっしょに berarti 'bersama-sama'. Letakkan sebelum kata kerja untuk menyatakan aktivitas bersama."
            },
            {
                id: "q_5_5",
                type: "mcq",
                node_id: "grammar_masen_ka",
                grammar_focus: "〜ませんか (masen ka) — Ajakan Sopan",
                question: "Manakah bentuk ajakan sopan yang paling tepat untuk 'Maukah minum kopi bersama?'",
                options: ["コーヒーを<ruby>飲<rt>の</rt></ruby>みましょう (koohii o nomimashou)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みませんか (koohii o nomimasen ka)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みますか (koohii o nomimasu ka)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みたいですか (koohii o nomitai desu ka)"],
                correctIndex: 1,
                hint: "〜ませんか (masen ka) adalah ajakan sopan yang memberikan pilihan. 〜ましょう lebih kepada 'ayo kita lakukan'."
            },
            {
                id: "q_5_6",
                type: "fill",
                node_id: "grammar_mashou",
                grammar_focus: "〜ましょう (mashou) — Ayo Melakukan",
                question: "Lengkapi ajakan: <ruby>行<rt>い</rt></ruby>き___！ (Ayo pergi!)",
                correct: ["mashou", "ましょう"],
                hint: "〜ましょう digunakan untuk mengajak bersama ('ayo kita'). Bentuk: masu-stem + ましょう."
            },
            {
                id: "q_5_7",
                type: "mcq",
                node_id: "grammar_doushite",
                grammar_focus: "どうして (doushite) — Kenapa / Mengapa",
                question: "Lengkapi kalimat tanya: ___ <ruby>学校<rt>がっこう</rt></ruby>を<ruby>休<rt>やす</rt></ruby>みましたか。 (Kenapa kamu tidak masuk sekolah?)",
                options: ["だれ (dare)", "どうして (doushite)", "いつ (itsu)", "いくら (ikura)"],
                correctIndex: 1,
                hint: "どうして dan なぜ keduanya berarti 'mengapa/kenapa'. どうして lebih umum dalam percakapan sehari-hari."
            },
            {
                id: "q_5_8",
                type: "fill",
                node_id: "grammar_kara_reason",
                grammar_focus: "から (kara) — Karena (Alasan)",
                question: "Lengkapi kalimat: きょうは<ruby>雨<rt>あめ</rt></ruby>が<ruby>降<rt>ふ</rt></ruby>りました ___、<ruby>学校<rt>がっこう</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きませんでした。 (Karena hari ini hujan, saya tidak pergi ke sekolah.)",
                correct: ["kara", "から"],
                hint: "から setelah klausa pertama berarti 'karena'. Pola: [alasan] から、[akibat]."
            },
            {
                id: "q_5_9",
                type: "mcq",
                node_id: "grammar_frequency",
                grammar_focus: "Keterangan Frekuensi (Itsumo)",
                question: "Pilihlah kata keterangan frekuensi yang bermakna 'selalu / setiap saat':",
                options: ["ときどき (tokidoki)", "よく (yoku)", "いつも (itsumo)", "あまり (amari)"],
                correctIndex: 2,
                hint: "Urutan frekuensi: いつも (selalu) > よく (sering) > ときどき (kadang) > あまり+ない (jarang) > ぜんぜん+ない (tidak pernah)."
            },
            {
                id: "q_5_10",
                type: "translate",
                node_id: "grammar_o_particle",
                grammar_focus: "を (wo) — Terjemahan Aktivitas",
                question: "Terjemahkan ke bahasa Jepang: 'Setiap hari saya makan apel.' (setiap hari = mainichi, apel = ringo, makan = tabemasu)",
                acceptedAnswers: [
                    "mainichi ringo o tabemasu",
                    "mainichi ringo o tabemasu.",
                    "watashi wa mainichi ringo o tabemasu",
                    "mainichi ringo wo tabemasu"
                ],
                hint: "setiap hari = まいにち, apel = りんご, partikel objek = を, makan = たべます."
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
                options: ["<ruby>お茶<rt>おちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>みたいです (ocha o nomitai desu)", "<ruby>お茶<rt>おちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>みていです (ocha o nomitei desu)", "<ruby>お茶<rt>おちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>むたいです (ocha o nomutai desu)", "<ruby>お茶<rt>おちゃ</rt></ruby>が<ruby>飲<rt>の</rt></ruby>みます (ocha ga nomimasu)"],
                correctIndex: 0,
                hint: "Pola keinginan: masu-stem + たい。のむ → のみ + たい → のみたいです。"
            },
            {
                id: "q_6_2",
                type: "fill",
                node_id: "grammar_ga_hoshii",
                grammar_focus: "がほしい (ga hoshii) — Ingin (Benda)",
                question: "Lengkapi kalimat: <ruby>新<rt>あたら</rt></ruby>しい<ruby>車<rt>くるま</rt></ruby>が ___ です。 (Saya ingin mobil baru.)",
                correct: ["hoshii", "ほしい", "欲しい"],
                hint: "ほしい digunakan untuk keinginan terhadap benda (kata benda + が + ほしい). Berbeda dengan 〜たい yang untuk tindakan."
            },
            {
                id: "q_6_3",
                type: "mcq",
                node_id: "grammar_no_ga_suki",
                grammar_focus: "のが好き (no ga suki) — Suka Melakukan",
                question: "Lengkapi kalimat: <ruby>私<rt>わたし</rt></ruby>は<ruby>音楽<rt>おんがく</rt></ruby>を<ruby>聞<rt>き</rt></ruby>く ___ が好きです。 (Saya suka mendengarkan musik.)",
                options: ["こと (koto)", "の (no)", "もの (mono)", "と (to)"],
                correctIndex: 1,
                hint: "V-dictionary + の + が好き untuk menyatakan suka melakukan aktivitas. の membuat kata kerja menjadi kata benda."
            },
            {
                id: "q_6_4",
                type: "fill",
                node_id: "grammar_jouzu_heta",
                grammar_focus: "下手 (heta) — Tidak Pandai",
                question: "Lengkapi kalimat: <ruby>私<rt>わたし</rt></ruby>は<ruby>歌<rt>うた</rt></ruby>が ___ です。 (Saya tidak pandai bernyanyi.)",
                correct: ["heta", "へた", "下手"],
                hint: "Kemampuan: じょうず (jouzu = pandai) ↔ へた (heta = tidak pandai). Gunakan が untuk topik kemampuan."
            },
            {
                id: "q_6_5",
                type: "fill",
                node_id: "grammar_wakaru",
                grammar_focus: "わかる (wakaru) — Mengerti / Paham",
                question: "Lengkapi kalimat: <ruby>私<rt>わたし</rt></ruby>は<ruby>英語<rt>えいご</rt></ruby>がよく ___。 (Saya sangat paham bahasa Inggris.)",
                correct: ["wakarimasu", "わかります", "wakaru", "わかる"],
                hint: "わかる adalah kata kerja intransitif (tidak perlu partikel を). Gunakan が untuk hal yang dimengerti."
            },
            {
                id: "q_6_6",
                type: "mcq",
                node_id: "grammar_ichiban",
                grammar_focus: "一番 (ichiban) — Paling / Nomor Satu",
                question: "Lengkapi kalimat: くだものの<ruby>中<rt>なか</rt></ruby>で、りんごが ___ 好きです。 (Di antara buah-buahan, saya paling suka apel.)",
                options: ["もっと (motto)", "一番 (ichiban)", "ずっと (zutto)", "とても (totemo)"],
                correctIndex: 1,
                hint: "一番 (いちばん) untuk superlatif: 〜の中で + [benda] が一番 + [sifat]. もっと berarti 'lebih lagi'."
            },
            {
                id: "q_6_7",
                type: "fill",
                node_id: "grammar_yori",
                grammar_focus: "より (yori) — Daripada (Perbandingan)",
                question: "Lengkapi kalimat: <ruby>猫<rt>ねこ</rt></ruby>は<ruby>犬<rt>いぬ</rt></ruby> ___ <ruby>小<rt>ちい</rt></ruby>さいです。 (Kucing lebih kecil daripada anjing.)",
                correct: ["yori", "より"],
                hint: "より ditempel pada standar pembanding: [A]は[B]より[sifat]です = A lebih [sifat] daripada B."
            },
            {
                id: "q_6_8",
                type: "mcq",
                node_id: "grammar_hou_ga_ii",
                grammar_focus: "ほうがいい (hou ga ii) — Lebih Baik / Saran",
                question: "Lengkapi kalimat saran: <ruby>風邪<rt>かぜ</rt></ruby>ですね。早く ___ ほうがいいですよ。 (Kamu flu ya. Sebaiknya tidur cepat.)",
                options: ["<ruby>寝<rt>ね</rt></ruby>る (neru)", "<ruby>寝<rt>ね</rt></ruby>て (nete)", "<ruby>寝<rt>ね</rt></ruby>た (neta)", "<ruby>寝<rt>ね</rt></ruby>ない (nenai)"],
                correctIndex: 2,
                hint: "Saran positif: V-ta (bentuk lampau kasual) + ほうがいい。Saran negatif: V-nai + ほうがいい。"
            },
            {
                id: "q_6_9",
                type: "fill",
                node_id: "grammar_dou_desu_ka",
                grammar_focus: "はどうですか (wa dou desu ka) — Bagaimana Kalau",
                question: "Lengkapi penawaran: <ruby>温<rt>あたた</rt></ruby>かいお<ruby>茶<rt>おちゃ</rt></ruby>は ___ ですか。 (Bagaimana kalau minum teh hangat?)",
                correct: ["dou", "どう"],
                hint: "どうですか digunakan untuk menawarkan sesuatu atau menanyakan pendapat. どう = bagaimana."
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
                hint: "pergi = ikimasu → masu-stem = iki + たい → いきたいです。Tujuan lokasi menggunakan に atau へ."
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
                hint: "〜てください = V-te + kudasai. かく (ku→ite) → かいて。Kata kerja く berubah menjadi いて dalam te-form."
            },
            {
                id: "q_7_2",
                type: "fill",
                node_id: "grammar_te_mo_ii",
                grammar_focus: "てもいいです (temo ii desu) — Boleh / Izin",
                question: "Lengkapi pertanyaan izin: <ruby>写真<rt>しゃしん</rt></ruby>を<ruby>撮<rt>と</rt></ruby>っても ___ ですか。 (Bolehkah saya mengambil foto?)",
                correct: ["ii", "いい"],
                hint: "Pola izin: V-te + もいいですか。Jawaban positif: いいですよ。Jawaban negatif: ちょっと…."
            },
            {
                id: "q_7_3",
                type: "mcq",
                node_id: "grammar_te_wa_ikenai",
                grammar_focus: "てはいけない (te wa ikenai) — Larangan",
                question: "Lengkapi kalimat larangan: ここは<ruby>危<rt>あぶ</rt></ruby>ないから、<ruby>入<rt>はい</rt></ruby>って ___。 (Karena di sini berbahaya, kamu tidak boleh masuk.)",
                options: ["はいいです (wa ii desu)", "はいけません (wa ikemasen)", "はだめです (wa dame desu)", "はいいですか (wa ii desu ka)"],
                correctIndex: 1,
                hint: "Larangan sopan: V-te + はいけません (ikemasen). Versi kasual: V-te + はだめ (dame)."
            },
            {
                id: "q_7_4",
                type: "fill",
                node_id: "grammar_te_iru",
                grammar_focus: "ている (te iru) — Sedang Berlangsung",
                question: "Lengkapi kalimat: かれはいま、<ruby>日本語<rt>にほんご</rt></ruby>を<ruby>勉強<rt>べんきょう</rt></ruby>して ___。 (Dia sekarang sedang belajar bahasa Jepang.)",
                correct: ["imasu", "います", "iru", "いる"],
                hint: "Sedang berlangsung: V-te + います (imasu). います menunjukkan aksi yang masih berjalan saat ini."
            },
            {
                id: "q_7_5",
                type: "mcq",
                node_id: "grammar_te_iru_state",
                grammar_focus: "ている — Keadaan Menetap",
                question: "Pilihlah bentuk yang tepat untuk menyatakan status 'sudah menikah' (kondisi saat ini):",
                options: ["<ruby>結婚<rt>けっこん</rt></ruby>します (kekkon shimasu)", "<ruby>結婚<rt>けっこん</rt></ruby>しています (kekkon shite imasu)", "<ruby>結婚<rt>けっこん</rt></ruby>しました (kekkon shimashita)", "<ruby>結婚<rt>けっこん</rt></ruby>してありました (kekkon shite arimashita)"],
                correctIndex: 1,
                hint: "V-te います juga digunakan untuk status/kondisi yang bertahan: しています = sedang/sudah dalam kondisi tersebut."
            },
            {
                id: "q_7_6",
                type: "fill",
                node_id: "grammar_te_kara",
                grammar_focus: "てから (te kara) — Setelah Melakukan",
                question: "Lengkapi kalimat: <ruby>手<rt>て</rt></ruby>を<ruby>洗<rt>あら</rt></ruby>ってから、ごはんを<ruby>食<rt>た</rt></ruby>べ ___。 (Setelah mencuci tangan, baru saya makan nasi.)",
                correct: ["masu", "ます"],
                hint: "〜てから：[A-te] + kara、[B]。Klausa A terjadi lebih dulu, baru klausa B."
            },
            {
                id: "q_7_7",
                type: "mcq",
                node_id: "grammar_te_ageru_morau_kureru",
                grammar_focus: "てあげる・てもらう・てくれる — Jasa/Bantuan",
                question: "Pilihlah kalimat yang tepat untuk menyatakan 'Teman saya membacakan buku untukku':",
                options: ["<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んであげました", "<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んでくれました", "<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んでもらいました", "<ruby>友<rt>とも</rt></ruby>だちは<ruby>私<rt>わたし</rt></ruby>に<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>んでいきました"],
                correctIndex: 1,
                hint: "くれる: orang lain berbuat untuk pembicara. あげる: pembicara berbuat untuk orang lain. もらう: pembicara menerima tindakan dari orang lain."
            },
            {
                id: "q_7_8",
                type: "fill",
                node_id: "grammar_tari_tari",
                grammar_focus: "たり〜たり (tari~tari) — Daftar Aktivitas Acak",
                question: "Lengkapi kalimat: やすみの<ruby>日<rt>ひ</rt></ruby>は<ruby>本<rt>ほん</rt></ruby>を<ruby>読<rt>よ</rt></ruby>ん ___ 、おんがくを<ruby>聞<rt>き</rt></ruby>いたりします。 (Pada hari libur, saya membaca buku, mendengar musik, dan lain-lain.)",
                correct: ["dari", "だり"],
                hint: "〜たり〜たりする: ubah ke bentuk ta (lampau kasual) lalu tambahkan り。よんだ → よんだり。のんで → のんだ → のんだり。"
            },
            {
                id: "q_7_9",
                type: "fill",
                node_id: "grammar_te_miru",
                grammar_focus: "てみる (te miru) — Mencoba Melakukan",
                question: "Lengkapi kalimat: おいしそうですね。たべて ___ ます。 (Kelihatannya enak. Saya akan mencoba memakannya.)",
                correct: ["mi", "み"],
                hint: "V-te + みる (miru) = mencoba melakukan. たべて + みます = たべてみます (mencoba makan)."
            },
            {
                id: "q_7_10",
                type: "translate",
                node_id: "grammar_te_kudasai",
                grammar_focus: "てください — Terjemahan Permintaan",
                question: "Terjemahkan ke bahasa Jepang: 'Tolong tunggu sebentar.' (tunggu = machimasu → te-form: matte)",
                acceptedAnswers: [
                    "chotto matte kudasai",
                    "chotto matte kudasai.",
                    "sukoshi matte kudasai"
                ],
                hint: "sebentar = ちょっと (chotto), tunggu = まちます → て-form = まって, tolong = ください."
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
                hint: "Pengalaman: V-ta (bentuk lampau kasual) + ことがあります。いく → いった → いったことがあります。"
            },
            {
                id: "q_8_2",
                type: "fill",
                node_id: "grammar_mae_ni",
                grammar_focus: "前に (mae ni) — Sebelum Melakukan",
                question: "<ruby>寝<rt>ね</rt></ruby>る ___ スマホを<ruby>見<rt>み</rt></ruby>てはダメですよ。 (Jangan melihat HP sebelum tidur.)",
                correct: ["mae ni", "まえに", "前に"],
                hint: "V-dictionary (neru) + まえに = sebelum melakukan. Berbeda dengan 〜てから yang berarti 'setelah'."
            },
            {
                id: "q_8_3",
                type: "mcq",
                node_id: "grammar_nagara",
                grammar_focus: "ながら (nagara) — Sambil Melakukan",
                question: "<ruby>音楽<rt>おんがく</rt></ruby>を ___ ごはんを<ruby>食<rt>た</rt></ruby>べます。 (Makan sambil mendengarkan musik.)",
                options: ["<ruby>聞<rt>き</rt></ruby>くながら (kiku nagara)", "<ruby>聞<rt>き</rt></ruby>いてながら (kiite nagara)", "<ruby>聞<rt>き</rt></ruby>きながら (kiki nagara)", "<ruby>聞<rt>き</rt></ruby>かながら (kika nagara)"],
                correctIndex: 2,
                hint: "〜ながら: masu-stem + ながら。きく → きき + ながら → ききながら。Bukan te-form, bukan bentuk kamus."
            },
            {
                id: "q_8_4",
                type: "mcq",
                node_id: "grammar_mou_mada",
                grammar_focus: "まだ (mada) — Belum",
                question: "A: もうごはんを<ruby>食<rt>た</rt></ruby>べましたか？ B: いいえ、___ <ruby>食<rt>た</rt></ruby>べていません。 (Belum makan.)",
                options: ["もう (mou)", "まだ (mada)", "いつも (itsumo)", "とても (totemo)"],
                correctIndex: 1,
                hint: "まだ〜ていません = belum. もう〜ました = sudah. Keduanya berpasangan dengan bentuk yang berbeda."
            },
            {
                id: "q_8_5",
                type: "fill",
                node_id: "grammar_naru",
                grammar_focus: "なる (naru) — Menjadi",
                question: "<ruby>暖<rt>あたた</rt></ruby>かく ___ ましたね。 (Sudah menjadi hangat ya.)",
                correct: ["nari", "なり"],
                hint: "なる dalam bentuk sopan = なります。Dengan い-adjektif: あたたかい → あたたかく + なります。"
            },
            {
                id: "q_8_6",
                type: "mcq",
                node_id: "grammar_ndesu",
                grammar_focus: "んです (ndesu) — Penjelasan / Penekanan",
                question: "Manakah bentuk yang paling tepat untuk menjelaskan alasan keterlambatan secara sopan?",
                options: ["<ruby>電車<rt>でんしゃ</rt></ruby>が<ruby>遅<rt>おく</rt></ruby>れました (densha ga okuremashita)", "<ruby>電車<rt>でんしゃ</rt></ruby>が<ruby>遅<rt>おく</rt></ruby>れたんです (densha ga okureta n desu)", "<ruby>電車<rt>でんしゃ</rt></ruby>が<ruby>遅<rt>おく</rt></ruby>れるんです (densha ga okuru n desu)", "<ruby>電車<rt>でんしゃ</rt></ruby>が<ruby>遅<rt>おく</rt></ruby>れてんです (densha ga okurete n desu)"],
                correctIndex: 1,
                hint: "〜んです (ndesu): V-ta + んです untuk menjelaskan alasan tentang kejadian yang sudah terjadi."
            },
            {
                id: "q_8_7",
                type: "fill",
                node_id: "grammar_toki",
                grammar_focus: "とき (toki) — Ketika / Saat",
                question: "<ruby>子供<rt>こども</rt></ruby>の ___ 、あまいものが好きでした。 (Ketika masih anak-anak, saya suka makanan manis.)",
                correct: ["toki", "とき", "時"],
                hint: "Kata benda + の + とき = ketika [masa itu]. Untuk kata kerja: V-dictionary/V-ta + とき."
            },
            {
                id: "q_8_8",
                type: "mcq",
                node_id: "grammar_sugiru",
                grammar_focus: "すぎる (sugiru) — Terlalu / Berlebihan",
                question: "きのうはおさけを ___ すぎました。 (Kemarin saya terlalu banyak minum alkohol.)",
                options: ["<ruby>飲<rt>の</rt></ruby>む (nomu)", "<ruby>飲<rt>の</rt></ruby>み (nomi)", "<ruby>飲<rt>の</rt></ruby>んで (nonde)", "<ruby>飲<rt>の</rt></ruby>んだ (nonda)"],
                correctIndex: 1,
                hint: "〜すぎる: masu-stem + すぎる。のむ → のみ + すぎます → のみすぎます。"
            },
            {
                id: "q_8_9",
                type: "fill",
                node_id: "grammar_deshou",
                grammar_focus: "でしょう (deshou) — Sepertinya / Kemungkinan",
                question: "<ruby>明日<rt>あした</rt></ruby>は<ruby>雨<rt>あめ</rt></ruby>が<ruby>降<rt>ふ</rt></ruby>る ___。 (Sepertinya besok akan turun hujan.)",
                correct: ["deshou", "でしょう"],
                hint: "でしょう digunakan untuk memperkirakan/menduga sesuatu. V-dictionary + でしょう."
            },
            {
                id: "q_8_10",
                type: "translate",
                node_id: "grammar_ta_koto_ga_aru",
                grammar_focus: "たことがある — Terjemahan Pengalaman",
                question: "Terjemahkan ke bahasa Jepang: 'Apakah kamu pernah makan sushi?' (sushi = sushi, makan = tabemasu)",
                acceptedAnswers: [
                    "sushi o tabeta koto ga arimasu ka",
                    "sushi o tabeta koto ga arimasu ka.",
                    "sushi wo tabeta koto ga arimasu ka",
                    "watashi wa sushi o tabeta koto ga arimasu ka"
                ],
                hint: "makan = たべます → V-ta = たべた → たべたことがありますか。"
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
                grammar_focus: "なければならない (nakereba naranai) — Harus",
                question: "<ruby>時間<rt>じかん</rt></ruby>がありませんから、<ruby>早<rt>はや</rt></ruby>く ___。 (Karena tidak ada waktu, harus cepat bangun.)",
                options: ["<ruby>起<rt>お</rt></ruby>きなければなりません (okinakereba narimasen)", "<ruby>起<rt>お</rt></ruby>きてはいけません (okite wa ikemasen)", "<ruby>起<rt>お</rt></ruby>きてもいいです (okite mo ii desu)", "<ruby>起<rt>お</rt></ruby>きないでください (okinaide kudasai)"],
                correctIndex: 0,
                hint: "Keharusan: V-nai (tanpa い) + ければなりません。おきる → おきない → おきなければなりません。"
            },
            {
                id: "q_9_2",
                type: "fill",
                node_id: "grammar_naide_kudasai",
                grammar_focus: "ないでください (naide kudasai) — Tolong Jangan",
                question: "<ruby>写真<rt>しゃしん</rt></ruby>を<ruby>撮<rt>と</rt></ruby>ら ___ ください。 (Tolong jangan ambil foto.)",
                correct: ["naide", "ないで"],
                hint: "V-nai + でください = tolong jangan lakukan. とる → とらない → とらないでください。"
            },
            {
                id: "q_9_3",
                type: "mcq",
                node_id: "grammar_tsumori",
                grammar_focus: "つもり (tsumori) — Berencana / Berniat",
                question: "<ruby>来年<rt>らいねん</rt></ruby>、<ruby>日本<rt>にほん</rt></ruby>へ<ruby>行<rt>い</rt></ruby>く ___ です。 (Tahun depan, saya berencana pergi ke Jepang.)",
                options: ["つもり (tsumori)", "よてい (yotei)", "から (kara)", "こと (koto)"],
                correctIndex: 0,
                hint: "V-dictionary + つもりです: niat/rencana pribadi yang sudah diputuskan. よてい lebih formal/jadwal resmi."
            },
            {
                id: "q_9_4",
                type: "fill",
                node_id: "grammar_naku_temo_ii",
                grammar_focus: "なくてもいい (naku temo ii) — Tidak Harus",
                question: "<ruby>急<rt>いそが</rt></ruby>なくても ___ ですよ。 (Kamu tidak harus terburu-buru lho.)",
                correct: ["ii", "いい"],
                hint: "V-nakute + もいい = tidak harus / boleh tidak melakukan. Lawan dari なければならない."
            },
            {
                id: "q_9_5",
                type: "mcq",
                node_id: "grammar_koto_ga_dekiru",
                grammar_focus: "ことができる (koto ga dekiru) — Bisa / Mampu",
                question: "<ruby>私<rt>わたし</rt></ruby>は<ruby>日本語<rt>にほんご</rt></ruby>を<ruby>話<rt>はな</rt></ruby>すこと ___ できます。 (Saya bisa berbicara bahasa Jepang.)",
                options: ["を (wo)", "が (ga)", "に (ni)", "は (wa)"],
                correctIndex: 1,
                hint: "V-dictionary + ことが + できます。こと = nominalizer, が = partikel subjek dari できる."
            },
            {
                id: "q_9_6",
                type: "mcq",
                node_id: "grammar_cha_ikenai",
                grammar_focus: "ちゃいけない — Larangan Kasual (Spoken)",
                question: "Pilihlah bentuk kasual lisan yang tepat untuk 'Jangan minum kopi itu':",
                options: ["コーヒーを<ruby>飲<rt>の</rt></ruby>んじゃダメ (koohii o nonja dame)", "コーヒーを<ruby>飲<rt>の</rt></ruby>みちゃダメ (koohii o nomicha dame)", "コーヒーを<ruby>飲<rt>の</rt></ruby>んだダメ (koohii o nonda dame)", "コーヒーを<ruby>飲<rt>の</rt></ruby>むちゃダメ (koohii o nomucha dame)"],
                correctIndex: 0,
                hint: "のんではいけない → casual: のんで + は → のんじゃ + ダメ。て-form berakhir 'で' + は → 'じゃ'."
            },
            {
                id: "q_9_7",
                type: "mcq",
                node_id: "grammar_node",
                grammar_focus: "ので (node) — Karena (Objektif)",
                question: "ここは<ruby>危険<rt>きけん</rt></ruby>な ___、<ruby>入<rt>はい</rt></ruby>ってはいけませんよ。 (Karena tempat ini berbahaya, dilarang masuk.)",
                options: ["ので (node)", "から (kara)", "ため (tame)", "と (to)"],
                correctIndex: 0,
                hint: "な-adjektif + な + ので。から lebih subjektif/percakapan. ので lebih objektif/sopan."
            },
            {
                id: "q_9_8",
                type: "fill",
                node_id: "grammar_shikashi",
                grammar_focus: "しかし (shikashi) — Namun / Tetapi (Formal)",
                question: "<ruby>日本<rt>にほん</rt></ruby>の<ruby>生活<rt>せいかつ</rt></ruby>は<ruby>大変<rt>たいへん</rt></ruby>です。___、おもしろいです。 (Kehidupan di Jepang berat. Namun, menarik.)",
                correct: ["shikashi", "しかし"],
                hint: "しかし adalah kata hubung formal untuk 'namun/tetapi', digunakan di awal kalimat. Versi kasualnya: でも (demo)."
            },
            {
                id: "q_9_9",
                type: "mcq",
                node_id: "grammar_ne_yo",
                grammar_focus: "よ (yo) — Partikel Penegas Akhir",
                question: "A: このケーキはおいしいですか？ B: はい、とてもおいしいです ___！ (Ya, sangat enak lho!)",
                options: ["ね (ne)", "よ (yo)", "か (ka)", "な (na)"],
                correctIndex: 1,
                hint: "よ menyampaikan informasi baru atau meyakinkan. ね mencari persetujuan. Contoh: これはいいですよ (ini bagus lho!) vs いいですね (bagus ya, setuju)."
            },
            {
                id: "q_9_10",
                type: "translate",
                node_id: "grammar_nakereba_naranai",
                grammar_focus: "なければならない — Terjemahan Keharusan",
                question: "Terjemahkan ke bahasa Jepang: 'Besok saya harus bangun jam 6.' (besok = ashita, bangun = okiru)",
                acceptedAnswers: [
                    "ashita roku-ji ni okinakereba narimasen",
                    "watashi wa ashita roku-ji ni okinakereba narimasen",
                    "ashita rokuji ni okinakereba narimasen",
                    "watashi wa ashita rokuji ni okinakereba narimasen"
                ],
                hint: "besok = あした, jam 6 = ろくじに, harus bangun = おきなければなりません."
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