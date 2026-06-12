<script>
    import { onMount, tick } from "svelte";
    import { fly, fade } from "svelte/transition";
    import { user } from "../stores/auth_store";
    import { sfx } from "../lib/sfx_manager";

    export let levelData;
    export let onFinish = () => {};
    export let onQuit = () => {};
    export let vrmController = null;

    let audioPlayer;
    let questionQueue = [];
    let currentIndex = 0;
    let currentQuestion = null;
    let score = 0;

    // Per-question tracking
    let wrongAttempts = {};
    let hintUsed = {};

    // Fill & Translate answer input
    let fillAnswer = "";

    // UI State
    let isEvaluating = false;
    let showAiFeedback = false;
    let aiFeedbackText = "";
    let lastAnswerWrong = false;  // Untuk visual feedback merah sekilas
    let lastUserAnswer = "";       // Menyimpan jawaban terakhir user
    let correctAnswerDisplay = ""; // Menyimpan jawaban benar untuk ditampilkan
    let isAiThinking = false;      // Untuk status loading AI

    $: if (vrmController) {
        vrmController.setLoading(isAiThinking);
    }

    // Session stats (dikirim ke backend di akhir level)
    // Format: { [node_id]: { correct: 0, wrong: 0, hint: 0 } }
    let sessionStats = {};

    onMount(() => {
        questionQueue = JSON.parse(JSON.stringify(levelData.questions));
        loadQuestion();
    });

    function loadQuestion() {
        if (currentIndex >= questionQueue.length) {
            // Level selesai — kirim session stats lalu finish
            submitSessionStats();
            onFinish({
                score,
                total: questionQueue.length,
                sessionStats,
                levelId: levelData.id
            });
            return;
        }
        currentQuestion = questionQueue[currentIndex];
        fillAnswer = "";
        showAiFeedback = false;
        aiFeedbackText = "";
        lastAnswerWrong = false;
        lastUserAnswer = "";
        correctAnswerDisplay = "";
        isAiThinking = false;
    }

    // ── Tracking Helper ────────────────────────────────────────────
    function trackStat(nodeId, type) {
        if (!sessionStats[nodeId]) sessionStats[nodeId] = { correct: 0, wrong: 0, hint: 0 };
        sessionStats[nodeId][type]++;
    }

    // ── Answer Handler ─────────────────────────────────────────────
    async function handleAnswer(userAnswer) {
        if (isEvaluating || showAiFeedback) return;
        isEvaluating = true;

        const isCorrect = checkAnswer(currentQuestion, userAnswer);

        if (isCorrect) {
            sfx.play('success');
            lastAnswerWrong = false;

            const attempts = wrongAttempts[currentQuestion.id] || 0;
            const wasHinted = hintUsed[currentQuestion.id] || false;

            // Scoring: 10 → 6 → 3 (berkurang per kesalahan), -2 jika pakai hint
            let earnedScore;
            if (attempts === 0) earnedScore = wasHinted ? 8 : 10;
            else if (attempts === 1) earnedScore = wasHinted ? 4 : 6;
            else earnedScore = wasHinted ? 1 : 3;

            score += earnedScore;
            trackStat(currentQuestion.node_id, 'correct');

            // Log mastery ke backend (per-soal, fire-and-forget)
            if ($user && currentQuestion.node_id) {
                const masteryStatus = attempts === 0 && !wasHinted ? "MASTERED" : "LEARNED";
                fetch("http://localhost:8000/api/v1/log-mastery", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        student_id: $user.id,
                        node_id: currentQuestion.node_id,
                        status: masteryStatus
                    })
                }).catch(e => console.error("Failed to log mastery:", e));
            }

            // Tunggu sebentar lalu lanjut
            setTimeout(() => {
                isEvaluating = false;
                currentIndex++;
                loadQuestion();
            }, 900);

        } else {
            sfx.play('error');
            lastAnswerWrong = true;
            trackStat(currentQuestion.node_id, 'wrong');

            wrongAttempts[currentQuestion.id] = (wrongAttempts[currentQuestion.id] || 0) + 1;
            const attempts = wrongAttempts[currentQuestion.id];

            if (attempts === 1) {
                // Kesalahan pertama: antrekan ulang, lanjut tanpa feedback
                questionQueue.push(JSON.parse(JSON.stringify(currentQuestion)));
                setTimeout(() => {
                    isEvaluating = false;
                    lastAnswerWrong = false;
                    currentIndex++;
                    loadQuestion();
                }, 1200);

            } else if (attempts === 2) {
                // Kesalahan kedua: minta AI feedback, antrekan ulang
                questionQueue.push(JSON.parse(JSON.stringify(currentQuestion)));
                await requestAIFeedback(userAnswer);
                isEvaluating = false;
                // Jangan auto-advance! Tunggu user klik "Lanjutkan"

            } else {
                // Kesalahan ke-3+: skip soal ini (sudah ada feedback sebelumnya)
                setTimeout(() => {
                    isEvaluating = false;
                    lastAnswerWrong = false;
                    currentIndex++;
                    loadQuestion();
                }, 1000);
            }
        }
    }

    // ── Answer Checker ─────────────────────────────────────────────
    function checkAnswer(q, ans) {
        if (q.type === 'mcq') {
            return ans === q.correctIndex;
        }
        if (q.type === 'fill') {
            const normalized = ans.toLowerCase().trim();
            return q.correct.map(c => c.toLowerCase().trim()).includes(normalized);
        }
        if (q.type === 'translate') {
            // Untuk translate: normalize spasi, huruf kecil, hapus tanda baca akhir
            const normalize = (str) => str.toLowerCase().trim().replace(/[.、。！？!?]+$/, '').replace(/\s+/g, ' ');
            const normalized = normalize(ans);
            return q.acceptedAnswers.map(a => normalize(a)).includes(normalized);
        }
        return false;
    }

    // ── Hint Handler ───────────────────────────────────────────────
    function useHint() {
        hintUsed[currentQuestion.id] = true;
        trackStat(currentQuestion.node_id, 'hint');
    }
    $: isHintVisible = currentQuestion && hintUsed[currentQuestion.id];

    function buildFallbackFeedback(question, userAnswer, correctAnswer) {
        const type = question.type;
        const focus = question.grammar_focus || "";
        const hint = question.hint || "";
        
        if (type === 'mcq') {
            return `Jawaban yang benar adalah "${correctAnswer}". ${focus ? `Topik: ${focus}. ` : ''}${hint}`;
        } else if (type === 'translate') {
            return `Kalimat yang benar: "${correctAnswer}". Perhatikan urutan kata dalam pola bahasa Jepang. ${hint}`;
        } else { // fill
            return `Yang benar adalah "${correctAnswer}". ${hint}`;
        }
    }

    // ── AI Feedback ────────────────────────────────────────────────
    async function requestAIFeedback(userAnswer) {
        showAiFeedback = true;
        isAiThinking = true;
        aiFeedbackText = "Alisa sedang merangkai penjelasan...";

        // Set last user answer and correct answer display
        if (currentQuestion.type === 'mcq') {
            lastUserAnswer = currentQuestion.options[userAnswer] || "";
        } else {
            lastUserAnswer = userAnswer;
        }

        correctAnswerDisplay = currentQuestion.type === 'mcq'
            ? currentQuestion.options[currentQuestion.correctIndex]
            : currentQuestion.type === 'translate'
                ? currentQuestion.acceptedAnswers[0]
                : currentQuestion.correct[0];

        try {
            const res = await fetch("http://localhost:8000/api/v1/quest/ai-correction", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    student_id: $user ? $user.id : "default",
                    question: currentQuestion.question,
                    grammar_focus: currentQuestion.grammar_focus || "",
                    user_answer: lastUserAnswer,
                    correct_answer: correctAnswerDisplay,
                    node_id: currentQuestion.node_id,
                    question_type: currentQuestion.type || "",
                    hint: currentQuestion.hint || "",
                    options: currentQuestion.options || null
                })
            });

            if (!res.ok) throw new Error("API Error");
            const data = await res.json();

            isAiThinking = false;

            // Typewriter effect
            aiFeedbackText = "";
            let i = 0;
            const textToType = data.feedback || buildFallbackFeedback(currentQuestion, lastUserAnswer, correctAnswerDisplay);

            const typeInterval = setInterval(() => {
                if (i < textToType.length) {
                    aiFeedbackText += textToType[i];
                    i++;
                } else {
                    clearInterval(typeInterval);
                }
            }, 20);

            // Audio TTS jika tersedia
            if (data.audio_url) {
                if (vrmController) vrmController.setSpeaking(true);
                audioPlayer.src = `http://localhost:8000/api/v1/get-audio/${data.audio_url}`;
                audioPlayer.play().catch(() => {
                    if (vrmController) vrmController.setSpeaking(false);
                });
                audioPlayer.onended = () => {
                    if (vrmController) vrmController.setSpeaking(false);
                };
            }
        } catch (error) {
            isAiThinking = false;
            aiFeedbackText = buildFallbackFeedback(currentQuestion, lastUserAnswer, correctAnswerDisplay);
        }
    }

    // ── Continue from AI Feedback ──────────────────────────────────
    function continueAfterFeedback() {
        showAiFeedback = false;
        lastAnswerWrong = false;
        fillAnswer = "";
        lastUserAnswer = "";
        correctAnswerDisplay = "";
        isAiThinking = false;
        currentIndex++;
        loadQuestion();
    }

    // ── Session Stats Submit ───────────────────────────────────────
    async function submitSessionStats() {
        if (!$user) return;
        try {
            await fetch("http://localhost:8000/api/v1/quest/session-stats", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    student_id: $user.id,
                    level_id: levelData.id,
                    stats: sessionStats
                })
            });
        } catch (e) {
            console.warn("Could not submit session stats:", e);
        }
    }

    // ── Progress ───────────────────────────────────────────────────
    // Progress bar hitung dari soal unik (bukan queue yang sudah repeat)
    $: originalTotal = levelData.questions.length;
    $: uniqueAnswered = Math.min(currentIndex, originalTotal);
    $: progressPercent = (uniqueAnswered / originalTotal) * 100;

    // ── Label tipe soal ────────────────────────────────────────────
    const questionTypeLabel = {
        mcq: "Pilihan Ganda",
        fill: "Isian",
        translate: "Terjemahkan"
    };
