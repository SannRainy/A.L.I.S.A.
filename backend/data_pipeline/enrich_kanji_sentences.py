"""
enrich_kanji_sentences.py
=========================
Fase 1 dari rencana implementasi RAG:
Menambahkan contoh kalimat dari dokumen JLPT N5 ke Knowledge Graph Neo4j,
sehingga setiap kanji memiliki minimal 1 contoh kalimat yang bisa di-retrieve.

Sumber data: dokumen/560045363-JLPT-N5-Grammar-Master-Ebok-by-JLPTsensei-com.txt
Target     : Neo4j (node Sentence + relasi CONTAINS_KANJI langsung)

Strategi: Direct Edge (lebih cepat & sederhana daripada 2-hop via Vocab)
  (Sentence)-[:CONTAINS_KANJI]->(Kanji)

Dijalankan SETELAH ingest_n5.py sudah berjalan (node Kanji sudah ada di Neo4j).

Cara pakai:
  cd backend
  python data_pipeline/enrich_kanji_sentences.py
"""

import os
import sys
import csv

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ---------------------------------------------------------------------------
# Dataset: kalimat-kalimat dari dokumen JLPT N5 Grammar Master
# Setiap entri: sentence_id, japanese_text, romaji, indonesian_translation, kanji_list
#
# CATATAN PENTING:
# - Kalimat dipilih berdasarkan kehadiran karakter kanji yang ADA di nodes_kanji.csv
# - Kalimat diambil verbatim dari dokumen sumber (tidak dimodifikasi / tidak dikarang)
# - Hanya kalimat yang jelas terjemahannya yang dimasukkan
# - kanji_list = daftar kanji N5 yang secara eksplisit muncul di kalimat tersebut
# ---------------------------------------------------------------------------

