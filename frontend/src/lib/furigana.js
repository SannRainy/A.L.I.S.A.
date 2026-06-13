// src/lib/furigana.js
// ============================================================
// FURIGANA MAP — N5 + N4 komprehensif
// Urutan entri tidak penting; Trie selalu memilih kecocokan terpanjang.
// Format nilai: HTML ruby lengkap, atau campuran teks+ruby untuk kata
// yang mengandung okurigana / hiragana di antara kanji.
// ============================================================

export const FURIGANA_MAP = {

    // ── FRASA PANJANG (prioritas tertinggi lewat Trie longest-match) ──────────

    "お茶を飲むこと": "お<ruby>茶<rt>ちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>むこと",
    "作ってあります": "<ruby>作<rt>つく</rt></ruby>ってあります",
    "知っています": "<ruby>知<rt>し</rt></ruby>っています",
    "言われています": "<ruby>言<rt>い</rt></ruby>われています",
    "混んでいます": "<ruby>混<rt>こ</rt></ruby>んでいます",
    "混んでいる": "<ruby>混<rt>こ</rt></ruby>んでいる",
    "お昼ご飯は": "お<ruby>昼<rt>ひる</rt></ruby>ご<ruby>飯<rt>はん</rt></ruby>は",
    "お昼ご飯を": "お<ruby>昼<rt>ひる</rt></ruby>ご<ruby>飯<rt>はん</rt></ruby>を",
    "お昼ご飯": "お<ruby>昼<rt>ひる</rt></ruby>ご<ruby>飯<rt>はん</rt></ruby>",
    "お昼ごはん": "お<ruby>昼<rt>ひる</rt></ruby>ごはん",
    "勉強したい": "<ruby>勉強<rt>べんきょう</rt></ruby>したい",
    "時間どおり": "<ruby>時間<rt>じかん</rt></ruby>どおり",
    "お待ちください": "お<ruby>待<rt>ま</rt></ruby>ちください",
    "何名様ですか": "<ruby>何名様<rt>なんめいさま</rt></ruby>ですか",
    "何名様": "<ruby>何名様<rt>なんめいさま</rt></ruby>",
    "何ですか": "<ruby>何<rt>なん</rt></ruby>ですか",
    "空いている": "<ruby>空<rt>す</rt></ruby>いている",
    "世界一番": "<ruby>世界一番<rt>せかいいちばん</rt></ruby>",
    "見ること": "<ruby>見<rt>み</rt></ruby>ること",
    "飲むこと": "<ruby>飲<rt>の</rt></ruby>むこと",
    "読むこと": "<ruby>読<rt>よ</rt></ruby>むこと",
    "作り方": "<ruby>作<rt>つく</rt></ruby>り<ruby>方<rt>かた</rt></ruby>",
    "使い方": "<ruby>使<rt>つか</rt></ruby>い<ruby>方<rt>かた</rt></ruby>",
    "買い物": "<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>",
    "お母さん": "お<ruby>母<rt>かあ</rt></ruby>さん",
    "お父さん": "お<ruby>父<rt>とう</rt></ruby>さん",
    "お兄さん": "お<ruby>兄<rt>にい</rt></ruby>さん",
    "お姉さん": "お<ruby>姉<rt>ねえ</rt></ruby>さん",
    "お弁当": "お<ruby>弁当<rt>べんとう</rt></ruby>",
    "お風呂": "お<ruby>風呂<rt>ふろ</rt></ruby>",
    "お酒": "お<ruby>酒<rt>さけ</rt></ruby>",
    "お茶": "お<ruby>茶<rt>ちゃ</rt></ruby>",
    "お金": "お<ruby>金<rt>かね</rt></ruby>",
    "お箸": "お<ruby>箸<rt>はし</rt></ruby>",
    "お年": "お<ruby>年<rt>とし</rt></ruby>",
    "お待ち": "お<ruby>待<rt>ま</rt></ruby>ち",

    // ── KATA MAJEMUK N5 ───────────────────────────────────────────────────────

    // Waktu & tanggal
    "午前中": "<ruby>午前中<rt>ごぜんちゅう</rt></ruby>",
    "午前": "<ruby>午前<rt>ごぜん</rt></ruby>",
    "午後": "<ruby>午後<rt>ごご</rt></ruby>",
    "今日": "<ruby>今日<rt>きょう</rt></ruby>",
    "今年": "<ruby>今年<rt>ことし</rt></ruby>",
    "今月": "<ruby>今月<rt>こんげつ</rt></ruby>",
    "今週": "<ruby>今週<rt>こんしゅう</rt></ruby>",
    "今朝": "<ruby>今朝<rt>けさ</rt></ruby>",
    "今夜": "<ruby>今夜<rt>こんや</rt></ruby>",
    "今晩": "<ruby>今晩<rt>こんばん</rt></ruby>",
    "昨日": "<ruby>昨日<rt>きのう</rt></ruby>",
    "明日": "<ruby>明日<rt>あした</rt></ruby>",
    "明後日": "<ruby>明後日<rt>あさって</rt></ruby>",
    "来年": "<ruby>来年<rt>らいねん</rt></ruby>",
    "来月": "<ruby>来月<rt>らいげつ</rt></ruby>",
    "来週": "<ruby>来週<rt>らいしゅう</rt></ruby>",
    "先週": "<ruby>先週<rt>せんしゅう</rt></ruby>",
    "先月": "<ruby>先月<rt>せんげつ</rt></ruby>",
    "去年": "<ruby>去年<rt>きょねん</rt></ruby>",
    "毎日": "<ruby>毎日<rt>まいにち</rt></ruby>",
    "毎週": "<ruby>毎週<rt>まいしゅう</rt></ruby>",
    "毎月": "<ruby>毎月<rt>まいつき</rt></ruby>",
    "毎年": "<ruby>毎年<rt>まいとし</rt></ruby>",
    "毎朝": "<ruby>毎朝<rt>まいあさ</rt></ruby>",
    "毎晩": "<ruby>毎晩<rt>まいばん</rt></ruby>",

    // Hari dalam seminggu
    "月曜日": "<ruby>月曜日<rt>げつようび</rt></ruby>",
    "火曜日": "<ruby>火曜日<rt>かようび</rt></ruby>",
    "水曜日": "<ruby>水曜日<rt>すいようび</rt></ruby>",
    "木曜日": "<ruby>木曜日<rt>もくようび</rt></ruby>",
    "金曜日": "<ruby>金曜日<rt>きんようび</rt></ruby>",
    "土曜日": "<ruby>土曜日<rt>どようび</rt></ruby>",
    "日曜日": "<ruby>日曜日<rt>にちようび</rt></ruby>",
    "何曜日": "<ruby>何曜日<rt>なんようび</rt></ruby>",

    // Bulan
    "一月": "<ruby>一月<rt>いちがつ</rt></ruby>",
    "二月": "<ruby>二月<rt>にがつ</rt></ruby>",
    "三月": "<ruby>三月<rt>さんがつ</rt></ruby>",
    "四月": "<ruby>四月<rt>しがつ</rt></ruby>",
    "五月": "<ruby>五月<rt>ごがつ</rt></ruby>",
    "六月": "<ruby>六月<rt>ろくがつ</rt></ruby>",
    "七月": "<ruby>七月<rt>しちがつ</rt></ruby>",
    "八月": "<ruby>八月<rt>はちがつ</rt></ruby>",
    "九月": "<ruby>九月<rt>くがつ</rt></ruby>",
    "十月": "<ruby>十月<rt>じゅうがつ</rt></ruby>",
    "十一月": "<ruby>十一月<rt>じゅういちがつ</rt></ruby>",
    "十二月": "<ruby>十二月<rt>じゅうにがつ</rt></ruby>",
    "何月": "<ruby>何月<rt>なんがつ</rt></ruby>",

    // Jam
    "一時": "<ruby>一時<rt>いちじ</rt></ruby>",
    "二時": "<ruby>二時<rt>にじ</rt></ruby>",
    "三時": "<ruby>三時<rt>さんじ</rt></ruby>",
    "四時": "<ruby>四時<rt>よじ</rt></ruby>",
    "五時": "<ruby>五時<rt>ごじ</rt></ruby>",
    "六時": "<ruby>六時<rt>ろくじ</rt></ruby>",
    "七時": "<ruby>七時<rt>しちじ</rt></ruby>",
    "八時": "<ruby>八時<rt>はちじ</rt></ruby>",
    "九時": "<ruby>九時<rt>くじ</rt></ruby>",
    "十時": "<ruby>十時<rt>じゅうじ</rt></ruby>",
    "十一時": "<ruby>十一時<rt>じゅういちじ</rt></ruby>",
    "十二時": "<ruby>十二時<rt>じゅうにじ</rt></ruby>",
    "何時": "<ruby>何時<rt>なんじ</rt></ruby>",
    "何分": "<ruby>何分<rt>なんぷん</rt></ruby>",
    "何人": "<ruby>何人<rt>なんにん</rt></ruby>",

    // Keluarga
    "家族": "<ruby>家族<rt>かぞく</rt></ruby>",
    "兄弟": "<ruby>兄弟<rt>きょうだい</rt></ruby>",
    "姉妹": "<ruby>姉妹<rt>しまい</rt></ruby>",
    "両親": "<ruby>両親<rt>りょうしん</rt></ruby>",
    "祖父": "<ruby>祖父<rt>そふ</rt></ruby>",
    "祖母": "<ruby>祖母<rt>そぼ</rt></ruby>",
    "父親": "<ruby>父親<rt>ちちおや</rt></ruby>",
    "母親": "<ruby>母親<rt>ははおや</rt></ruby>",
    "子供": "<ruby>子供<rt>こども</rt></ruby>",

    // Tempat
    "学校": "<ruby>学校<rt>がっこう</rt></ruby>",
    "大学": "<ruby>大学<rt>だいがく</rt></ruby>",
    "小学校": "<ruby>小学校<rt>しょうがっこう</rt></ruby>",
    "中学校": "<ruby>中学校<rt>ちゅうがっこう</rt></ruby>",
    "高校": "<ruby>高校<rt>こうこう</rt></ruby>",
    "高等学校": "<ruby>高等学校<rt>こうとうがっこう</rt></ruby>",
    "図書館": "<ruby>図書館<rt>としょかん</rt></ruby>",
    "病院": "<ruby>病院<rt>びょういん</rt></ruby>",
    "銀行": "<ruby>銀行<rt>ぎんこう</rt></ruby>",
    "郵便局": "<ruby>郵便局<rt>ゆうびんきょく</rt></ruby>",
    "百貨店": "<ruby>百貨店<rt>ひゃっかてん</rt></ruby>",
    "デパート": "デパート",
    "食堂": "<ruby>食堂<rt>しょくどう</rt></ruby>",
    "公園": "<ruby>公園<rt>こうえん</rt></ruby>",
    "空港": "<ruby>空港<rt>くうこう</rt></ruby>",
    "会社": "<ruby>会社<rt>かいしゃ</rt></ruby>",
    "電話": "<ruby>電話<rt>でんわ</rt></ruby>",
    "電車": "<ruby>電車<rt>でんしゃ</rt></ruby>",
    "地下鉄": "<ruby>地下鉄<rt>ちかてつ</rt></ruby>",
    "自転車": "<ruby>自転車<rt>じてんしゃ</rt></ruby>",
    "飛行機": "<ruby>飛行機<rt>ひこうき</rt></ruby>",
    "新幹線": "<ruby>新幹線<rt>しんかんせん</rt></ruby>",
    "駐車場": "<ruby>駐車場<rt>ちゅうしゃじょう</rt></ruby>",
    "美術館": "<ruby>美術館<rt>びじゅつかん</rt></ruby>",
    "博物館": "<ruby>博物館<rt>はくぶつかん</rt></ruby>",

    // Bahasa & studi
    "日本語": "<ruby>日本語<rt>にほんご</rt></ruby>",
    "英語": "<ruby>英語<rt>えいご</rt></ruby>",
    "中国語": "<ruby>中国語<rt>ちゅうごくご</rt></ruby>",
    "韓国語": "<ruby>韓国語<rt>かんこくご</rt></ruby>",
    "外国語": "<ruby>外国語<rt>がいこくご</rt></ruby>",
    "数学": "<ruby>数学<rt>すうがく</rt></ruby>",
    "化学": "<ruby>化学<rt>かがく</rt></ruby>",
    "科学": "<ruby>科学<rt>かがく</rt></ruby>",
    "音楽": "<ruby>音楽<rt>おんがく</rt></ruby>",
    "体育": "<ruby>体育<rt>たいいく</rt></ruby>",
    "歴史": "<ruby>歴史<rt>れきし</rt></ruby>",
    "地理": "<ruby>地理<rt>ちり</rt></ruby>",
    "社会": "<ruby>社会<rt>しゃかい</rt></ruby>",

    // Makanan & minuman
    "料理": "<ruby>料理<rt>りょうり</rt></ruby>",
    "野菜": "<ruby>野菜<rt>やさい</rt></ruby>",
    "果物": "<ruby>果物<rt>くだもの</rt></ruby>",
    "牛乳": "<ruby>牛乳<rt>ぎゅうにゅう</rt></ruby>",
    "水道水": "<ruby>水道水<rt>すいどうすい</rt></ruby>",
    "定食": "<ruby>定食<rt>ていしょく</rt></ruby>",
    "弁当": "<ruby>弁当<rt>べんとう</rt></ruby>",

    // Benda sehari-hari
    "電気": "<ruby>電気<rt>でんき</rt></ruby>",
    "冷蔵庫": "<ruby>冷蔵庫<rt>れいぞうこ</rt></ruby>",
    "洗濯機": "<ruby>洗濯機<rt>せんたくき</rt></ruby>",
    "掃除機": "<ruby>掃除機<rt>そうじき</rt></ruby>",
    "新聞": "<ruby>新聞<rt>しんぶん</rt></ruby>",
    "雑誌": "<ruby>雑誌<rt>ざっし</rt></ruby>",
    "眼鏡": "<ruby>眼鏡<rt>めがね</rt></ruby>",
    "財布": "<ruby>財布<rt>さいふ</rt></ruby>",
    "切符": "<ruby>切符<rt>きっぷ</rt></ruby>",
    "手紙": "<ruby>手紙<rt>てがみ</rt></ruby>",
    "封筒": "<ruby>封筒<rt>ふうとう</rt></ruby>",
    "辞書": "<ruby>辞書<rt>じしょ</rt></ruby>",

    // Kata sifat majemuk
    "大切": "<ruby>大切<rt>たいせつ</rt></ruby>",
    "大丈夫": "<ruby>大丈夫<rt>だいじょうぶ</rt></ruby>",
    "大変": "<ruby>大変<rt>たいへん</rt></ruby>",
    "大好き": "<ruby>大好<rt>だいす</rt></ruby>き",
    "大嫌い": "<ruby>大嫌<rt>だいきら</rt></ruby>い",
    "上手": "<ruby>上手<rt>じょうず</rt></ruby>",
    "下手": "<ruby>下手<rt>へた</rt></ruby>",
    "簡単": "<ruby>簡単<rt>かんたん</rt></ruby>",
    "便利": "<ruby>便利<rt>べんり</rt></ruby>",
    "不便": "<ruby>不便<rt>ふべん</rt></ruby>",
    "正確": "<ruby>正確<rt>せいかく</rt></ruby>",
    "元気": "<ruby>元気<rt>げんき</rt></ruby>",
    "大事": "<ruby>大事<rt>だいじ</rt></ruby>",
    "素敵": "<ruby>素敵<rt>すてき</rt></ruby>",
    "親切": "<ruby>親切<rt>しんせつ</rt></ruby>",
    "丁寧": "<ruby>丁寧<rt>ていねい</rt></ruby>",
    "有名": "<ruby>有名<rt>ゆうめい</rt></ruby>",
    "特別": "<ruby>特別<rt>とくべつ</rt></ruby>",
    "普通": "<ruby>普通<rt>ふつう</rt></ruby>",
    "自由": "<ruby>自由<rt>じゆう</rt></ruby>",
    "安全": "<ruby>安全<rt>あんぜん</rt></ruby>",
    "危険": "<ruby>危険<rt>きけん</rt></ruby>",
    "必要": "<ruby>必要<rt>ひつよう</rt></ruby>",
    "大切な": "<ruby>大切<rt>たいせつ</rt></ruby>な",

    // Kata keterangan & penghubung
    "調子": "<ruby>調子<rt>ちょうし</rt></ruby>",
    "季節": "<ruby>季節<rt>きせつ</rt></ruby>",
    "将来": "<ruby>将来<rt>しょうらい</rt></ruby>",
    "予定": "<ruby>予定<rt>よてい</rt></ruby>",
    "一番": "<ruby>一番<rt>いちばん</rt></ruby>",
    "世界": "<ruby>世界<rt>せかい</rt></ruby>",
    "文化": "<ruby>文化<rt>ぶんか</rt></ruby>",
    "一緒": "<ruby>一緒<rt>いっしょ</rt></ruby>",
    "少々": "<ruby>少々<rt>しょうしょう</rt></ruby>",

    // Orang & masyarakat
    "学生": "<ruby>学生<rt>がくせい</rt></ruby>",
    "先生": "<ruby>先生<rt>せんせい</rt></ruby>",
    "友達": "<ruby>友達<rt>ともだち</rt></ruby>",
    "外国人": "<ruby>外国人<rt>がいこくじん</rt></ruby>",
    "日本人": "<ruby>日本人<rt>にほんじん</rt></ruby>",
    "店員": "<ruby>店員<rt>てんいん</rt></ruby>",
    "会社員": "<ruby>会社員<rt>かいしゃいん</rt></ruby>",
    "医者": "<ruby>医者<rt>いしゃ</rt></ruby>",
    "看護師": "<ruby>看護師<rt>かんごし</rt></ruby>",
    "警察官": "<ruby>警察官<rt>けいさつかん</rt></ruby>",

    // Kota Jepang
    "東京": "<ruby>東京<rt>とうきょう</rt></ruby>",
    "大阪": "<ruby>大阪<rt>おおさか</rt></ruby>",
    "京都": "<ruby>京都<rt>きょうと</rt></ruby>",
    "名古屋": "<ruby>名古屋<rt>なごや</rt></ruby>",
    "横浜": "<ruby>横浜<rt>よこはま</rt></ruby>",
    "神戸": "<ruby>神戸<rt>こうべ</rt></ruby>",
    "広島": "<ruby>広島<rt>ひろしま</rt></ruby>",
    "福岡": "<ruby>福岡<rt>ふくおか</rt></ruby>",
    "北海道": "<ruby>北海道<rt>ほっかいどう</rt></ruby>",
    "沖縄": "<ruby>沖縄<rt>おきなわ</rt></ruby>",
    "日本": "<ruby>日本<rt>にほん</rt></ruby>",

    // Alam & cuaca
    "天気": "<ruby>天気<rt>てんき</rt></ruby>",
    "天気予報": "<ruby>天気予報<rt>てんきよほう</rt></ruby>",
    "紅葉": "<ruby>紅葉<rt>こうよう</rt></ruby>",

    // Kesehatan & tubuh
    "頭痛": "<ruby>頭痛<rt>ずつう</rt></ruby>",
    "腹痛": "<ruby>腹痛<rt>ふくつう</rt></ruby>",

    // Kegiatan
    "勉強": "<ruby>勉強<rt>べんきょう</rt></ruby>",
    "練習": "<ruby>練習<rt>れんしゅう</rt></ruby>",
    "運動": "<ruby>運動<rt>うんどう</rt></ruby>",
    "仕事": "<ruby>仕事<rt>しごと</rt></ruby>",
    "掃除": "<ruby>掃除<rt>そうじ</rt></ruby>",
    "旅行": "<ruby>旅行<rt>りょこう</rt></ruby>",
    "趣味": "<ruby>趣味<rt>しゅみ</rt></ruby>",
    "映画": "<ruby>映画<rt>えいが</rt></ruby>",
    "買い物": "<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>",
    "散歩": "<ruby>散歩<rt>さんぽ</rt></ruby>",
    "水泳": "<ruby>水泳<rt>すいえい</rt></ruby>",
    "料理": "<ruby>料理<rt>りょうり</rt></ruby>",
    "読書": "<ruby>読書<rt>どくしょ</rt></ruby>",
    "旅行": "<ruby>旅行<rt>りょこう</rt></ruby>",

    // ── KATA MAJEMUK N4 ───────────────────────────────────────────────────────

    "経験": "<ruby>経験<rt>けいけん</rt></ruby>",
    "関係": "<ruby>関係<rt>かんけい</rt></ruby>",
    "関心": "<ruby>関心<rt>かんしん</rt></ruby>",
    "意味": "<ruby>意味<rt>いみ</rt></ruby>",
    "意見": "<ruby>意見<rt>いけん</rt></ruby>",
    "意思": "<ruby>意思<rt>いし</rt></ruby>",
    "考え": "<ruby>考<rt>かんが</rt></ruby>え",
    "気持ち": "<ruby>気持<rt>きも</rt></ruby>ち",
    "気分": "<ruby>気分<rt>きぶん</rt></ruby>",
    "心配": "<ruby>心配<rt>しんぱい</rt></ruby>",
    "感情": "<ruby>感情<rt>かんじょう</rt></ruby>",
    "感謝": "<ruby>感謝<rt>かんしゃ</rt></ruby>",
    "注意": "<ruby>注意<rt>ちゅうい</rt></ruby>",
    "注文": "<ruby>注文<rt>ちゅうもん</rt></ruby>",
    "連絡": "<ruby>連絡<rt>れんらく</rt></ruby>",
    "説明": "<ruby>説明<rt>せつめい</rt></ruby>",
    "相談": "<ruby>相談<rt>そうだん</rt></ruby>",
    "準備": "<ruby>準備<rt>じゅんび</rt></ruby>",
    "計画": "<ruby>計画<rt>けいかく</rt></ruby>",
    "決定": "<ruby>決定<rt>けってい</rt></ruby>",
    "確認": "<ruby>確認<rt>かくにん</rt></ruby>",
    "記念": "<ruby>記念<rt>きねん</rt></ruby>",
    "記録": "<ruby>記録<rt>きろく</rt></ruby>",
    "成功": "<ruby>成功<rt>せいこう</rt></ruby>",
    "失敗": "<ruby>失敗<rt>しっぱい</rt></ruby>",
    "問題": "<ruby>問題<rt>もんだい</rt></ruby>",
    "原因": "<ruby>原因<rt>げんいん</rt></ruby>",
    "結果": "<ruby>結果<rt>けっか</rt></ruby>",
    "理由": "<ruby>理由<rt>りゆう</rt></ruby>",
    "目的": "<ruby>目的<rt>もくてき</rt></ruby>",
    "方法": "<ruby>方法<rt>ほうほう</rt></ruby>",
    "場合": "<ruby>場合<rt>ばあい</rt></ruby>",
    "以前": "<ruby>以前<rt>いぜん</rt></ruby>",
    "以後": "<ruby>以後<rt>いご</rt></ruby>",
    "以来": "<ruby>以来<rt>いらい</rt></ruby>",
    "最近": "<ruby>最近<rt>さいきん</rt></ruby>",
    "最後": "<ruby>最後<rt>さいご</rt></ruby>",
    "最初": "<ruby>最初<rt>さいしょ</rt></ruby>",
    "最大": "<ruby>最大<rt>さいだい</rt></ruby>",
    "最小": "<ruby>最小<rt>さいしょう</rt></ruby>",
    "最高": "<ruby>最高<rt>さいこう</rt></ruby>",
    "最低": "<ruby>最低<rt>さいてい</rt></ruby>",
    "合格": "<ruby>合格<rt>ごうかく</rt></ruby>",
    "不合格": "<ruby>不合格<rt>ふごうかく</rt></ruby>",
    "試験": "<ruby>試験<rt>しけん</rt></ruby>",
    "卒業": "<ruby>卒業<rt>そつぎょう</rt></ruby>",
    "入学": "<ruby>入学<rt>にゅうがく</rt></ruby>",
    "留学": "<ruby>留学<rt>りゅうがく</rt></ruby>",
    "授業": "<ruby>授業<rt>じゅぎょう</rt></ruby>",
    "宿題": "<ruby>宿題<rt>しゅくだい</rt></ruby>",
    "教室": "<ruby>教室<rt>きょうしつ</rt></ruby>",
    "黒板": "<ruby>黒板<rt>こくばん</rt></ruby>",
    "消しゴム": "<ruby>消<rt>け</rt></ruby>しゴム",
    "返事": "<ruby>返事<rt>へんじ</rt></ruby>",
    "都合": "<ruby>都合<rt>つごう</rt></ruby>",
    "様子": "<ruby>様子<rt>ようす</rt></ruby>",
    "生活": "<ruby>生活<rt>せいかつ</rt></ruby>",
    "生命": "<ruby>生命<rt>せいめい</rt></ruby>",
    "経済": "<ruby>経済<rt>けいざい</rt></ruby>",
    "政治": "<ruby>政治<rt>せいじ</rt></ruby>",
    "社会": "<ruby>社会<rt>しゃかい</rt></ruby>",
    "国際": "<ruby>国際<rt>こくさい</rt></ruby>",
    "世代": "<ruby>世代<rt>せだい</rt></ruby>",
    "現代": "<ruby>現代<rt>げんだい</rt></ruby>",
    "伝統": "<ruby>伝統<rt>でんとう</rt></ruby>",
    "文明": "<ruby>文明<rt>ぶんめい</rt></ruby>",
    "技術": "<ruby>技術<rt>ぎじゅつ</rt></ruby>",
    "科学技術": "<ruby>科学技術<rt>かがくぎじゅつ</rt></ruby>",
    "交通": "<ruby>交通<rt>こうつう</rt></ruby>",
    "交通機関": "<ruby>交通機関<rt>こうつうきかん</rt></ruby>",
    "環境": "<ruby>環境<rt>かんきょう</rt></ruby>",
    "自然": "<ruby>自然<rt>しぜん</rt></ruby>",
    "地球": "<ruby>地球<rt>ちきゅう</rt></ruby>",
    "宇宙": "<ruby>宇宙<rt>うちゅう</rt></ruby>",
    "台風": "<ruby>台風<rt>たいふう</rt></ruby>",
    "地震": "<ruby>地震<rt>じしん</rt></ruby>",
    "火山": "<ruby>火山<rt>かざん</rt></ruby>",
    "海岸": "<ruby>海岸<rt>かいがん</rt></ruby>",

    // Tubuh (N4)
    "頭": "<ruby>頭<rt>あたま</rt></ruby>",
    "顔": "<ruby>顔<rt>かお</rt></ruby>",
    "目": "<ruby>目<rt>め</rt></ruby>",
    "耳": "<ruby>耳<rt>みみ</rt></ruby>",
    "鼻": "<ruby>鼻<rt>はな</rt></ruby>",
    "口": "<ruby>口<rt>くち</rt></ruby>",
    "首": "<ruby>首<rt>くび</rt></ruby>",
    "肩": "<ruby>肩<rt>かた</rt></ruby>",
    "腕": "<ruby>腕<rt>うで</rt></ruby>",
    "手": "<ruby>手<rt>て</rt></ruby>",
    "指": "<ruby>指<rt>ゆび</rt></ruby>",
    "腹": "<ruby>腹<rt>はら</rt></ruby>",
    "背中": "<ruby>背中<rt>せなか</rt></ruby>",
    "足": "<ruby>足<rt>あし</rt></ruby>",
    "体": "<ruby>体<rt>からだ</rt></ruby>",
    "心": "<ruby>心<rt>こころ</rt></ruby>",
    "声": "<ruby>声<rt>こえ</rt></ruby>",
    "歯": "<ruby>歯<rt>は</rt></ruby>",
    "舌": "<ruby>舌<rt>した</rt></ruby>",
    "皮膚": "<ruby>皮膚<rt>ひふ</rt></ruby>",

    // ── KATA SIFAT (I-ADJECTIVE) ──────────────────────────────────────────────

    "新しい": "<ruby>新<rt>あたら</rt></ruby>しい",
    "古い": "<ruby>古<rt>ふる</rt></ruby>い",
    "大きい": "<ruby>大<rt>おお</rt></ruby>きい",
    "小さい": "<ruby>小<rt>ちい</rt></ruby>さい",
    "長い": "<ruby>長<rt>なが</rt></ruby>い",
    "短い": "<ruby>短<rt>みじか</rt></ruby>い",
    "高い": "<ruby>高<rt>たか</rt></ruby>い",
    "低い": "<ruby>低<rt>ひく</rt></ruby>い",
    "安い": "<ruby>安<rt>やす</rt></ruby>い",
    "広い": "<ruby>広<rt>ひろ</rt></ruby>い",
    "狭い": "<ruby>狭<rt>せま</rt></ruby>い",
    "遠い": "<ruby>遠<rt>とお</rt></ruby>い",
    "近い": "<ruby>近<rt>ちか</rt></ruby>い",
    "重い": "<ruby>重<rt>おも</rt></ruby>い",
    "軽い": "<ruby>軽<rt>かる</rt></ruby>い",
    "難しい": "<ruby>難<rt>むずか</rt></ruby>しい",
    "易しい": "<ruby>易<rt>やさ</rt></ruby>しい",
    "優しい": "<ruby>優<rt>やさ</rt></ruby>しい",
    "厳しい": "<ruby>厳<rt>きび</rt></ruby>しい",
    "楽しい": "<ruby>楽<rt>たの</rt></ruby>しい",
    "悲しい": "<ruby>悲<rt>かな</rt></ruby>しい",
    "嬉しい": "<ruby>嬉<rt>うれ</rt></ruby>しい",
    "暖かい": "<ruby>暖<rt>あたた</rt></ruby>かい",
    "涼しい": "<ruby>涼<rt>すず</rt></ruby>しい",
    "暑い": "<ruby>暑<rt>あつ</rt></ruby>い",
    "寒い": "<ruby>寒<rt>さむ</rt></ruby>い",
    "熱い": "<ruby>熱<rt>あつ</rt></ruby>い",
    "冷たい": "<ruby>冷<rt>つめ</rt></ruby>たい",
    "甘い": "<ruby>甘<rt>あま</rt></ruby>い",
    "辛い": "<ruby>辛<rt>から</rt></ruby>い",
    "酸っぱい": "<ruby>酸<rt>す</rt></ruby>っぱい",
    "苦い": "<ruby>苦<rt>にが</rt></ruby>い",
    "美味しい": "<ruby>美味<rt>おい</rt></ruby>しい",
    "不味い": "<ruby>不味<rt>まず</rt></ruby>い",
    "早い": "<ruby>早<rt>はや</rt></ruby>い",
    "遅い": "<ruby>遅<rt>おそ</rt></ruby>い",
    "速い": "<ruby>速<rt>はや</rt></ruby>い",
    "忙しい": "<ruby>忙<rt>いそが</rt></ruby>しい",
    "暇": "<ruby>暇<rt>ひま</rt></ruby>",
    "面白い": "<ruby>面白<rt>おもしろ</rt></ruby>い",
    "つまらない": "つまらない",
    "強い": "<ruby>強<rt>つよ</rt></ruby>い",
    "弱い": "<ruby>弱<rt>よわ</rt></ruby>い",
    "痛い": "<ruby>痛<rt>いた</rt></ruby>い",
    "危ない": "<ruby>危<rt>あぶ</rt></ruby>ない",
    "正しい": "<ruby>正<rt>ただ</rt></ruby>しい",
    "欲しい": "<ruby>欲<rt>ほ</rt></ruby>しい",
    "嬉しい": "<ruby>嬉<rt>うれ</rt></ruby>しい",
    "恥ずかしい": "<ruby>恥<rt>は</rt></ruby>ずかしい",
    "眠い": "<ruby>眠<rt>ねむ</rt></ruby>い",
    "多い": "<ruby>多<rt>おお</rt></ruby>い",
    "少ない": "<ruby>少<rt>すく</rt></ruby>ない",

    // Infleksi i-adjective lampau
    "安かった": "<ruby>安<rt>やす</rt></ruby>かった",
    "早く": "<ruby>早<rt>はや</rt></ruby>く",
    "近く": "<ruby>近<rt>ちか</rt></ruby>く",
    "簡単に": "<ruby>簡単<rt>かんたん</rt></ruby>に",

    // ── KATA KERJA & INFLEKSI ─────────────────────────────────────────────────

    // 食べる
    "食べます": "<ruby>食<rt>た</rt></ruby>べます",
    "食べた": "<ruby>食<rt>た</rt></ruby>べた",
    "食べて": "<ruby>食<rt>た</rt></ruby>べて",
    "食べる": "<ruby>食<rt>た</rt></ruby>べる",
    "食べない": "<ruby>食<rt>た</rt></ruby>べない",
    "食べたい": "<ruby>食<rt>た</rt></ruby>べたい",

    // 飲む
    "飲みます": "<ruby>飲<rt>の</rt></ruby>みます",
    "飲んだ": "<ruby>飲<rt>の</rt></ruby>んだ",
    "飲んで": "<ruby>飲<rt>の</rt></ruby>んで",
    "飲む": "<ruby>飲<rt>の</rt></ruby>む",
    "飲まない": "<ruby>飲<rt>の</rt></ruby>まない",

    // 行く
    "行きます": "<ruby>行<rt>い</rt></ruby>きます",
    "行った": "<ruby>行<rt>い</rt></ruby>った",
    "行って": "<ruby>行<rt>い</rt></ruby>って",
    "行く": "<ruby>行<rt>い</rt></ruby>く",
    "行かない": "<ruby>行<rt>い</rt></ruby>かない",
    "行きたい": "<ruby>行<rt>い</rt></ruby>きたい",

    // 来る
    "来ます": "<ruby>来<rt>き</rt></ruby>ます",
    "来た": "<ruby>来<rt>き</rt></ruby>た",
    "来て": "<ruby>来<rt>き</rt></ruby>て",
    "来る": "<ruby>来<rt>く</rt></ruby>る",
    "来ない": "<ruby>来<rt>こ</rt></ruby>ない",

    // 帰る
    "帰ります": "<ruby>帰<rt>かえ</rt></ruby>ります",
    "帰った": "<ruby>帰<rt>かえ</rt></ruby>った",
    "帰って": "<ruby>帰<rt>かえ</rt></ruby>って",
    "帰る": "<ruby>帰<rt>かえ</rt></ruby>る",

    // 見る
    "見ます": "<ruby>見<rt>み</rt></ruby>ます",
    "見た": "<ruby>見<rt>み</rt></ruby>た",
    "見て": "<ruby>見<rt>み</rt></ruby>て",
    "見る": "<ruby>見<rt>み</rt></ruby>る",
    "見ない": "<ruby>見<rt>み</rt></ruby>ない",

    // 聞く
    "聞きます": "<ruby>聞<rt>き</rt></ruby>きます",
    "聞いた": "<ruby>聞<rt>き</rt></ruby>いた",
    "聞いて": "<ruby>聞<rt>き</rt></ruby>いて",
    "聞く": "<ruby>聞<rt>き</rt></ruby>く",

    // 読む
    "読みます": "<ruby>読<rt>よ</rt></ruby>みます",
    "読んだ": "<ruby>読<rt>よ</rt></ruby>んだ",
    "読んで": "<ruby>読<rt>よ</rt></ruby>んで",
    "読む": "<ruby>読<rt>よ</rt></ruby>む",

    // 書く
    "書きます": "<ruby>書<rt>か</rt></ruby>きます",
    "書いた": "<ruby>書<rt>か</rt></ruby>いた",
    "書いて": "<ruby>書<rt>か</rt></ruby>いて",
    "書く": "<ruby>書<rt>か</rt></ruby>く",

    // 話す
    "話します": "<ruby>話<rt>はな</rt></ruby>します",
    "話した": "<ruby>話<rt>はな</rt></ruby>した",
    "話して": "<ruby>話<rt>はな</rt></ruby>して",
    "話す": "<ruby>話<rt>はな</rt></ruby>す",

    // 買う
    "買います": "<ruby>買<rt>か</rt></ruby>います",
    "買った": "<ruby>買<rt>か</rt></ruby>った",
    "買って": "<ruby>買<rt>か</rt></ruby>って",
    "買う": "<ruby>買<rt>か</rt></ruby>う",

    // 会う
    "会います": "<ruby>会<rt>あ</rt></ruby>います",
    "会った": "<ruby>会<rt>あ</rt></ruby>った",
    "会って": "<ruby>会<rt>あ</rt></ruby>って",
    "会う": "<ruby>会<rt>あ</rt></ruby>う",

    // 言う
    "言いました": "<ruby>言<rt>い</rt></ruby>いました",
    "言います": "<ruby>言<rt>い</rt></ruby>います",
    "言った": "<ruby>言<rt>い</rt></ruby>った",
    "言って": "<ruby>言<rt>い</rt></ruby>って",
    "言う": "<ruby>言<rt>い</rt></ruby>う",

    // 寝る
    "寝ます": "<ruby>寝<rt>ね</rt></ruby>ます",
    "寝た": "<ruby>寝<rt>ね</rt></ruby>た",
    "寝て": "<ruby>寝<rt>ね</rt></ruby>て",
    "寝る": "<ruby>寝<rt>ね</rt></ruby>る",

    // 起きる
    "起きます": "<ruby>起<rt>お</rt></ruby>きます",
    "起きた": "<ruby>起<rt>お</rt></ruby>きた",
    "起きて": "<ruby>起<rt>お</rt></ruby>きて",
    "起きる": "<ruby>起<rt>お</rt></ruby>きる",

    // 教える
    "教えます": "<ruby>教<rt>おし</rt></ruby>えます",
    "教えた": "<ruby>教<rt>おし</rt></ruby>えた",
    "教えて": "<ruby>教<rt>おし</rt></ruby>えて",
    "教える": "<ruby>教<rt>おし</rt></ruby>える",

    // 働く
    "働きます": "<ruby>働<rt>はたら</rt></ruby>きます",
    "働いた": "<ruby>働<rt>はたら</rt></ruby>いた",
    "働いて": "<ruby>働<rt>はたら</rt></ruby>いて",
    "働く": "<ruby>働<rt>はたら</rt></ruby>く",

    // 使う
    "使います": "<ruby>使<rt>つか</rt></ruby>います",
    "使った": "<ruby>使<rt>つか</rt></ruby>った",
    "使って": "<ruby>使<rt>つか</rt></ruby>って",
    "使う": "<ruby>使<rt>つか</rt></ruby>う",

    // 磨く
    "磨きます": "<ruby>磨<rt>みが</rt></ruby>きます",
    "磨く": "<ruby>磨<rt>みが</rt></ruby>く",

    // 驚く
    "驚きます": "<ruby>驚<rt>おどろ</rt></ruby>きます",
    "驚いた": "<ruby>驚<rt>おどろ</rt></ruby>いた",
    "驚く": "<ruby>驚<rt>おどろ</rt></ruby>く",

    // 歌う
    "歌います": "<ruby>歌<rt>うた</rt></ruby>います",
    "歌った": "<ruby>歌<rt>うた</rt></ruby>った",
    "歌ったり": "<ruby>歌<rt>うた</rt></ruby>ったり",
    "歌って": "<ruby>歌<rt>うた</rt></ruby>って",
    "歌う": "<ruby>歌<rt>うた</rt></ruby>う",

    // N4 動詞
    "覚える": "<ruby>覚<rt>おぼ</rt></ruby>える",
    "覚えた": "<ruby>覚<rt>おぼ</rt></ruby>えた",
    "覚えて": "<ruby>覚<rt>おぼ</rt></ruby>えて",
    "忘れる": "<ruby>忘<rt>わす</rt></ruby>れる",
    "忘れた": "<ruby>忘<rt>わす</rt></ruby>れた",
    "止まる": "<ruby>止<rt>と</rt></ruby>まる",
    "止まった": "<ruby>止<rt>と</rt></ruby>まった",
    "止める": "<ruby>止<rt>と</rt></ruby>める",
    "始まる": "<ruby>始<rt>はじ</rt></ruby>まる",
    "始める": "<ruby>始<rt>はじ</rt></ruby>める",
    "終わる": "<ruby>終<rt>お</rt></ruby>わる",
    "終わった": "<ruby>終<rt>お</rt></ruby>わった",
    "終わって": "<ruby>終<rt>お</rt></ruby>わって",
    "決める": "<ruby>決<rt>き</rt></ruby>める",
    "決めた": "<ruby>決<rt>き</rt></ruby>めた",
    "考える": "<ruby>考<rt>かんが</rt></ruby>える",
    "考えた": "<ruby>考<rt>かんが</rt></ruby>えた",
    "調べる": "<ruby>調<rt>しら</rt></ruby>べる",
    "調べた": "<ruby>調<rt>しら</rt></ruby>べた",
    "伝える": "<ruby>伝<rt>つた</rt></ruby>える",
    "助ける": "<ruby>助<rt>たす</rt></ruby>ける",
    "助かる": "<ruby>助<rt>たす</rt></ruby>かる",
    "集める": "<ruby>集<rt>あつ</rt></ruby>める",
    "集まる": "<ruby>集<rt>あつ</rt></ruby>まる",
    "比べる": "<ruby>比<rt>くら</rt></ruby>べる",
    "変える": "<ruby>変<rt>か</rt></ruby>える",
    "変わる": "<ruby>変<rt>か</rt></ruby>わる",
    "続ける": "<ruby>続<rt>つづ</rt></ruby>ける",
    "続く": "<ruby>続<rt>つづ</rt></ruby>く",
    "乗る": "<ruby>乗<rt>の</rt></ruby>る",
    "乗った": "<ruby>乗<rt>の</rt></ruby>った",
    "降りる": "<ruby>降<rt>お</rt></ruby>りる",
    "降りた": "<ruby>降<rt>お</rt></ruby>りた",
    "走る": "<ruby>走<rt>はし</rt></ruby>る",
    "走った": "<ruby>走<rt>はし</rt></ruby>った",
    "歩く": "<ruby>歩<rt>ある</rt></ruby>く",
    "歩いた": "<ruby>歩<rt>ある</rt></ruby>いた",
    "泳ぐ": "<ruby>泳<rt>およ</rt></ruby>ぐ",
    "泳いだ": "<ruby>泳<rt>およ</rt></ruby>いだ",
    "待つ": "<ruby>待<rt>ま</rt></ruby>つ",
    "待った": "<ruby>待<rt>ま</rt></ruby>った",
    "持つ": "<ruby>持<rt>も</rt></ruby>つ",
    "持った": "<ruby>持<rt>も</rt></ruby>った",
    "切る": "<ruby>切<rt>き</rt></ruby>る",
    "切った": "<ruby>切<rt>き</rt></ruby>った",
    "送る": "<ruby>送<rt>おく</rt></ruby>る",
    "送った": "<ruby>送<rt>おく</rt></ruby>った",
    "受ける": "<ruby>受<rt>う</rt></ruby>ける",
    "受けた": "<ruby>受<rt>う</rt></ruby>けた",
    "開ける": "<ruby>開<rt>あ</rt></ruby>ける",
    "開けた": "<ruby>開<rt>あ</rt></ruby>けた",
    "閉める": "<ruby>閉<rt>し</rt></ruby>める",
    "閉めた": "<ruby>閉<rt>し</rt></ruby>めた",
    "開く": "<ruby>開<rt>あ</rt></ruby>く",
    "閉まる": "<ruby>閉<rt>し</rt></ruby>まる",
    "入れる": "<ruby>入<rt>い</rt></ruby>れる",
    "入れた": "<ruby>入<rt>い</rt></ruby>れた",
    "出す": "<ruby>出<rt>だ</rt></ruby>す",
    "出した": "<ruby>出<rt>だ</rt></ruby>した",
    "出る": "<ruby>出<rt>で</rt></ruby>る",
    "出た": "<ruby>出<rt>で</rt></ruby>た",
    "入る": "<ruby>入<rt>はい</rt></ruby>る",
    "入った": "<ruby>入<rt>はい</rt></ruby>った",
    "貸す": "<ruby>貸<rt>か</rt></ruby>す",
    "借りる": "<ruby>借<rt>か</rt></ruby>りる",
    "借りた": "<ruby>借<rt>か</rt></ruby>りた",
    "返す": "<ruby>返<rt>かえ</rt></ruby>す",
    "返した": "<ruby>返<rt>かえ</rt></ruby>した",
    "洗う": "<ruby>洗<rt>あら</rt></ruby>う",
    "洗った": "<ruby>洗<rt>あら</rt></ruby>った",
    "掃除する": "<ruby>掃除<rt>そうじ</rt></ruby>する",
    "練習する": "<ruby>練習<rt>れんしゅう</rt></ruby>する",
    "勉強する": "<ruby>勉強<rt>べんきょう</rt></ruby>する",
    "運動する": "<ruby>運動<rt>うんどう</rt></ruby>する",
    "旅行する": "<ruby>旅行<rt>りょこう</rt></ruby>する",
    "結婚する": "<ruby>結婚<rt>けっこん</rt></ruby>する",
    "離婚する": "<ruby>離婚<rt>りこん</rt></ruby>する",
    "卒業する": "<ruby>卒業<rt>そつぎょう</rt></ruby>する",
    "入学する": "<ruby>入学<rt>にゅうがく</rt></ruby>する",
    "連絡する": "<ruby>連絡<rt>れんらく</rt></ruby>する",
    "説明する": "<ruby>説明<rt>せつめい</rt></ruby>する",
    "相談する": "<ruby>相談<rt>そうだん</rt></ruby>する",
    "準備する": "<ruby>準備<rt>じゅんび</rt></ruby>する",
    "確認する": "<ruby>確認<rt>かくにん</rt></ruby>する",
    "注文する": "<ruby>注文<rt>ちゅうもん</rt></ruby>する",

    // ── KATA TUNGGAL & KANJI DASAR ───────────────────────────────────────────

    // Musim & alam
    "春": "<ruby>春<rt>はる</rt></ruby>",
    "夏": "<ruby>夏<rt>なつ</rt></ruby>",
    "秋": "<ruby>秋<rt>あき</rt></ruby>",
    "冬": "<ruby>冬<rt>ふゆ</rt></ruby>",
    "雪": "<ruby>雪<rt>ゆき</rt></ruby>",
    "雨": "<ruby>雨<rt>あめ</rt></ruby>",
    "風": "<ruby>風<rt>かぜ</rt></ruby>",
    "雲": "<ruby>雲<rt>くも</rt></ruby>",
    "空": "<ruby>空<rt>そら</rt></ruby>",
    "星": "<ruby>星<rt>ほし</rt></ruby>",
    "月": "<ruby>月<rt>つき</rt></ruby>",
    "太陽": "<ruby>太陽<rt>たいよう</rt></ruby>",
    "海": "<ruby>海<rt>うみ</rt></ruby>",
    "山": "<ruby>山<rt>やま</rt></ruby>",
    "川": "<ruby>川<rt>かわ</rt></ruby>",
    "池": "<ruby>池<rt>いけ</rt></ruby>",
    "湖": "<ruby>湖<rt>みずうみ</rt></ruby>",
    "森": "<ruby>森<rt>もり</rt></ruby>",
    "林": "<ruby>林<rt>はやし</rt></ruby>",
    "花": "<ruby>花<rt>はな</rt></ruby>",
    "木": "<ruby>木<rt>き</rt></ruby>",
    "桜": "<ruby>桜<rt>さくら</rt></ruby>",
    "草": "<ruby>草<rt>くさ</rt></ruby>",
    "土": "<ruby>土<rt>つち</rt></ruby>",
    "石": "<ruby>石<rt>いし</rt></ruby>",
    "火": "<ruby>火<rt>ひ</rt></ruby>",
    "水": "<ruby>水<rt>みず</rt></ruby>",

    // Makanan (tunggal)
    "魚": "<ruby>魚<rt>さかな</rt></ruby>",
    "肉": "<ruby>肉<rt>にく</rt></ruby>",
    "卵": "<ruby>卵<rt>たまご</rt></ruby>",
    "米": "<ruby>米<rt>こめ</rt></ruby>",
    "麦": "<ruby>麦<rt>むぎ</rt></ruby>",
    "茶": "<ruby>茶<rt>ちゃ</rt></ruby>",
    "酒": "<ruby>酒<rt>さけ</rt></ruby>",
    "塩": "<ruby>塩<rt>しお</rt></ruby>",
    "砂糖": "<ruby>砂糖<rt>さとう</rt></ruby>",
    "箸": "<ruby>箸<rt>はし</rt></ruby>",

    // Kata benda umum
    "本": "<ruby>本<rt>ほん</rt></ruby>",
    "紙": "<ruby>紙<rt>かみ</rt></ruby>",
    "机": "<ruby>机<rt>つくえ</rt></ruby>",
    "椅子": "<ruby>椅子<rt>いす</rt></ruby>",
    "窓": "<ruby>窓<rt>まど</rt></ruby>",
    "戸": "<ruby>戸<rt>と</rt></ruby>",
    "部屋": "<ruby>部屋<rt>へや</rt></ruby>",
    "台所": "<ruby>台所<rt>だいどころ</rt></ruby>",
    "玄関": "<ruby>玄関<rt>げんかん</rt></ruby>",
    "庭": "<ruby>庭<rt>にわ</rt></ruby>",
    "道": "<ruby>道<rt>みち</rt></ruby>",
    "橋": "<ruby>橋<rt>はし</rt></ruby>",
    "町": "<ruby>町<rt>まち</rt></ruby>",
    "村": "<ruby>村<rt>むら</rt></ruby>",
    "国": "<ruby>国<rt>くに</rt></ruby>",
    "地図": "<ruby>地図<rt>ちず</rt></ruby>",
    "写真": "<ruby>写真<rt>しゃしん</rt></ruby>",
    "車": "<ruby>車<rt>くるま</rt></ruby>",
    "船": "<ruby>船<rt>ふね</rt></ruby>",
    "駅": "<ruby>駅<rt>えき</rt></ruby>",
    "客": "<ruby>客<rt>きゃく</rt></ruby>",

    // Orang (tunggal)
    "私": "<ruby>私<rt>わたし</rt></ruby>",
    "父": "<ruby>父<rt>ちち</rt></ruby>",
    "母": "<ruby>母<rt>はは</rt></ruby>",
    "兄": "<ruby>兄<rt>あに</rt></ruby>",
    "姉": "<ruby>姉<rt>あね</rt></ruby>",
    "弟": "<ruby>弟<rt>おとうと</rt></ruby>",
    "妹": "<ruby>妹<rt>いもうと</rt></ruby>",
    "子": "<ruby>子<rt>こ</rt></ruby>",
    "男": "<ruby>男<rt>おとこ</rt></ruby>",
    "女": "<ruby>女<rt>おんな</rt></ruby>",
    "人": "<ruby>人<rt>ひと</rt></ruby>",

    // Angka & satuan
    "百": "<ruby>百<rt>ひゃく</rt></ruby>",
    "千": "<ruby>千<rt>せん</rt></ruby>",
    "万": "<ruby>万<rt>まん</rt></ruby>",
    "億": "<ruby>億<rt>おく</rt></ruby>",
    "半": "<ruby>半<rt>はん</rt></ruby>",
    "一人": "<ruby>一人<rt>ひとり</rt></ruby>",
    "二人": "<ruby>二人<rt>ふたり</rt></ruby>",
    "三人": "<ruby>三<rt>さん</rt></ruby><ruby>人<rt>にん</rt></ruby>",
    "四人": "<ruby>四人<rt>よにん</rt></ruby>",

    // Kata keterangan waktu
    "初めて": "<ruby>初<rt>はじ</rt></ruby>めて",
    "最近": "<ruby>最近<rt>さいきん</rt></ruby>",

    // Kanji tunggal esensial (fallback)
    "天": "<ruby>天<rt>てん</rt></ruby>",
    "気": "<ruby>気<rt>き</rt></ruby>",
    "門": "<ruby>門<rt>もん</rt></ruby>",
    "高": "<ruby>高<rt>たか</rt></ruby>",
    "多": "<ruby>多<rt>おお</rt></ruby>",
    "少": "<ruby>少<rt>すく</rt></ruby>",
    "古": "<ruby>古<rt>ふる</rt></ruby>",
    "長": "<ruby>長<rt>なが</rt></ruby>",
    "短": "<ruby>短<rt>みじか</rt></ruby>",
    "遠": "<ruby>遠<rt>とお</rt></ruby>",
    "広": "<ruby>広<rt>ひろ</rt></ruby>",
    "曜": "<ruby>曜<rt>よう</rt></ruby>",
    "年": "<ruby>年<rt>ねん</rt></ruby>",
    "日": "<ruby>日<rt>ひ</rt></ruby>",
    "時": "<ruby>時<rt>じ</rt></ruby>",
    "分": "<ruby>分<rt>ふん</rt></ruby>",
    "好き": "<ruby>好<rt>す</rt></ruby>き",
};