</script>

<div class="quest-engine h-full flex flex-col items-center justify-center p-6 text-slate-200">
    <div class="w-full max-w-2xl glass-panel rounded-[2.5rem] p-10 shadow-2xl relative overflow-hidden flex flex-col min-h-[520px] max-h-full">
        <!-- Subtle Glow -->
        <div class="absolute -top-20 -right-20 w-64 h-64 bg-indigo-200/20 rounded-full blur-[80px] pointer-events-none"></div>

        <!-- Header -->
        <div class="flex items-center gap-6 mb-10 relative z-10 shrink-0">
            <button on:click={onQuit} class="w-10 h-10 rounded-xl bg-white/20 hover:bg-rose-500/10 hover:text-rose-600 transition flex items-center justify-center text-slate-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
            <!-- Progress bar based on unique questions answered -->
            <div class="flex-grow bg-slate-200/50 h-2.5 rounded-full overflow-hidden border border-white/40">
                <div
                    class="bg-gradient-to-r from-indigo-500 to-purple-500 h-full transition-all duration-700"
                    style="width: {progressPercent}%"
                ></div>
            </div>
            <div class="px-4 py-2 bg-indigo-500 text-white font-black rounded-xl shadow-lg shadow-indigo-500/20 flex items-center gap-2">
                <span class="text-xs uppercase tracking-widest">XP</span>
                <span class="text-lg leading-none">{score}</span>
            </div>
        </div>

        <!-- Scrollable Content Wrapper -->
        <div class="flex-grow flex flex-col overflow-y-auto custom-scroll pr-1 relative z-10">
            {#if currentQuestion}
                <div class="flex-grow flex flex-col justify-center mb-6">
                    {#key currentQuestion.id + currentIndex}
                        <div in:fly={{ y: 20, duration: 500 }} out:fade={{ duration: 200 }} class="flex flex-col">
                            <!-- Question Header -->
                            <div class="text-center mb-6">
                                <div class="flex items-center justify-center gap-2 mb-3">
                                    <span class="inline-block px-3 py-1 bg-indigo-100 text-indigo-600 rounded-lg text-[10px] font-black uppercase tracking-[0.2em]">
                                        Soal {uniqueAnswered + 1} / {originalTotal}
                                    </span>
                                    <span class="inline-block px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-[0.15em]
                                        {currentQuestion.type === 'translate' ? 'bg-amber-100 text-amber-700' :
                                         currentQuestion.type === 'fill' ? 'bg-emerald-100 text-emerald-700' :
                                         'bg-slate-100 text-slate-600'}">
                                        {questionTypeLabel[currentQuestion.type] || currentQuestion.type}
                                    </span>
                                </div>
                                <!-- Grammar focus tag -->
                                {#if currentQuestion.grammar_focus}
                                    <p class="text-xs text-indigo-400 font-semibold mb-3 opacity-80">📚 {currentQuestion.grammar_focus}</p>
                                {/if}
                                <h3 class="text-2xl md:text-[1.65rem] font-black text-white leading-tight">
                                    {currentQuestion.question}
                                </h3>
                            </div>

                            <!-- ── MCQ ── -->
                            {#if currentQuestion.type === 'mcq'}
                                {#if !showAiFeedback}
                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {#each currentQuestion.options as option, i}
                                            <button
                                                on:click={() => handleAnswer(i)}
                                                disabled={isEvaluating || showAiFeedback}
                                                class="glass-card p-5 font-bold text-lg text-slate-200 hover:text-white hover:border-indigo-400 hover:bg-indigo-600/20 hover:shadow-indigo-500/10 transition-all disabled:opacity-50 text-left flex items-center gap-4"
                                            >
                                                <div class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-xs text-indigo-500 font-black shrink-0">
                                                    {String.fromCharCode(65 + i)}
                                                </div>
                                                {option}
                                            </button>
                                        {/each}
                                    </div>
                                {/if}

                            <!-- ── FILL ── -->
                            {:else if currentQuestion.type === 'fill'}
                                {#if !showAiFeedback}
                                    <div class="flex flex-col items-center">
                                        <input
                                            type="text"
                                            bind:value={fillAnswer}
                                            disabled={isEvaluating || showAiFeedback}
                                            placeholder="Ketik jawabanmu di sini..."
                                            class="w-full p-5 text-center rounded-2xl bg-white/90 border-2 transition-all text-xl font-bold text-slate-900 placeholder:text-slate-400 shadow-inner
                                                {lastAnswerWrong ? 'border-rose-400 bg-rose-50 focus:border-rose-400' : 'border-white/60 focus:border-indigo-400 focus:bg-white'}
                                                focus:outline-none focus:ring-4 focus:ring-indigo-500/5"
                                            on:keydown={(e) => e.key === 'Enter' && handleAnswer(fillAnswer)}
                                        />
                                        {#if lastAnswerWrong}
                                            <p class="text-rose-500 text-sm font-semibold mt-2" in:fade>❌ Belum tepat, coba lagi!</p>
                                        {/if}
                                        <button
                                            on:click={() => handleAnswer(fillAnswer)}
                                            disabled={isEvaluating || showAiFeedback || !fillAnswer.trim()}
                                            class="mt-6 px-10 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl shadow-xl shadow-indigo-500/20 transition-all active:scale-95 disabled:opacity-30 uppercase tracking-widest text-sm"
                                        >
                                            Periksa Jawaban
                                        </button>
                                    </div>
                                {/if}

                            <!-- ── TRANSLATE ── -->
                            {:else if currentQuestion.type === 'translate'}
                                {#if !showAiFeedback}
                                    <div class="flex flex-col items-center">
                                        <div class="w-full mb-3 p-4 bg-amber-500/10 border border-amber-500/25 rounded-2xl text-sm text-amber-300 font-medium text-center">
                                            💡 Tulis dalam romaji atau hiragana. Tidak perlu huruf kapital atau tanda baca.
                                        </div>
                                        <textarea
                                            bind:value={fillAnswer}
                                            disabled={isEvaluating || showAiFeedback}
                                            placeholder="Ketik terjemahan kalimat Jepangmu di sini..."
                                            rows="2"
                                            class="w-full p-5 text-center rounded-2xl bg-white/90 border-2 transition-all text-lg font-bold text-slate-900 placeholder:text-slate-400 shadow-inner resize-none
                                                {lastAnswerWrong ? 'border-rose-400 bg-rose-50' : 'border-white/60 focus:border-amber-400 focus:bg-white'}
                                                focus:outline-none focus:ring-4 focus:ring-amber-500/10"
                                            on:keydown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleAnswer(fillAnswer))}
                                        ></textarea>
                                        {#if lastAnswerWrong}
                                            <p class="text-rose-500 text-sm font-semibold mt-2" in:fade>❌ Belum tepat, coba lagi!</p>
                                        {/if}
                                        <button
                                            on:click={() => handleAnswer(fillAnswer)}
                                            disabled={isEvaluating || showAiFeedback || !fillAnswer.trim()}
                                            class="mt-5 px-10 py-4 bg-amber-500 hover:bg-amber-600 text-white font-black rounded-2xl shadow-xl shadow-amber-500/20 transition-all active:scale-95 disabled:opacity-30 uppercase tracking-widest text-sm"
                                        >
                                            Kirim Terjemahan
                                        </button>
                                    </div>
                                {/if}
                            {/if}

                            <!-- ── Hint Button ── -->
                            {#if !showAiFeedback && currentQuestion.hint}
                                <div class="mt-6 text-center">
                                    {#if !isHintVisible}
                                        <button
                                            on:click={useHint}
                                            class="text-xs text-slate-400 hover:text-indigo-500 transition font-semibold py-2 px-4 rounded-lg hover:bg-indigo-50/50"
                                        >
                                            🔍 Lihat Petunjuk <span class="opacity-60">(−2 XP)</span>
                                        </button>
                                    {:else}
                                        <div class="inline-block px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-sm text-slate-200 font-medium" in:fly={{ y: 5 }}>
                                            💡 {currentQuestion.hint}
                                        </div>
                                    {/if}
                                </div>
                            {/if}
                        </div>
                    {/key}
                </div>
            {/if}

            <!-- ── AI Feedback Panel ── -->
            {#if showAiFeedback}
                <div class="flex flex-col gap-6" in:fly={{ y: 20, duration: 400 }}>
                    <!-- Comparative display -->
                    <div class="flex flex-col sm:flex-row gap-4 w-full">
                        <div class="flex-1 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex flex-col shadow-sm backdrop-blur-sm">
                            <span class="text-[10px] text-rose-400 font-bold uppercase tracking-wider mb-1">Jawaban Kamu</span>
                            <span class="text-sm font-bold text-rose-200 line-through leading-relaxed">{lastUserAnswer || '-'}</span>
                        </div>
                        <div class="flex-1 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex flex-col shadow-sm backdrop-blur-sm">
                            <span class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider mb-1">Jawaban Benar</span>
                            <span class="text-sm font-bold text-emerald-200 leading-relaxed">{correctAnswerDisplay || '-'}</span>
                        </div>
                    </div>

                    <!-- Explanatory Bubble -->
                    <div class="p-8 glass-card border-indigo-200/50 bg-indigo-50/30 relative overflow-hidden">
                        <div class="absolute -top-10 -right-10 w-32 h-32 bg-indigo-500/5 rounded-full blur-2xl"></div>
                        <div class="flex items-center gap-3 mb-4">
                            <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-xl">👩‍🏫</div>
                            <div>
                                <h4 class="font-black text-white text-sm">A.L.I.S.A</h4>
                                <p class="text-[10px] text-indigo-400 font-bold uppercase tracking-wider">Penjelasan Pembelajaran</p>
                            </div>
                        </div>
                        
                        {#if isAiThinking}
                            <div class="thinking-content py-2">
                                <div class="thinking-dots-premium">
                                    <span></span><span></span><span></span>
                                </div>
                                <p class="thinking-label">A.L.I.S.A. sedang merangkai penjelasan...</p>
                            </div>
                        {:else}
                            <p class="text-slate-200 font-semibold leading-relaxed mb-6 italic">"{aiFeedbackText}"</p>

                            <button
                                on:click={continueAfterFeedback}
                                class="w-full py-4 bg-white/60 hover:bg-white/80 border border-white text-indigo-600 font-black rounded-2xl transition-all shadow-sm uppercase tracking-widest text-xs"
                            >
                                Mengerti, Lanjutkan Misi →
                            </button>
                        {/if}
                    </div>
                </div>
            {/if}
        </div>
    </div>
    <audio bind:this={audioPlayer} hidden></audio>
</div>

<style>
    .thinking-content {
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
        z-index: 1;
    }
    .thinking-dots-premium {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .thinking-dots-premium span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, #a78bfa, #818cf8);
        animation: think-bounce 1.4s infinite ease-in-out;
        box-shadow: 0 0 8px rgba(139, 92, 246, 0.4);
    }
    .thinking-dots-premium span:nth-child(2) {
        animation-delay: 0.16s;
    }
    .thinking-dots-premium span:nth-child(3) {
        animation-delay: 0.32s;
    }
    @keyframes think-bounce {
        0%, 80%, 100% {
            transform: translateY(0) scale(1);
            opacity: 0.5;
        }
        40% {
            transform: translateY(-8px) scale(1.2);
            opacity: 1;
        }
    }
    .thinking-label {
        font-size: 14px;
        font-weight: 600;
        color: #6366f1;
        letter-spacing: 0.02em;
        animation: label-fade 2s ease-in-out infinite;
        margin: 0;
    }
    @keyframes label-fade {
        0%, 100% {
            opacity: 0.6;
        }
        50% {
            opacity: 1;
        }
    }
</style>
