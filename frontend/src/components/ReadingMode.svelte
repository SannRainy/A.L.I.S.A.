<script>
    import { onMount } from "svelte";
    import { fade } from "svelte/transition";
    import { user } from "../stores/auth_store";

    let passages = [];
    let selectedPassage = null;
    let loading = true;
    let showTranslation = false;
    let unknownWords = [];
    let currentQuestionIndex = 0;
    let answers = [];
    let result = null;
    let submitting = false;
    let selectedLevel = null;

    onMount(async () => {
        await loadPassages();
        loading = false;
    });

    async function loadPassages(level = null) {
        try {
            const url = level
                ? `http://localhost:8000/api/v1/reading/passages?level=${level}`
                : "http://localhost:8000/api/v1/reading/passages";
            const res = await fetch(url);
            const data = await res.json();
            if (data.status === "success") {
                passages = data.passages;
            }
        } catch (e) {
            console.error("Failed to load passages:", e);
        }
    }

    async function selectPassage(passageId) {
        try {
            const res = await fetch(`http://localhost:8000/api/v1/reading/passage/${passageId}`);
            const data = await res.json();
            if (data.status === "success") {
                selectedPassage = data.passage;
                unknownWords = [];
                currentQuestionIndex = 0;
                answers = [];
                result = null;
                showTranslation = false;
            }
        } catch (e) {
            console.error("Failed to load passage:", e);
        }
    }

    function toggleUnknownWord(word) {
        if (unknownWords.includes(word)) {
            unknownWords = unknownWords.filter(w => w !== word);
        } else {
            unknownWords = [...unknownWords, word];
        }
    }

    function answerQuestion(optionIndex) {
        const question = selectedPassage.questions[currentQuestionIndex];
        const isCorrect = optionIndex === question.correct;

        answers.push({
            question_id: question.id,
            selected: optionIndex,
            is_correct: isCorrect,
        });

        if (currentQuestionIndex < selectedPassage.questions.length - 1) {
            currentQuestionIndex++;
        } else {
            submitReading();
        }
    }

    async function submitReading() {
        if (!$user || submitting) return;
        submitting = true;

        try {
            const res = await fetch("http://localhost:8000/api/v1/reading/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: $user.id,
                    passage_id: selectedPassage.id,
                    unknown_words: unknownWords,
                    comprehension_answers: answers,
                }),
            });

            const data = await res.json();
            if (data.status === "success") {
                result = data;
            }
        } catch (e) {
            console.error("Failed to submit reading:", e);
        } finally {
            submitting = false;
        }
    }

    function backToList() {
        selectedPassage = null;
        result = null;
    }

    function parseSegments(text, vocabList) {
        if (!vocabList || vocabList.length === 0) {
            return [{ isVocab: false, text }];
        }
        const sortedVocab = [...vocabList].sort((a, b) => b.word.length - a.word.length);
        const escapedWords = sortedVocab.map(v => v.word.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
        const regex = new RegExp(`(${escapedWords.join('|')})`, 'g');
        const parts = text.split(regex);
        return parts.map(part => {
            const vocabItem = sortedVocab.find(v => v.word === part);
            if (vocabItem) {
                return {
                    isVocab: true,
                    word: vocabItem.word,
                    reading: vocabItem.reading,
                    meaning: vocabItem.meaning
                };
            }
            return {
                isVocab: false,
                text: part
            };
        });
    }

    const FURIGANA_MAP = {
        // Compound words and specific inflections
        "いらっしゃいませ": "いらっしゃいませ",
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
        "歌ったり": "<ruby>歌<rt>うた</rt></ruby>ったり",
        "安かった": "<ruby>安<rt>やす</rt></ruby>かった",
        "十一月": "<ruby>十一月<rt>じゅういちがつ</rt></ruby>",
        "十二月": "<ruby>十二月<rt>じゅうにがつ</rt></ruby>",
        "日本語": "<ruby>日本語<rt>にほんご</rt></ruby>",
        "外国人": "<ruby>外国人<rt>がいこくじん</rt></ruby>",
        "自転車": "<ruby>自転車<rt>じてんしゃ</rt></ruby>",
        "新しい": "<ruby>新<rt>あたら</rt></ruby>しい",
        "買い物": "<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>",
        "日曜日": "<ruby>日曜日<rt>にちようび</rt></ruby>",
        "お母さん": "お<ruby>母<rt>かあ</rt></ruby>さん",
        "教えて": "<ruby>教<rt>おし</rt></ruby>えて",
        "簡単に": "<ruby>簡単<rt>かんたん</rt></ruby>に",
        "簡単": "<ruby>簡単<rt>かんたん</rt></ruby>",
        "練習": "<ruby>練習<rt>れんしゅう</rt></ruby>",
        "食堂": "<ruby>食堂<rt>しょくどう</rt></ruby>",
        "料理": "<ruby>料理<rt>りょうり</rt></ruby>",
        "野菜": "<ruby>野菜<rt>やさい</rt></ruby>",
        "映画": "<ruby>映画<rt>えいが</rt></ruby>",
        "将来": "<ruby>将来<rt>しょうらい</rt></ruby>",
        "会社": "<ruby>会社<rt>かいしゃ</rt></ruby>",
        "学生": "<ruby>学生<rt>がくせい</rt></ruby>",
        "会い": "<ruby>会<rt>あ</rt></ruby>い",
        "見た": "<ruby>見<rt>み</rt></ruby>た",
        "見て": "<ruby>見<rt>み</rt></ruby>て",
        "買い": "<ruby>買<rt>か</rt></ruby>い",
        "早く": "<ruby>早<rt>はや</rt></ruby>く",
        "寝る": "<ruby>寝<rt>ね</rt></ruby>る",
        "今日": "<ruby>今日<rt>きょう</rt></ruby>",
        "日本": "<ruby>日本<rt>にほん</rt></ruby>",
        "好き": "<ruby>好<rt>す</rt>き</ruby>",
        "駅": "<ruby>駅<rt>えき</rt></ruby>",
        "魚": "<ruby>魚<rt>さかな</rt></ruby>",
        "肉": "<ruby>肉<rt>にく</rt></ruby>",
        "私": "<ruby>私<rt>わたし</rt></ruby>",
        "本": "<ruby>本<rt>ほん</rt></ruby>",
        "家": "<ruby>家<rt>いえ</rt></ruby>",
        "前": "<ruby>前<rt>まえ</rt></ruby>",
        "お酒": "お<ruby>酒<rt>さけ</rt></ruby>",
        "学校": "<ruby>学校<rt>がっこう</rt></ruby>",
        "公園": "<ruby>公園<rt>こうえん</rt></ruby>",
        "牛乳": "<ruby>牛乳<rt>ぎゅうにゅう</rt></ruby>",
        "水": "<ruby>水<rt>みず</rt></ruby>",
        "見ること": "<ruby>見<rt>み</rt></ruby>ること",
        "飲むこと": "<ruby>飲<rt>の</rt></ruby>むこと",
        "読むこと": "<ruby>読<rt>よ</rt></ruby>むこと",
        "飲む": "<ruby>飲<rt>の</rt></ruby>む",
        "磨く": "<ruby>磨<rt>みが</rt></ruby>く",
        "歯": "<ruby>歯<rt>は</rt></ruby>",
        "七時": "<ruby>七時<rt>しちじ</rt></ruby>",
        "八時": "<ruby>八時<rt>はちじ</rt></ruby>",
        "三時": "<ruby>三時<rt>さんじ</rt></ruby>",
        "何時": "<ruby>何時<rt>なんじ</rt></ruby>",
        "何月": "<ruby>何月<rt>なんがつ</rt></ruby>",
        "何人": "<ruby>何人<rt>なんにん</rt></ruby>",
        "季節": "<ruby>季節<rt>きせつ</rt></ruby>",
        "三月": "<ruby>三月<rt>さんがつ</rt></ruby>",
        "五月": "<ruby>五月<rt>ごがつ</rt></ruby>",
        "六月": "<ruby>六月<rt>ろくがつ</rt></ruby>",
        "八月": "<ruby>八月<rt>はちがつ</rt></ruby>",
        "九月": "<ruby>九月<rt>くがつ</rt></ruby>",
        "二月": "<ruby>二月<rt>にがつ</rt></ruby>",
        "桜": "<ruby>桜<rt>さくら</rt></ruby>",
        "紅葉": "<ruby>紅葉<rt>こうよう</rt></ruby>",
        "暑い": "<ruby>暑<rt>あつ</rt></ruby>い",
        "店員": "<ruby>店員<rt>てんいん</rt></ruby>",
        "定食": "<ruby>定食<rt>ていしょく</rt></ruby>",
        "少々": "<ruby>少々<rt>しょうしょう</rt></ruby>",
        "電車": "<ruby>電車<rt>でんしゃ</rt></ruby>",
        "便利": "<ruby>便利<rt>べんり</rt></ruby>",
        "世界": "<ruby>世界<rt>せかい</rt></ruby>",
        "一番": "<ruby>一番<rt>いちばん</rt></ruby>",
        "正確": "<ruby>正確<rt>せいかく</rt></ruby>",
        "初めて": "<ruby>初<rt>はじ</rt></ruby>めて",
        "驚きます": "<ruby>驚<rt>おどろ</rt></ruby>きます",
        "不便": "<ruby>不便<rt>ふべん</rt></ruby>",
        "危ない": "<ruby>危<rt>あぶ</rt></ruby>ない",
        "遅い": "<ruby>遅<rt>おそ</rt></ruby>い",
        "早い": "<ruby>早<rt>はや</rt></ruby>い",
        "お年": "お<ruby>年<rt>とし</rt></ruby>",
        "春": "<ruby>春<rt>はる</rt></ruby>",
        "夏": "<ruby>夏<rt>なつ</rt></ruby>",
        "秋": "<ruby>秋<rt>あき</rt></ruby>",
        "冬": "<ruby>冬<rt>ふゆ</rt></ruby>",
        "雪": "<ruby>雪<rt>ゆき</rt></ruby>",
        "朝": "<ruby>朝<rt>あさ</rt></ruby>",
        "国": "<ruby>国<rt>くに</rt></ruby>",
        "山": "<ruby>山<rt>やま</rt></ruby>",
        "川": "<ruby>川<rt>かわ</rt></ruby>",
        "空": "<ruby>空<rt>そら</rt></ruby>",
        "雨": "<ruby>雨<rt>あめ</rt></ruby>",
        "天": "<ruby>天<rt>てん</rt></ruby>",
        "気": "<ruby>気<rt>き</rt></ruby>",
        "車": "<ruby>車<rt>くるま</rt></ruby>",
        "門": "<ruby>門<rt>もん</rt></ruby>",
        "道": "<ruby>道<rt>みち</rt></ruby>",
        "校": "<ruby>校<rt>こう</rt></ruby>",
        "書": "<ruby>書<rt>か</rt></ruby>",
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
        "月": "<ruby>月<rt>つき</rt></ruby>",
        "日": "<ruby>日<rt>ひ</rt></ruby>",
        "時": "<ruby>時<rt>じ</rt></ruby>",
        "分": "<ruby>分<rt>ふん</rt></ruby>",
        "半": "<ruby>半<rt>はん</rt></ruby>",
        "百": "<ruby>百<rt>ひゃく</rt></ruby>",
        "千": "<ruby>千<rt>せん</rt></ruby>",
        "万": "<ruby>万<rt>まん</rt></ruby>",
        "一": "<ruby>一<rt>いち</rt></ruby>",
        "二": "<ruby>二<rt>に</rt></ruby>",
        "三": "<ruby>三<rt>さん</rt></ruby>",
        "四": "<ruby>四<rt>よん</rt></ruby>",
        "五": "<ruby>五<rt>ご</rt></ruby>",
        "六": "<ruby>六<rt>ろく</rt></ruby>",
        "七": "<ruby>七<rt>なな</rt></ruby>",
        "八": "<ruby>八<rt>はち</rt></ruby>",
        "九": "<ruby>九<rt>きゅう</rt></ruby>",
        "十": "<ruby>十<rt>じゅう</rt></ruby>",
        "父": "<ruby>父<rt>ちち</rt></ruby>",
        "母": "<ruby>母<rt>はは</rt></ruby>",
        "子": "<ruby>子<rt>こ</rt></ruby>",
        "男": "<ruby>男<rt>おとこ</rt></ruby>",
        "女": "<ruby>女<rt>おんな</rt></ruby>",
        "人": "<ruby>人<rt>ひと</rt></ruby>",

        // New mappings for compound words and fallbacks
        "日本人": "<ruby>日本人<rt>にほんじん</rt></ruby>",
        "東京": "<ruby>東京<rt>とうきょう</rt></ruby>",
        "京都": "<ruby>京都<rt>きょうと</rt></ruby>",
        "大阪": "<ruby>大阪<rt>おおさか</rt></ruby>",
        "名古屋": "<ruby>名古屋<rt>なごや</rt></ruby>",
        "英語": "<ruby>英語<rt>えいご</rt></ruby>",
        "数学": "<ruby>数学<rt>すうがく</rt></ruby>",
        "化学": "<ruby>化学<rt>かがく</rt></ruby>",
        "一緒": "<ruby>一緒<rt>いっしょ</rt></ruby>",
        "二人": "<ruby>二人<rt>ふたり</rt></ruby>",
        "一人": "<ruby>一人<rt>ひとり</rt></ruby>",
        "三人": "<ruby>三<rt>さん</rt></ruby><ruby>人<rt>にん</rt></ruby>",
        "四人": "<ruby>四人<rt>よにん</rt></ruby>",
        "毎日": "<ruby>毎日<rt>まいにち</rt></ruby>",
        "お昼": "お<ruby>昼<rt>ひる</rt></ruby>",
        "ご飯": "ご<ruby>飯<rt>はん</rt></ruby>",
        "近く": "<ruby>近<rt>ちか</rt></ruby>く",
        "作り方": "<ruby>作<rt>つく</rt></ruby>り<ruby>方<rt>かた</rt></ruby>",
        "使い方": "<ruby>使<rt>つか</rt></ruby>い<ruby>方<rt>かた</rt></ruby>",
        "知って": "<ruby>知<rt>し</rt></ruby>して",
        "時間": "<ruby>時間<rt>じかん</rt></ruby>",
        "美味しい": "<ruby>美味<rt>おい</rt></ruby>しい",
        "買い物": "<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>",
        "勉強": "<ruby>勉強<rt>べんきょう</rt></ruby>",
        "働く": "<ruby>働<rt>はたら</rt></ruby>く",
        "働きます": "<ruby>働<rt>はたら</rt></ruby>きます",
        "働いた": "<ruby>働<rt>はたら</rt></ruby>いた",
        "働いて": "<ruby>働<rt>はたら</rt></ruby>いて",
        "お茶": "お<ruby>茶<rt>ちゃ</rt></ruby>",
        "お酒": "お<ruby>酒<rt>さけ</rt></ruby>",
        "お待ち": "お<ruby>待<rt>ま</rt></ruby>ち",
        "お客": "お<ruby>客<rt>きゃく</rt></ruby>",
        "店員": "<ruby>店員<rt>てんいん</rt></ruby>",
        "世界一番": "<ruby>世界一番<rt>せかいいちばん</rt></ruby>",
        "使います": "<ruby>使<rt>つか</rt></ruby>います",
        "使い": "<ruby>使<rt>つか</rt></ruby>い",
        "来ます": "<ruby>来<rt>き</rt></ruby>ます",
        "来た": "<ruby>来<rt>き</rt></ruby>た",
        "来て": "<ruby>来<rt>き</rt></ruby>て",
        "来る": "<ruby>来<rt>く</rt></ruby>る",
        "行く": "<ruby>行<rt>い</rt></ruby>く",
        "行った": "<ruby>行<rt>い</rt></ruby>った",
        "行って": "<ruby>行<rt>い</rt></ruby>って",
        "食べる": "<ruby>食<rt>た</rt></ruby>べる",
        "食べた": "<ruby>食<rt>た</rt></ruby>べた",
        "食べて": "<ruby>食<rt>た</rt></ruby>べて",
        "食べます": "<ruby>食<rt>た</rt></ruby>べます",
        "飲む": "<ruby>飲<rt>の</rt></ruby>む",
        "飲みます": "<ruby>飲<rt>の</rt></ruby>みます",
        "飲んだ": "<ruby>飲<rt>の</rt></ruby>んだ",
        "飲んで": "<ruby>飲<rt>の</rt></ruby>んで",
        "言う": "<ruby>言<rt>い</rt></ruby>う",
        "言います": "<ruby>言<rt>い</rt></ruby>ます",
        "言った": "<ruby>言<rt>い</rt></ruby>った",
        "言って": "<ruby>言<rt>い</rt></ruby>って",
        "言いました": "<ruby>言<rt>い</rt></ruby>いました",
        "帰る": "<ruby>帰<rt>かえ</rt></ruby>る",
        "帰った": "<ruby>帰<rt>かえ</rt></ruby>った",
        "帰って": "<ruby>帰<rt>かえ</rt></ruby>って",
        "見ます": "<ruby>見<rt>み</rt></ruby>ます",
        "買います": "<ruby>買<rt>か</rt></ruby>います",
        "買った": "<ruby>買<rt>か</rt></ruby>った",
        "買って": "<ruby>買<rt>か</rt></ruby>て",
        "会う": "<ruby>会<rt>あ</rt></ruby>う",
        "会います": "<ruby>会<rt>あ</rt></ruby>います",
        "会った": "<ruby>会<rt>あ</rt></ruby>った",
        "会って": "<ruby>会<rt>あ</rt></ruby>って",

        // Single character Kanjis as robust fallbacks
        "私": "<ruby>私<rt>わたし</rt></ruby>",
        "国": "<ruby>国<rt>くに</rt></ruby>",
        "山": "<ruby>山<rt>やま</rt></ruby>",
        "川": "<ruby>川<rt>かわ</rt></ruby>",
        "空": "<ruby>空<rt>そら</rt></ruby>",
        "雨": "<ruby>雨<rt>あめ</rt></ruby>",
        "天": "<ruby>天<rt>てん</rt></ruby>",
        "気": "<ruby>気<rt>き</rt></ruby>",
        "車": "<ruby>車<rt>くるま</rt></ruby>",
        "門": "<ruby>門<rt>もん</rt></ruby>",
        "道": "<ruby>道<rt>みち</rt></ruby>",
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
        "月": "<ruby>月<rt>つき</rt></ruby>",
        "日": "<ruby>日<rt>ひ</rt></ruby>",
        "時": "<ruby>時<rt>じ</rt></ruby>",
        "分": "<ruby>分<rt>ふん</rt></ruby>",
        "半": "<ruby>半<rt>はん</rt></ruby>",
        "百": "<ruby>百<rt>ひゃく</rt></ruby>",
        "千": "<ruby>千<rt>せん</rt></ruby>",
        "万": "<ruby>万<rt>まん</rt></ruby>",
        "一": "<ruby>一<rt>いち</rt></ruby>",
        "二": "<ruby>二<rt>に</rt></ruby>",
        "三": "<ruby>三<rt>さん</rt></ruby>",
        "四": "<ruby>四<rt>よん</rt></ruby>",
        "五": "<ruby>五<rt>ご</rt></ruby>",
        "六": "<ruby>六<rt>ろく</rt></ruby>",
        "七": "<ruby>七<rt>なな</rt></ruby>",
        "八": "<ruby>八<rt>はち</rt></ruby>",
        "九": "<ruby>九<rt>きゅう</rt></ruby>",
        "十": "<ruby>十<rt>じゅう</rt></ruby>",
        "父": "<ruby>父<rt>ちち</rt></ruby>",
        "母": "<ruby>母<rt>はは</rt></ruby>",
        "子": "<ruby>子<rt>こ</rt></ruby>",
        "男": "<ruby>男<rt>おとこ</rt></ruby>",
        "女": "<ruby>女<rt>おんな</rt></ruby>",
        "人": "<ruby>人<rt>ひと</rt></ruby>",
        "見": "<ruby>見<rt>み</rt></ruby>",
        "言": "<ruby>言<rt>い</rt></ruby>",
        "話": "<ruby>話<rt>はな</rt></ruby>",
        "聞": "<ruby>聞<rt>き</rt></ruby>",
        "書": "<ruby>書<rt>か</rt></ruby>",
        "読": "<ruby>読<rt>よ</rt></ruby>",
        "会": "<ruby>会<rt>あ</rt></ruby>",
        "買": "<ruby>買<rt>か</rt></ruby>",
        "帰": "<ruby>帰<rt>かえ</rt></ruby>",
        "働": "<ruby>働<rt>はたら</rt></ruby>",
        "来": "<ruby>来<rt>く</rt></ruby>",
        "行": "<ruby>行<rt>い</rt></ruby>",
        "食": "<ruby>食<rt>た</rt></ruby>",
        "飲": "<ruby>飲<rt>の</rt></ruby>",
        "作": "<ruby>作<rt>つく</rt></ruby>",
        "知": "<ruby>知<rt>し</rt></ruby>",
        "教": "<ruby>教<rt>おし</rt></ruby>",
        "何": "<ruby>何<rt>なに</rt></ruby>",
        "客": "<ruby>客<rt>きゃく</rt></ruby>",
        "店": "<ruby>店<rt>みせ</rt></ruby>",
        "駅": "<ruby>駅<rt>えき</rt></ruby>",
        "東": "<ruby>東<rt>ひがし</rt></ruby>",
        "京": "<ruby>京<rt>きょう</rt></ruby>",
        "都": "<ruby>都<rt>と</rt></ruby>",
        "阪": "<ruby>阪<rt>さか</rt></ruby>",
        "毎": "<ruby>毎<rt>まい</rt></ruby>",
        "昼": "<ruby>昼<rt>ひる</rt></ruby>",
        "朝": "<ruby>朝<rt>あさ</rt></ruby>",
        "晩": "<ruby>晩<rt>ばん</rt></ruby>",
        "夜": "<ruby>夜<rt>よる</rt></ruby>",
        "校": "<ruby>校<rt>こう</rt></ruby>",
        "学": "<ruby>学<rt>まな</rt></ruby>",
        "生": "<ruby>生<rt>せい</rt></ruby>",
        "茶": "<ruby>茶<rt>ちゃ</rt></ruby>",
        "酒": "<ruby>酒<rt>さけ</rt></ruby>",
        "魚": "<ruby>魚<rt>さかな</rt></ruby>",
        "肉": "<ruby>肉<rt>にく</rt></ruby>",
        "室": "<ruby>室<rt>しつ</rt></ruby>",
        "物": "<ruby>物<rt>もの</rt></ruby>",
        "新": "<ruby>新<rt>あたら</rt></ruby>",
        "古": "<ruby>古<rt>ふる</rt></ruby>",
        "長": "<ruby>長<rt>なが</rt></ruby>",
        "短": "<ruby>短<rt>みじか</rt></ruby>",
        "高": "<ruby>高<rt>たか</rt></ruby>",
        "安": "<ruby>安<rt>やす</rt></ruby>",
        "暑": "<ruby>暑<rt>あつ</rt></ruby>",
        "寒": "<ruby>寒<rt>さむ</rt></ruby>",
        "暖": "<ruby>暖<rt>あたた</rt></ruby>",
        "涼": "<ruby>涼<rt>すず</rt></ruby>",
        "春": "<ruby>春<rt>はる</rt></ruby>",
        "夏": "<ruby>夏<rt>なつ</rt></ruby>",
        "秋": "<ruby>秋<rt>あき</rt></ruby>",
        "冬": "<ruby>冬<rt>ふゆ</rt></ruby>",
        "雪": "<ruby>雪<rt>ゆき</rt></ruby>",
        "花": "<ruby>花<rt>はな</rt></ruby>",
        "風": "<ruby>風<rt>かぜ</rt></ruby>",
        "林": "<ruby>林<rt>はやし</rt></ruby>",
        "森": "<ruby>森<rt>もり</rt></ruby>",
        "英": "<ruby>英<rt>えい</rt></ruby>",
        "語": "<ruby>語<rt>ご</rt></ruby>",
        "文": "<ruby>文<rt>ぶん</rt></ruby>",
        "化": "<ruby>化<rt>か</rt></ruby>",
        "強": "<ruby>強<rt>つよ</rt></ruby>",
        "弱": "<ruby>弱<rt>よわ</rt></ruby>",
        "同": "<ruby>同<rt>おな</rt></ruby>",
        "自": "<ruby>自<rt>じ</rt></ruby>",
        "転": "<ruby>転<rt>てん</rt></ruby>",
        "車": "<ruby>車<rt>くるま</rt></ruby>",
        "軽": "<ruby>軽<rt>かる</rt></ruby>",
        "重": "<ruby>重<rt>おも</rt></ruby>",
        "早": "<ruby>早<rt>はや</rt></ruby>",
        "速": "<ruby>速<rt>はや</rt></ruby>",
        "遅": "<ruby>遅<rt>おそ</rt></ruby>",
        "正": "<ruby>正<rt>ただ</rt></ruby>",
        "常": "<ruby>常<rt>つね</rt></ruby>",
        "平": "<ruby>平<rt>たいら</rt></ruby>",
        "和": "<ruby>和<rt>わ</rt></ruby>",
        "洋": "<ruby>洋<rt>よう</rt></ruby>",
        "服": "<ruby>服<rt>ふく</rt></ruby>",
        "洗": "<ruby>洗<rt>あら</rt></ruby>",
        "濯": "<ruby>濯<rt>たく</rt></ruby>",
        "掃": "<ruby>掃<rt>そう</rt></ruby>",
        "除": "<ruby>除<rt>じ</rt></ruby>",
        "予": "<ruby>予<rt>よ</rt></ruby>",
        "定": "<ruby>定<rt>さだ</rt></ruby>",
        "計": "<ruby>計<rt>けい</rt></ruby>",
        "画": "<ruby>画<rt>が</rt></ruby>",
        "乗": "<ruby>乗<rt>の</rt></ruby>",
        "降": "<ruby>降<rt>お</rt></ruby>",
        "出": "<ruby>出<rt>で</rt></ruby>",
        "入": "<ruby>入<rt>はい</rt></ruby>",
        "開": "<ruby>開<rt>あ</rt></ruby>",
        "閉": "<ruby>閉<rt>し</rt></ruby>",
        "始": "<ruby>始<rt>はじ</rt></ruby>",
        "終": "<ruby>終<rt>お</rt></ruby>",
        "思": "<ruby>思<rt>おも</rt></ruby>",
        "考": "<ruby>考<rt>かんが</rt></ruby>",
        "決": "<ruby>決<rt>き</rt></ruby>",
        "願": "<ruby>願<rt>ねが</rt></ruby>",
        "送": "<ruby>送<rt>おく</rt></ruby>",
        "借": "<ruby>借<rt>か</rt></ruby>",
        "貸": "<ruby>貸<rt>か</rt></ruby>",
        "返": "<ruby>返<rt>かえ</rt></ruby>",
        "待": "<ruby>待<rt>ま</rt></ruby>",
        "持": "<ruby>持<rt>も</rt></ruby>",
        "連": "<ruby>連<rt>つ</rt></ruby>",
        "答": "<ruby>答<rt>こた</rt></ruby>",
        "問": "<ruby>問<rt>と</rt></ruby>",
        "題": "<ruby>題<rt>だい</rt></ruby>",
        "宿": "<ruby>宿<rt>しゅく</rt></ruby>",
        "館": "<ruby>館<rt>かん</rt></ruby>",
        "病": "<ruby>病<rt>びょう</rt></ruby>",
        "院": "<ruby>院<rt>いん</rt></ruby>",
        "薬": "<ruby>薬<rt>くすり</rt></ruby>",
        "医": "<ruby>医<rt>い</rt></ruby>",
        "者": "<ruby>者<rt>しゃ</rt></ruby>",
        "味": "<ruby>味<rt>あじ</rt></ruby>",
        "楽": "<ruby>楽<rt>たの</rt></ruby>",
        "歌": "<ruby>歌<rt>うた</rt></ruby>",
        "画": "<ruby>画<rt>が</rt></ruby>",
        "映": "<ruby>映<rt>えい</rt></ruby>",
        "旅": "<ruby>旅<rt>たび</rt></ruby>",
        "行": "<ruby>行<rt>い</rt></ruby>",
        "館": "<ruby>館<rt>かん</rt></ruby>",
        "図": "<ruby>図<rt>ず</rt></ruby>",
        "書": "<ruby>書<rt>しょ</rt></ruby>",
        "高": "<ruby>高<rt>たか</rt></ruby>",
        "低": "<ruby>低<rt>ひく</rt></ruby>",
        "深": "<ruby>深<rt>ふか</rt></ruby>",
        "浅": "<ruby>浅<rt>あさ</rt></ruby>",
        "広": "<ruby>広<rt>ひろ</rt></ruby>",
        "狭": "<ruby>狭<rt>せま</rt></ruby>",
        "良": "<ruby>良<rt>よ</rt></ruby>",
        "悪": "<ruby>悪<rt>わる</rt></ruby>",
        "難": "<ruby>難<rt>むずか</rt></ruby>",
        "易": "<ruby>易<rt>やさ</rt></ruby>",
        "忙": "<ruby>忙<rt>いそが</rt></ruby>",
        "静": "<ruby>静<rt>しず</rt></ruby>",
        "暗": "<ruby>暗<rt>くら</rt></ruby>",
        "明": "<ruby>明<rt>あか</rt></ruby>",
        "休": "<ruby>休<rt>やす</rt></ruby>"
    };

    function applyFurigana(text) {
        if (!text) return "";
        const keys = Object.keys(FURIGANA_MAP).sort((a, b) => b.length - a.length);
        const escapedKeys = keys.map(k => k.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
        const regex = new RegExp(`(<ruby>[\\s\\S]*?<\\/ruby>)|(${escapedKeys.join('|')})`, 'g');
        return text.replace(regex, (match, rubyPart, keyPart) => {
            if (rubyPart) return rubyPart;
            return FURIGANA_MAP[keyPart] || keyPart;
        });
    }

    $: currentQuestion = selectedPassage?.questions?.[currentQuestionIndex];
</script>

<div class="reading-mode-container p-6 h-full overflow-y-auto custom-scroll" in:fade>
    <div class="max-w-4xl mx-auto">
        {#if loading}
            <div class="text-center py-12">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-500 mx-auto mb-4"></div>
                <p class="text-slate-300">Loading passages...</p>
            </div>
        {:else if result}
            <!-- Result view -->
            <div class="text-center py-8" in:fade>
                <div class="text-6xl mb-4">
                    {#if result.comprehension_score >= 80}
                        🎉
                    {:else if result.comprehension_score >= 60}
                        👍
                    {:else}
                        💪
                    {/if}
                </div>
                <h3 class="text-2xl font-bold text-white mb-2">Reading Complete!</h3>
                <p class="text-lg text-slate-400 mb-6">
                    Score: <span class="font-bold text-indigo-400">{result.correct}/{result.total}</span>
                    ({result.comprehension_score}%)
                </p>
                <button
                    on:click={backToList}
                    class="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition"
                >
                    Back to Passages
                </button>
            </div>
        {:else if selectedPassage}
            <!-- Reading view -->
            <div in:fade>
                <button
                    on:click={backToList}
                    class="mb-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition"
                >
                    ← Back
                </button>

                <div class="bg-slate-800/50 backdrop-blur rounded-2xl p-6 border border-slate-700 mb-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h2 class="text-2xl font-bold text-white mb-2">{@html applyFurigana(selectedPassage.title)}</h2>
                            <span class="px-3 py-1 bg-indigo-500/20 text-indigo-400 text-xs font-bold uppercase rounded-full">
                                {selectedPassage.level}
                            </span>
                        </div>
                        <button
                            on:click={() => showTranslation = !showTranslation}
                            class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm rounded-lg transition"
                        >
                            {showTranslation ? "Hide" : "Show"} Translation
                        </button>
                    </div>

                    <!-- Japanese text -->
                    <div class="bg-slate-700/50 rounded-xl p-6 mb-4 max-h-60 overflow-y-auto custom-scroll">
                        <p class="text-lg leading-relaxed text-white" style="font-family: 'Noto Sans JP', sans-serif; line-height: 2;">
                            {#each parseSegments(selectedPassage.text, selectedPassage.vocab_annotations) as segment}
                                {#if segment.isVocab}
                                    <button
                                        on:click={() => toggleUnknownWord(segment.word)}
                                        class="px-1.5 py-0.5 rounded border transition inline-block mx-0.5 font-bold {unknownWords.includes(segment.word)
                                            ? 'bg-red-500/20 border-red-500/50 text-red-400'
                                            : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30'}"
                                        title="{segment.reading}: {segment.meaning}"
                                    >
                                        {@html applyFurigana(segment.word)}
                                    </button>
                                {:else}
                                    <span>{@html applyFurigana(segment.text)}</span>
                                {/if}
                            {/each}
                        </p>
                    </div>

                    <!-- Translation (toggle) -->
                    {#if showTranslation}
                        <div class="bg-indigo-500/10 border border-indigo-500/30 rounded-xl p-4" in:fade>
                            <p class="text-slate-300 text-sm leading-relaxed">{selectedPassage.translation}</p>
                        </div>
                    {/if}

                    <!-- Vocab annotations -->
                    {#if selectedPassage.vocab_annotations?.length > 0}
                        <div class="mt-6">
                            <p class="text-sm text-slate-400 mb-3">Vocabulary:</p>
                            <div class="flex flex-wrap gap-2">
                                {#each selectedPassage.vocab_annotations as vocab}
                                    <button
                                        on:click={() => toggleUnknownWord(vocab.word)}
                                        class="px-3 py-2 rounded-lg border transition {unknownWords.includes(vocab.word)
                                            ? 'bg-red-500/20 border-red-500/50 text-red-400'
                                            : 'bg-slate-700 border-slate-600 text-slate-300 hover:border-slate-500'}"
                                        title="Click if unknown"
                                    >
                                        <span class="font-bold">{@html applyFurigana(vocab.word)}</span>
                                        <span class="text-xs ml-2 opacity-70">({vocab.reading})</span>
                                        <span class="block text-xs mt-1">{vocab.meaning}</span>
                                    </button>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>

                <!-- Questions -->
                {#if currentQuestion}
                    <div class="bg-slate-800/50 backdrop-blur rounded-2xl p-6 border border-slate-700" in:fade>
                        <p class="text-sm text-slate-400 mb-4">
                            Question {currentQuestionIndex + 1} of {selectedPassage.questions.length}
                        </p>
                        <h3 class="text-lg font-bold text-white mb-2">{@html applyFurigana(currentQuestion.question)}</h3>
                        <p class="text-sm text-slate-400 mb-4 italic">{currentQuestion.question_id}</p>
 
                        <div class="space-y-3">
                            {#each currentQuestion.options as option, i}
                                <button
                                    on:click={() => answerQuestion(i)}
                                    class="w-full text-left p-4 rounded-xl border-2 border-slate-600 bg-slate-700/30 hover:border-indigo-500 hover:bg-indigo-500/10 transition"
                                >
                                    <span class="text-white font-medium">{String.fromCharCode(65 + i)}. {@html applyFurigana(option)}</span>
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        {:else}
            <!-- Passage list -->
            <div in:fade>
                <div class="mb-6">
                    <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                        <span>📖</span>
                        <span>Reading Comprehension</span>
                    </h2>

                    <div class="flex gap-3">
                        <button
                            on:click={() => { selectedLevel = null; loadPassages(); }}
                            class="px-4 py-2 rounded-lg font-bold transition {selectedLevel === null ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
                        >
                            All
                        </button>
                        <button
                            on:click={() => { selectedLevel = 'beginner'; loadPassages('beginner'); }}
                            class="px-4 py-2 rounded-lg font-bold transition {selectedLevel === 'beginner' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
                        >
                            Beginner
                        </button>
                        <button
                            on:click={() => { selectedLevel = 'intermediate'; loadPassages('intermediate'); }}
                            class="px-4 py-2 rounded-lg font-bold transition {selectedLevel === 'intermediate' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
                        >
                            Intermediate
                        </button>
                        <button
                            on:click={() => { selectedLevel = 'advanced'; loadPassages('advanced'); }}
                            class="px-4 py-2 rounded-lg font-bold transition {selectedLevel === 'advanced' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
                        >
                            Advanced
                        </button>
                    </div>
                </div>

                <div class="grid gap-4">
                    {#each passages as passage}
                        <button
                            on:click={() => selectPassage(passage.id)}
                            class="bg-slate-800/50 backdrop-blur rounded-2xl p-6 border border-slate-700 hover:border-indigo-500 transition text-left"
                        >
                            <div class="flex justify-between items-start mb-2">
                                <h3 class="text-lg font-bold text-white">{@html applyFurigana(passage.title)}</h3>
                                <span class="px-3 py-1 bg-indigo-500/20 text-indigo-400 text-xs font-bold uppercase rounded-full">
                                    {passage.level}
                                </span>
                            </div>
                            <p class="text-sm text-slate-400 mb-3">{passage.translation}</p>
                            <p class="text-xs text-slate-500">{passage.question_count} questions</p>
                        </button>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</div>
