<script>
    import { fly, fade, scale } from "svelte/transition";
    import { backOut } from "svelte/easing";
    import { user } from "../stores/auth_store";
    import { profile, fetchFullProfile } from "../stores/profile_store";
    import { kanjiSets, totalKanjiCount } from "../lib/data/kanji_n5_dataset.js";
    import { themeStore } from "../stores/theme_store.js";
    import KanjiFlashcard from "./KanjiFlashcard.svelte";

    export let vrmController = null;
    export let onBack; // callback kembali ke QuestMap

    // ALISA Sticker state
    let activeStickers = [];

    function triggerSticker(type) {
        const config = {
            benar: [
                {
                    img: "/img/stickers/Yatta Benar.png",
                    audio: "/audio/stickers/Yatta Benar.wav",
                },
                {
                    img: "/img/stickers/Ganbare.png",
                    audio: "/audio/stickers/Ganbare.wav",
                },
            ],
            salah: {
                img: "/img/stickers/Masih Salah Nih.png",
                audio: "/audio/stickers/Masih Salah Nih.wav",
            },
            partially: {
                img: "/img/stickers/Dikit Lagi Nih.png",
                audio: "/audio/stickers/Dikit Lagi Nih.wav",
            },
        };

        let target;
        if (type === "benar") {
            const list = config.benar;
            target = list[Math.floor(Math.random() * list.length)];
        } else {
            target = config[type];
        }

        if (!target) return;

        const audio = new Audio(target.audio);
        audio.volume = 0.85;

        if (vrmController) vrmController.setSpeaking(true);
        audio.play().catch((e) => {
            console.warn("Audio play blocked:", e);
            if (vrmController) vrmController.setSpeaking(false);
        });
        audio.onended = () => {
            if (vrmController) vrmController.setSpeaking(false);
        };

        const isLeft = Math.random() < 0.5;
        const randomY = Math.random() * 70 + 10;
        const baseRot = isLeft ? 50 : -50;
        const randomRot = baseRot + (Math.random() - 0.5) * 10;
        const positionX = isLeft ? 75 : -75;

        const stickerId = `sticker_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
        const newSticker = {
            id: stickerId,
            img: target.img,
            side: isLeft ? "left" : "right",
            y: randomY,
            x: positionX,
            rotation: randomRot,
        };

        activeStickers = [...activeStickers, newSticker];

        setTimeout(() => {
            activeStickers = activeStickers.filter((s) => s.id !== stickerId);
        }, 2500);
    }

    // ── State ──────────────────────────────────────────────────────────────
    let view = "dojo_map"; // 'dojo_map' | 'study' | 'quiz' | 'set_result'

    let activeSetData   = null;
    let activeSetIndex  = 0;  // index kartu saat ini dalam set
    let quizAnswers     = []; // tracking jawaban per kartu
    let sessionResults  = null;

    // Quiz state
    let quizQueue      = [];
    let quizIndex      = 0;
    let quizScore      = 0;
    let quizInput      = "";
    let quizFeedback   = null; // null | 'correct' | 'wrong'
    let quizAnswerText = "";
    let showQuizHint   = false;

    // ── Computed: mastery state per set (dari profile) ────────────────────
    $: masteredKanjiIds = $profile?.mastery_path?.filter(n => (n.type === 'Kanji' || n.type === 'kanji') && n.status === 'MASTERED').map(n => n.id) || [];
    
    // Gabungkan data dari localStorage (MVP) dan dari database Neo4j
    let localMasteredSets = loadMasteredSets();
    $: masteredSets = [...new Set([
        ...localMasteredSets,
        ...kanjiSets.filter(set => {
            const masteredInSet = set.kanji.filter(k => masteredKanjiIds.includes(k.id)).length;
            return masteredInSet > 0 && (masteredInSet / set.kanji.length) >= 0.8;
        }).map(s => s.id)
    ])];

    function loadMasteredSets() {
        try {
            return JSON.parse(localStorage.getItem('tvjp_kanji_mastered') || '[]');
        } catch { return []; }
    }

    function saveMasteredSets(arr) {
        localStorage.setItem('tvjp_kanji_mastered', JSON.stringify(arr));
    }

    $: masteredCount = kanjiSets.filter(s => masteredSets.includes(s.id)).reduce((sum, s) => sum + s.kanji.length, 0);

    // ── Mode: STUDY (Flashcard) ────────────────────────────────────────────
    function startStudy(set) {
        activeSetData  = set;
        activeSetIndex = 0;
        quizAnswers    = [];
        view = "study";
    }

    function handleFlashcardNext() {
        quizAnswers.push({ seen: true });
        activeSetIndex++;
        if (activeSetIndex >= activeSetData.kanji.length) {
            // Semua kartu sudah dilihat → langsung ke quiz
            startQuiz();
        }
    }

    // ── Mode: QUIZ ─────────────────────────────────────────────────────────
    function startQuiz() {
        // Acak urutan soal
        quizQueue = [...activeSetData.kanji].sort(() => Math.random() - 0.5);
        quizIndex   = 0;
        quizScore   = 0;
        quizInput   = "";
        quizFeedback = null;
        showQuizHint = false;
        view = "quiz";
    }

    $: currentQuizKanji = quizQueue[quizIndex] ?? null;

    function checkAnswer() {
        if (!currentQuizKanji || !quizInput.trim()) return;

        const userAns = quizInput.toLowerCase().trim();
        // Jawaban benar: cocok dengan salah satu bagian arti (pisah koma/slash)
        const correctAnswers = currentQuizKanji.arti
            .toLowerCase()
            .split(/[,\/]/)
            .map(a => a.trim());

        const isCorrect = correctAnswers.some(a => userAns.includes(a) || a.includes(userAns));

        quizFeedback = isCorrect ? 'correct' : 'wrong';
        quizAnswerText = currentQuizKanji.arti;
        if (isCorrect) {
            quizScore++;
            triggerSticker("benar");
        } else {
            triggerSticker("salah");
        }
    }

    function nextQuiz() {
        quizIndex++;
        quizInput   = "";
        quizFeedback = null;
        showQuizHint = false;
        quizAnswerText = "";

        if (quizIndex >= quizQueue.length) {
            // Selesai quiz
            finishSet();
        }
    }

    // ── Selesai Set ────────────────────────────────────────────────────────
    async function finishSet() {
        const total = quizQueue.length;
        const pct   = Math.round((quizScore / total) * 100);
        const passed = pct >= 60;

        sessionResults = {
            setTitle:    activeSetData.title,
            setIcon:     activeSetData.icon,
            score:       quizScore,
            total,
            pct,
            passed
        };
        view = "set_result";
        triggerSticker(passed ? "benar" : "salah");

        // Tandai set sebagai MASTERED jika lulus
        if (passed && !masteredSets.includes(activeSetData.id)) {
            localMasteredSets = [...localMasteredSets, activeSetData.id];
            saveMasteredSets(localMasteredSets);

            // Kirim ke backend dan refresh profile setelah sukses
            if ($user) {
                fetch("http://localhost:8000/api/v1/kanji/mastery", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        student_id:  $user.id,
                        set_id:      activeSetData.id,
                        kanji_ids:   activeSetData.kanji.map(k => k.id),
                        score:       quizScore,
                        total
                    })
                }).then(async (res) => {
                    if (!res.ok) {
                        const errBody = await res.text().catch(() => "(no body)");
                        console.warn(`[KanjiDojo] Sync gagal (HTTP ${res.status}):`, errBody);
                    } else {
                        console.info("[KanjiDojo] Kanji mastery berhasil disimpan ke Neo4j ✅");
                        await fetchFullProfile($user.id); // refresh peta kanji
                    }
                }).catch(e => console.warn("[KanjiDojo] Network error saat sync kanji mastery:", e));
            }
        }

        view = "set_result";
    }

    function backToDojo() {
        view      = "dojo_map";
        activeSetData = null;
        quizAnswers = [];
    }

    // ── Warna tier berdasarkan progress ───────────────────────────────────
    const setColors = [
        "from-rose-400 to-pink-500",
        "from-orange-400 to-amber-500",
        "from-yellow-400 to-lime-500",
        "from-emerald-400 to-teal-500",
        "from-cyan-400 to-blue-500",
        "from-blue-400 to-indigo-500",
        "from-indigo-400 to-violet-500",
        "from-violet-400 to-purple-500",
        "from-fuchsia-400 to-pink-500",
        "from-rose-500 to-red-500",
        "from-amber-500 to-orange-500",
        "from-teal-500 to-emerald-500",
        "from-indigo-500 to-blue-500",
    ];
</script>

<div class="h-full overflow-hidden flex flex-col glass-panel rounded-[2.5rem] relative">
    <!-- Ambient glow -->
    <div class="absolute top-0 right-0 w-80 h-80 bg-amber-200/20 rounded-full blur-[100px] pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-96 h-96 bg-orange-200/10 rounded-full blur-[120px] pointer-events-none"></div>

    <!-- ═══════════════════════════════════════════════════════
         VIEW: DOJO MAP
    ══════════════════════════════════════════════════════════ -->
    {#if view === "dojo_map"}
        <div class="flex-grow overflow-y-auto custom-scroll p-6 md:p-8 relative z-10" in:fade>
            <!-- Header -->
            <div class="flex items-center gap-4 mb-8">
                <button on:click={onBack}
                    class="w-10 h-10 rounded-xl transition flex items-center justify-center shrink-0 {$themeStore === 'light' ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-white/20 hover:bg-slate-200/40 text-slate-500 hover:text-slate-800'}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
                    </svg>
                </button>
                <div>
                    <h2 class="text-2xl font-black tracking-tight {$themeStore === 'light' ? 'text-slate-900' : 'text-white'}">漢字 Dojo</h2>
                    <p class="text-xs font-medium mt-0.5 {$themeStore === 'light' ? 'text-slate-600' : 'text-slate-300'}">{totalKanjiCount} kanji N5 dalam 13 set terstruktur</p>
                </div>
                <!-- Overall progress -->
                <div class="ml-auto flex flex-col items-end shrink-0">
                    <span class="text-xs font-bold uppercase tracking-widest {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-300'}">Progress</span>
                    <span class="text-xl font-black text-amber-500">{masteredSets.length}<span class="font-bold text-sm {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-300'}"> / 13</span></span>
                </div>
            </div>

            <!-- Master progress bar -->
            <div class="mb-8">
                <div class="w-full rounded-full h-3 overflow-hidden border shadow-inner {$themeStore === 'light' ? 'bg-slate-200 border-slate-300' : 'bg-slate-200/60 border-white/50'}">
                    <div class="bg-gradient-to-r from-amber-400 to-orange-500 h-full rounded-full transition-all duration-1000"
                         style="width: {(masteredSets.length / 13) * 100}%"></div>
                </div>
                <p class="text-[10px] font-semibold mt-1.5 text-center {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-400'}">
                    {masteredSets.length === 0
                        ? 'Mulai dari Set 1 untuk membangun fondasi!'
                        : masteredSets.length < 13
                            ? `${masteredSets.length} set dikuasai — terus maju!`
                            : '🎉 Semua kanji N5 dikuasai! Luar biasa!'}
                </p>
            </div>

            <!-- Set Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {#each kanjiSets as set, i}
                    {@const isMastered = masteredSets.includes(set.id)}
                    {@const isLocked = i > 0 && !masteredSets.includes(kanjiSets[i-1].id)}
                    <button
                        on:click={() => !isLocked && startStudy(set)}
                        disabled={isLocked}
                        class="glass-card p-5 flex flex-col items-start text-left transition-all duration-300 group
                            {isMastered ? 'border-emerald-300/50 bg-emerald-50/20' :
                             isLocked ? 'opacity-50 grayscale cursor-not-allowed' :
                             'hover:scale-[1.02] hover:shadow-xl'}
                            {!isLocked && !isMastered ? 'active:scale-[0.99]' : ''}"
                    >
                        <!-- Set icon + number -->
                        <div class="flex items-center justify-between w-full mb-3">
                            <div class="w-10 h-10 rounded-xl bg-gradient-to-br {setColors[i]} flex items-center justify-center text-xl shadow-md border border-white/30">
                                {isLocked ? '🔒' : set.icon}
                            </div>
                            <div class="flex flex-col items-end">
                                <span class="text-[9px] font-black uppercase tracking-widest {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-400'}">Set {i + 1}</span>
                                {#if isMastered}
                                    <span class="text-[9px] font-black text-emerald-500 uppercase">✅ Mastered</span>
                                {:else if isLocked}
                                    <span class="text-[9px] font-black text-slate-400 uppercase">🔒 Locked</span>
                                {:else}
                                    <span class="text-[9px] font-black text-amber-500 uppercase">▶ Siap</span>
                                {/if}
                            </div>
                        </div>

                        <!-- Info set -->
                        <h4 class="font-black text-sm mb-1 {$themeStore === 'light' ? 'text-slate-900' : 'text-white'}">{set.title}</h4>
                        <p class="text-[11px] leading-relaxed line-clamp-2 {$themeStore === 'light' ? 'text-slate-600' : 'text-slate-300'}">{set.theme}</p>

                        <!-- Kanji preview (5 karakter) -->
                        <div class="flex gap-1 mt-3 flex-wrap">
                            {#each set.kanji.slice(0, 6) as k}
                                <span class="w-7 h-7 rounded-lg flex items-center justify-center text-base font-bold shadow-sm {$themeStore === 'light' ? 'bg-indigo-50 border border-indigo-200/80 text-indigo-900' : 'bg-white/60 border border-slate-200/60 text-slate-700'}">
                                    {k.id}
                                </span>
                            {/each}
                            {#if set.kanji.length > 6}
                                <span class="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-black shadow-sm {$themeStore === 'light' ? 'bg-slate-100 border border-slate-200 text-slate-500' : 'bg-slate-100/60 border border-slate-200/60 text-slate-400'}">
                                    +{set.kanji.length - 6}
                                </span>
                            {/if}
                        </div>
                    </button>
                {/each}
            </div>
        </div>

    <!-- ═══════════════════════════════════════════════════════
         VIEW: STUDY (Flashcard)
    ══════════════════════════════════════════════════════════ -->
    {:else if view === "study" && activeSetData}
        <div class="flex-grow overflow-hidden relative z-10 flex flex-col h-full" in:fly={{ x: 40, duration: 400 }}>
            <!-- Set Header -->
            <div class="p-5 border-b flex items-center gap-3 flex-shrink-0 {$themeStore === 'light' ? 'border-slate-200 bg-white/60' : 'border-white/20'}">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-br {setColors[kanjiSets.findIndex(s => s.id === activeSetData.id)]} flex items-center justify-center text-lg shadow-md">
                    {activeSetData.icon}
                </div>
                <div>
                    <h3 class="font-black text-sm {$themeStore === 'light' ? 'text-slate-900' : 'text-white'}">{activeSetData.title}</h3>
                    <p class="text-[10px] font-semibold {$themeStore === 'light' ? 'text-slate-600' : 'text-slate-300'}">Fase 1 dari 2 — Hafal Kartu</p>
                </div>
                <div class="ml-auto text-xs font-black {$themeStore === 'light' ? 'text-slate-600' : 'text-slate-400'}">
                    {activeSetIndex + 1} / {activeSetData.kanji.length}
                </div>
            </div>

            {#if activeSetIndex < activeSetData.kanji.length}
                <KanjiFlashcard
                    kanji={activeSetData.kanji[activeSetIndex]}
                    setIndex={activeSetIndex}
                    setTotal={activeSetData.kanji.length}
                    onNext={handleFlashcardNext}
                    onQuit={backToDojo}
                />
            {/if}
        </div>

    <!-- ═══════════════════════════════════════════════════════
         VIEW: QUIZ
    ══════════════════════════════════════════════════════════ -->
    {:else if view === "quiz" && currentQuizKanji}
        <div class="flex-grow overflow-y-auto p-6 flex flex-col items-center justify-center relative z-10" in:fly={{ x: 40, duration: 400 }}>

            <!-- Quiz Header -->
            <div class="w-full max-w-sm mb-6">
                <div class="flex items-center gap-3 mb-3">
                    <button on:click={backToDojo} class="w-8 h-8 rounded-lg transition flex items-center justify-center text-xs cursor-pointer {$themeStore === 'light' ? 'bg-slate-100 hover:bg-rose-100 text-slate-500 hover:text-rose-600 border border-slate-200' : 'bg-white/20 hover:bg-rose-100 text-slate-400'}">✕</button>
                    <div class="flex-grow h-2 rounded-full overflow-hidden {$themeStore === 'light' ? 'bg-slate-200 border border-slate-300' : 'bg-slate-200/50'}">
                        <div class="bg-gradient-to-r from-amber-400 to-orange-500 h-full rounded-full transition-all duration-500"
                             style="width: {(quizIndex / quizQueue.length) * 100}%"></div>
                    </div>
                    <span class="text-xs font-black {$themeStore === 'light' ? 'text-slate-600' : 'text-slate-400'}">{quizIndex + 1}/{quizQueue.length}</span>
                </div>
                <p class="text-[10px] font-black text-amber-500 uppercase tracking-widest text-center">Fase 2 — Ujian Kanji</p>
            </div>

            <!-- Soal Kanji -->
            {#key currentQuizKanji.id + quizIndex}
                <div class="w-full max-w-sm" in:fly={{ y: 20, duration: 400, easing: backOut }}>
                    <div class="backdrop-blur-xl rounded-[2rem] p-8 shadow-2xl border text-center transition-colors duration-300 {$themeStore === 'light' ? 'bg-white/95 border-indigo-100 shadow-slate-200' : 'bg-white/90 border-white/80'}">
                        <!-- Kanji besar -->
                        <div class="text-[6rem] leading-none font-bold text-slate-900 mb-2 select-none"
                             style="font-family: 'Noto Serif JP', serif;">
                            {currentQuizKanji.id}
                        </div>
                        <p class="text-xs font-semibold mb-6 {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-400'}">Apa artinya dalam bahasa Indonesia?</p>

                        <!-- Hint onyomi (toggle) -->
                        {#if !showQuizHint}
                            <button on:click={() => showQuizHint = true}
                                class="text-xs font-semibold transition mb-4 block w-full cursor-pointer {$themeStore === 'light' ? 'text-slate-500 hover:text-amber-600' : 'text-slate-400 hover:text-amber-500'}">
                                💡 Lihat petunjuk bacaan
                            </button>
                        {:else}
                            <div class="flex justify-center gap-3 mb-4" in:fade>
                                <span class="px-3 py-1 bg-indigo-50 border border-indigo-100 rounded-xl text-xs font-bold text-indigo-600">
                                    On: {currentQuizKanji.onyomi}
                                </span>
                                {#if currentQuizKanji.kunyomi !== '-'}
                                    <span class="px-3 py-1 bg-emerald-50 border border-emerald-100 rounded-xl text-xs font-bold text-emerald-600">
                                        Kun: {currentQuizKanji.kunyomi}
                                    </span>
                                {/if}
                            </div>
                        {/if}

                        <!-- Input jawaban -->
                        {#if quizFeedback === null}
                            <input
                                type="text"
                                bind:value={quizInput}
                                placeholder="Ketik artinya..."
                                class="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-200 focus:border-amber-400 focus:outline-none text-center font-bold text-slate-800 text-base transition placeholder:text-slate-300 mb-4"
                                on:keydown={(e) => e.key === 'Enter' && quizInput.trim() && checkAnswer()}
                            />
                            <button
                                on:click={checkAnswer}
                                disabled={!quizInput.trim()}
                                class="w-full py-4 bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-300 text-white font-black rounded-2xl shadow-xl shadow-amber-500/25 transition active:scale-95 disabled:opacity-30 uppercase tracking-widest text-sm cursor-pointer"
                            >
                                Periksa Jawaban
                            </button>

                        <!-- Feedback -->
                        {:else}
                            <div class="mb-4 p-4 rounded-2xl border {quizFeedback === 'correct' ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200'}" in:scale={{ duration: 300 }}>
                                <p class="font-black text-lg {quizFeedback === 'correct' ? 'text-emerald-600' : 'text-rose-500'}">
                                    {quizFeedback === 'correct' ? '✅ Benar!' : '❌ Kurang tepat'}
                                </p>
                                <p class="text-sm font-bold text-slate-700 mt-1">Jawaban: <span class="text-slate-900">{quizAnswerText}</span></p>
                            </div>
                            <button
                                on:click={nextQuiz}
                                class="w-full py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-black rounded-2xl shadow-xl shadow-indigo-500/25 transition active:scale-95 uppercase tracking-widest text-sm cursor-pointer"
                            >
                                {quizIndex + 1 < quizQueue.length ? 'Lanjut →' : 'Lihat Hasil'}
                            </button>
                        {/if}
                    </div>
                </div>
            {/key}
        </div>

    <!-- ═══════════════════════════════════════════════════════
         VIEW: SET RESULT
    ══════════════════════════════════════════════════════════ -->
    {:else if view === "set_result" && sessionResults}
        <div class="flex-grow overflow-y-auto p-6 flex flex-col items-center justify-center relative z-10" in:fly={{ y: 40, duration: 500, easing: backOut }}>
            <div class="w-full max-w-sm backdrop-blur-xl rounded-[2.5rem] p-10 shadow-2xl border text-center transition-colors duration-300 {$themeStore === 'light' ? 'bg-white/95 border-indigo-100 shadow-slate-200' : 'bg-white/90 border-white/80'}">
                <!-- Emoji besar -->
                <div class="text-6xl mb-4">{sessionResults.passed ? '🎉' : '💪'}</div>

                <h3 class="text-2xl font-black text-slate-900 mb-1">
                    {sessionResults.passed ? 'Set Dikuasai!' : 'Hampir!'}
                </h3>
                <p class="text-slate-500 text-sm mb-6">
                    {sessionResults.setIcon} {sessionResults.setTitle}
                </p>

                <!-- Score -->
                <div class="w-28 h-28 rounded-full mx-auto mb-6 flex flex-col items-center justify-center border-4 shadow-xl
                    {sessionResults.passed ? 'border-emerald-400 bg-emerald-50 shadow-emerald-500/20' : 'border-amber-400 bg-amber-50 shadow-amber-500/20'}">
                    <span class="text-3xl font-black {sessionResults.passed ? 'text-emerald-600' : 'text-amber-600'}">
                        {sessionResults.score}
                    </span>
                    <span class="text-xs font-bold text-slate-400">dari {sessionResults.total}</span>
                </div>

                <div class="mb-6 text-center">
                    <div class="text-xl font-black {sessionResults.passed ? 'text-emerald-600' : 'text-amber-500'}">
                        {sessionResults.pct}%
                    </div>
                    <p class="text-xs text-slate-500 mt-1">
                        {sessionResults.passed
                            ? 'Minimal 60% untuk dianggap MASTERED ✅'
                            : 'Perlu 60% untuk unlock set berikutnya'}
                    </p>
                </div>

                <!-- Pesan -->
                <p class="text-sm text-slate-600 font-medium mb-8 leading-relaxed">
                    {sessionResults.passed
                        ? 'Kanji di set ini sudah masuk ke Knowledge Graph-mu! Set berikutnya sudah terbuka.'
                        : 'Jangan menyerah! Ulangi flashcard dan coba lagi. Kamu pasti bisa! 🌟'}
                </p>

                <div class="flex flex-col gap-3">
                    {#if !sessionResults.passed}
                        <button on:click={() => startStudy(activeSetData)}
                            class="w-full py-4 bg-gradient-to-r from-amber-400 to-orange-500 text-white font-black rounded-2xl shadow-xl transition active:scale-95 uppercase tracking-widest text-sm cursor-pointer">
                            Ulangi Set Ini
                        </button>
                    {/if}
                    <button on:click={backToDojo}
                        class="w-full py-4 font-black rounded-2xl shadow-lg transition active:scale-95 uppercase tracking-widest text-sm cursor-pointer {$themeStore === 'light' ? 'bg-slate-200 hover:bg-slate-300 text-slate-800' : 'bg-slate-800 hover:bg-slate-900 text-white'}">
                        Kembali ke Dojo Map
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- ALISA Sticker Overlay -->
    <div class="alisa-stickers-container">
        {#each activeStickers as sticker (sticker.id)}
            <div
                class="alisa-sticker-overlay {sticker.side}"
                style="top: {sticker.y}%; --rot: {sticker.rotation}deg;"
                in:fly={{
                    x: sticker.side === "left" ? -100 : 100,
                    duration: 550,
                }}
                out:fly={{
                    x: sticker.side === "left" ? -100 : 100,
                    duration: 450,
                }}
            >
                <img
                    src={sticker.img}
                    alt="Alisa Sticker"
                    class="alisa-sticker-img"
                />
            </div>
        {/each}
    </div>
</div>

<style>
    .alisa-stickers-container {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
        overflow: hidden;
    }
    .alisa-sticker-overlay {
        position: absolute;
        width: 300px;
        height: 300px;
        margin-top: -150px;
        filter: drop-shadow(0 12px 25px rgba(0, 0, 0, 0.45));
    }
    .alisa-sticker-overlay.left {
        left: -225px; /* Peek exactly half of the sticker */
    }
    .alisa-sticker-overlay.right {
        right: -235px; /* Peek exactly half of the sticker */
    }
    .alisa-sticker-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        transform: rotate(var(--rot));
        animation: stickerSway 3s ease-in-out infinite alternate;
        transform-origin: bottom center;
    }
    @keyframes stickerSway {
        0% {
            transform: rotate(calc(var(--rot) - 4deg));
        }
        100% {
            transform: rotate(calc(var(--rot) + 4deg));
        }
    }
</style>
