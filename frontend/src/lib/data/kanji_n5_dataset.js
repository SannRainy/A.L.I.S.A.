/**
 * kanji_n5_dataset.js
 * 103 Kanji JLPT N5 — dikelompokkan menjadi 13 set (7-8 kanji per set)
 * Sumber: nodes_kanji.csv
 *
 * Pengelompokan berdasarkan tema/kategori semantik agar pembelajaran
 * lebih terstruktur dan bermakna (meaningful chunking).
 *
 * Field per kanji:
 *   id        : karakter kanji itu sendiri (digunakan sebagai node_id)
 *   onyomi    : bacaan on (katakana asal, disimpan romaji)
 *   kunyomi   : bacaan kun (romaji, format: verb-ending)
 *   arti      : terjemahan Indonesia
 *   strokes   : jumlah coretan
 *   frequency : urutan frekuensi dalam bahasa Jepang
 *   mnemonic  : bantuan mengingat (ditambahkan untuk pedagogis)
 */

export const kanjiSets = [
    // ══════════════════════════════════════════════════════
    // SET 1 — Angka (1–8 → termasuk set angka dasar)
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_1",
        title: "Angka Dasar",
        icon: "🔢",
        theme: "Bilangan yang paling sering dipakai sehari-hari.",
        kanji: [
            { id: "一", onyomi: "ichi", kunyomi: "hito-tsu", arti: "satu", strokes: 1,  frequency: 2,   mnemonic: "Satu garis = satu." },
            { id: "二", onyomi: "ni",   kunyomi: "futa-tsu", arti: "dua",  strokes: 2,  frequency: 20,  mnemonic: "Dua garis = dua." },
            { id: "三", onyomi: "san",  kunyomi: "mi-tsu",   arti: "tiga", strokes: 3,  frequency: 30,  mnemonic: "Tiga garis = tiga." },
            { id: "四", onyomi: "shi",  kunyomi: "yo-tsu",   arti: "empat", strokes: 5, frequency: 103, mnemonic: "Seperti kotak dengan jendela — 4 sudut." },
            { id: "五", onyomi: "go",   kunyomi: "itsu-tsu", arti: "lima", strokes: 4,  frequency: 75,  mnemonic: "Lima jari tangan." },
            { id: "六", onyomi: "roku", kunyomi: "mu-tsu",   arti: "enam", strokes: 4,  frequency: 173, mnemonic: "Atap dengan dua kaki = 6." },
            { id: "七", onyomi: "shichi", kunyomi: "nana-tsu", arti: "tujuh", strokes: 2, frequency: 199, mnemonic: "Seperti angka 7 terbalik." },
            { id: "八", onyomi: "hachi", kunyomi: "ya-tsu",  arti: "delapan", strokes: 2, frequency: 144, mnemonic: "Dua garis menyebar = 8." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 2 — Angka Lanjutan & Besaran
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_2",
        title: "Angka Lanjutan",
        icon: "💯",
        theme: "Angka besar dan satuan bilangan.",
        kanji: [
            { id: "九",  onyomi: "kyuu",  kunyomi: "kokono-tsu", arti: "sembilan",      strokes: 2, frequency: 137, mnemonic: "Seperti angka 9 di Jepang." },
            { id: "十",  onyomi: "juu",   kunyomi: "tou",        arti: "sepuluh",        strokes: 2, frequency: 27,  mnemonic: "Salib = 10 (silang jari)." },
            { id: "百",  onyomi: "hyaku", kunyomi: "-",          arti: "seratus",        strokes: 6, frequency: 279, mnemonic: "Satu di atas kotak = 100." },
            { id: "千",  onyomi: "sen",   kunyomi: "chi",        arti: "seribu",         strokes: 3, frequency: 307, mnemonic: "Seseorang dengan topi = 1000." },
            { id: "万",  onyomi: "man",   kunyomi: "-",          arti: "sepuluh ribu",   strokes: 3, frequency: 193, mnemonic: "Rumput yang banyak = banyak sekali." },
            { id: "半",  onyomi: "han",   kunyomi: "naka-ba",    arti: "separuh",        strokes: 5, frequency: 250, mnemonic: "Potong di tengah = setengah." },
            { id: "分",  onyomi: "fun/bun", kunyomi: "wa-keru", arti: "menit/membagi",  strokes: 4, frequency: 14,  mnemonic: "Pisau membelah sesuatu = membagi." },
            { id: "円",  onyomi: "en",    kunyomi: "maru",       arti: "yen/lingkaran",  strokes: 4, frequency: 208, mnemonic: "Lingkaran = koin yen." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 3 — Waktu
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_3",
        title: "Waktu",
        icon: "⏰",
        theme: "Ekspresi waktu: hari, bulan, tahun, jam.",
        kanji: [
            { id: "日",  onyomi: "nichi/jitsu", kunyomi: "hi/-ka",    arti: "hari/matahari", strokes: 4,  frequency: 3,   mnemonic: "Lingkaran dengan garis = matahari." },
            { id: "月",  onyomi: "getsu/gatsu", kunyomi: "tsuki",     arti: "bulan/bulan",   strokes: 4,  frequency: 49,  mnemonic: "Bulan sabit = bulan." },
            { id: "年",  onyomi: "nen",   kunyomi: "toshi",           arti: "tahun",          strokes: 6,  frequency: 5,   mnemonic: "Atas ke bawah = waktu berlalu = tahun." },
            { id: "時",  onyomi: "ji",    kunyomi: "toki",            arti: "waktu/jam",      strokes: 10, frequency: 24,  mnemonic: "Matahari di kuil = waktu." },
            { id: "週",  onyomi: "shuu",  kunyomi: "-",               arti: "minggu",         strokes: 11, frequency: 679, mnemonic: "Jalan melingkar = siklus minggu." },
            { id: "午",  onyomi: "go",    kunyomi: "-",               arti: "siang",          strokes: 4,  frequency: 873, mnemonic: "Tengah hari — garis tengah." },
            { id: "今",  onyomi: "kon",   kunyomi: "ima",             arti: "sekarang",       strokes: 4,  frequency: 71,  mnemonic: "Atap kecil = momen ini." },
            { id: "前",  onyomi: "zen",   kunyomi: "mae",             arti: "sebelum/depan",  strokes: 9,  frequency: 31,  mnemonic: "Kaki di depan = di depan." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 4 — Orang & Keluarga
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_4",
        title: "Orang & Keluarga",
        icon: "👨‍👩‍👧",
        theme: "Manusia dan anggota keluarga.",
        kanji: [
            { id: "人",  onyomi: "jin/nin", kunyomi: "hito", arti: "orang",       strokes: 2, frequency: 1,   mnemonic: "Dua kaki berdiri = orang." },
            { id: "男",  onyomi: "dan/nan", kunyomi: "otoko", arti: "laki-laki",  strokes: 7, frequency: 84,  mnemonic: "Sawah + kekuatan = laki-laki kerja keras." },
            { id: "女",  onyomi: "jo",  kunyomi: "onna",     arti: "perempuan",   strokes: 3, frequency: 29,  mnemonic: "Silang tangan duduk anggun = perempuan." },
            { id: "子",  onyomi: "shi/su", kunyomi: "ko",    arti: "anak",        strokes: 3, frequency: 9,   mnemonic: "Bayi dengan lengan terangkat." },
            { id: "父",  onyomi: "fu",  kunyomi: "chichi",   arti: "ayah",        strokes: 4, frequency: 227, mnemonic: "Tangan memegang sesuatu = ayah bekerja." },
            { id: "母",  onyomi: "bo",  kunyomi: "haha",     arti: "ibu",         strokes: 5, frequency: 238, mnemonic: "Wanita menyusui = ibu." },
            { id: "友",  onyomi: "yuu", kunyomi: "tomo",     arti: "teman",       strokes: 4, frequency: 458, mnemonic: "Tangan berjabat = teman." },
            { id: "名",  onyomi: "mei/myou", kunyomi: "na",  arti: "nama",        strokes: 6, frequency: 78,  mnemonic: "Malam + mulut = perkenalkan nama malam hari." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 5 — Alam & Arah Mata Angin
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_5",
        title: "Alam & Arah",
        icon: "🌏",
        theme: "Alam sekitar dan empat arah mata angin.",
        kanji: [
            { id: "山",  onyomi: "san",  kunyomi: "yama",   arti: "gunung",   strokes: 3, frequency: 60,  mnemonic: "Tiga puncak gunung." },
            { id: "川",  onyomi: "sen",  kunyomi: "kawa",   arti: "sungai",   strokes: 3, frequency: 109, mnemonic: "Tiga garis mengalir = sungai." },
            { id: "空",  onyomi: "kuu",  kunyomi: "sora",   arti: "langit",   strokes: 8, frequency: 253, mnemonic: "Gua kosong di bawah langit." },
            { id: "天",  onyomi: "ten",  kunyomi: "ama",    arti: "surga",    strokes: 4, frequency: 159, mnemonic: "Orang besar dengan garis di atas = langit." },
            { id: "東",  onyomi: "tou",  kunyomi: "higashi", arti: "timur",   strokes: 8, frequency: 110, mnemonic: "Matahari di balik pohon = timur (matahari terbit)." },
            { id: "西",  onyomi: "sei/sai", kunyomi: "nishi", arti: "barat",  strokes: 6, frequency: 291, mnemonic: "Burung di sarang = barat (pulang sore)." },
            { id: "南",  onyomi: "nan",  kunyomi: "minami", arti: "selatan",  strokes: 9, frequency: 378, mnemonic: "Tanaman tumbuh ke selatan (tropis = hangat)." },
            { id: "北",  onyomi: "hoku", kunyomi: "kita",   arti: "utara",    strokes: 5, frequency: 232, mnemonic: "Dua orang memunggungi = utara (dingin)." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 6 — Tubuh & Indera
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_6",
        title: "Tubuh & Indera",
        icon: "👁️",
        theme: "Bagian tubuh dan indera manusia.",
        kanji: [
            { id: "目",  onyomi: "moku",  kunyomi: "me",    arti: "mata",    strokes: 5,  frequency: 39,  mnemonic: "Kotak tegak dengan garis = mata." },
            { id: "耳",  onyomi: "ji",    kunyomi: "mimi",  arti: "telinga", strokes: 6,  frequency: 735, mnemonic: "Kotak dengan garis menyilang = bentuk telinga." },
            { id: "口",  onyomi: "kou",   kunyomi: "kuchi", arti: "mulut",   strokes: 3,  frequency: 108, mnemonic: "Kotak kecil terbuka = mulut." },
            { id: "手",  onyomi: "shu",   kunyomi: "te",    arti: "tangan",  strokes: 4,  frequency: 16,  mnemonic: "Jari-jari tangan = tangan." },
            { id: "足",  onyomi: "soku",  kunyomi: "ashi",  arti: "kaki",    strokes: 7,  frequency: 207, mnemonic: "Mulut + berjalan = kaki (alat berjalan)." },
            { id: "気",  onyomi: "ki/ke", kunyomi: "-",     arti: "semangat/rasa", strokes: 6, frequency: 25, mnemonic: "Beras mengepul = energi/semangat." },
            { id: "白",  onyomi: "haku",  kunyomi: "shiro-i", arti: "putih", strokes: 5, frequency: 196, mnemonic: "Matahari + satu tetes = cahaya putih." },
            { id: "立",  onyomi: "ritsu", kunyomi: "ta-tsu", arti: "berdiri", strokes: 5, frequency: 45, mnemonic: "Orang dengan kaki lebar = berdiri." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 7 — Tempat & Bangunan
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_7",
        title: "Tempat & Bangunan",
        icon: "🏫",
        theme: "Lokasi dan jenis tempat dalam kehidupan sehari-hari.",
        kanji: [
            { id: "国",  onyomi: "koku",  kunyomi: "kuni",  arti: "negara",     strokes: 8,  frequency: 11,  mnemonic: "Kotak besar dengan tanah di dalam = negara." },
            { id: "校",  onyomi: "kou",   kunyomi: "-",     arti: "sekolah",    strokes: 10, frequency: 316, mnemonic: "Pohon dihitung = sekolah (belajar menghitung)." },
            { id: "社",  onyomi: "sha",   kunyomi: "yashiro", arti: "perusahaan", strokes: 7, frequency: 57, mnemonic: "Tanah + tunjukkan = altar perusahaan." },
            { id: "店",  onyomi: "ten",   kunyomi: "mise",  arti: "toko",       strokes: 8,  frequency: 275, mnemonic: "Tempat berteduh untuk menjual = toko." },
            { id: "道",  onyomi: "dou",   kunyomi: "michi", arti: "jalan",      strokes: 12, frequency: 96,  mnemonic: "Kepala + berjalan = memimpin di jalan." },
            { id: "駅",  onyomi: "eki",   kunyomi: "-",     arti: "stasiun",    strokes: 14, frequency: 976, mnemonic: "Kuda berhenti = stasiun (dulu pakai kuda)." },
            { id: "外",  onyomi: "gai/ge", kunyomi: "soto", arti: "luar",       strokes: 5,  frequency: 97,  mnemonic: "Bulan di malam = di luar (pergi malam)." },
            { id: "中",  onyomi: "chuu",  kunyomi: "naka",  arti: "tengah",     strokes: 4,  frequency: 8,   mnemonic: "Panah menembus kotak = tengah." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 8 — Kata Kerja Inti (Aksi Sehari-hari)
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_8",
        title: "Aksi Sehari-hari",
        icon: "⚡",
        theme: "Kata kerja dasar yang sangat sering digunakan.",
        kanji: [
            { id: "行",  onyomi: "gyou/kou", kunyomi: "i-ku",    arti: "pergi",     strokes: 6,  frequency: 18,  mnemonic: "Jalan dengan kaki = pergi." },
            { id: "来",  onyomi: "rai",  kunyomi: "ku-ru",       arti: "datang",    strokes: 7,  frequency: 52,  mnemonic: "Gandum berjalan = datang membawa hasil." },
            { id: "見",  onyomi: "ken",  kunyomi: "mi-ru",       arti: "melihat",   strokes: 7,  frequency: 10,  mnemonic: "Mata di atas kaki = melihat ke sekitar." },
            { id: "言",  onyomi: "gen/gon", kunyomi: "i-u",      arti: "berkata",   strokes: 7,  frequency: 12,  mnemonic: "Mulut dengan suara = berkata." },
            { id: "聞",  onyomi: "bun/mon", kunyomi: "ki-ku",    arti: "mendengar", strokes: 14, frequency: 115, mnemonic: "Telinga di pintu gerbang = mendengar dari luar." },
            { id: "読",  onyomi: "doku",  kunyomi: "yo-mu",      arti: "membaca",   strokes: 14, frequency: 306, mnemonic: "Kata-kata dijual = membaca." },
            { id: "書",  onyomi: "sho",   kunyomi: "ka-ku",      arti: "menulis",   strokes: 10, frequency: 72,  mnemonic: "Tangan memegang kuas = menulis." },
            { id: "話",  onyomi: "wa",    kunyomi: "hana-su",    arti: "berbicara", strokes: 13, frequency: 54,  mnemonic: "Kata + lidah = berbicara." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 9 — Makanan & Aktivitas Fisik
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_9",
        title: "Makan & Minum",
        icon: "🍱",
        theme: "Makanan, minuman, dan aktivitas fisik dasar.",
        kanji: [
            { id: "食",  onyomi: "shoku", kunyomi: "ta-beru",  arti: "makan",     strokes: 9,  frequency: 142, mnemonic: "Sendok di dekat nasi = makan." },
            { id: "飲",  onyomi: "in",    kunyomi: "no-mu",    arti: "minum",     strokes: 12, frequency: 549, mnemonic: "Air masuk ke mulut = minum." },
            { id: "買",  onyomi: "bai",   kunyomi: "ka-u",     arti: "membeli",   strokes: 12, frequency: 339, mnemonic: "Mata mengincar barang = membeli." },
            { id: "出",  onyomi: "shutsu", kunyomi: "de-ru",   arti: "keluar",    strokes: 5,  frequency: 6,   mnemonic: "Gunung ganda = keluar dari dalam." },
            { id: "入",  onyomi: "nyuu",  kunyomi: "hai-ru",   arti: "masuk",     strokes: 2,  frequency: 34,  mnemonic: "V terbalik = masuk ke dalam." },
            { id: "休",  onyomi: "kyuu",  kunyomi: "yasu-mu",  arti: "istirahat", strokes: 6,  frequency: 811, mnemonic: "Orang bersandar di pohon = istirahat." },
            { id: "魚",  onyomi: "gyo",   kunyomi: "sakana",   arti: "ikan",      strokes: 11, frequency: 935, mnemonic: "Bentuk ikan dengan sirip dan ekor." },
            { id: "花",  onyomi: "ka",    kunyomi: "hana",     arti: "bunga",     strokes: 7,  frequency: 436, mnemonic: "Tanaman dengan perubahan indah = bunga." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 10 — Kata Sifat & Deskripsi
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_10",
        title: "Deskripsi & Sifat",
        icon: "🎨",
        theme: "Kata sifat dasar untuk mendeskripsikan benda dan situasi.",
        kanji: [
            { id: "大",  onyomi: "dai/tai", kunyomi: "oo-kii",  arti: "besar",    strokes: 3,  frequency: 4,   mnemonic: "Orang dengan tangan terentang lebar = besar." },
            { id: "小",  onyomi: "shou",   kunyomi: "chii-sai", arti: "kecil",    strokes: 3,  frequency: 35,  mnemonic: "Garis di tengah kecil = kecil." },
            { id: "高",  onyomi: "kou",    kunyomi: "taka-i",   arti: "tinggi/mahal", strokes: 10, frequency: 65, mnemonic: "Bangunan tinggi = tinggi/mahal." },
            { id: "長",  onyomi: "chou",   kunyomi: "naga-i",   arti: "panjang",  strokes: 8,  frequency: 40,  mnemonic: "Rambut panjang = panjang." },
            { id: "多",  onyomi: "ta",     kunyomi: "oo-i",     arti: "banyak",   strokes: 6,  frequency: 112, mnemonic: "Dua bulan = berlipat ganda = banyak." },
            { id: "少",  onyomi: "shou",   kunyomi: "suku-nai", arti: "sedikit",  strokes: 4,  frequency: 152, mnemonic: "Kecil terpotong lagi = sedikit." },
            { id: "古",  onyomi: "ko",     kunyomi: "furu-i",   arti: "kuno/lama", strokes: 5, frequency: 301, mnemonic: "Sepuluh mulut ceritakan = kuno (sudah lama)." },
            { id: "新",  onyomi: "shin",   kunyomi: "atara-shii", arti: "baru",   strokes: 13, frequency: 69,  mnemonic: "Pohon dipotong kapak = kayu baru." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 11 — Posisi & Arah
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_11",
        title: "Posisi & Arah",
        icon: "🧭",
        theme: "Arah dan posisi dalam ruang.",
        kanji: [
            { id: "上",  onyomi: "jou",   kunyomi: "ue",     arti: "atas",     strokes: 3,  frequency: 13,  mnemonic: "Garis di atas garis = di atas." },
            { id: "下",  onyomi: "ka/ge", kunyomi: "shita",  arti: "bawah",    strokes: 3,  frequency: 44,  mnemonic: "Garis di bawah garis = di bawah." },
            { id: "右",  onyomi: "u/yuu", kunyomi: "migi",   arti: "kanan",    strokes: 5,  frequency: 341, mnemonic: "Tangan di mulut = kanan (tangan dominan)." },
            { id: "左",  onyomi: "sa",    kunyomi: "hidari", arti: "kiri",     strokes: 5,  frequency: 384, mnemonic: "Tangan pegang alat = kiri (tangan bantu)." },
            { id: "後",  onyomi: "go/kou", kunyomi: "ato",   arti: "setelah/belakang", strokes: 9, frequency: 38, mnemonic: "Berjalan mundur perlahan = di belakang." },
            { id: "間",  onyomi: "kan",   kunyomi: "aida",   arti: "interval/di antara", strokes: 12, frequency: 21, mnemonic: "Matahari di antara pintu gerbang = jarak waktu." },
            { id: "先",  onyomi: "sen",   kunyomi: "saki",   arti: "ujung/duluan", strokes: 6, frequency: 104, mnemonic: "Kaki melangkah duluan = duluan/ujung." },
            { id: "土",  onyomi: "do/to", kunyomi: "tsuchi", arti: "tanah",    strokes: 3,  frequency: 284, mnemonic: "Garis di bawah dengan tiang = tanah." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 12 — Pendidikan & Bahasa
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_12",
        title: "Pendidikan & Bahasa",
        icon: "📚",
        theme: "Belajar, bahasa, dan ekspresi akademis.",
        kanji: [
            { id: "学",  onyomi: "gaku",  kunyomi: "mana-bu", arti: "belajar",  strokes: 8,  frequency: 47,  mnemonic: "Anak di bawah atap = belajar di sekolah." },
            { id: "語",  onyomi: "go",    kunyomi: "kata-ru",  arti: "bahasa",   strokes: 14, frequency: 129, mnemonic: "Kata-kata diperbanyak = bahasa." },
            { id: "本",  onyomi: "hon",   kunyomi: "moto",     arti: "buku/asal", strokes: 5, frequency: 7,   mnemonic: "Pohon dengan akar jelas = asal/buku." },
            { id: "何",  onyomi: "ka",    kunyomi: "nani/nan", arti: "apa",      strokes: 7,  frequency: 51,  mnemonic: "Orang dengan beban tanya = apa ini?" },
            { id: "生",  onyomi: "sei",   kunyomi: "i-kiru",   arti: "hidup/lahir", strokes: 5, frequency: 15, mnemonic: "Tanaman tumbuh dari tanah = hidup." },
            { id: "会",  onyomi: "kai",   kunyomi: "a-u",      arti: "bertemu",  strokes: 6,  frequency: 26,  mnemonic: "Berkumpul di bawah atap = bertemu." },
            { id: "電",  onyomi: "den",   kunyomi: "-",        arti: "listrik",  strokes: 13, frequency: 214, mnemonic: "Hujan dengan kilat = listrik." },
            { id: "火",  onyomi: "ka",    kunyomi: "hi",       arti: "api",      strokes: 4,  frequency: 465, mnemonic: "Nyala api dengan percikan = api." },
        ]
    },

    // ══════════════════════════════════════════════════════
    // SET 13 — Alam & Elemen
    // ══════════════════════════════════════════════════════
    {
        id: "kanji_set_13",
        title: "Alam & Elemen",
        icon: "🌿",
        theme: "Elemen alam dan kata terkait lingkungan.",
        kanji: [
            { id: "木",  onyomi: "moku/boku", kunyomi: "ki",    arti: "pohon",    strokes: 4,  frequency: 162, mnemonic: "Pohon dengan cabang dan akar = pohon." },
            { id: "水",  onyomi: "sui",   kunyomi: "mizu",      arti: "air",      strokes: 4,  frequency: 146, mnemonic: "Aliran air dengan percikan = air." },
            { id: "雨",  onyomi: "u",     kunyomi: "ame",       arti: "hujan",    strokes: 8,  frequency: 798, mnemonic: "Awan dengan tetes hujan = hujan." },
            { id: "金",  onyomi: "kin",   kunyomi: "kane",      arti: "emas/uang", strokes: 8, frequency: 79,  mnemonic: "Tanah dengan kilap = emas dari tanah." },
            { id: "安",  onyomi: "an",    kunyomi: "yasu-i",    arti: "murah/tenang", strokes: 6, frequency: 170, mnemonic: "Wanita di dalam rumah = tenang/aman." },
            { id: "車",  onyomi: "sha",   kunyomi: "kuruma",    arti: "mobil/kendaraan", strokes: 7, frequency: 234, mnemonic: "Roda dari atas = kendaraan." },
            { id: "毎",  onyomi: "mai",   kunyomi: "-",         arti: "setiap",   strokes: 6,  frequency: 669, mnemonic: "Ibu setiap hari mengurusi keluarga = setiap." },
        ]
    },
];

/** Total kanji di semua set */
export const totalKanjiCount = kanjiSets.reduce((sum, s) => sum + s.kanji.length, 0);

/** Ambil kanji flat (semua set jadi satu array) */
export const allKanji = kanjiSets.flatMap(s => s.kanji);

/** Ambil set berdasarkan ID */
export function getKanjiSet(setId) {
    return kanjiSets.find(s => s.id === setId) ?? null;
}
