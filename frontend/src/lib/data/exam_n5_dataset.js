// src/lib/data/exam_n5_dataset.js
/**
 * Dataset Ujian Akhir (Exam Mode) JLPT N5
 * Berdasarkan: JLPT N5 Grammar Master by JLPTsensei.com (80 Grammar Lessons)
 *
 * Struktur: 3 Batch Ujian × 25 Soal = 75 Soal Total
 * Tingkat Kesulitan: TINGGI — tanpa petunjuk (no hints selama ujian)
 *
 * Perbedaan dari Quest Dataset:
 *   - TIDAK ADA field 'hint' (ujian tanpa bantuan)
 *   - Ada field 'explanation' (untuk review setelah ujian selesai)
 *   - Soal lebih kompleks: menggabungkan banyak poin grammar sekaligus
 *   - Termasuk soal deteksi kesalahan, pemahaman konteks, dan kanji
 *
 * Field per Batch:
 *   id, title, icon, description, time_limit_minutes, passing_score, questions
 *
 * Field per Soal:
 *   id, type, grammar_focus, question, [options/correct/acceptedAnswers], explanation
 */

export const examBatches = [

    // ══════════════════════════════════════════════════════════════════════
    // BATCH 1 — "Ujian Pertama" | Grammar Dasar & Menengah (Tier 1–2)
    // ══════════════════════════════════════════════════════════════════════
    {
        id: "exam_1",
        title: "Ujian Pertama",
        icon: "📝",
        description: "Grammar dasar hingga menengah: partikel, kata sifat, bentuk kata kerja, keberadaan, dan pola kalimat N5 Tier 1–2. Tanpa bantuan, tanpa petunjuk.",
        time_limit_minutes: 15,
        passing_score: 70,
        questions: [
            {
                id: "ex1_q1",
                type: "mcq",
                grammar_focus: "Partikel に vs で — Lokasi keberadaan vs tempat aktivitas",
                question: "「毎朝、田中さんは公園___ジョギングをしています。」\n\nPartikel yang tepat untuk kalimat di atas adalah?",
                options: [
                    "に (ni) — menunjukkan lokasi keberadaan (imasu/arimasu)",
                    "で (de) — menunjukkan tempat berlangsungnya aktivitas",
                    "へ (e) — menunjukkan arah pergerakan",
                    "を (o) — menunjukkan objek dari kata kerja"
                ],
                correctIndex: 1,
                explanation: "で digunakan untuk menandai TEMPAT terjadinya suatu AKTIVITAS (jogging). に digunakan untuk lokasi keberadaan (imasu/arimasu) atau tujuan perjalanan. Jogging adalah aktivitas yang TERJADI di taman → で."
            },
            {
                id: "ex1_q2",
                type: "mcq",
                grammar_focus: "い-adjective — Bentuk negatif kata sifat tidak beraturan",
                question: "Bentuk NEGATIF FORMAL yang BENAR dari「いい (ii — bagus)」adalah?",
                options: [
                    "いいじゃないです (ii janai desu)",
                    "よくないです (yoku nai desu)",
                    "いいくないです (ii kunai desu)",
                    "いないです (i nai desu)"
                ],
                correctIndex: 1,
                explanation: "いい (ii) adalah i-adjective TIDAK BERATURAN. Bentuk perubahannya menggunakan 'yoku', bukan 'iiku'. Sehingga: ii → yoku nai desu (tidak bagus). Sama halnya dengan bentuk lampau: いい → よかった (yokatta)."
            },
            {
                id: "ex1_q3",
                type: "mcq",
                grammar_focus: "な-adjective vs い-adjective — Penggunaan sebelum kata benda",
                question: "Manakah kata sifat yang TIDAK memerlukan 「な」sebelum kata benda?",
                options: [
                    "きれい (kirei — cantik) → きれいな + kata benda",
                    "やさしい (yasashii — baik hati) → やさしい + kata benda (langsung)",
                    "しずか (shizuka — tenang) → しずかな + kata benda",
                    "げんき (genki — ceria/sehat) → げんきな + kata benda"
                ],
                correctIndex: 1,
                explanation: "Hanya い-adjective yang langsung ditambahkan sebelum kata benda TANPA 'na'. やさしい adalah i-adjective sejati → やさしい人。きれい, しずか, dan げんき adalah na-adjective (pengecualian meski terlihat berakhiran -i) → きれいな人、しずかな人、げんきな人。"
            },
            {
                id: "ex1_q4",
                type: "mcq",
                grammar_focus: "があります vs がいます — Deteksi kesalahan penggunaan",
                question: "Manakah kalimat yang menggunakan あります/います secara SALAH?",
                options: [
                    "机の上に本があります。(Di atas meja ada buku.)",
                    "公園に子どもたちがいます。(Di taman ada anak-anak.)",
                    "水族館に魚がいます。(Di akuarium ada ikan.)",
                    "冷蔵庫に牛乳がいます。(Di kulkas ada susu.)"
                ],
                correctIndex: 3,
                explanation: "牛乳 (susu) adalah benda mati — harus menggunakan ARIMASU, bukan IMASU. Yang benar: 冷蔵庫に牛乳があります。IMASU hanya untuk makhluk hidup: manusia, hewan, serangga. 魚 (ikan) adalah makhluk hidup → がいます sudah benar."
            },
            {
                id: "ex1_q5",
                type: "mcq",
                grammar_focus: "こ・そ・あ・ど系 — Pemilihan kata penunjuk dalam konteks",
                question: "A dan B berdiri BERJAUHAN. A mengambil sebuah buku yang ada di dekat A dan berkata:\n「___本、面白そうですね。」\n\nKata penunjuk yang tepat dari sudut pandang A adalah?",
                options: [
                    "この (kono) — benda dekat PEMBICARA (A)",
                    "その (sono) — benda dekat PENDENGAR (B)",
                    "あの (ano) — benda jauh dari keduanya",
                    "どの (dono) — menanyakan benda"
                ],
                correctIndex: 0,
                explanation: "この digunakan untuk benda yang DEKAT dengan PEMBICARA (A). A memegang buku itu → この本。Jika B yang merujuk ke buku yang dipegang A, B akan menggunakan その本 (dekat pendengar/lawan bicara)."
            },
            {
                id: "ex1_q6",
                type: "fill",
                grammar_focus: "助数詞 (Counter) — Penghitung untuk buku/majalah",
                question: "「すみません、この雑誌を二___ください。」\n(Permisi, tolong berikan saya 2 majalah.)\n\nCounter yang tepat untuk majalah adalah:",
                correct: ["satsu", "さつ", "冊", "二冊", "にさつ"],
                explanation: "冊 (satsu) adalah counter untuk buku, majalah, dan buku catatan. Ni-satsu (二冊) = 2 majalah. Jangan tertukar: 枚 (mai) untuk benda tipis-flat (kertas/baju), 本 (hon/bon) untuk benda panjang (pensil/botol)."
            },
            {
                id: "ex1_q7",
                type: "mcq",
                grammar_focus: "て-form — Perubahan dari kata kerja berakhiran -ku (Kelompok 1)",
                question: "「書く (kaku — menulis)」→ Bentuk て-form yang BENAR adalah?",
                options: [
                    "かいて (kaite)",
                    "かくて (kakute)",
                    "かって (katte)",
                    "かんて (kante)"
                ],
                correctIndex: 0,
                explanation: "書く (kaku) termasuk Kata Kerja Kelompok 1 berakhiran -ku. Aturan te-form: -ku → -ite. Maka: kaku → kai+te = かいて (kaite). PENTING - Pengecualian: 行く (iku) → いって (itte), bukan いいて!"
            },
            {
                id: "ex1_q8",
                type: "mcq",
                grammar_focus: "ている — Makna keadaan menetap (bukan aksi berlangsung)",
                question: "「山田さんは眼鏡をかけています。」(Yamada-san wa megane o kakete imasu.)\n\nKalimat ini paling tepat diterjemahkan sebagai?",
                options: [
                    "Yamada-san sedang memasang kacamata (aksi berlangsung saat ini)",
                    "Yamada-san berkacamata / memakai kacamata (kondisi menetap)",
                    "Yamada-san ingin memakai kacamata",
                    "Yamada-san pernah memakai kacamata"
                ],
                correctIndex: 1,
                explanation: "かける (memasang) dengan ている menyatakan KEADAAN MENETAP sebagai hasil dari aksi: 'kondisi memakai kacamata sudah terjadi dan berlanjut' = berkacamata. Sama seperti: 結婚している (sudah menikah = status menikah menetap)."
            },
            {
                id: "ex1_q9",
                type: "mcq",
                grammar_focus: "から vs ので vs のに — Kata hubung kausal dan kontras",
                question: "Seorang murid ingin memberikan alasan secara FORMAL kepada guru mengapa ia terlambat. Kalimat yang paling tepat adalah?",
                options: [
                    "電車が遅れたから、遅刻しました。(kara — subjektif/kasual)",
                    "電車が遅れたので、遅刻しました。(node — objektif/formal)",
                    "電車が遅れたのに、遅刻しました。(noni — 'meskipun' → makna berlawanan dengan harapan)",
                    "電車が遅れたけど、遅刻しました。(kedo — 'tapi' → kontras)"
                ],
                correctIndex: 1,
                explanation: "ので (node) terdengar lebih OBJEKTIF dan SOPAN daripada kara, cocok untuk situasi formal (berbicara dengan guru). のに menyatakan kontras dengan harapan ('meskipun') sehingga menghasilkan makna aneh di sini. けど = 'tapi/namun'."
            },
            {
                id: "ex1_q10",
                type: "mcq",
                grammar_focus: "漢字 — KUN-yomi kanji alam (山・川・木・水)",
                question: "Pasangan kanji dan bacaan KUN-yomi (bacaan Jepang asli) mana yang SALAH?",
                options: [
                    "山 → yama (gunung) ✓",
                    "川 → kawa (sungai) ✓",
                    "木 → moku (pohon) ✗",
                    "水 → mizu (air) ✓"
                ],
                correctIndex: 2,
                explanation: "木 (pohon) memiliki KUN-yomi: き (ki), BUKAN 'moku'. Moku (もく) adalah ON-yomi (bacaan Cina). Contoh KUN: 木の葉 (ko-no-ha = daun pohon). Contoh ON: 木曜日 (Moku-you-bi = hari Kamis)."
            },
            {
                id: "ex1_q11",
                type: "fill",
                grammar_focus: "前に (mae ni) — Menyatakan 'sebelum' dalam urutan waktu",
                question: "「寝る___歯を磨いてください。」\n(Sebelum tidur, tolong gosok gigi.)\n\nKata yang tepat untuk melengkapi bagian kosong adalah:",
                correct: ["mae ni", "まえに", "前に"],
                explanation: "前に (mae ni) = 'SEBELUM melakukan sesuatu'. Pola: V-dictionary + 前に. Berbeda dengan てから (te kara) yang berarti 'SETELAH melakukan sesuatu'. 寝る前に = sebelum tidur."
            },
            {
                id: "ex1_q12",
                type: "mcq",
                grammar_focus: "が vs を — Partikel setelah 好き・嫌い・上手・下手",
                question: "Manakah kalimat yang SALAH secara gramatikal?\n(Temukan kesalahan penggunaan partikel!)",
                options: [
                    "私はピアノを弾くのが好きです。(Saya suka bermain piano.)",
                    "彼はスポーツを上手です。(Dia pandai olahraga.)",
                    "日本語が分かりますか。(Apakah kamu mengerti bahasa Jepang?)",
                    "音楽が聞こえます。(Terdengar suara musik.)"
                ],
                correctIndex: 1,
                explanation: "上手 (jouzu), 下手 (heta), 好き (suki), 嫌い (kirai), 分かる (wakaru), dan ほしい semuanya membutuhkan partikel が, BUKAN を. Yang benar: 彼はスポーツが上手です。Partikel を hanya untuk objek dari kata kerja aksi transitif."
            },
            {
                id: "ex1_q13",
                type: "mcq",
                grammar_focus: "もう vs まだ — Sudah/Belum dalam berbagai konteks",
                question: "A menanyakan:「宿題はもう終わりましたか？」\nB ingin menjawab「BELUM」. Jawaban yang TEPAT adalah?",
                options: [
                    "はい、もう終わりました。(Ya, sudah selesai.)",
                    "いいえ、まだ終わっていません。(Tidak, belum selesai.)",
                    "いいえ、もう終わっていません。(Tidak tepat — もう + negatif = 'tidak lagi')",
                    "はい、まだ終わりました。(Tidak tepat — まだ + positif)"
                ],
                correctIndex: 1,
                explanation: "まだ + ていません = 'BELUM'. もう + negatif (もう〜ていません) berarti 'TIDAK LAGI' (sudah berhenti). Contoh: もう食べていません = Saya tidak makan lagi. まだ食べていません = Saya belum makan."
            },
            {
                id: "ex1_q14",
                type: "mcq",
                grammar_focus: "ましょう vs ませんか vs ましょうか — Nuansa ajakan",
                question: "Kamu melihat orang lanjut usia kesulitan membawa barang. Ungkapan yang paling tepat untuk MENAWARKAN BANTUAN adalah?",
                options: [
                    "荷物を持ちましょう！(Ayo kita bawa barang — pembicara mengambil inisiatif sendiri)",
                    "荷物を持ちませんか？(Maukah membawa barang? — mengajak, menunggu respons)",
                    "荷物を持ちましょうか？(Bolehkah saya bantu bawa? — menawarkan bantuan kepada pendengar)",
                    "荷物を持ってください。(Tolong bawa barang — permintaan)"
                ],
                correctIndex: 2,
                explanation: "ましょうか = 'Bolehkah saya...? / Maukah saya membantu?' Pola untuk MENAWARKAN BANTUAN kepada pendengar. ましょう = 'Ayo kita!' (pembicara lebih proaktif). ませんか = 'Maukah kamu...?' (mengajak orang lain ikut serta)."
            },
            {
                id: "ex1_q15",
                type: "translate",
                grammar_focus: "に行く — Pergi untuk melakukan + partikel majemuk",
                question: "Terjemahkan ke dalam bahasa Jepang (romaji):\n\n「Setiap hari Minggu, saya pergi ke perpustakaan untuk membaca buku.」\n\nGunakan: nichiyoubi / ni / toshokan / hon / o / yomi / ni / ikimasu / watashi wa",
                acceptedAnswers: [
                    "watashi wa nichiyoubi ni toshokan ni hon o yomi ni ikimasu",
                    "nichiyoubi ni toshokan ni hon o yomi ni ikimasu",
                    "watashi wa mainichi nichiyoubi ni toshokan ni hon o yomi ni ikimasu"
                ],
                explanation: "Pola 'pergi untuk melakukan': V-masu stem + に + 行きます. Hon o yomu → yomi + ni + ikimasu. Toshokan = perpustakaan, nichiyoubi ni = pada hari Minggu. Urutan: Topik wa + Waktu ni + Tempat ni + V-masu stem ni + ikimasu."
            },
            {
                id: "ex1_q16",
                type: "mcq",
                grammar_focus: "漢字 — Arti kanji institusi pendidikan",
                question: "Manakah pasangan kanji → arti yang BENAR SEMUA?",
                options: [
                    "学校 = sekolah / 大学 = universitas / 図書館 = perpustakaan",
                    "学校 = universitas / 大学 = sekolah / 図書館 = perpustakaan",
                    "学校 = sekolah / 大学 = rumah sakit / 図書館 = toko",
                    "学校 = toko / 大学 = sekolah / 図書館 = kantor"
                ],
                correctIndex: 0,
                explanation: "学 (gaku) = belajar, 校 (kou) = sekolah → 学校 = sekolah. 大 (dai) = besar, 学 = institusi belajar → 大学 = universitas. 図書館 (toshokan) = perpustakaan. Perhatikan: 大学 terdiri dari 大 (besar) + 学 (belajar) = tempat belajar yang besar."
            },
            {
                id: "ex1_q17",
                type: "mcq",
                grammar_focus: "い-adjective — Bentuk lampau (past tense)",
                question: "「昨日の天気はとても___。」(Cuaca kemarin sangat panas.)\n\nBentuk kata sifat yang tepat (lampau/past) untuk 暑い (atsui — panas) adalah?",
                options: [
                    "あつい (atsui) — bentuk sekarang",
                    "あつかった (atsukatta) — bentuk lampau i-adj",
                    "あついでした (atsui deshita) — SALAH (deshita tidak bisa langsung setelah i-adj)",
                    "あつだった (atsu datta) — SALAH (pola na-adj/kata benda)"
                ],
                correctIndex: 1,
                explanation: "i-adjective LAMPAU: hapus -i, tambahkan -katta. atsui → atsu + katta = atsukatta (あつかった). PENTING: Jangan pernah pakai 'deshita' langsung setelah i-adj! 'Atsui deshita' adalah SALAH. Yang benar: atsukatta desu (あつかったです)."
            },
            {
                id: "ex1_q18",
                type: "mcq",
                grammar_focus: "に vs で vs へ — Perbedaan partikel lokasi dan tujuan",
                question: "「来週、東京___出張があります。」(Minggu depan, ada perjalanan dinas ke Tokyo.)\n\nPartikel yang paling tepat adalah?",
                options: [
                    "に (ni) — tujuan yang spesifik (paling umum dalam percakapan)",
                    "へ (e) — menekankan ARAH perjalanan (lebih sastrawi)",
                    "で (de) — tempat berlangsungnya aktivitas",
                    "から (kara) — titik awal"
                ],
                correctIndex: 0,
                explanation: "に lebih umum dalam percakapan sehari-hari, terutama untuk tujuan SPESIFIK seperti Tokyo. へ lebih menekankan ARAH dan terasa lebih sastrawi. Keduanya gramatikal, tapi に adalah pilihan yang lebih natural dan sering digunakan."
            },
            {
                id: "ex1_q19",
                type: "fill",
                grammar_focus: "ながら — Melakukan dua hal bersamaan (bentuk kata kerja)",
                question: "「音楽を聴き___勉強するのは良くないと言われています。」\n(Mendengarkan musik sambil belajar katanya tidak baik.)\n\nKata yang tepat untuk mengisi bagian kosong adalah:",
                correct: ["nagara", "ながら"],
                explanation: "ながら (nagara) menyatakan melakukan dua aktivitas secara BERSAMAAN. Pola: V-masu stem + ながら. 聴く → 聴き (kiki) + ながら = sambil mendengarkan. Subjek dari dua aksi tersebut harus SAMA orangnya."
            },
            {
                id: "ex1_q20",
                type: "mcq",
                grammar_focus: "漢字 — Kanji arah mata angin dalam kata majemuk",
                question: "Manakah bacaan yang BENAR untuk kanji「北東」?",
                options: [
                    "nansei (南西) — barat daya",
                    "hokutou (北東) — timur laut",
                    "nanboku (南北) — utara-selatan",
                    "tousei (東西) — timur-barat"
                ],
                correctIndex: 1,
                explanation: "北 (kita/hoku) = utara. 東 (higashi/tou) = timur. 北東 dibaca hoku-tou = timur laut (northeast). Kompas N5: 北 (utara), 南 (selatan), 東 (timur), 西 (barat)."
            },
            {
                id: "ex1_q21",
                type: "mcq",
                grammar_focus: "てはいけない vs ないでください — Larangan vs Permintaan negatif",
                question: "Dokter berkata kepada pasien sebelum operasi:\n「手術の前に食べ物を___。」\n(Tolong jangan makan sebelum operasi.)\n\nPola yang paling tepat untuk situasi ini adalah?",
                options: [
                    "食べてはいけません (te wa ikemasen) — larangan umum/peraturan",
                    "食べないでください (naide kudasai) — permintaan sopan personal",
                    "食べちゃいけません (cha ikemasen) — larangan kasual",
                    "食べないほうがいいです (nai hou ga ii desu) — saran 'lebih baik jangan'"
                ],
                correctIndex: 1,
                explanation: "ないでください adalah PERMINTAAN sopan dari seseorang ke seseorang secara langsung ('Tolong jangan...'). Dokter meminta secara personal kepada pasien → ないでください lebih tepat dan natural. てはいけない lebih kuat sebagai larangan umum/peraturan."
            },
            {
                id: "ex1_q22",
                type: "mcq",
                grammar_focus: "たことがある — Pengalaman 'pernah melakukan' (bentuk kata kerja)",
                question: "「富士山に___ことがあります。」\n(Saya pernah mendaki Gunung Fuji.)\n\nBentuk kata kerja「登る (noboru — mendaki)」yang tepat adalah?",
                options: [
                    "登る (noboru) — dictionary form",
                    "登って (nobotte) — te-form",
                    "登った (nobotta) — ta-form (past)",
                    "登り (nobori) — masu-stem"
                ],
                correctIndex: 2,
                explanation: "Pola pengalaman: V-TA + ことがあります. V-ta (bentuk lampau) + koto ga arimasu. Jadi: 登る → 登った + ことがあります = 登ったことがあります. INGAT: dictionary form + koto ga arimasu memiliki makna berbeda ('ada hal mendaki')."
            },
            {
                id: "ex1_q23",
                type: "mcq",
                grammar_focus: "Deteksi Kesalahan — Grammar N5 dalam kalimat",
                question: "Manakah kalimat yang BENAR secara gramatikal?",
                options: [
                    "私は毎日コーヒーを飲んでいます。",
                    "駅の近くに新しい店があります。",
                    "彼女はピアノを弾くことが上手です。",
                    "A dan B benar; C salah (harusnya: ピアノを弾くのが上手)"
                ],
                correctIndex: 3,
                explanation: "C SALAH: 「ピアノを弾くことが上手」→ harus menggunakan の, bukan こと. Pola yang benar: V-dictionary + のが + 上手/下手/好き/嫌い。Contoh benar: ピアノを弾くのが上手です. こと digunakan untuk nominalisasi dalam konteks yang berbeda (seperti dalam rules/facts)."
            },
            {
                id: "ex1_q24",
                type: "translate",
                grammar_focus: "てから — Urutan tindakan (setelah A, lalu B)",
                question: "Terjemahkan ke dalam bahasa Jepang (romaji):\n\n「Setelah mandi, saya minum susu.」\n\nGunakan: ofuro / ni / haitte / kara / gyuunyuu / o / nomimasu",
                acceptedAnswers: [
                    "ofuro ni haitte kara gyuunyuu o nomimasu",
                    "ofuro ni haitte kara, gyuunyuu o nomimasu",
                    "watashi wa ofuro ni haitte kara gyuunyuu o nomimasu"
                ],
                explanation: "Pola: V-te + から + V2 = setelah melakukan V, lalu V2. Hairu (masuk/mandi) → haitte + kara. Gyuunyuu = susu. Struktur lengkap: [Tempat] ni haitte kara + [Objek] o + [Kata Kerja]."
            },
            {
                id: "ex1_q25",
                type: "mcq",
                grammar_focus: "だけ vs しか〜ない — 'Hanya' dalam kalimat positif vs negatif",
                question: "Dua kalimat berikut memiliki arti yang SAMA.\n①「お金が百円だけあります。」\n②「お金が百円___ありません。」\n\nKata yang mengisi bagian kosong di kalimat ② adalah?",
                options: [
                    "だけ (dake) — karena sama-sama berarti 'hanya'",
                    "しか (shika) — digunakan dengan kalimat NEGATIF",
                    "も (mo) — berarti 'juga/pula'",
                    "ばかり (bakari) — berarti 'hanya saja (konotasi berlebihan)'"
                ],
                correctIndex: 1,
                explanation: "だけ digunakan dalam kalimat POSITIF: お金が百円だけあります (Hanya ada 100 yen). しか digunakan dalam kalimat NEGATIF dan SELALU diikuti bentuk negatif: お金が百円しかありません (Hanya ada 100 yen — menekankan sedikit/hanya itu)."
            }
        ]
    },

    // ══════════════════════════════════════════════════════════════════════
    // BATCH 2 — "Ujian Kedua" | Grammar Menengah & Lanjutan (Tier 2–3)
    // ══════════════════════════════════════════════════════════════════════
    {
        id: "exam_2",
        title: "Ujian Kedua",
        icon: "📋",
        description: "Grammar menengah hingga lanjutan: pola te-form kompleks, kewajiban, kemampuan, perbandingan, dan pengalaman N5 Tier 2–3.",
        time_limit_minutes: 15,
        passing_score: 70,
        questions: [
            {
                id: "ex2_q1",
                type: "mcq",
                grammar_focus: "一番 vs より — Superlatif vs Komparatif",
                question: "「クラスの中でだれが___背が高いですか。」\n(Di antara anggota kelas, siapa yang paling tinggi?)\n\nKata yang tepat mengisi bagian kosong adalah?",
                options: [
                    "より (yori) — digunakan untuk membandingkan DUA hal",
                    "一番 (ichiban) — 'paling' dalam suatu kelompok",
                    "もっと (motto) — lebih lagi (tanpa perbandingan langsung)",
                    "ずっと (zutto) — jauh lebih atau sepanjang waktu"
                ],
                correctIndex: 1,
                explanation: "一番 (ichiban) = 'paling/nomor satu' → SUPERLATIF dalam kelompok. Pola: [Kelompok] の中で + [Topik] が + 一番 + [sifat]. より digunakan untuk membandingkan DUA hal: A は B より sifat desu (A lebih [sifat] daripada B)."
            },
            {
                id: "ex2_q2",
                type: "mcq",
                grammar_focus: "てくれる vs てもらう vs てあげる — Arah pemberian jasa",
                question: "「先生が宿題を説明してくれました。」\nKalimat ini menunjukkan bahwa...",
                options: [
                    "Saya menjelaskan PR kepada guru",
                    "Guru meminta saya menjelaskan PR",
                    "Guru menjelaskan PR kepada saya/grup saya (orang lain berbuat baik untuk saya)",
                    "Saya memohon guru untuk menjelaskan PR"
                ],
                correctIndex: 2,
                explanation: "くれる/くれました = seseorang melakukan sesuatu untuk SAYA atau kelompok saya. Perspektif: orang lain → saya. もらう = saya menerima jasa. あげる = saya memberi jasa kepada orang lain. 先生が〜してくれた = Guru yang melakukan itu UNTUKKU."
            },
            {
                id: "ex2_q3",
                type: "mcq",
                grammar_focus: "ながら — Bentuk kata kerja yang wajib digunakan",
                question: "「コーヒーを___ながら、新聞を読みます。」\n(Membaca koran sambil minum kopi.)\n\nBentuk kata kerja「飲む (nomu)」yang tepat sebelum ながら adalah?",
                options: [
                    "のんで (nonde) — te-form",
                    "のみ (nomi) — masu-stem (V-masu tanpa 'masu')",
                    "のむ (nomu) — dictionary form",
                    "のんだ (nonda) — ta-form (past)"
                ],
                correctIndex: 1,
                explanation: "ながら membutuhkan V-MASU STEM (bentuk masu tanpa 'masu'). Nomu → nomimasu → nomi + nagara = nomINAgara. Bukan te-form! Ini berbeda dari pola te iru, te kara, dll yang menggunakan te-form."
            },
            {
                id: "ex2_q4",
                type: "mcq",
                grammar_focus: "たり〜たりする — Menyebutkan sampel aktivitas (bukan daftar lengkap)",
                question: "「週末は本を読ん___映画を見___します。」\n(Di akhir pekan, saya melakukan hal-hal seperti membaca buku dan menonton film.)\n\nKedua bagian kosong diisi dengan?",
                options: [
                    "で〜で (te-form berurutan — daftar aksi pasti)",
                    "だり〜だり (bentuk yang tidak ada)",
                    "たり〜たり (ta-form + ri — menyebutkan contoh/sampel)",
                    "て〜て (te-form — urutan aksi)"
                ],
                correctIndex: 2,
                explanation: "たり〜たりする = melakukan berbagai hal (tidak terbatas hanya itu, menunjukkan SAMPEL). Pola: V-ta + り, V-ta + り + する. 読んだり、見たりします. Ini berbeda dari te-form berurutan yang menunjukkan urutan pasti."
            },
            {
                id: "ex2_q5",
                type: "fill",
                grammar_focus: "つもり — Rencana/niat yang sudah dipikirkan serius",
                question: "「来年、日本へ留学する___です。」\n(Saya berencana untuk belajar di Jepang tahun depan.)\n\nKata yang tepat mengisi bagian kosong adalah:",
                correct: ["tsumori", "つもり"],
                explanation: "つもり (tsumori) = rencana atau niat yang sudah dipikirkan cukup serius. Pola: V-dictionary + つもりです. Berbeda dari たい yang menggambarkan 'keinginan' daripada 'rencana matang'."
            },
            {
                id: "ex2_q6",
                type: "mcq",
                grammar_focus: "すぎる — Bentuk penggabungan 'terlalu' dengan i-adjective",
                question: "Untuk menyatakan 'terlalu mahal' menggunakan kata「高い (takai)」, bentuk yang BENAR adalah?",
                options: [
                    "高いすぎる (takai sugiru) — langsung ditambah (SALAH)",
                    "高すぎる (taka sugiru) — hapus -i lalu tambah すぎる",
                    "高だすぎる (takada sugiru) — pola na-adj (SALAH)",
                    "高くすぎる (takaku sugiru) — bentuk adverbial (SALAH untuk ini)"
                ],
                correctIndex: 1,
                explanation: "i-adjective + すぎる: hapus -i, tambah すぎる langsung. 高い → 高(taka) + すぎる = 高すぎる (terlalu mahal). Pola serupa: 暑い → 暑すぎる, 古い → 古すぎる. Na-adj + sugiru: langsung saja, tanpa な."
            },
            {
                id: "ex2_q7",
                type: "mcq",
                grammar_focus: "なければならない — Kewajiban dalam konteks yang tepat",
                question: "Kalimat mana yang paling tepat untuk situasi: \"Sebagai karyawan baru, saya harus datang tepat waktu.\"",
                options: [
                    "新入社員として、時間通りに来てもいいです。(boleh datang — bukan kewajiban)",
                    "新入社員として、時間通りに来たいです。(ingin datang — keinginan, bukan wajib)",
                    "新入社員として、時間通りに来なければなりません。(harus datang — kewajiban)",
                    "新入社員として、時間通りに来ないでください。(tolong jangan datang — SALAH ARTI)"
                ],
                correctIndex: 2,
                explanation: "なければなりません (nakereba narimasen) = 'HARUS melakukan'. Pola dari negatif: V-nai → V-nakereba + naranai/narimasen. Ini bentuk FORMAL. Bentuk kasualnya: nakucha (なくちゃ) atau nai to ikenai (ないといけない)."
            },
            {
                id: "ex2_q8",
                type: "mcq",
                grammar_focus: "なくてもいい vs なければならない — Tidak harus vs Harus",
                question: "「明日は休日だから、早く起き___。」\n(Besok hari libur, jadi tidak perlu bangun pagi.)\n\nBentuk yang tepat (menyatakan 'tidak perlu') adalah?",
                options: [
                    "なければなりません (nakereba narimasen) — harus",
                    "なくてもいいです (nakute mo ii desu) — tidak harus",
                    "てはいけません (te wa ikemasen) — tidak boleh",
                    "ないでください (naide kudasai) — tolong jangan"
                ],
                correctIndex: 1,
                explanation: "なくてもいい = 'tidak harus / boleh tidak melakukan'. Pola: V-nai → V-naku + te mo ii. 起きる → 起きない → 起きなくてもいいです. Jangan tertukar: なければならない = HARUS. なくてもいい = TIDAK HARUS."
            },
            {
                id: "ex2_q9",
                type: "mcq",
                grammar_focus: "ことができる vs のが上手 — Kemampuan vs Kepandaian",
                question: "「山田さんはギターを___。」\nKalimat yang paling tepat untuk menyatakan 'Yamada BISA main gitar (ability)' adalah?",
                options: [
                    "弾くことができます (hiku koto ga dekimasu) — bisa/mampu melakukan",
                    "弾くのが上手です (hiku no ga jouzu desu) — pandai bermain (bukan sekedar bisa)",
                    "弾きたいです (hikitai desu) — ingin bermain",
                    "弾いています (hiite imasu) — sedang bermain"
                ],
                correctIndex: 0,
                explanation: "ことができる = 'BISA/MAMPU melakukan' (ability). Pola: V-dictionary + ことができます. 上手 (jouzu) = 'pandai/mahir' (keahlian tinggi). 'Bisa bermain' → koto ga dekimasu. 'Pandai bermain' → no ga jouzu desu."
            },
            {
                id: "ex2_q10",
                type: "mcq",
                grammar_focus: "漢字複合語 — Bacaan kanji dalam kata majemuk (电话・电车)",
                question: "Manakah pasangan kanji → bacaan yang BENAR?",
                options: [
                    "電話 → densha / 電車 → denwa (TERBALIK)",
                    "電話 → denwa (telepon) / 電車 → densha (kereta listrik)",
                    "電話 → denwasha / 電車 → denko (SALAH)",
                    "電話 → denko / 電車 → denki (SALAH)"
                ],
                correctIndex: 1,
                explanation: "電 (den) = listrik/elektrik. 話 (wa) = bicara → 電話 (denwa) = telepon. 車 (sha) = kendaraan → 電車 (densha) = kereta listrik. Kanji 電 juga muncul di: 電気 (denki = listrik), 電子 (denshi = elektronik)."
            },
            {
                id: "ex2_q11",
                type: "fill",
                grammar_focus: "ないでください — Permintaan untuk tidak melakukan sesuatu",
                question: "「授業中にスマホを使わ___ください。」\n(Tolong jangan menggunakan smartphone selama pelajaran.)\n\nKata yang tepat mengisi bagian kosong adalah:",
                correct: ["nai de", "ないで", "naide"],
                explanation: "Pola: V-nai + でください. 使う (tsukau) → 使わない (tsukawanai) → 使わないでください. Ini adalah permintaan sopan untuk TIDAK melakukan sesuatu. Berbeda dari てはいけません yang merupakan LARANGAN lebih kuat."
            },
            {
                id: "ex2_q12",
                type: "mcq",
                grammar_focus: "ので vs から — Nuansa objektif (formal) vs subjektif (kasual)",
                question: "「熱がある___、今日は学校を休みます。」\nUntuk konteks SURAT RESMI kepada wali kelas, pilihan yang tepat adalah?",
                options: [
                    "から (kara) — lebih subjektif, umum dalam percakapan sehari-hari",
                    "ので (node) — lebih objektif, cocok untuk konteks formal/surat resmi",
                    "けど (kedo) — kontras (namun), bukan sebab-akibat",
                    "のに (noni) — berlawanan dengan harapan"
                ],
                correctIndex: 1,
                explanation: "ので (node) terdengar lebih OBJEKTIF dan FORMAL. Digunakan dalam: surat resmi, laporan, penjelasan kepada atasan/guru. から (kara) lebih SUBJEKTIF dan kasual. Keduanya berarti 'karena', tapi tingkat formalitasnya berbeda."
            },
            {
                id: "ex2_q13",
                type: "mcq",
                grammar_focus: "ね vs よ — Partikel akhir: konfirmasi vs informasi baru",
                question: "「このラーメン、おいしい___！」\nKamu baru pertama kali mencoba ramen ini dan ingin MEMBERITAHU temanmu bahwa ini enak (teman belum tahu rasanya). Partikel yang tepat adalah?",
                options: [
                    "ね (ne) — 'enak ya?' mencari konfirmasi/persetujuan bersama",
                    "よ (yo) — 'ini enak lho!' memberikan informasi baru kepada pendengar",
                    "な (na) — pernyataan pada diri sendiri (monolog)",
                    "か (ka) — pertanyaan"
                ],
                correctIndex: 1,
                explanation: "よ (yo) = memberikan INFORMASI BARU kepada pendengar yang belum tahu. ね (ne) = mencari KONFIRMASI atau berbagi perasaan ('ya kan? setuju kan?'). Temanmu belum tahu rasanya → gunakan よ untuk memberitahu."
            },
            {
                id: "ex2_q14",
                type: "mcq",
                grammar_focus: "がほしい vs 〜たい — Ingin benda vs Ingin melakukan",
                question: "Manakah penggunaan がほしい dan 〜たい yang KEDUANYA BENAR?",
                options: [
                    "新しいパソコンがほしいです。/ 日本語を勉強したいです。",
                    "新しいパソコンを勉強したいです。/ 日本語がほしいです。(terbalik)",
                    "新しいパソコンがほしいです。/ 日本語がほしいです。(ほしい untuk keduanya — tidak tepat untuk bahasa)",
                    "新しいパソコンを欲しいです。/ 日本語をしたいです。(partikel salah)"
                ],
                correctIndex: 0,
                explanation: "ほしい (hoshii) = ingin memiliki suatu BENDA → パソコンがほしい. たい (tai) = ingin MELAKUKAN suatu tindakan → V-masu stem + たい. 勉強する → 勉強し + たい = 勉強したい. 日本語 bukan benda konkret yang bisa 'dimiliki' → lebih tepat menggunakan たい untuk 'belajar bahasa Jepang'."
            },
            {
                id: "ex2_q15",
                type: "translate",
                grammar_focus: "なければならない — Produksi kalimat kewajiban kompleks",
                question: "Terjemahkan ke dalam bahasa Jepang (romaji):\n\n「Untuk lulus ujian, saya harus belajar setiap hari.」\n\nGunakan: shiken ni / ukaru tame ni / mainichi / benkyou shi / nakereba narimasen",
                acceptedAnswers: [
                    "shiken ni ukaru tame ni mainichi benkyou shinakereba narimasen",
                    "shiken ni ukaru tame ni, mainichi benkyou shinakereba narimasen",
                    "mainichi benkyou shinakereba narimasen"
                ],
                explanation: "benkyou suru → benkyou shi + nakereba narimasen (benkyou shinakereba narimasen). ために (tame ni) = 'untuk tujuan'. 試験に受かる = lulus ujian. Urutan: Tujuan + tame ni + Kewajiban."
            },
            {
                id: "ex2_q16",
                type: "mcq",
                grammar_focus: "漢字 — Urutan dan nama hari dalam seminggu (曜日)",
                question: "Manakah urutan hari yang BENAR dari Senin sampai Minggu dalam bahasa Jepang?",
                options: [
                    "月・火・水・木・金・土・日 (Getsu, Ka, Sui, Moku, Kin, Do, Nichi)",
                    "日・月・火・水・木・金・土 (Nichi, Getsu, Ka, Sui, Moku, Kin, Do)",
                    "火・水・木・金・土・日・月 (Ka, Sui, Moku, Kin, Do, Nichi, Getsu)",
                    "月・水・火・木・金・土・日 (Getsu, Sui, Ka, Moku, Kin, Do, Nichi)"
                ],
                correctIndex: 0,
                explanation: "Hari dalam seminggu dari Senin: 月曜日 (Senin/Bulan), 火曜日 (Selasa/Api), 水曜日 (Rabu/Air), 木曜日 (Kamis/Kayu), 金曜日 (Jumat/Emas), 土曜日 (Sabtu/Tanah), 日曜日 (Minggu/Matahari). Mudah diingat dengan: Bulan, Api, Air, Kayu, Emas, Tanah, Matahari."
            },
            {
                id: "ex2_q17",
                type: "mcq",
                grammar_focus: "てから + ている — Menggabungkan urutan waktu dan kondisi berlangsung",
                question: "「大学を卒業してから、東京で働いています。」\nKalimat ini paling tepat diterjemahkan sebagai?",
                options: [
                    "Setelah lulus universitas, saya bekerja di Tokyo (dan masih bekerja di sana sekarang)",
                    "Saya ingin bekerja di Tokyo setelah lulus universitas",
                    "Saya lulus universitas dan kemudian pindah ke Tokyo",
                    "Sebelum lulus universitas, saya bekerja di Tokyo"
                ],
                correctIndex: 0,
                explanation: "Menggabungkan dua pola: てから (setelah) dan ている (kondisi berlangsung hingga sekarang). 卒業してから = setelah lulus. 働いています = sedang bekerja (masih berlanjut). Jadi: 'Setelah lulus, saya bekerja di Tokyo dan masih bekerja hingga sekarang'."
            },
            {
                id: "ex2_q18",
                type: "mcq",
                grammar_focus: "ちゃいけない vs てはいけない — Tingkat formalitas larangan",
                question: "「ここでたばこを吸っちゃだめだよ。」\nKalimat ini paling cocok diucapkan dalam konteks apa?",
                options: [
                    "Pengumuman resmi di tempat publik (formal)",
                    "Surat peringatan dari kantor (sangat formal)",
                    "Percakapan kasual antara teman sehari-hari",
                    "Instruksi tertulis dalam peraturan perusahaan"
                ],
                correctIndex: 2,
                explanation: "ちゃだめ/ちゃいけない (cha dame/cha ikenai) adalah bentuk KASUAL dari larangan. Hanya digunakan dalam percakapan informal (antar teman, keluarga). Untuk konteks formal: てはいけません. Indikator kasual lainnya: だよ di akhir kalimat."
            },
            {
                id: "ex2_q19",
                type: "mcq",
                grammar_focus: "Deteksi Kesalahan — Partikel yang benar setelah 好き・嫌い・上手・下手",
                question: "Manakah kalimat yang BENAR?",
                options: [
                    "私はサッカーを好きです。(× を → が)",
                    "彼女はダンスを上手です。(× を → が)",
                    "弟はゲームが大好きです。",
                    "先生は英語を嫌いではありません。(× を → が)"
                ],
                correctIndex: 2,
                explanation: "好き (suki), 嫌い (kirai), 上手 (jouzu), 下手 (heta), 大好き (daisuki) semuanya membutuhkan partikel が, BUKAN を. Yang benar: 私はサッカーが好きです / 彼女はダンスが上手です / 先生は英語が嫌いではありません. Kalimat C sudah benar."
            },
            {
                id: "ex2_q20",
                type: "mcq",
                grammar_focus: "でしょう vs だろう — Perkiraan formal vs kasual",
                question: "Seorang pembawa acara berita memperkirakan cuaca:「明日は晴れ___。」\nKata yang paling tepat untuk konteks siaran berita (formal) adalah?",
                options: [
                    "だろう (darou) — bentuk kasual/percakapan biasa",
                    "でしょう (deshou) — bentuk sopan/formal",
                    "だね (da ne) — mengonfirmasi ke pendengar",
                    "かな (kana) — berbicara pada diri sendiri"
                ],
                correctIndex: 1,
                explanation: "でしょう (deshou) adalah bentuk FORMAL/SOPAN dari perkiraan. Digunakan dalam siaran berita, laporan cuaca, presentasi. だろう lebih kasual, untuk percakapan biasa atau tulisan informal."
            },
            {
                id: "ex2_q21",
                type: "fill",
                grammar_focus: "は〜より — 'Lebih ... daripada' (perbandingan komparatif)",
                question: "「東京は大阪___人口が多いです。」\n(Tokyo memiliki populasi yang lebih besar daripada Osaka.)\n\nKata yang tepat mengisi bagian kosong adalah:",
                correct: ["yori", "より"],
                explanation: "より (yori) = 'daripada' dalam perbandingan. Pola: A は B より [sifat] desu = A lebih [sifat] daripada B. Sering dipasangkan dengan の方が: 東京は大阪より(も)人口が多いです atau 東京の方が大阪より人口が多いです."
            },
            {
                id: "ex2_q22",
                type: "mcq",
                grammar_focus: "とき — Nuansa dictionary form vs ta-form sebelum toki",
                question: "「日本に___とき、富士山を見ました。」\n(Ketika [saya] di Jepang, saya melihat Gunung Fuji.)\n\nBentuk yang paling tepat adalah?",
                options: [
                    "行く (iku) — dictionary: 'ketika akan pergi' (belum sampai)",
                    "行った (itta) — ta-form: 'ketika sudah berada di' Jepang",
                    "行き (iki) — masu-stem",
                    "行って (itte) — te-form"
                ],
                correctIndex: 1,
                explanation: "V-dictionary + とき = 'ketika (akan/sedang) melakukan' (SEBELUM aksi selesai). V-ta + とき = 'ketika sudah (dalam kondisi hasil dari aksi selesai)'. Melihat Fuji SAAT SUDAH BERADA di Jepang → itta (sudah sampai/berada di sana) + toki."
            },
            {
                id: "ex2_q23",
                type: "mcq",
                grammar_focus: "漢字 — Tingkat sekolah (小・中・高・大)",
                question: "「私の妹は今年___に入学しました。」Manakah yang bermakna 'Sekolah Dasar'?",
                options: [
                    "大学 (daigaku) — universitas (大=besar)",
                    "中学校 (chuugakkou) — SMP (中=tengah)",
                    "高校 (koukou) — SMA (高=tinggi)",
                    "小学校 (shougakkou) — Sekolah Dasar (小=kecil)"
                ],
                correctIndex: 3,
                explanation: "小 (shou) = kecil/dasar. 小学校 = SD (sekolah kecil/dasar). Tingkat sekolah: 小学校 (SD), 中学校 (SMP), 高校/高等学校 (SMA), 大学 (Universitas). Kanji kuncinya: 小 (kecil) = SD, 中 (tengah) = SMP, 高 (tinggi) = SMA, 大 (besar) = Universitas."
            },
            {
                id: "ex2_q24",
                type: "translate",
                grammar_focus: "のが好き + が + のが下手 — Kalimat kompleks dengan kontras",
                question: "Terjemahkan ke dalam bahasa Jepang (romaji):\n\n「Saya suka memasak, tapi saya tidak pandai mencuci piring.」\n\nGunakan: ryouri suru / no ga / suki desu / ga / sara o arau / no ga / heta desu",
                acceptedAnswers: [
                    "ryouri suru no ga suki desu ga sara o arau no ga heta desu",
                    "ryouri suru no ga suki desu kedo sara o arau no ga heta desu",
                    "watashi wa ryouri suru no ga suki desu ga sara o arau no ga heta desu"
                ],
                explanation: "のが好き (suka melakukan) dan のが下手 (tidak pandai melakukan). Koneksi kontras: が (tapi/namun). Ryouri suru no ga suki = suka memasak. Sara o arau no ga heta = tidak pandai mencuci piring."
            },
            {
                id: "ex2_q25",
                type: "mcq",
                grammar_focus: "ましょうか vs ませんか vs ましょう — Situasi yang tepat",
                question: "Rekan kerja baru terlihat bingung dengan tugasnya. Kamu ingin MENAWARKAN BANTUAN. Kalimat paling tepat adalah?",
                options: [
                    "手伝ってください。(Tolong bantu saya → meminta bantuan UNTUK DIRI SENDIRI)",
                    "一緒に手伝いましょうか。(Bolehkah saya membantu? → menawarkan bantuan)",
                    "手伝いたいです。(Saya ingin membantu → menyatakan keinginan, tidak langsung menawarkan)",
                    "手伝わないでください。(Tolong jangan bantu → SALAH ARTI)"
                ],
                correctIndex: 1,
                explanation: "ましょうか (mashou ka) = 'Bolehkah saya...? / Maukah saya...?' Digunakan untuk MENAWARKAN BANTUAN kepada pendengar tanpa memaksa. Ini cara paling sopan untuk menawarkan bantuan dalam bahasa Jepang."
            }
        ]
    },

    // ══════════════════════════════════════════════════════════════════════
    // BATCH 3 — "Ujian Final JLPT N5" | Komprehensif & Tertinggi
    // ══════════════════════════════════════════════════════════════════════
    {
        id: "exam_3",
        title: "Ujian Final JLPT N5",
        icon: "🏆",
        description: "Simulasi ujian JLPT N5 sesungguhnya: menggabungkan seluruh grammar N5, kanji kompleks, pemahaman konteks, dan deteksi kesalahan tingkat lanjut.",
        time_limit_minutes: 20,
        passing_score: 70,
        questions: [
            {
                id: "ex3_q1",
                type: "mcq",
                grammar_focus: "総合判断 — Identifikasi satu-satunya kalimat yang benar",
                question: "Manakah satu-satunya kalimat yang BENAR secara gramatikal?",
                options: [
                    "彼女はピアノをひくことが上手です。(× ことが → のが)",
                    "私は毎朝コーヒーを飲むのが好きだです。(× だです → です atau だ)",
                    "明日、友達と映画を見に行くつもりです。",
                    "今日はあまり疲れいです。(× 疲れいです → 疲れています atau 疲れた)"
                ],
                correctIndex: 2,
                explanation: "Kalimat C benar: 明日、友達と映画を見に行くつもりです (Besok berencana pergi menonton film dengan teman). Menggunakan: V-dictionary + つもりです. A salah: こと → の sebelum が上手. B salah: 好きだです tidak gramatikal. D salah: 疲れいです bukan kata sifat-i yang valid."
            },
            {
                id: "ex3_q2",
                type: "mcq",
                grammar_focus: "のに — Kontras dengan harapan (meskipun/padahal)",
                question: "「一生懸命練習した___、試合に負けてしまいました。」\n(Meskipun sudah berlatih keras, (saya) kalah dalam pertandingan.)\n\nKata yang tepat adalah?",
                options: [
                    "から (kara) — karena (sebab menyebabkan kalah)",
                    "ので (node) — karena (formal)",
                    "けど (kedo) — tapi/namun (kontras netral)",
                    "のに (noni) — meskipun/padahal (berlawanan dengan harapan + kekecewaan)"
                ],
                correctIndex: 3,
                explanation: "のに (noni) = 'meskipun/padahal' — digunakan ketika hasilnya BERLAWANAN dengan yang diharapkan, mengandung nuansa kekecewaan atau keheranan. Berlatih keras → seharusnya menang, tapi malah kalah → のに. から/ので = 'karena'. けど = 'tapi' (kontras netral tanpa nuansa kecewa)."
            },
            {
                id: "ex3_q3",
                type: "mcq",
                grammar_focus: "複合て-form — Menganalisis rantai te-form yang panjang",
                question: "「宿題を終わらせてから、シャワーを浴びて、それから夕食を食べます。」\n\nUrutan kegiatan yang BENAR adalah?",
                options: [
                    "Mandi → Selesaikan PR → Makan malam",
                    "Selesaikan PR → Mandi → Makan malam",
                    "Makan malam → Selesaikan PR → Mandi",
                    "Selesaikan PR → Makan malam → Mandi"
                ],
                correctIndex: 1,
                explanation: "てから menunjukkan urutan jelas: A てから B = setelah A, baru B. 宿題を終わらせてから (setelah selesaikan PR) → シャワーを浴びて (mandi, lalu) → それから夕食を食べます (kemudian makan malam). Urutan: PR → Mandi → Makan malam."
            },
            {
                id: "ex3_q4",
                type: "mcq",
                grammar_focus: "も — Partikel dengan berbagai makna dalam konteks angka",
                question: "「もう３時間も待っています！」\n\nPartikel も dalam kalimat ini memiliki fungsi?",
                options: [
                    "Menyatakan 'juga/pula' (A juga, B juga)",
                    "Menyatakan jumlah yang terasa BANYAK/BERLEBIH (penekanan pada kuantitas yang mengejutkan)",
                    "Menyatakan hanya (sama dengan だけ)",
                    "Menunjukkan topik kalimat (sama dengan は)"
                ],
                correctIndex: 1,
                explanation: "も dalam konteks angka/waktu bisa menyatakan bahwa jumlah tersebut terasa BANYAK atau mengejutkan: '3時間も' = 'sudah 3 jam pula! (terasa sangat lama)'. Nuansa frustrasi karena lamanya waktu. Ini berbeda dari も yang berarti 'juga'."
            },
            {
                id: "ex3_q5",
                type: "translate",
                grammar_focus: "ほうがいい + ので — Saran dengan alasan formal",
                question: "Terjemahkan ke dalam bahasa Jepang (romaji):\n\n「Sebaiknya kamu tidur lebih awal karena besok ada ujian.」\n\nGunakan: ashita / shiken ga aru node / hayaku / neta hou ga ii desu yo",
                acceptedAnswers: [
                    "ashita shiken ga aru node hayaku neta hou ga ii desu yo",
                    "ashita shiken ga aru node hayaku neta hou ga ii desu",
                    "shiken ga aru node hayaku neta hou ga ii yo",
                    "ashita wa shiken ga aru node hayaku neta hou ga ii desu yo"
                ],
                explanation: "Menggabungkan: ① ので (node = karena, objektif) dan ② ほうがいい (hou ga ii = sebaiknya). Saran dengan ほうがいい menggunakan V-ta: neru → neta + hou ga ii. よ di akhir memperkuat keyakinan pembicara ('lho!'/'ya!')."
            },
            {
                id: "ex3_q6",
                type: "mcq",
                grammar_focus: "漢字 生 — Kanji dengan berbagai bacaan dalam kata majemuk",
                question: "Kanji 生 muncul dalam berbagai kata dengan bacaan berbeda. Manakah pasangan yang BENAR?",
                options: [
                    "学生 (gakusei = pelajar) / 先生 (sensei = guru) / 生まれる (umareru = lahir)",
                    "学生 (gakushou = pelajar) / 先生 (senshei = guru) / 生まれる (namareru = lahir)",
                    "学生 (manabuse = pelajar) / 先生 (maese = guru) / 生まれる (ikimaru = lahir)",
                    "学生 (gakusei = guru) / 先生 (sensei = pelajar) / 生まれる (umareru = mati)"
                ],
                correctIndex: 0,
                explanation: "生 memiliki banyak bacaan: 生 (sei) dalam 学生 (gakusei=pelajar), 先生 (sensei=guru). 生 (i) dalam 生きる (ikiru=hidup). 生 (u) dalam 生まれる (umareru=lahir). 生 (nama) dalam 生ビール (namabiru=bir segar). Kanji paling polimorfik di N5!"
            },
            {
                id: "ex3_q7",
                type: "mcq",
                grammar_focus: "動詞て-form — Pola perubahan yang menghasilkan -nde",
                question: "Untuk membuat te-form dari kata kerja berikut, manakah yang menggunakan pola「〜んで (nde)」?",
                options: [
                    "書く (kaku) → かいて (te: -ku → -ite)",
                    "飲む (nomu) → のんで (te: -mu → -nde)",
                    "食べる (taberu) → たべて (te: Group 2, drop ru + te)",
                    "来る (kuru) → きて (irregular)"
                ],
                correctIndex: 1,
                explanation: "Te-form Group 1 — pola 〜nde: kata kerja berakhiran -mu, -bu, -nu. 飲む (nomu) → のんで (nonde). Pola lain: -ku/-gu → -ite/-ide; -u/-tsu/-ru → -tte; Group 2 → drop ru + te; 来る → きて; する → して."
            },
            {
                id: "ex3_q8",
                type: "mcq",
                grammar_focus: "丁寧語 — Urutan tingkat kesopanan dalam bahasa Jepang",
                question: "Urutkan kalimat dari PALING KASUAL ke PALING FORMAL:\n①「早く寝ろ！」②「早く寝てください。」③「早く寝なさい。」④「お早めにお休みになってください。」",
                options: [
                    "① → ③ → ② → ④ (kasual → formal)",
                    "④ → ② → ③ → ① (formal → kasual)",
                    "① → ② → ③ → ④",
                    "③ → ① → ② → ④"
                ],
                correctIndex: 0,
                explanation: "Tingkat formalitas: ① 寝ろ = imperatif kasar (sangat kasual) → ③ 寝なさい = perintah lembut tapi tegas (orang tua ke anak) → ② 寝てください = permintaan sopan (standar sehari-hari) → ④ お休みになってください = keigo/bahasa hormat (sangat formal). Dalam percakapan umum, ② yang paling sering digunakan."
            },
            {
                id: "ex3_q9",
                type: "mcq",
                grammar_focus: "長文解析 — Memahami kalimat majemuk yang kompleks",
                question: "「田中さんは医者になるために、毎日一生懸命勉強していて、もう10年以上も日本語の勉強を続けています。」\n\nKalimat ini menyatakan bahwa Tanaka-san...",
                options: [
                    "Sudah menjadi dokter dan sekarang belajar bahasa Jepang",
                    "Sedang belajar keras untuk menjadi dokter DAN sudah belajar bahasa Jepang lebih dari 10 tahun",
                    "Telah berhenti belajar Jepang setelah 10 tahun dan sekarang menjadi dokter",
                    "Ingin belajar bahasa Jepang selama 10 tahun lagi"
                ],
                correctIndex: 1,
                explanation: "Parsing: ために (tame ni) = untuk tujuan. 医者になるために = untuk menjadi dokter. 毎日一生懸命勉強していて = belajar keras setiap hari. もう10年以上も = sudah lebih dari 10 tahun. 続けています = terus melanjutkan (kondisi berlangsung hingga sekarang)."
            },
            {
                id: "ex3_q10",
                type: "mcq",
                grammar_focus: "その (anafora) — Penggunaan dalam teks tertulis",
                question: "Dalam surat/email, ketika penulis merujuk pada informasi yang baru saja disebutkan OLEH PENULIS SENDIRI di paragraf sebelumnya, kata penunjuk yang digunakan adalah?",
                options: [
                    "この (kono) — benda dekat pembicara",
                    "その (sono) — merujuk ke informasi yang sudah disebutkan sebelumnya dalam teks",
                    "あの (ano) — jauh dari keduanya",
                    "どの (dono) — menanyakan"
                ],
                correctIndex: 1,
                explanation: "Dalam TULISAN, その/それ digunakan sebagai 'anafora' — merujuk ke informasi yang sudah disebutkan sebelumnya dalam teks. Ini adalah konvensi penulisan bahasa Jepang. Dalam percakapan lisan, ini berbeda (この untuk dekat pembicara, その untuk dekat pendengar)."
            },
            {
                id: "ex3_q11",
                type: "mcq",
                grammar_focus: "漢字 — Identifikasi kanji dengan jumlah coretan terbanyak",
                question: "Manakah kanji yang memiliki jumlah coretan (stroke) PALING BANYAK?",
                options: [
                    "山 (yama — gunung) — 3 coretan",
                    "学 (gaku — belajar) — 8 coretan",
                    "語 (go — bahasa) — 14 coretan",
                    "見 (mi — melihat) — 7 coretan"
                ],
                correctIndex: 2,
                explanation: "Jumlah coretan: 山 = 3, 見 = 7, 学 = 8, 語 = 14 coretan. 語 adalah yang terbanyak. Kanji 語 terdiri dari: 言 (7 coretan) + 吾 (7 coretan) = 14 total. Mengetahui jumlah coretan penting untuk pencarian di kamus tradisional (部首/bushu index)."
            },
            {
                id: "ex3_q12",
                type: "fill",
                grammar_focus: "〜たら — Pola kondisional (jika/kalau)",
                question: "「熱が___、学校を休んでもいいですよ。」\n(Kalau ada demam, boleh tidak masuk sekolah.)\n\nBentuk「ある (aru)」dengan pola kondisional 〜たら adalah:",
                correct: ["attara", "あったら"],
                explanation: "Pola kondisional たら: V-ta + ら. ある → あった (past) + ら = あったら (kalau ada). Pola たら digunakan untuk kondisi 'jika/kalau [sesuatu terjadi], maka [akibatnya]'. Ini adalah pola kondisional paling umum di level N5."
            },
            {
                id: "ex3_q13",
                type: "mcq",
                grammar_focus: "は vs が — Topik kalimat vs Subjek gramatikal",
                question: "「象は鼻が長い。」(Gajah, hidungnya panjang.)\n\nMengapa kalimat ini menggunakan は untuk 象 dan が untuk 鼻?",
                options: [
                    "Tidak ada alasan khusus, bisa ditukar sesuka hati",
                    "は menandai TOPIK yang sedang dibahas. が menandai SUBJEK gramatikal dari predikat 長い",
                    "は selalu untuk hewan, が selalu untuk bagian tubuh",
                    "が digunakan karena 鼻 (hidung) adalah subjek yang bergerak"
                ],
                correctIndex: 1,
                explanation: "は (wa) = TOPIK pembicaraan: 'Mengenai gajah...'. が (ga) = SUBJEK gramatikal dari predikat: '...hidungnyalah yang panjang'. Ini adalah konstruksi topik-komentar yang khas: [Topik は] + [Subjek が] + [Predikat]. Gajah = topik, hidung = yang secara gramatikal 'panjang'."
            },
            {
                id: "ex3_q14",
                type: "mcq",
                grammar_focus: "て-form — Deteksi kesalahan te-form tidak beraturan",
                question: "Manakah te-form yang SALAH?",
                options: [
                    "話す (hanasu) → 話して (hanashite)",
                    "泳ぐ (oyogu) → 泳いで (oyoide)",
                    "急ぐ (isogu) → 急いで (isoide)",
                    "行く (iku) → 行いて (ikite)"
                ],
                correctIndex: 3,
                explanation: "行く (iku = pergi) memiliki te-form TIDAK BERATURAN: 行って (itte), BUKAN 行いて (ikite)! Meskipun -ku seharusnya → -ite (書く→かいて), 行く adalah PENGECUALIAN WAJIB HAFAL. Ini salah satu jebakan paling umum di N5. Selalu ingat: 行く → 行って."
            },
            {
                id: "ex3_q15",
                type: "mcq",
                grammar_focus: "は〜よりも〜のほうが — Perbandingan kompleks dalam konteks",
                question: "「バスより電車の方が___です。」\nKalimat mana yang PALING LOGIS dalam konteks Tokyo (kota dengan sistem kereta tercepat)?",
                options: [
                    "安い (yasui — murah) — bus biasanya lebih murah dari kereta",
                    "遅い (osoi — lambat) — kereta biasanya lebih cepat",
                    "速い (hayai — cepat) — kereta memang lebih cepat dari bus di Tokyo",
                    "危ない (abunai — berbahaya) — kereta lebih aman dari bus"
                ],
                correctIndex: 2,
                explanation: "Di Tokyo, kereta jauh lebih cepat dan tepat waktu dibanding bus. 速い (hayai = cepat) adalah yang paling logis untuk 'バスより電車のほうが___'. Pola: A より B の方が + kata sifat = B lebih [sifat] daripada A."
            },
            {
                id: "ex3_q16",
                type: "translate",
                grammar_focus: "たことがない + てみたい — Kombinasi pengalaman dan keinginan mencoba",
                question: "Terjemahkan ke dalam bahasa Jepang (romaji):\n\n「Saya belum pernah makan sushi, tapi saya ingin mencobanya.」\n\nGunakan: sushi o / tabeta / koto ga / arimasen / ga / tabete / mitai desu",
                acceptedAnswers: [
                    "sushi o tabeta koto ga arimasen ga tabete mitai desu",
                    "mada sushi o tabeta koto ga arimasen ga tabete mitai desu",
                    "sushi o tabeta koto wa arimasen ga tabete mitai desu"
                ],
                explanation: "Menggabungkan: ① たことがない (belum pernah) dan ② てみたい (ingin mencoba). tabeta koto ga arimasen = belum pernah makan. が = tapi/namun. tabete mitai desu = ingin mencoba makan (melihat hasilnya)."
            },
            {
                id: "ex3_q17",
                type: "mcq",
                grammar_focus: "漢字 — Pasangan lawan kata (antonym) kanji N5",
                question: "Manakah pasangan kanji LAWAN KATA yang BENAR SEMUA?",
                options: [
                    "大 (besar) ↔ 小 (kecil) / 上 (atas) ↔ 下 (bawah) / 古 (lama) ↔ 新 (baru)",
                    "大 (besar) ↔ 長 (panjang) / 上 (atas) ↔ 前 (depan) / 古 (lama) ↔ 多 (banyak)",
                    "大 (besar) ↔ 小 (kecil) / 上 (atas) ↔ 右 (kanan) / 古 (lama) ↔ 高 (tinggi)",
                    "大 (besar) ↔ 少 (sedikit) / 上 (atas) ↔ 下 (bawah) / 古 (lama) ↔ 多 (banyak)"
                ],
                correctIndex: 0,
                explanation: "Pasangan antonym kanji N5: 大↔小 (besar↔kecil), 上↔下 (atas↔bawah), 古↔新 (lama↔baru), 多↔少 (banyak↔sedikit), 長↔短 (panjang↔pendek), 男↔女 (laki-laki↔perempuan), 入↔出 (masuk↔keluar). Opsi A memiliki semua pasangan yang benar."
            },
            {
                id: "ex3_q18",
                type: "mcq",
                grammar_focus: "てみる — Identifikasi grammar point dari konteks Inggris",
                question: "Pola grammar N5 manakah yang paling sesuai untuk: 'I tried eating natto for the first time to see if I'd like it.'",
                options: [
                    "〜たことがある (ta koto ga aru) — pernah melakukan (pengalaman saja)",
                    "〜てみる (te miru) — mencoba melakukan untuk melihat hasilnya",
                    "〜たい (tai) — ingin melakukan (keinginan, belum tentu dilakukan)",
                    "〜ながら (nagara) — sambil melakukan"
                ],
                correctIndex: 1,
                explanation: "てみる (te miru) = 'mencoba melakukan untuk melihat hasilnya' — persis seperti 'tried to see if I'd like it'. Contoh: 初めてなっとうを食べてみました。たことがある hanya menyatakan 'pernah melakukan' tanpa nuansa 'mencoba'. たい = keinginan (belum dilakukan)."
            },
            {
                id: "ex3_q19",
                type: "mcq",
                grammar_focus: "会話理解 — Memahami konteks percakapan lengkap",
                question: "Baca percakapan:\nA:「週末、映画を見に行きませんか？」\nB:「いいですね！何の映画ですか？」\n\nApa yang sedang terjadi?",
                options: [
                    "A memberitahu B bahwa A tidak akan pergi menonton film",
                    "A mengajak B menonton film, dan B merespons positif sambil bertanya filmnya apa",
                    "A bertanya kepada B apakah B sudah menonton film",
                    "B mengajak A menonton film, dan A bertanya filmnya apa"
                ],
                correctIndex: 1,
                explanation: "ませんか = ajakan sopan. A: 映画を見に行きませんか = 'Maukah pergi menonton film?' B: いいですね！(Baik/Ide bagus! → setuju positif) + 何の映画ですか = film apa? Ini pola percakapan ajakan yang sangat umum dalam bahasa Jepang."
            },
            {
                id: "ex3_q20",
                type: "mcq",
                grammar_focus: "漢字 — Membaca kalimat lengkap dengan kanji N5",
                question: "「今日は天気がいいから、外で昼ごはんを食べましょう。」\nBacaan yang BENAR adalah?",
                options: [
                    "kyou wa tenki ga ii kara, soto de hirugohan o tabemashou",
                    "kyou wa tenchi ga ii kara, hoka de hiruhan o tabemashou",
                    "ima wa tensou ga ii kara, sotoni hiru o tabemasu",
                    "kyou wa tenkimono ga ii kara, soto de gohan o tabemashou"
                ],
                correctIndex: 0,
                explanation: "Bacaan: 今日(きょう/kyou) = hari ini. 天気(てんき/tenki) = cuaca. 外(そと/soto) = luar. 昼ごはん(ひるごはん/hirugohan) = makan siang. 食べましょう(たべましょう/tabemashou) = ayo makan. 今日 dibaca 'kyou' (bukan 'imabi' atau 'konnichi')."
            },
            {
                id: "ex3_q21",
                type: "mcq",
                grammar_focus: "でしょう vs はずです — Nuansa perkiraan vs ekspektasi berbasis fakta",
                question: "「彼は今、図書館にいるでしょう。」vs「彼は今、図書館にいるはずです。」\n\nPerbedaan UTAMA antara kedua kalimat ini adalah?",
                options: [
                    "Tidak ada perbedaan, keduanya berarti 'dia mungkin di perpustakaan'",
                    "でしょう = perkiraan/spekulasi umum. はずです = ekspektasi kuat berdasarkan informasi/logika konkret",
                    "でしょう lebih yakin dari はずです",
                    "はずです digunakan di masa lalu, でしょう untuk masa depan"
                ],
                correctIndex: 1,
                explanation: "でしょう = spekulasi/dugaan ('sepertinya dia di perpustakaan' — tanpa dasar kuat). はずです = ekspektasi KUAT berdasarkan ALASAN KONKRET ('seharusnya dia di perpustakaan' — karena tahu jadwalnya). はずです menunjukkan keyakinan lebih tinggi dengan dasar yang lebih logis."
            },
            {
                id: "ex3_q22",
                type: "mcq",
                grammar_focus: "んですか — Keheranan positif dalam percakapan natural",
                question: "Teman memberi makanan yang ia masak sendiri. Kamu ingin berkata: 'Ini enak sekali! Kamu masak ini sendiri?' Pilihan yang paling natural adalah?",
                options: [
                    "おいしいです。自分で作りましたか？(formal tapi kaku)",
                    "とてもおいしいですね！自分で作ったんですか？(natural — んですか menunjukkan keheranan positif)",
                    "おいしすぎます。作りましたか？(すぎる di sini terdengar berlebihan — konotasi 'terlalu')",
                    "おいしいと思います。作りましたか？(と思います = saya pikir — terlalu tidak yakin)"
                ],
                correctIndex: 1,
                explanation: "んですか (n desu ka) mengekspresikan keheranan atau rasa penasaran yang mengalir natural dari konteks. 自分で作ったんですか = 'Kamu masak sendiri?! (wah!)' — nuansa terkejut positif. ね menambahkan nuansa berbagi perasaan, membuat percakapan terasa lebih hidup dan natural."
            },
            {
                id: "ex3_q23",
                type: "mcq",
                grammar_focus: "漢字 + 文法 — Kanji dan grammar dalam kalimat panjang",
                question: "「毎週水曜日に、家族と一緒に夕食を食べます。」\nManakah terjemahan yang PALING AKURAT?",
                options: [
                    "Setiap Rabu, saya makan malam bersama keluarga.",
                    "Setiap Selasa, saya makan siang dengan keluarga.",
                    "Setiap Kamis, keluarga saya makan malam.",
                    "Beberapa kali seminggu, saya makan bersama keluarga di malam hari."
                ],
                correctIndex: 0,
                explanation: "Parsing: 毎週 (maishuu) = setiap minggu. 水曜日 (suiyoubi) = hari Rabu (水=air). に = penanda waktu. 家族と一緒に = bersama keluarga. 夕食 (yuushoku) = makan malam. 食べます = makan. Ingat hari-hari: 水曜日 = Rabu (Air/Wednesday)."
            },
            {
                id: "ex3_q24",
                type: "translate",
                grammar_focus: "たり〜たりする + ている — Kalimat kompleks multi-pola",
                question: "Terjemahkan ke dalam bahasa Jepang (romaji):\n\n「Di waktu luang, saya biasanya melakukan hal-hal seperti membaca buku dan mendengarkan musik.」\n\nGunakan: hima na toki / wa / hon o yon dari / ongaku o kiitari / shite imasu / itsumo",
                acceptedAnswers: [
                    "hima na toki wa itsumo hon o yondari ongaku o kiitari shite imasu",
                    "hima na toki itsumo hon o yondari ongaku o kiitari shite imasu",
                    "watashi wa hima na toki wa itsumo hon o yondari ongaku o kiitari shite imasu"
                ],
                explanation: "たり〜たりしている = sedang melakukan berbagai hal seperti... Yomu → yonda + ri = yondari. Kiku → kiita + ri = kiitari. して + います = sedang dalam kondisi/kebiasaan. 暇な時は = saat waktu luang."
            },
            {
                id: "ex3_q25",
                type: "mcq",
                grammar_focus: "JLPT N5 最終問題 — Pemahaman nuansa budaya + grammar tingkat akhir",
                question: "「子供のとき、よく祖父母の家に泊まったものです。今はもうそんな機会がなくなってしまいました。」\n\nKalimat ini mengungkapkan perasaan apa?",
                options: [
                    "Kebanggaan bahwa pembicara sering mengunjungi kakek-neneknya",
                    "Rencana untuk mengunjungi kakek-nenek di masa depan",
                    "Nostalgia dan kerinduan akan kebiasaan masa kecil yang sudah tidak bisa dilakukan lagi",
                    "Keluhan bahwa kakek-nenek tidak pernah mengunjungi pembicara"
                ],
                correctIndex: 2,
                explanation: "「〜たものです」= kebiasaan masa lalu yang sudah tidak berlaku sekarang — nuansa NOSTALGIA. 「もう〜なくなってしまいました」= 'sudah tidak ada lagi' + rasa kehilangan (てしまいました menunjukkan penyesalan). Kombinasi keduanya = KERINDUAN mendalam akan masa kecil yang indah. Ini adalah tingkat pemahaman N5 tertinggi."
            }
        ]
    }
];