// ============================================================
// TRIE ENGINE — Longest-match tanpa Regex, O(N) per karakter
// ============================================================

class TrieNode {
    constructor() {
        this.children = Object.create(null);
        this.value = null;   // nilai HTML jika ini akhir kata
    }
}

class FuriganaTrie {
    constructor(map) {
        this.root = new TrieNode();
        for (const [key, val] of Object.entries(map)) {
            let node = this.root;
            for (const ch of key) {
                if (!node.children[ch]) node.children[ch] = new TrieNode();
                node = node.children[ch];
            }
            node.value = val;
        }
    }

    /**
     * Ubah teks biasa menjadi HTML dengan tag <ruby>.
     * Lewati konten yang sudah berada di dalam tag <ruby>…</ruby>.
     * @param {string} text
     * @returns {string}
     */
    convert(text) {
        if (!text) return "";

        const RUBY_OPEN = "<ruby>";
        const RUBY_CLOSE = "</ruby>";
        let result = "";
        let i = 0;

        while (i < text.length) {
            // ── Lewati tag ruby yang sudah ada ──────────────────────────────
            if (text.startsWith(RUBY_OPEN, i)) {
                const end = text.indexOf(RUBY_CLOSE, i);
                if (end !== -1) {
                    result += text.slice(i, end + RUBY_CLOSE.length);
                    i = end + RUBY_CLOSE.length;
                    continue;
                }
            }

            // ── Cari kecocokan terpanjang di Trie ───────────────────────────
            let node = this.root;
            let j = i;
            let lastMatch = null;
            let lastJ = i;

            while (j < text.length && node.children[text[j]]) {
                node = node.children[text[j]];
                j++;
                if (node.value !== null) {
                    lastMatch = node.value;
                    lastJ = j;
                }
            }

            if (lastMatch !== null) {
                result += lastMatch;
                i = lastJ;
            } else {
                result += text[i];
                i++;
            }
        }

        return result;
    }
}

// ── Instansiasi sekali saat modul dimuat (compile-time) ──────────────────────
const trie = new FuriganaTrie(FURIGANA_MAP);

/**
 * Fungsi publik utama.
 * Ganti semua kemunculan kanji/kata dalam FURIGANA_MAP dengan HTML ruby.
 * @param {string} text
 * @returns {string}
 */
export function applyFurigana(text) {
    return trie.convert(text);
}