NEW_SENTENCES = [
    # ── 安 (murah/aman) ─────────────────────────────────────────────────────
    {
        "id": "EX001", "japanese": "この店は安くて美味しい。",
        "romaji": "kono mise wa yasukute oishii.",
        "indonesian": "Toko ini murah dan enak.",
        "kanji": ["安", "店", "美"]
    },
    {
        "id": "EX002", "japanese": "安い服を買いました。",
        "romaji": "yasui fuku o kaimashita.",
        "indonesian": "Saya membeli pakaian yang murah.",
        "kanji": ["安", "買"]
    },

    # ── 一 (satu) ────────────────────────────────────────────────────────────
    {
        "id": "EX003", "japanese": "一人だけ。",
        "romaji": "hitori dake.",
        "indonesian": "Hanya satu orang.",
        "kanji": ["一", "人"]
    },
    {
        "id": "EX004", "japanese": "出来るだけ新しい漢字を勉強したい。",
        "romaji": "dekiru dake atarashii kanji o benkyou shitai.",
        "indonesian": "Saya ingin belajar kanji baru sebanyak mungkin.",
        "kanji": ["一", "新", "学"]
    },

    # ── 飲 (minum) ───────────────────────────────────────────────────────────
    {
        "id": "EX005", "japanese": "２０歳未満の人はお酒を飲んじゃいけません。",
        "romaji": "hatachi miman no hito wa osake o nonja ikemasen.",
        "indonesian": "Orang di bawah 20 tahun tidak boleh minum alkohol.",
        "kanji": ["飲", "人"]
    },
    {
        "id": "EX006", "japanese": "コーヒーには、いつもさとうを入れないで飲みます。",
        "romaji": "koohii ni wa, itsumo satou o irenaide nomimasu.",
        "indonesian": "Saya selalu minum kopi tanpa gula.",
        "kanji": ["飲"]
    },

    # ── 右 (kanan) ───────────────────────────────────────────────────────────
    {
        "id": "EX007", "japanese": "右に曲がってください。",
        "romaji": "migi ni magatte kudasai.",
        "indonesian": "Tolong belok ke kanan.",
        "kanji": ["右"]
    },

    # ── 雨 (hujan) ───────────────────────────────────────────────────────────
    {
        "id": "EX008", "japanese": "明日はたぶん雨が降るだろう。空に雲がたくさんあるから。",
        "romaji": "ashita wa tabun ame ga furu darou. sora ni kumo ga takusan aru kara.",
        "indonesian": "Kemungkinan besar besok hujan. Karena ada banyak awan di langit.",
        "kanji": ["雨", "空"]
    },
    {
        "id": "EX009", "japanese": "明日は雨が降るでしょう。",
        "romaji": "ashita wa ame ga furu deshou.",
        "indonesian": "Sepertinya besok akan hujan.",
        "kanji": ["雨"]
    },
    {
        "id": "EX010", "japanese": "明日は雨かどうか分からない。",
        "romaji": "ashita wa ame ka dou ka wakaranai.",
        "indonesian": "Saya tidak tahu apakah besok akan hujan atau tidak.",
        "kanji": ["雨", "分"]
    },

    # ── 駅 (stasiun) ─────────────────────────────────────────────────────────
    {
        "id": "EX011", "japanese": "駅までどうやって行きますか。",
        "romaji": "eki made douyatte ikimasu ka.",
        "indonesian": "Bagaimana cara ke stasiun?",
        "kanji": ["駅", "行"]
    },
    {
        "id": "EX012", "japanese": "駅まで行きたいんですが、どう行ったらいいですか。",
        "romaji": "eki made ikitai ndesu ga, dou ittara ii desu ka.",
        "indonesian": "Saya ingin ke stasiun, bagaimana cara pergi ke sana?",
        "kanji": ["駅", "行"]
    },

    # ── 円 (yen) ──────────────────────────────────────────────────────────────
    {
        "id": "EX013", "japanese": "私の持っているお金はこれだけだ。",
        "romaji": "watashi no motteiru okane wa kore dake da.",
        "indonesian": "Inilah semua uang yang saya punya.",
        "kanji": ["円", "金"]
    },

    # ── 火 (api) ──────────────────────────────────────────────────────────────
    {
        "id": "EX014", "japanese": "火曜日に来てください。",
        "romaji": "kayoubi ni kite kudasai.",
        "indonesian": "Tolong datang pada hari Selasa.",
        "kanji": ["火"]
    },

    # ── 花 (bunga) ────────────────────────────────────────────────────────────
    {
        "id": "EX015", "japanese": "花が好きです。",
        "romaji": "hana ga suki desu.",
        "indonesian": "Saya suka bunga.",
        "kanji": ["花"]
    },

    # ── 下 (bawah) ────────────────────────────────────────────────────────────
    {
        "id": "EX016", "japanese": "カバンがテーブルの下にあります。",
        "romaji": "kaban ga teeburu no shita ni arimasu.",
        "indonesian": "Tas ada di bawah meja.",
        "kanji": ["下"]
    },

    # ── 何 (apa) ──────────────────────────────────────────────────────────────
    {
        "id": "EX017", "japanese": "今日はやることがたくさんある。",
        "romaji": "kyou wa, yaru koto ga takusan aru.",
        "indonesian": "Hari ini ada banyak hal yang harus dilakukan.",
        "kanji": ["何", "今", "日"]
    },

    # ── 会 (bertemu) ──────────────────────────────────────────────────────────
    {
        "id": "EX018", "japanese": "駅で会いましょう！",
        "romaji": "eki de ai mashou!",
        "indonesian": "Ayo ketemu di stasiun!",
        "kanji": ["会", "駅"]
    },
    {
        "id": "EX019", "japanese": "今日一緒に食べませんか？",
        "romaji": "kyou isshoni tabemasen ka?",
        "indonesian": "Mau makan bareng hari ini?",
        "kanji": ["会", "今", "日", "食"]
    },

    # ── 外 (diluar) ───────────────────────────────────────────────────────────
    {
        "id": "EX020", "japanese": "外は暑いけれど、家の中は暖かいです。",
        "romaji": "soto wa atsui keredo, ie no naka wa atatakai desu.",
        "indonesian": "Di luar panas, tapi di dalam rumah hangat.",
        "kanji": ["外", "中"]
    },

    # ── 学 (belajar) ─────────────────────────────────────────────────────────
    {
        "id": "EX021", "japanese": "学校で日本語を勉強する。",
        "romaji": "gakkou de nihongo wo benkyou suru.",
        "indonesian": "Saya belajar bahasa Jepang di sekolah.",
        "kanji": ["学", "校", "語", "言"]
    },
    {
        "id": "EX022", "japanese": "どこで日本語を学びましたか？",
        "romaji": "doko de nihongo wo manabimashita ka?",
        "indonesian": "Di mana Anda belajar bahasa Jepang?",
        "kanji": ["学", "語", "言"]
    },
    {
        "id": "EX023", "japanese": "日本語を勉強しています。",
        "romaji": "nihongo o benkyou shiteimasu.",
        "indonesian": "Saya sedang belajar bahasa Jepang.",
        "kanji": ["学", "語", "言"]
    },
    {
        "id": "EX024", "japanese": "一緒に日本語を勉強しましょう。",
        "romaji": "isshoni nihongo o benkyou shimashou.",
        "indonesian": "Ayo belajar bahasa Jepang bersama-sama!",
        "kanji": ["学", "語", "言"]
    },

    # ── 間 (waktu/interval) ──────────────────────────────────────────────────
    {
        "id": "EX025", "japanese": "少し時間をください。",
        "romaji": "sukoshi jikan o kudasai.",
        "indonesian": "Saya butuh sedikit waktu.",
        "kanji": ["間", "時", "少"]
    },

    # ── 気 (mood/spirit) ─────────────────────────────────────────────────────
    {
        "id": "EX026", "japanese": "道を渡るとき、車に気をつけてください。",
        "romaji": "michi o wataru toki, kuruma ni ki o tsukete kudasai.",
        "indonesian": "Ketika menyeberang jalan, hati-hati dengan mobil.",
        "kanji": ["気", "道", "車"]
    },
    {
        "id": "EX027", "japanese": "彼はいつも元気ですね。",
        "romaji": "kare wa itsumo genki desu ne.",
        "indonesian": "Dia selalu bersemangat, ya.",
        "kanji": ["気"]
    },

    # ── 九 (sembilan) ────────────────────────────────────────────────────────
    {
        "id": "EX028", "japanese": "九時に起きます。",
        "romaji": "kuji ni okimasu.",
        "indonesian": "Saya bangun jam sembilan.",
        "kanji": ["九", "時"]
    },

    # ── 休 (istirahat) ───────────────────────────────────────────────────────
    {
        "id": "EX029", "japanese": "疲れたら、早く寝たほうがいい。",
        "romaji": "tsukaretara, hayaku neta hou ga ii.",
        "indonesian": "Jika lelah, lebih baik segera tidur.",
        "kanji": ["休"]
    },
    {
        "id": "EX030", "japanese": "明日は休みだから、学校に行かなくてもいい。",
        "romaji": "ashita wa yasumi dakara, gakkou ni ikanaku temo ii.",
        "indonesian": "Besok libur, jadi tidak perlu pergi ke sekolah.",
        "kanji": ["休", "学", "校", "行"]
    },

    # ── 魚 (ikan) ─────────────────────────────────────────────────────────────
    {
        "id": "EX031", "japanese": "私は魚が好すきです。でも肉も好きです。",
        "romaji": "watashi wa sakana ga suki desu. demo niku mo suki desu.",
        "indonesian": "Saya suka ikan. Tapi juga suka daging.",
        "kanji": ["魚", "人"]
    },

    # ── 金 (uang/emas) ────────────────────────────────────────────────────────
    {
        "id": "EX032", "japanese": "金はないけど夢はある。",
        "romaji": "kane wa nai kedo yume wa aru.",
        "indonesian": "Tidak punya uang, tapi punya mimpi.",
        "kanji": ["金"]
    },
    {
        "id": "EX033", "japanese": "このカメラを買いたいですがお金がない。",
        "romaji": "kono kamera o kaitai desu ga okane ga nai.",
        "indonesian": "Saya ingin beli kamera ini tapi tidak punya uang.",
        "kanji": ["金", "買"]
    },
    {
        "id": "EX034", "japanese": "私はできるだけ金を借りないようにしている。",
        "romaji": "watashi wa dekiru dake kane o karinai youni shiteiru.",
        "indonesian": "Saya berusaha meminjam uang sesedikit mungkin.",
        "kanji": ["金", "人"]
    },

    # ── 空 (langit/kosong) ───────────────────────────────────────────────────
    {
        "id": "EX035", "japanese": "空港まで来なくてもいいよ。",
        "romaji": "kuukou made konaku temo ii yo.",
        "indonesian": "Tidak perlu datang sampai ke bandara.",
        "kanji": ["空", "来"]
    },

    # ── 月 (bulan) ────────────────────────────────────────────────────────────
    {
        "id": "EX036", "japanese": "先月、日本語の試験を受けました。",
        "romaji": "sengetsu, nihongo no shiken o ukemashita.",
        "indonesian": "Bulan lalu saya ikut ujian bahasa Jepang.",
        "kanji": ["月", "先", "語", "言"]
    },
    {
        "id": "EX037", "japanese": "1月と2月はとても寒いです。",
        "romaji": "ichigatsu to nigatsu wa totemo samui desu.",
        "indonesian": "Bulan Januari dan Februari sangat dingin.",
        "kanji": ["月", "一", "二"]
    },

    # ── 見 (melihat) ─────────────────────────────────────────────────────────
    {
        "id": "EX038", "japanese": "寝る前にスマホを見ちゃダメよ。",
        "romaji": "neru mae ni sumaho o micha dame yo.",
        "indonesian": "Jangan lihat smartphone sebelum tidur.",
        "kanji": ["見", "前"]
    },
    {
        "id": "EX039", "japanese": "ちょっと見ているだけです。",
        "romaji": "chotto mitteiru dake desu.",
        "indonesian": "Saya hanya melihat-lihat.",
        "kanji": ["見"]
    },
    {
        "id": "EX040", "japanese": "うちで映画を見ませんか。",
        "romaji": "uchi de eiga o mimasen ka.",
        "indonesian": "Ingin nonton film di rumah saya?",
        "kanji": ["見"]
    },

    # ── 言 / 語 (berkata/bahasa) ─────────────────────────────────────────────
    {
        "id": "EX041", "japanese": "日本語を話します。",
        "romaji": "nihongo o hanashimasu.",
        "indonesian": "Saya bicara bahasa Jepang.",
        "kanji": ["言", "語", "話"]
    },
    {
        "id": "EX042", "japanese": "子どもの前に悪いことばを言っちゃいけません。",
        "romaji": "kodomo no mae ni warui kotoba o iccha ikemasen.",
        "indonesian": "Tidak boleh mengatakan kata-kata buruk di depan anak-anak.",
        "kanji": ["言", "前", "子"]
    },

    # ── 古 (kuno/lama) ────────────────────────────────────────────────────────
    {
        "id": "EX043", "japanese": "この古い車は私のです。",
        "romaji": "kono furui kuruma wa watashi no desu.",
        "indonesian": "Mobil tua ini adalah milik saya.",
        "kanji": ["古", "車", "人"]
    },

    # ── 五 (lima) ─────────────────────────────────────────────────────────────
    {
        "id": "EX044", "japanese": "五時に起きます。",
        "romaji": "goji ni okimasu.",
        "indonesian": "Saya bangun jam lima.",
        "kanji": ["五", "時"]
    },

    # ── 後 (setelah/belakang) ────────────────────────────────────────────────
    {
        "id": "EX045", "japanese": "ご飯を食べてから散歩しました。",
        "romaji": "gohan o tabete kara sanpo shimashita.",
        "indonesian": "Setelah makan, saya jalan-jalan.",
        "kanji": ["後", "食"]
    },
    {
        "id": "EX046", "japanese": "学校の後で図書館に行きました。",
        "romaji": "gakkou no ato de toshokan ni ikimashita.",
        "indonesian": "Setelah sekolah, saya pergi ke perpustakaan.",
        "kanji": ["後", "学", "校", "行"]
    },

    # ── 午 (siang) ───────────────────────────────────────────────────────────
    {
        "id": "EX047", "japanese": "午後から雨が降るでしょう。",
        "romaji": "gogo kara ame ga furu deshou.",
        "indonesian": "Sepertinya akan hujan dari siang hari.",
        "kanji": ["午", "雨"]
    },

    # ── 校 (sekolah) ─────────────────────────────────────────────────────────
    {
        "id": "EX048", "japanese": "リサさんは毎日どうやって学校へ来ますか。",
        "romaji": "risa san wa mainichi douyatte gakkou e kimasu ka.",
        "indonesian": "Lisa, bagaimana kamu pergi ke sekolah setiap hari?",
        "kanji": ["校", "学", "来", "毎", "日"]
    },
    {
        "id": "EX049", "japanese": "今朝学校に行きました。でも、休みでした。",
        "romaji": "kesa gakkou ni ikimashita. demo, yasumi deshita.",
        "indonesian": "Tadi pagi saya pergi ke sekolah. Tapi ternyata libur.",
        "kanji": ["校", "学", "行", "休"]
    },

    # ── 口 (mulut) ───────────────────────────────────────────────────────────
    {
        "id": "EX050", "japanese": "口の中に入れないでください。",
        "romaji": "kuchi no naka ni irenaide kudasai.",
        "indonesian": "Jangan masukkan ke dalam mulut.",
        "kanji": ["口", "中", "入"]
    },

    # ── 行 (pergi) ───────────────────────────────────────────────────────────
    {
        "id": "EX051", "japanese": "車で行く。",
        "romaji": "kuruma de iku.",
        "indonesian": "Pergi dengan mobil.",
        "kanji": ["行", "車"]
    },
    {
        "id": "EX052", "japanese": "本当にすぐ行かなくてはいけない。",
        "romaji": "hontouni sugu ika nakute wa ikenai.",
        "indonesian": "Saya harus benar-benar pergi sekarang.",
        "kanji": ["行", "本"]
    },

    # ── 高 (tinggi/mahal) ────────────────────────────────────────────────────
    {
        "id": "EX053", "japanese": "このカメラは高かったけれど、すぐ壊れてしまいました。",
        "romaji": "kono kamera wa takaaktta keredo, sugu kowarete shimaimashita.",
        "indonesian": "Kamera ini mahal, tapi langsung rusak.",
        "kanji": ["高"]
    },
    {
        "id": "EX054", "japanese": "スポーツは上手じゃないけど、好きです。",
        "romaji": "supootsu wa jouzu janai kedo, suki desu.",
        "indonesian": "Saya tidak mahir olahraga, tapi suka.",
        "kanji": ["高", "上"]
    },

    # ── 国 (negara) ───────────────────────────────────────────────────────────
    {
        "id": "EX055", "japanese": "ベトナムはどんな国ですか。",
        "romaji": "betonamu wa donna kuni desu ka.",
        "indonesian": "Vietnam itu negara seperti apa?",
        "kanji": ["国"]
    },

    # ── 今 (sekarang) ────────────────────────────────────────────────────────
    {
        "id": "EX056", "japanese": "今日はラーメンを食べるつもりだ。",
        "romaji": "kyou wa raamen o taberu tsumori da.",
        "indonesian": "Hari ini saya berencana makan ramen.",
        "kanji": ["今", "日", "食"]
    },

    # ── 左 (kiri) ────────────────────────────────────────────────────────────
    {
        "id": "EX057", "japanese": "左に曲がってください。",
        "romaji": "hidari ni magatte kudasai.",
        "indonesian": "Tolong belok ke kiri.",
        "kanji": ["左"]
    },

    # ── 三 (tiga) ────────────────────────────────────────────────────────────
    {
        "id": "EX058", "japanese": "三時間かかります。",
        "romaji": "sanjikan kakarimasu.",
        "indonesian": "Dibutuhkan tiga jam.",
        "kanji": ["三", "時", "間"]
    },

    # ── 山 (gunung) ──────────────────────────────────────────────────────────
    {
        "id": "EX059", "japanese": "山が高いです。",
        "romaji": "yama ga takai desu.",
        "indonesian": "Gunungnya tinggi.",
        "kanji": ["山", "高"]
    },

    # ── 四 (empat) ───────────────────────────────────────────────────────────
    {
        "id": "EX060", "japanese": "四時に来てください。",
        "romaji": "yoji ni kite kudasai.",
        "indonesian": "Tolong datang jam empat.",
        "kanji": ["四", "時", "来"]
    },

    # ── 子 (anak) ────────────────────────────────────────────────────────────
    {
        "id": "EX061", "japanese": "子どものとき、甘いものが好きでした。",
        "romaji": "kodomo no toki, amai mono ga suki deshita.",
        "indonesian": "Waktu kecil, saya suka makanan manis.",
        "kanji": ["子"]
    },

    # ── 耳 (telinga) ─────────────────────────────────────────────────────────
    {
        "id": "EX062", "japanese": "耳が痛いです。",
        "romaji": "mimi ga itai desu.",
        "indonesian": "Telinga saya sakit.",
        "kanji": ["耳"]
    },

    # ── 時 (waktu) ───────────────────────────────────────────────────────────
    {
        "id": "EX063", "japanese": "分からないときは、早く先生に聞きましょうね。",
        "romaji": "wakaranai toki wa, hayaku sensei ni kikimashou ne.",
        "indonesian": "Ketika tidak mengerti, segera tanya guru, ya!",
        "kanji": ["時", "先", "生", "聞"]
    },

    # ── 七 (tujuh) ───────────────────────────────────────────────────────────
    {
        "id": "EX064", "japanese": "七時に起きます。",
        "romaji": "shichiji ni okimasu.",
        "indonesian": "Saya bangun jam tujuh.",
        "kanji": ["七", "時"]
    },

    # ── 車 (mobil) ───────────────────────────────────────────────────────────
    {
        "id": "EX065", "japanese": "電車はバスより速いです。",
        "romaji": "densha wa basu yori hayai desu.",
        "indonesian": "Kereta lebih cepat daripada bus.",
        "kanji": ["車", "電"]
    },
    {
        "id": "EX066", "japanese": "今日は電車で来ました。",
        "romaji": "kyou wa densha de kimashita.",
        "indonesian": "Hari ini saya datang dengan kereta.",
        "kanji": ["車", "電", "今", "日", "来"]
    },

    # ── 社 (perusahaan) ──────────────────────────────────────────────────────
    {
        "id": "EX067", "japanese": "会社で働いています。",
        "romaji": "kaisha de hataraite imasu.",
        "indonesian": "Saya bekerja di perusahaan.",
        "kanji": ["社", "会", "行"]
    },

    # ── 手 (tangan) ──────────────────────────────────────────────────────────
    {
        "id": "EX068", "japanese": "トイレを使ってから、手を洗わないといけません。",
        "romaji": "toire o tsukatte kara, te o arawanai to ikemasen.",
        "indonesian": "Harus mencuci tangan setelah menggunakan toilet.",
        "kanji": ["手"]
    },

    # ── 週 (minggu) ──────────────────────────────────────────────────────────
    {
        "id": "EX069", "japanese": "今週の新しい単語をまだ覚えていません。",
        "romaji": "konshuu no atarashii tango o mada oboete imasen.",
        "indonesian": "Saya belum menghafal kosakata baru minggu ini.",
        "kanji": ["週", "新"]
    },

    # ── 十 (sepuluh) ─────────────────────────────────────────────────────────
    {
        "id": "EX070", "japanese": "いつも夜10時に寝ます。",
        "romaji": "itsumo yoru juuji ni nemasu.",
        "indonesian": "Saya selalu tidur pukul 10 malam.",
        "kanji": ["十", "時"]
    },

    # ── 出 (keluar) ───────────────────────────────────────────────────────────
    {
        "id": "EX071", "japanese": "彼女はカサを持たないで出てしまった。",
        "romaji": "kanojo wa kasa o mota naide deteshimatta.",
        "indonesian": "Dia pergi tanpa membawa payung.",
        "kanji": ["出"]
    },
    {
        "id": "EX072", "japanese": "この問題は、明日の試験に出るでしょうか。",
        "romaji": "kono mondai wa, ashita no shiken ni deru deshou ka.",
        "indonesian": "Apakah soal ini akan keluar di ujian besok?",
        "kanji": ["出", "日"]
    },

    # ── 書 (menulis) ─────────────────────────────────────────────────────────
    {
        "id": "EX073", "japanese": "この字はどうして書くんですか？",
        "romaji": "kono ji wa doushite kaku n desuka?",
        "indonesian": "Bagaimana cara menulis huruf ini?",
        "kanji": ["書"]
    },
    {
        "id": "EX074", "japanese": "漫画を読むのが好きだ。",
        "romaji": "manga o yomu no ga suki da.",
        "indonesian": "Saya suka membaca manga.",
        "kanji": ["書", "読"]
    },

    # ── 女 (perempuan) ───────────────────────────────────────────────────────
    {
        "id": "EX075", "japanese": "その女の子はただ泣くだけだった。",
        "romaji": "sono onna no ko wa tada naku dake datta.",
        "indonesian": "Anak perempuan itu hanya menangis saja.",
        "kanji": ["女", "子"]
    },

    # ── 小 (kecil) ───────────────────────────────────────────────────────────
    {
        "id": "EX076", "japanese": "小さい犬が好きです。",
        "romaji": "chiisai inu ga suki desu.",
        "indonesian": "Saya suka anjing kecil.",
        "kanji": ["小"]
    },

    # ── 少 (sedikit) ─────────────────────────────────────────────────────────
    {
        "id": "EX077", "japanese": "もっと少し時間が欲しいです。",
        "romaji": "motto sukoshi jikan ga hoshii desu.",
        "indonesian": "Saya ingin sedikit lebih banyak waktu.",
        "kanji": ["少", "時", "間"]
    },

    # ── 上 (atas) ────────────────────────────────────────────────────────────
    {
        "id": "EX078", "japanese": "カバンがテーブルの上にあります。",
        "romaji": "kaban ga teeburu no ue ni arimasu.",
        "indonesian": "Tas ada di atas meja.",
        "kanji": ["上"]
    },
    {
        "id": "EX079", "japanese": "あなたは教えるのが上手です。",
        "romaji": "anata wa oshieru no ga jouzu desu.",
        "indonesian": "Kamu pandai mengajar.",
        "kanji": ["上"]
    },

    # ── 食 (makan) ───────────────────────────────────────────────────────────
    {
        "id": "EX080", "japanese": "野菜を食べるまでデザートを食べちゃいけないよ。",
        "romaji": "yasai o taberu made dezaato o tabecha ikenai yo.",
        "indonesian": "Tidak boleh makan dessert sebelum habis makannya sayuran.",
        "kanji": ["食"]
    },
    {
        "id": "EX081", "japanese": "どんな食べ物が好きですか。",
        "romaji": "donna tabemono ga suki desu ka.",
        "indonesian": "Makanan apa yang kamu suka?",
        "kanji": ["食"]
    },

    # ── 新 (baru) ────────────────────────────────────────────────────────────
    {
        "id": "EX082", "japanese": "新しい先生はどんな人ですか。",
        "romaji": "atarashii sensei wa donna hito desu ka.",
        "indonesian": "Seperti apa guru baru itu?",
        "kanji": ["新", "先", "生", "人"]
    },

    # ── 人 (orang) ───────────────────────────────────────────────────────────
    {
        "id": "EX083", "japanese": "たくさんの人がいるなあ。",
        "romaji": "takusan no hito ga iru naa.",
        "indonesian": "Wah, banyak orang di sini!",
        "kanji": ["人", "多"]
    },
    {
        "id": "EX084", "japanese": "アメリカ人は日本人より背が高いです。",
        "romaji": "amerika jin wa nihon jin yori se ga takai.",
        "indonesian": "Orang Amerika lebih tinggi dari orang Jepang.",
        "kanji": ["人", "本", "高"]
    },

    # ── 水 (air) ─────────────────────────────────────────────────────────────
    {
        "id": "EX085", "japanese": "すみません、お水をください。",
        "romaji": "sumimasen, omizu o kudasai.",
        "indonesian": "Permisi, tolong beri saya air.",
        "kanji": ["水"]
    },
    {
        "id": "EX086", "japanese": "水曜日は休みです。",
        "romaji": "suiyoubi wa yasumi desu.",
        "indonesian": "Hari Rabu libur.",
        "kanji": ["水", "休", "日"]
    },

    # ── 生 (hidup/lahir) ─────────────────────────────────────────────────────
    {
        "id": "EX087", "japanese": "学生は毎日学校に来ます。",
        "romaji": "gakusei wa mainichi gakkou ni kimasu.",
        "indonesian": "Pelajar datang ke sekolah setiap hari.",
        "kanji": ["生", "学", "校", "来", "毎", "日"]
    },

    # ── 西 (barat) ───────────────────────────────────────────────────────────
    {
        "id": "EX088", "japanese": "駅の西口で待っています。",
        "romaji": "eki no nishiguchi de matte imasu.",
        "indonesian": "Saya menunggu di pintu barat stasiun.",
        "kanji": ["西", "駅", "口"]
    },

    # ── 川 (sungai) ──────────────────────────────────────────────────────────
    {
        "id": "EX089", "japanese": "川のそばに家があります。",
        "romaji": "kawa no soba ni ie ga arimasu.",
        "indonesian": "Ada rumah di dekat sungai.",
        "kanji": ["川"]
    },

    # ── 千 (seribu) ──────────────────────────────────────────────────────────
    {
        "id": "EX090", "japanese": "千円でおつりをください。",
        "romaji": "sen en de otsuri o kudasai.",
        "indonesian": "Tolong kembalikan uang dari seribu yen.",
        "kanji": ["千", "円"]
    },

    # ── 先 (tadi/ujung) ──────────────────────────────────────────────────────
    {
        "id": "EX091", "japanese": "先生はまもなく来るでしょう。",
        "romaji": "sensei wa mamonaku kuru deshou.",
        "indonesian": "Guru sepertinya akan segera datang.",
        "kanji": ["先", "生", "来"]
    },

    # ── 前 (sebelum/depan) ───────────────────────────────────────────────────
    {
        "id": "EX092", "japanese": "旅行の前に切符を買っておきます。",
        "romaji": "ryokou no mae ni kippu o katte okimasu.",
        "indonesian": "Saya akan membeli tiket sebelum perjalanan.",
        "kanji": ["前", "買"]
    },
    {
        "id": "EX093", "japanese": "コンビニの前にじてんしゃがたくさんあります。",
        "romaji": "konbini no mae ni jitensha ga takusan arimasu.",
        "indonesian": "Di depan minimarket banyak sepeda.",
        "kanji": ["前"]
    },

    # ── 足 (kaki) ─────────────────────────────────────────────────────────────
    {
        "id": "EX094", "japanese": "足が痛いので、歩けません。",
        "romaji": "ashi ga itai node, arukemasen.",
        "indonesian": "Kaki sakit, jadi tidak bisa berjalan.",
        "kanji": ["足"]
    },

    # ── 多 (banyak) ───────────────────────────────────────────────────────────
    {
        "id": "EX095", "japanese": "今日は、やることがたくさんある。",
        "romaji": "kyou wa, yaru koto ga takusan aru.",
        "indonesian": "Hari ini banyak hal yang harus dilakukan.",
        "kanji": ["多", "今", "日"]
    },

    # ── 大 (besar) ────────────────────────────────────────────────────────────
    {
        "id": "EX096", "japanese": "大きくなっているね！",
        "romaji": "ookiku natteiru ne!",
        "indonesian": "Kamu semakin besar!",
        "kanji": ["大"]
    },
    {
        "id": "EX097", "japanese": "頑張れば、いい大学に行けるでしょう。",
        "romaji": "ganbareba, ii daigaku ni ikeru deshou.",
        "indonesian": "Jika berusaha keras, kamu bisa masuk universitas yang bagus.",
        "kanji": ["大", "学", "行"]
    },

    # ── 男 (laki-laki) ───────────────────────────────────────────────────────
    {
        "id": "EX098", "japanese": "彼は金はあるが、バカな男だ。",
        "romaji": "kare wa kane wa aru ga, baka na otoko da.",
        "indonesian": "Dia punya uang, tapi orang bodoh.",
        "kanji": ["男", "金"]
    },

    # ── 中 (tengah/dalam) ────────────────────────────────────────────────────
    {
        "id": "EX099", "japanese": "日本の食べ物の中でラーメンが一番好きだ。",
        "romaji": "nihon no tabemono no naka de raamen ga ichiban suki da.",
        "indonesian": "Dari semua makanan Jepang, ramen adalah yang paling saya suka.",
        "kanji": ["中", "本", "食", "一"]
    },
    {
        "id": "EX100", "japanese": "クラスの中でジェシカが一番頭いい。",
        "romaji": "kurasu no naka de jeshika ga ichiban atama ii.",
        "indonesian": "Di kelas, Jessica yang paling cerdas.",
        "kanji": ["中", "一"]
    },

    # ── 長 (panjang) ─────────────────────────────────────────────────────────
    {
        "id": "EX101", "japanese": "この道は長いです。",
        "romaji": "kono michi wa nagai desu.",
        "indonesian": "Jalan ini panjang.",
        "kanji": ["長", "道"]
    },

    # ── 天 (surga/langit) ────────────────────────────────────────────────────
    {
        "id": "EX102", "japanese": "今日の天気はいいですね。",
        "romaji": "kyou no tenki wa ii desu ne.",
        "indonesian": "Cuaca hari ini bagus, ya.",
        "kanji": ["天", "今", "日"]
    },
    {
        "id": "EX103", "japanese": "天気はどうですか。",
        "romaji": "tenki wa dou desu ka.",
        "indonesian": "Bagaimana cuacanya?",
        "kanji": ["天"]
    },

    # ── 店 (toko) ────────────────────────────────────────────────────────────
    {
        "id": "EX104", "japanese": "そのシャツどこで買いました？",
        "romaji": "sono shatsu doko de kaimashita?",
        "indonesian": "Di mana kamu beli baju itu?",
        "kanji": ["店", "買"]
    },

    # ── 電 (listrik) ─────────────────────────────────────────────────────────
    {
        "id": "EX105", "japanese": "昨日は疲れていて、電気を消さないで寝てしまった。",
        "romaji": "kinou wa tsukarete ite, denki o kesanaide nete shimatta.",
        "indonesian": "Kemarin terlalu lelah, tidur tanpa matikan lampu.",
        "kanji": ["電"]
    },
    {
        "id": "EX106", "japanese": "ここで電話しないでください。",
        "romaji": "koko de denwa shinai de kudasai.",
        "indonesian": "Tolong jangan gunakan telepon di sini.",
        "kanji": ["電", "話"]
    },

    # ── 土 (tanah) ───────────────────────────────────────────────────────────
    {
        "id": "EX107", "japanese": "土曜日に会いましょう。",
        "romaji": "doyoubi ni aimashou.",
        "indonesian": "Ayo bertemu pada hari Sabtu.",
        "kanji": ["土", "会"]
    },

    # ── 東 (timur) ───────────────────────────────────────────────────────────
    {
        "id": "EX108", "japanese": "東京に行きたいです。",
        "romaji": "toukyou ni ikitai desu.",
        "indonesian": "Saya ingin pergi ke Tokyo.",
        "kanji": ["東", "行"]
    },

    # ── 道 (jalan) ───────────────────────────────────────────────────────────
    {
        "id": "EX109", "japanese": "道を渡るとき、車に気をつけてください。",
        "romaji": "michi o wataru toki, kuruma ni ki o tsukete kudasai.",
        "indonesian": "Ketika menyeberang jalan, hati-hati dengan mobil.",
        "kanji": ["道", "車", "気"]
    },

    # ── 読 (membaca) ─────────────────────────────────────────────────────────
    {
        "id": "EX110", "japanese": "私は日本語を話すことはできますが、読むことはできません。",
        "romaji": "watashi wa nihongo o hanasu koto wa dekimasu ga, yomu koto wa dekimasen.",
        "indonesian": "Saya bisa berbicara bahasa Jepang, tapi tidak bisa membaca.",
        "kanji": ["読", "話", "語", "言", "人"]
    },
    {
        "id": "EX111", "japanese": "本は映画より面白いです。",
        "romaji": "hon wa eiga yori omoshiroi desu.",
        "indonesian": "Buku lebih menarik daripada film.",
        "kanji": ["読", "本"]
    },

    # ── 南 (selatan) ─────────────────────────────────────────────────────────
    {
        "id": "EX112", "japanese": "駅の南口で待ちましょう。",
        "romaji": "eki no minamiguchi de machimashoo.",
        "indonesian": "Mari menunggu di pintu selatan stasiun.",
        "kanji": ["南", "駅", "口"]
    },

    # ── 二 (dua) ──────────────────────────────────────────────────────────────
    {
        "id": "EX113", "japanese": "コーヒーを二つください。",
        "romaji": "koohii o futatsu kudasai.",
        "indonesian": "Tolong berikan dua cangkir kopi.",
        "kanji": ["二"]
    },

    # ── 日 (hari/matahari) ───────────────────────────────────────────────────
    {
        "id": "EX114", "japanese": "日曜日は買い物したり、映画を見たりした。",
        "romaji": "nichiyoubi wa kaimono shitari, eiga o mitari shita.",
        "indonesian": "Hari Minggu saya belanja dan nonton film.",
        "kanji": ["日", "買", "見"]
    },

    # ── 入 (masuk) ───────────────────────────────────────────────────────────
    {
        "id": "EX115", "japanese": "ここはきけんなので、入っちゃダメだよ。",
        "romaji": "koko wa kiken nano de, haiccha dame da yo.",
        "indonesian": "Area ini berbahaya, jadi tidak boleh masuk.",
        "kanji": ["入"]
    },

    # ── 年 (tahun) ───────────────────────────────────────────────────────────
    {
        "id": "EX116", "japanese": "今年は忙しいです。",
        "romaji": "kotoshi wa isogashii desu.",
        "indonesian": "Tahun ini sibuk.",
        "kanji": ["年", "今"]
    },

    # ── 買 (membeli) ─────────────────────────────────────────────────────────
    {
        "id": "EX117", "japanese": "買い物をしてから家に帰ります。",
        "romaji": "kaimono o shite kara ie ni kaerimasu.",
        "indonesian": "Saya pulang setelah berbelanja.",
        "kanji": ["買"]
    },

    # ── 白 (putih) ───────────────────────────────────────────────────────────
    {
        "id": "EX118", "japanese": "白い犬がいます。",
        "romaji": "shiroi inu ga imasu.",
        "indonesian": "Ada anjing putih.",
        "kanji": ["白"]
    },

    # ── 八 (delapan) ─────────────────────────────────────────────────────────
    {
        "id": "EX119", "japanese": "八時に起きます。",
        "romaji": "hachiji ni okimasu.",
        "indonesian": "Saya bangun jam delapan.",
        "kanji": ["八", "時"]
    },

    # ── 半 (separuh) ─────────────────────────────────────────────────────────
    {
        "id": "EX120", "japanese": "今は三時半です。",
        "romaji": "ima wa sanji han desu.",
        "indonesian": "Sekarang jam tiga setengah.",
        "kanji": ["半", "今", "時", "三"]
    },

    # ── 百 (seratus) ─────────────────────────────────────────────────────────
    {
        "id": "EX121", "japanese": "百人が来ました。",
        "romaji": "hyakunin ga kimashita.",
        "indonesian": "Seratus orang datang.",
        "kanji": ["百", "人", "来"]
    },

    # ── 父 (ayah) ────────────────────────────────────────────────────────────
    {
        "id": "EX122", "japanese": "家族の中で父がいちばん背が高いです。",
        "romaji": "kazoku no naka de chichi ga ichiban se ga takai desu.",
        "indonesian": "Di keluarga, ayah saya yang paling tinggi.",
        "kanji": ["父", "中", "高"]
    },

    # ── 分 (menit/memahami) ──────────────────────────────────────────────────
    {
        "id": "EX123", "japanese": "パソコンの使いかたがわかりません。",
        "romaji": "pasokon no tsukai kata ga wakarimasen.",
        "indonesian": "Saya tidak tahu cara menggunakan komputer.",
        "kanji": ["分"]
    },

    # ── 聞 (mendengar) ───────────────────────────────────────────────────────
    {
        "id": "EX124", "japanese": "それを聞いたことがある。",
        "romaji": "sore o kiita koto ga aru.",
        "indonesian": "Saya pernah mendengar itu sebelumnya.",
        "kanji": ["聞"]
    },

    # ── 母 (ibu) ──────────────────────────────────────────────────────────────
    {
        "id": "EX125", "japanese": "母は料理をするのが下手だ。",
        "romaji": "haha wa ryouri o suru no ga heta da.",
        "indonesian": "Ibu saya kurang pandai memasak.",
        "kanji": ["母"]
    },
    {
        "id": "EX126", "japanese": "お母さんと買い物に行った。",
        "romaji": "okaasan to kaimono ni itta.",
        "indonesian": "Saya pergi belanja bersama ibu.",
        "kanji": ["母", "買", "行"]
    },

    # ── 北 (utara) ───────────────────────────────────────────────────────────
    {
        "id": "EX127", "japanese": "北海道は寒いです。",
        "romaji": "hokkaidou wa samui desu.",
        "indonesian": "Hokkaido dingin.",
        "kanji": ["北"]
    },

    # ── 木 (pohon) ───────────────────────────────────────────────────────────
    {
        "id": "EX128", "japanese": "木曜日に映画を見ます。",
        "romaji": "mokuyoubi ni eiga o mimasu.",
        "indonesian": "Saya menonton film pada hari Kamis.",
        "kanji": ["木", "見"]
    },

    # ── 本 (buku/asli) ───────────────────────────────────────────────────────
    {
        "id": "EX129", "japanese": "本は映画より面白いです。",
        "romaji": "hon wa eiga yori omoshiroi desu.",
        "indonesian": "Buku lebih menarik daripada film.",
        "kanji": ["本"]
    },

    # ── 毎 (setiap) ───────────────────────────────────────────────────────────
    {
        "id": "EX130", "japanese": "毎朝、パンやベーコンなどを食べています。",
        "romaji": "mai asa, pan ya beekon nado wo tabeteimasu.",
        "indonesian": "Setiap pagi saya makan roti dan bacon, dll.",
        "kanji": ["毎", "食"]
    },

    # ── 万 (sepuluh ribu) ────────────────────────────────────────────────────
    {
        "id": "EX131", "japanese": "五万円で新しい自転車を買いました。",
        "romaji": "goman en de atarashii jitensha o kaimashita.",
        "indonesian": "Saya membeli sepeda baru seharga lima puluh ribu yen.",
        "kanji": ["万", "円", "新", "買"]
    },

    # ── 名 (nama) ────────────────────────────────────────────────────────────
    {
        "id": "EX132", "japanese": "あなたの名前は何ですか？",
        "romaji": "anata no namae wa nan desu ka?",
        "indonesian": "Siapa namamu?",
        "kanji": ["名", "何"]
    },

    # ── 目 (mata) ────────────────────────────────────────────────────────────
    {
        "id": "EX133", "japanese": "目が痛いです。",
        "romaji": "me ga itai desu.",
        "indonesian": "Mata saya sakit.",
        "kanji": ["目"]
    },

    # ── 友 (teman) ───────────────────────────────────────────────────────────
    {
        "id": "EX134", "japanese": "友だちの家に遊びに行く。",
        "romaji": "tomodachi no ie ni asobi ni iku.",
        "indonesian": "Saya pergi ke rumah teman untuk bermain.",
        "kanji": ["友", "行"]
    },
    {
        "id": "EX135", "japanese": "かれは私の友だちです。",
        "romaji": "kare wa watashi no tomodachi desu.",
        "indonesian": "Dia adalah teman saya.",
        "kanji": ["友", "人"]
    },

    # ── 来 (datang) ───────────────────────────────────────────────────────────
    {
        "id": "EX136", "japanese": "彼はもうすぐ来るだろう。",
        "romaji": "kare wa mou sugu kuru darou.",
        "indonesian": "Dia seharusnya segera datang.",
        "kanji": ["来"]
    },
    {
        "id": "EX137", "japanese": "どうして日本に来たんですか？",
        "romaji": "doushite nihon ni kitan desu ka?",
        "indonesian": "Mengapa kamu datang ke Jepang?",
        "kanji": ["来", "本"]
    },

    # ── 立 (berdiri) ─────────────────────────────────────────────────────────
    {
        "id": "EX138", "japanese": "立って待ってください。",
        "romaji": "tatte matte kudasai.",
        "indonesian": "Tolong berdiri dan tunggu.",
        "kanji": ["立"]
    },

    # ── 六 (enam) ────────────────────────────────────────────────────────────
    {
        "id": "EX139", "japanese": "六時に会いましょう。",
        "romaji": "rokuji ni aimashou.",
        "indonesian": "Mari bertemu jam enam.",
        "kanji": ["六", "時", "会"]
    },

    # ── 話 (berbicara) ───────────────────────────────────────────────────────
    {
        "id": "EX140", "japanese": "日本人ともっと話したいです。",
        "romaji": "nihonjin to motto hanashitai desu.",
        "indonesian": "Saya ingin lebih banyak berbicara dengan orang Jepang.",
        "kanji": ["話", "人", "本"]
    },
    {
        "id": "EX141", "japanese": "日本語より、話す方が上手だ。",
        "romaji": "nihongo yori, hanasu hou ga jouzu da.",
        "indonesian": "Saya lebih mahir berbicara daripada menulis bahasa Jepang.",
        "kanji": ["話", "語", "言", "上"]
    },
]

