"""
fix_grammar_names_and_kanji_sentences.py
==========================================
Skrip untuk dua perbaikan sekaligus:

1. PERBAIKAN NAMA GRAMMAR
   Memperbarui nama node Grammar yang verbose ke nama yang lebih ringkas & selaras
   dengan eBook JLPTsensei N5 Grammar Master, sehingga:
   - Mudah dicocokkan oleh sistem validasi
   - Konsisten dengan cara AI menuliskan pola grammar dalam responsnya

2. PENAMBAHAN CONTOH KALIMAT KANJI (CONTAINS_KANJI edges)
   Menambah relasi langsung Sentence-[:CONTAINS_KANJI]->Kanji untuk kanji yang
   belum memiliki contoh kalimat melalui jalur via-Vocab.
   Setiap kanji N5 harus memiliki setidaknya 1 contoh kalimat.

Cara menjalankan:
  cd c:\\Users\\satya\\OneDrive\\Desktop\\TVJP
  .\\venv-backend\\Scripts\\python backend\\data_pipeline\\fix_grammar_names_and_kanji_sentences.py
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(BASE_DIR)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from neo4j import GraphDatabase

try:
    from core.config import settings
    URI  = settings.NEO4J_URI
    USER = settings.NEO4J_USERNAME
    PASS = settings.NEO4J_PASSWORD
    print(f"[INFO] Menggunakan kredensial dari .env (URI: {URI})")
except Exception as e:
    URI  = "bolt://localhost:7687"
    USER = "neo4j"
    PASS = "tvjp08052004"
    print(f"[WARN] Fallback credentials (URI: {URI}): {e}")


# =============================================================================
# PART 1: Pemetaan Nama Grammar Lama → Baru (selaras eBook JLPTsensei)
# =============================================================================
# Format: "id_lama": ("id_baru", "nama_tampilan_baru")
# Hanya grammar yang namanya terlalu verbose/tidak selaras dengan AI response
GRAMMAR_RENAME_MAP = {
    "Akhiran です、 だ": ("です・だ (Kopula)", "です・だ (Kopula)"),
    "Partikel subject は、も、 が": ("は・も・が (Partikel Subjek)", "は・も・が (Partikel Subjek)"),
    "Partikel object を、に、へ、 で": ("を・に・へ・で (Partikel Objek)", "を・に・へ・で (Partikel Objek)"),
    "Partikel と、や、と か": ("と・や・とか (Partikel Penghubung)", "と・や・とか (Partikel Penghubung)"),
    "Partikel  の": ("の (Partikel Kepemilikan)", "の (Partikel Kepemilikan)"),
    "Memahami Kelompok Kata Kerja Bahasa Jepang (Godan, Ichidan, dan Fukisoku Doushi)": (
        "Kelompok Kata Kerja (Godan/Ichidan)", "Kelompok Kata Kerja (Godan/Ichidan)"
    ),
    "Memahami Konjugasi Kata Kerja, Kata Benda dan Kata Sifat (Positif, Negatif, Lampau, Negatif Lampau)": (
        "Konjugasi Dasar (Positif/Negatif/Lampau)", "Konjugasi Dasar (Positif/Negatif/Lampau)"
    ),
    "Kata Kerja Bentuk Sopan (masu-kei)": ("〜ます形 (Bentuk Sopan)", "〜ます形 (Bentuk Sopan)"),
    "Tata bahasa ~がある dan ~がい る": ("〜がある / 〜がいる", "〜がある / 〜がいる"),
    "Tata bahasa ~てください dan ~ないでくださ い": ("〜てください / 〜ないでください", "〜てください / 〜ないでください"),
    "Tata bahasa ~ましょう、~ましょうか、~ません か": ("〜ましょう / 〜ましょうか / 〜ませんか", "〜ましょう / 〜ましょうか / 〜ませんか"),
    "Tata bahasa ~てもいい、~なくてもい い": ("〜てもいい / 〜なくてもいい", "〜てもいい / 〜なくてもいい"),
    "Tata bahasa ~てはいけない、~なくてはいけな い": ("〜てはいけない / 〜なくてはいけない", "〜てはいけない / 〜なくてはいけない"),
    "Tata bahasa ~から、~の で": ("〜から / 〜ので (Alasan)", "〜から / 〜ので (Alasan)"),
    "Tata bahasa ~ている、~ていく、~てく る": ("〜ている / 〜ていく / 〜てくる", "〜ている / 〜ていく / 〜てくる"),
    "Tata bahasa ~のほうが　~よ り": ("〜より〜のほうが (Perbandingan)", "〜より〜のほうが (Perbandingan)"),
    "Tata bahasa ~ほうがい い": ("〜ほうがいい (Saran)", "〜ほうがいい (Saran)"),
    "Tata bahasa ~の中で、~がいちば ん": ("〜の中で〜がいちばん (Superlatif)", "〜の中で〜がいちばん (Superlatif)"),
    "Tata bahasa ~つもりで す": ("〜つもりです (Niat)", "〜つもりです (Niat)"),
    "Mengubah kata adjective jadi adverb ~く／にな る": ("〜く/になる (Perubahan Keadaan)", "〜く/になる (Perubahan Keadaan)"),
    "Tata bahasa ~たいです、~たくないで す": ("〜たいです / 〜たくないです (Keinginan)", "〜たいです / 〜たくないです (Keinginan)"),
    "Tata bahasa ~たりす る": ("〜たり〜たりする (Aktivitas Paralel)", "〜たり〜たりする (Aktivitas Paralel)"),
    "Tata bahasa ~たことがある、~たことがな い": ("〜たことがある / 〜たことがない (Pengalaman)", "〜たことがある / 〜たことがない (Pengalaman)"),
    "Akhiran だろう、でしょう、かもしれな い": ("だろう / でしょう / かもしれない (Dugaan)", "だろう / でしょう / かもしれない (Dugaan)"),
    "Tata bahasa ~まえに、~てか ら": ("〜まえに / 〜てから (Urutan Waktu)", "〜まえに / 〜てから (Urutan Waktu)"),
}


# =============================================================================
# PART 2: Kalimat contoh untuk Kanji yang tidak punya relasi via-Vocab
# =============================================================================
# Format: kanji_id → list of (japanese_text, romaji, indonesian_translation)
# Sumber: eBook JLPTsensei N5 Grammar Master & standar N5 JLPT
KANJI_DIRECT_SENTENCES = {
    "安": [("この店の食べ物は安いです。", "kono mise no tabemono wa yasui desu.", "Makanan di toko ini murah.")],
    "一": [("一つのリンゴがあります。", "hitotsu no ringo ga arimasu.", "Ada satu buah apel.")],
    "飲": [("水を飲みます。", "mizu o nomimasu.", "Saya minum air.")],
    "右": [("交差点を右に曲がってください。", "kousaten o migi ni magatte kudasai.", "Silakan belok kanan di persimpangan.")],
    "雨": [("今日は雨が降っています。", "kyou wa ame ga futte imasu.", "Hari ini hujan turun.")],
    "駅": [("駅まで歩いて行きます。", "eki made aruite ikimasu.", "Saya berjalan kaki ke stasiun.")],
    "円": [("このペンは百円です。", "kono pen wa hyaku en desu.", "Pena ini harganya seratus yen.")],
    "火": [("火は熱いです。", "hi wa atsui desu.", "Api itu panas.")],
    "花": [("花の水やりをしなくてはいけません。", "hana no mizu yari o shi nakute wa ikemasen.", "Kamu harus menyiram bunga.")],
    "下": [("木の下に大きな犬がいます。", "ki no shita ni ookina inu ga imasu.", "Ada anjing besar di bawah pohon itu.")],
    "何": [("あなたの名前は何ですか？", "anata no namae wa nan desu ka?", "Siapa namamu?")],
    "会": [("駅で会いましょう！", "eki de ai mashou!", "Ayo ketemu di stasiun!")],
    "外": [("外は暑いですね。", "soto wa atsui desu ne.", "Di luar panas ya.")],
    "学": [("学校まで歩いて行きます。", "gakkou made aruite ikimasu.", "Saya berjalan ke sekolah.")],
    "間": [("少し時間をください。", "sukoshi jikan o kudasai.", "Aku butuh sedikit waktu.")],
    "気": [("元気ですか？", "genki desu ka?", "Apa kabar?")],
    "九": [("九時に駅で会いましょう。", "ku ji ni eki de aimashou.", "Mari bertemu di stasiun jam sembilan.")],
    "休": [("土曜日は学校が休みです。", "doyoubi wa gakkou ga yasumi desu.", "Hari Sabtu sekolah libur.")],
    "魚": [("私は魚が好きです。", "watashi wa sakana ga suki desu.", "Saya suka ikan.")],
    "金": [("お金がたくさんほしい。", "okane ga takusan hoshii.", "Aku ingin banyak uang.")],
    "空": [("空港まで来なくてもいいよ。", "kuukou made konaku temo ii yo.", "Kamu tidak perlu datang sampai ke bandara.")],
    "月": [("1月と2月はとても寒いです。", "ichigatsu to nigatsu wa totemo samui desu.", "Bulan Januari dan Februari sangat dingin.")],
    "見": [("映画を見ませんか。", "eiga o mimasen ka.", "Ingin menonton film?")],
    "言": [("もっとゆっくり言ってください。", "motto yukkuri itte kudasai.", "Tolong bicara lebih pelan.")],
    "古": [("あの古い図書館は静かです。", "ano furui toshokan wa shizuka desu.", "Perpustakaan tua itu tenang.")],
    "五": [("りんごが五つあります。", "ringo ga itsutsu arimasu.", "Ada lima buah apel.")],
    "後": [("ご飯の後で歯を磨いた方がいいですよ。", "gohan no ato de ha o migaita hou ga ii desu yo.", "Lebih baik menyikat gigi setelah makan.")],
    "午": [("午前中が一番調子がいい。", "gozen chuu ga ichiban choushi ga ii.", "Saya merasa paling sehat di pagi hari.")],
    "語": [("日本語を勉強しています。", "nihongo o benkyou shiteimasu.", "Saya sedang belajar bahasa Jepang.")],
    "校": [("学校まで歩いて行きます。", "gakkou made aruite ikimasu.", "Saya berjalan ke sekolah.")],
    "口": [("口を大きく開けてください。", "kuchi o ookiku akete kudasai.", "Tolong buka mulutnya lebar-lebar.")],
    "行": [("今日は電車で行きました。", "kyou wa densha de ikimashita.", "Hari ini saya pergi dengan kereta.")],
    "高": [("このカメラは高かった。", "kono kamera wa takakatta.", "Kamera ini mahal.")],
    "国": [("ベトナムはどんな国ですか。", "betonamu wa donna kuni desu ka.", "Apa saja karakteristik negara Vietnam?")],
    "今": [("今日は暑いですね。", "kyou wa atsui desu ne.", "Hari ini panas ya.")],
    "左": [("左手で食べようとしたが難しかった。", "hidari te de tabeyou to shita ga muzukashikatta.", "Saya mencoba makan dengan tangan kiri, tapi sulit.")],
    "三": [("このマンションにはへやが三つあります。", "kono manshon niwa heya ga mitsu arimasu.", "Ada tiga kamar di apartemen ini.")],
    "山": [("チームの中で山田が一番強い！", "chiimu no naka de yamada ga ichiban tsuyoi!", "Di tim kami, Yamada yang paling kuat!")],
    "四": [("私の部屋には窓が四つあります。", "watashi no heya ni wa mado ga yotsu arimasu.", "Ada empat jendela di kamar saya.")],
    "子": [("子どもの前に悪いことばを言ってはいけません。", "kodomo no mae ni warui kotoba o itte wa ikemasen.", "Jangan ucapkan kata buruk di depan anak-anak.")],
    "耳": [("ウサギは耳が長いです。", "usagi wa mimi ga nagai desu.", "Kelinci memiliki telinga yang panjang.")],
    "時": [("時間がありません。", "jikan ga arimasen.", "Tidak ada waktu.")],
    "七": [("七時に起きます。", "shichi ji ni okimasu.", "Saya bangun jam tujuh.")],
    "車": [("道を渡るとき、車に気をつけてください。", "michi o wataru toki, kuruma ni ki o tsukete kudasai.", "Hati-hati dengan mobil saat menyeberang.")],
    "社": [("将来は日本の会社で働きたいです。", "shourai wa nihon no kaisha de hatarakitai desu.", "Di masa depan, saya ingin bekerja di perusahaan Jepang.")],
    "手": [("トイレを使ってから、手を洗わないといけません。", "toire o tsukatte kara, te o arawanai to ikemasen.", "Kita harus mencuci tangan setelah menggunakan kamar mandi.")],
    "週": [("今週の単語をまだ覚えていません。", "konshuu no tango o mada oboete imasen.", "Aku belum hafal kata-kata minggu ini.")],
    "十": [("十個の卵を買いました。", "jukko no tamago o kaimashita.", "Saya membeli sepuluh butir telur.")],
    "出": [("電気を消さないで寝てしまった。", "denki o kesanaide nete shimatta.", "Saya tidur tanpa mematikan lampu.")],
    "書": [("手紙を書いています。", "tegami o kaite imasu.", "Saya sedang menulis surat.")],
    "女": [("彼女がほしい。", "kanojo ga hoshii.", "Aku ingin punya pacar.")],
    "小": [("小学生以下はお金を払わなくてもいいです。", "shougakusei ika wa okane o harawanaku temo ii desu.", "Anak sekolah dasar ke bawah tidak perlu bayar.")],
    "少": [("少し時間をください。", "sukoshi jikan o kudasai.", "Tolong beri saya sedikit waktu.")],
    "上": [("スポーツは上手じゃないけど、好きです。", "supootsu wa jouzu janai kedo, suki desu.", "Saya tidak mahir olahraga, tapi suka.")],
    "食": [("朝ごはんを食べないで仕事に来ました。", "asa gohan o tabenaide shigoto ni kimashita.", "Saya datang kerja tanpa sarapan.")],
    "新": [("今週の新しい単語をまだ覚えていません。", "konshuu no atarashii tango o mada oboete imasen.", "Belum hafal kata baru minggu ini.")],
    "人": [("図書館には百人以上の学生がいます。", "toshokan ni wa hyaku nin ijou no gakusei ga imasu.", "Ada lebih dari seratus siswa di perpustakaan.")],
    "水": [("すみません、お水をください。", "sumimasen, omizu o kudasai.", "Maaf, boleh minta air?")],
    "生": [("今年、私は20歳になります。", "kotoshi, watashi wa hatachi ni narimasu.", "Tahun ini saya berusia 20 tahun.")],
    "西": [("太陽は西に沈みます。", "taiyou wa nishi ni shizumimasu.", "Matahari terbenam di sebelah barat.")],
    "川": [("この川はとてもきれいです。", "kono kawa wa totemo kirei desu.", "Sungai ini sangat bersih.")],
    "千": [("お財布の中に千円あります。", "osaifu no naka ni sen en arimasu.", "Ada seribu yen di dalam dompet.")],
    "先": [("分からないときは、早く先生に聞きましょうね。", "wakaranai toki wa, hayaku sensei ni kikimashou ne.", "Kalau tidak paham, langsung tanya guru ya!")],
    "前": [("旅行の前に切符を買っておきます。", "ryokou no mae ni kippu o katte okimasu.", "Aku beli tiket sebelum perjalanan.")],
    "足": [("足が痛いです。", "ashi ga itai desu.", "Kaki saya sakit.")],
    "多": [("図書館には多くの本があります。", "toshokan ni wa ooku no hon ga arimasu.", "Di perpustakaan ada banyak buku.")],
    "大": [("大きくなっているね！", "ookiku natteiru ne!", "Kamu semakin besar!")],
    "男": [("彼は金はあるが、バカな男だ。", "kare wa kane wa aru ga, baka na otoko da.", "Dia punya uang tapi orang yang bodoh.")],
    "中": [("お財布の中に千円あります。", "osaifu no naka ni sen en arimasu.", "Ada seribu yen di dalam dompet.")],
    "長": [("パソコンを長く見ると、目が疲れます。", "pasokon o nagaku miru to, me ga tsukaremasu.", "Mata lelah jika lama menatap komputer.")],
    "天": [("今日の天気はいいですね。", "kyou no tenki wa ii desu ne.", "Cuaca hari ini bagus ya.")],
    "店": [("お店は何時から開いていますか？", "omise wa nanji kara aiteimasu ka?", "Toko buka dari jam berapa?")],
    "電": [("電車の席がなかったので、立っていました。", "densha no seki ga nakatta node, tatte imashita.", "Tidak ada kursi di kereta, jadi saya berdiri.")],
    "土": [("土曜日は学校が休みです。", "doyoubi wa gakkou ga yasumi desu.", "Hari Sabtu sekolah libur.")],
    "東": [("東京駅に観光者がいっぱいいる。", "toukyou eki ni kankousha ga ippai iru.", "Ada banyak turis di Stasiun Tokyo.")],
    "道": [("道を渡るとき、車に気をつけてください。", "michi o wataru toki, kuruma ni ki o tsukete kudasai.", "Hati-hati dengan mobil saat menyeberang.")],
    "読": [("漫画を読むのが好きだ。", "manga o yomu no ga suki da.", "Saya suka baca manga.")],
    "南": [("鳥が南の国へ飛びます。", "tori ga minami no kuni he tobimasu.", "Burung-burung terbang ke negara selatan.")],
    "二": [("コーヒーを二つください。", "koohii o futatsu kudasai.", "Berikan saya 2 cangkir kopi.")],
    "日": [("今日は電車で来ました。", "kyou wa densha de kimashita.", "Hari ini saya datang dengan kereta.")],
    "入": [("夜には学校の入り口が閉めてある。", "yoru ni wa gakkou no iriguchi ga shimete aru.", "Pintu masuk sekolah ditutup pada malam hari.")],
    "年": [("今年、私は20歳になります。", "kotoshi, watashi wa hatachi ni narimasu.", "Tahun ini saya berusia 20 tahun.")],
    "買": [("買い物をしてから家に帰ります。", "kaimono o shite kara ie ni kaerimasu.", "Saya pulang setelah selesai berbelanja.")],
    "白": [("白いシャツを着ています。", "shiroi shatsu o kite imasu.", "Saya memakai kemeja putih.")],
    "八": [("八時に朝ご飯を食べます。", "hachi ji ni asagohan o tabemasu.", "Saya sarapan pukul delapan.")],
    "半": [("会議は十一時半から始まります。", "kaigi wa juuichi ji han kara hajimarimasu.", "Rapat dimulai dari jam sebelas setengah.")],
    "百": [("図書館には百人以上の学生がいます。", "toshokan ni wa hyaku nin ijou no gakusei ga imasu.", "Ada lebih dari seratus siswa di perpustakaan.")],
    "父": [("家族のなかで父がいちばん背が高いです。", "kazoku no naka de chichi ga ichiban se ga takai desu.", "Di keluarga saya, ayah yang paling tinggi.")],
    "分": [("少し時間をください。", "sukoshi jikan o kudasai.", "Tolong beri saya sedikit waktu.")],
    "聞": [("それを聞いたことがある。", "sore o kiita koto ga aru.", "Aku pernah mendengar itu sebelumnya.")],
    "母": [("母は料理をするのが下手だ。", "haha wa ryouri o suru no ga heta da.", "Ibu saya kurang mahir memasak.")],
    "北": [("北海道は台湾より大きいです。", "hokkaidou wa taiwan yori ookii desu.", "Hokkaido lebih besar daripada Taiwan.")],
    "木": [("木の下に大きな犬がいます。", "ki no shita ni ookina inu ga imasu.", "Ada anjing besar di bawah pohon itu.")],
    "本": [("漫画を読むのが好きだ。", "manga o yomu no ga suki da.", "Saya suka baca manga.")],
    "毎": [("毎朝、パンなどを食べています。", "mai asa, pan nado wo tabeteimasu.", "Setiap pagi saya makan roti, dll.")],
    "万": [("このカメラは五万円です。", "kono kamera wa go man en desu.", "Kamera ini harganya lima puluh ribu yen.")],
    "名": [("あなたの名前は何ですか？", "anata no namae wa nan desu ka?", "Siapa namamu?")],
    "目": [("パソコンを長く見ると、目が疲れます。", "pasokon o nagaku miru to, me ga tsukaremasu.", "Mata lelah jika lama menatap komputer.")],
    "友": [("友だちの家に遊びに行く。", "tomodachi no ie ni asobi ni iku.", "Aku akan pergi ke rumah teman untuk mengobrol.")],
    "来": [("バスはまだ来ていません。", "basu wa mada kiteimasen.", "Busnya masih belum tiba.")],
    "立": [("電車の席がなかったので、立っていました。", "densha no seki ga nakatta node, tatte imashita.", "Tidak ada kursi di kereta, jadi saya berdiri.")],
    "六": [("六時の電車に乗ります。", "roku ji no densha ni norimasu.", "Saya akan naik kereta jam enam.")],
    "話": [("日本語を話します。", "nihongo o hanashimasu.", "Saya bicara bahasa Jepang.")],
}


def run_fixes():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    try:
        with driver.session() as session:
            # ─────────────────────────────────────────────────────────────────
            # PART 1: Perbarui nama Grammar node
            # ─────────────────────────────────────────────────────────────────
            print("\n" + "="*60)
            print("PART 1: Memperbarui nama Grammar nodes...")
            print("="*60)
            
            renamed = 0
            skipped = 0
            for old_id, (new_id, new_name) in GRAMMAR_RENAME_MAP.items():
                # Cek apakah node lama masih ada
                result = session.run(
                    "MATCH (g:Grammar {id: $old_id}) RETURN count(g) as cnt",
                    old_id=old_id
                )
                cnt = result.single()["cnt"]
                
                if cnt == 0:
                    # Mungkin sudah di-rename sebelumnya atau belum di-ingest
                    # Cek apakah new_id sudah ada
                    result2 = session.run(
                        "MATCH (g:Grammar {id: $new_id}) RETURN count(g) as cnt",
                        new_id=new_id
                    )
                    cnt2 = result2.single()["cnt"]
                    if cnt2 > 0:
                        print(f"  ✅ Sudah ada: '{new_id}' (skip)")
                    else:
                        print(f"  ⚠️  Tidak ditemukan: '{old_id}'")
                    skipped += 1
                    continue
                
                # Update id dan name sekaligus
                session.run("""
                    MATCH (g:Grammar {id: $old_id})
                    SET g.id = $new_id,
                        g.name = $new_name
                """, old_id=old_id, new_id=new_id, new_name=new_name)
                
                print(f"  ✏️  '{old_id}'\n      → '{new_id}'")
                renamed += 1
            
            print(f"\n  Selesai: {renamed} grammar di-rename, {skipped} di-skip")

            # ─────────────────────────────────────────────────────────────────
            # PART 2: Tambah contoh kalimat langsung untuk Kanji
            # ─────────────────────────────────────────────────────────────────
            print("\n" + "="*60)
            print("PART 2: Menambah contoh kalimat untuk Kanji...")
            print("="*60)
            
            added_sentences = 0
            added_edges = 0
            already_has = 0
            kanji_missing = 0
            
            for kanji_id, sentences in KANJI_DIRECT_SENTENCES.items():
                # Cek apakah kanji ada di Neo4j
                result = session.run(
                    "MATCH (k:Kanji {id: $kid}) RETURN count(k) as cnt",
                    kid=kanji_id
                )
                cnt = result.single()["cnt"]
                if cnt == 0:
                    print(f"  ⚠️  Kanji tidak ditemukan di Neo4j: '{kanji_id}'")
                    kanji_missing += 1
                    continue
                
                # Cek apakah sudah punya contoh kalimat (via Vocab atau direct)
                result2 = session.run("""
                    MATCH (k:Kanji {id: $kid})
                    OPTIONAL MATCH (k)<-[:WRITTEN_IN]-(v:Vocab)<-[:CONTAINS_VOCAB]-(sv:Sentence)
                    OPTIONAL MATCH (sk:Sentence)-[:CONTAINS_KANJI]->(k)
                    WITH k, count(DISTINCT sv) + count(DISTINCT sk) AS total_examples
                    RETURN total_examples
                """, kid=kanji_id)
                total_ex = result2.single()["total_examples"]
                
                if total_ex > 0:
                    already_has += 1
                    continue
                
                # Kanji belum punya contoh — tambahkan
                for i, (jp_text, romaji, translation) in enumerate(sentences):
                    sentence_id = f"KS_{kanji_id}_{i+1:03d}"
                    
                    session.run("""
                        MERGE (s:Sentence {id: $sid})
                        SET s.japanese_text = $jp,
                            s.romaji = $rom,
                            s.indonesian_translation = $trans,
                            s.level = 'N5',
                            s.source = 'kanji_direct'
                        WITH s
                        MATCH (k:Kanji {id: $kid})
                        MERGE (s)-[:CONTAINS_KANJI]->(k)
                    """, sid=sentence_id, jp=jp_text, rom=romaji,
                         trans=translation, kid=kanji_id)
                    
                    added_sentences += 1
                    added_edges += 1
                
                print(f"  ➕ '{kanji_id}': {len(sentences)} kalimat ditambahkan")
            
            print(f"\n  Selesai:")
            print(f"    {added_sentences} kalimat baru ditambahkan")
            print(f"    {added_edges} relasi CONTAINS_KANJI dibuat")
            print(f"    {already_has} kanji sudah punya kalimat (skip)")
            print(f"    {kanji_missing} kanji tidak ditemukan di Neo4j")
            
            # Verifikasi akhir
            print("\n" + "="*60)
            print("VERIFIKASI: Kanji N5 yang masih belum punya contoh kalimat...")
            print("="*60)
            result_check = session.run("""
                MATCH (k:Kanji {level: 'N5'})
                OPTIONAL MATCH (k)<-[:WRITTEN_IN]-(v:Vocab)<-[:CONTAINS_VOCAB]-(sv:Sentence)
                OPTIONAL MATCH (sk:Sentence)-[:CONTAINS_KANJI]->(k)
                WITH k, count(DISTINCT sv) + count(DISTINCT sk) AS total
                WHERE total = 0
                RETURN k.id AS kanji
                ORDER BY k.id
            """)
            missing_after = [r["kanji"] for r in result_check]
            if missing_after:
                print(f"  ⚠️  Masih {len(missing_after)} kanji tanpa contoh: {', '.join(missing_after)}")
            else:
                print("  ✅ Semua kanji N5 sudah memiliki setidaknya 1 contoh kalimat!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.close()
    
    print("\n✅ Semua perbaikan selesai!")


if __name__ == "__main__":
    run_fixes()