/**
 * Ambil batch ujian berdasarkan ID.
 * @param {string} batchId — "exam_1" | "exam_2" | "exam_3"
 * @returns {Object|null}
 */
export function getExamBatch(batchId) {
    return examBatches.find(b => b.id === batchId) ?? null;
}

/**
 * Hitung skor ujian secara akumulatif.
 * Setiap soal bernilai 4 poin (25 soal × 4 = 100 poin total).
 *
 * @param {Array<{ questionId: string, answer: any }>} userAnswers
 * @param {Object} batch — Objek batch dari examBatches
 * @returns {{ score: number, total: number, correctCount: number, totalQuestions: number,
 *             percentage: number, correctIds: string[], wrongIds: string[], passed: boolean }}
 */
export function calculateExamScore(userAnswers, batch) {
    let correctCount = 0;
    const correctIds = [];
    const wrongIds = [];
    const pointsPerQuestion = Math.floor(100 / batch.questions.length);

    for (const q of batch.questions) {
        const userAnswer = userAnswers.find(a => a.questionId === q.id);
        if (!userAnswer) {
            wrongIds.push(q.id);
            continue;
        }

        let isCorrect = false;
        if (q.type === 'mcq') {
            isCorrect = userAnswer.answer === q.correctIndex;
        } else if (q.type === 'fill') {
            const normalized = String(userAnswer.answer).toLowerCase().trim();
            isCorrect = q.correct.map(c => c.toLowerCase().trim()).includes(normalized);
        } else if (q.type === 'translate') {
            const normalize = (str) =>
                str.toLowerCase().trim()
                    .replace(/[.、。！？!?]+$/, '')
                    .replace(/\s+/g, ' ');
            const normalized = normalize(String(userAnswer.answer));
            isCorrect = q.acceptedAnswers.map(a => normalize(a)).includes(normalized);
        }

        if (isCorrect) {
            correctCount++;
            correctIds.push(q.id);
        } else {
            wrongIds.push(q.id);
        }
    }

    const score = correctCount * pointsPerQuestion;
    return {
        score,
        total: 100,
        correctCount,
        totalQuestions: batch.questions.length,
        percentage: score,
        correctIds,
        wrongIds,
        passed: score >= (batch.passing_score ?? 70)
    };
}