# ---------------------------------------------------------------------------
# Ingest ke Neo4j
# ---------------------------------------------------------------------------

def run_enrichment():
    try:
        from core.config import settings
        uri      = settings.NEO4J_URI
        user     = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        print(f"[OK] Menggunakan kredensial dari .env (URI: {uri})")
    except Exception:
        uri      = "bolt://localhost:7687"
        user     = "neo4j"
        password = "tvjp08052004"
        print(f"[WARN] Fallback credentials (URI: {uri})")

    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("[OK] Terhubung ke Neo4j")

    added_sentences  = 0
    added_edges      = 0
    skipped_kanji    = []

    with driver.session() as session:
        # Pastikan index Sentence ada
        session.run("CREATE INDEX IF NOT EXISTS FOR (s:Sentence) ON (s.id)")
        session.run("CREATE INDEX IF NOT EXISTS FOR (k:Kanji) ON (k.id)")

        for s in NEW_SENTENCES:
            # 1. MERGE node Sentence (tidak menimpa data lama jika sudah ada)
            result = session.run("""
                MERGE (s:Sentence {id: $id})
                ON CREATE SET
                    s.japanese_text          = $japanese,
                    s.romaji                 = $romaji,
                    s.indonesian_translation = $indonesian,
                    s.level                  = 'N5',
                    s.source                 = 'JLPT N5 Grammar Master (JLPTsensei.com)'
                RETURN s.id AS sid
            """, id=s["id"], japanese=s["japanese"],
                 romaji=s["romaji"], indonesian=s["indonesian"])

            rec = result.single()
            if rec:
                added_sentences += 1

            # 2. MERGE relasi CONTAINS_KANJI (direct edge - tanpa perantara Vocab)
            for kanji_char in s["kanji"]:
                # Cek apakah kanji ada di graph
                exists = session.run(
                    "MATCH (k:Kanji {id: $kid}) RETURN count(k) > 0 AS exists",
                    kid=kanji_char
                ).single()

                if exists and exists["exists"]:
                    session.run("""
                        MATCH (s:Sentence {id: $sid})
                        MATCH (k:Kanji    {id: $kid})
                        MERGE (s)-[:CONTAINS_KANJI]->(k)
                    """, sid=s["id"], kid=kanji_char)
                    added_edges += 1
                else:
                    skipped_kanji.append(f"{s['id']}->{kanji_char}")

    driver.close()

    print(f"\n[DONE] Enrichment selesai!")
    print(f"   Sentence nodes diproses : {added_sentences}")
    print(f"   Relasi CONTAINS_KANJI   : {added_edges}")
    if skipped_kanji:
        print(f"   [WARN] Kanji tidak ditemukan di graph ({len(skipped_kanji)} relasi dilewati):")
        for sk in skipped_kanji:
            print(f"      - {sk}")


def patch_graph_engine():
    """
    Cek apakah get_random_kanji sudah support CONTAINS_KANJI.
    """
    ge_path = os.path.join(BACKEND_DIR, "services", "graph_engine.py")
    if not os.path.exists(ge_path):
        print(f"[ERR] graph_engine.py tidak ditemukan di {ge_path}")
        return

    with open(ge_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "CONTAINS_KANJI" in content:
        print("[OK] graph_engine.py sudah support CONTAINS_KANJI")
    else:
        print("[WARN] graph_engine.py belum support CONTAINS_KANJI.")
        print("       Update get_random_kanji untuk include direct edge.")


if __name__ == "__main__":
    run_enrichment()
    print()
    patch_graph_engine()

