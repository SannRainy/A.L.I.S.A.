<script>
    import { onMount, onDestroy, tick } from "svelte";
    import { fly, fade } from "svelte/transition";
    import {
        examBatches,
        calculateExamScore,
    } from "../lib/data/exam_n5_dataset.js";
    import { user } from "../stores/auth_store";
    import { sfx } from "../lib/sfx_manager";
    import { applyFurigana } from "../lib/furigana";


    export let batchId = "exam_1";
    export let onFinish = () => {};
    export let onQuit = () => {};

    // ── State mesin ──────────────────────────────────────────────────
    let phase = "intro"; // 'intro' | 'exam' | 'review'
    let batch = null;
    let questions = [];
    let currentIndex = 0;
    let currentQuestion = null;

    // Jawaban yang dikumpulkan selama ujian
    let userAnswers = []; // [{ questionId, answer }]
    let selectedOption = null; // MCQ - pilihan terpilih
    let fillAnswer = ""; // Fill/Translate - input teks
    let isEvaluating = false;

    // Timer
    let timeLeft = 0; // detik
    let timerInterval = null;
    let timerWarning = false; // merah ketika ≤ 2 menit

    // Review state
    let examResult = null; // output dari calculateExamScore
    let reviewIndex = 0; // soal yang sedang dilihat di review

    // ── Inisialisasi ─────────────────────────────────────────────────
    onMount(() => {
        batch = examBatches.find((b) => b.id === batchId);
        if (!batch) return;
        questions = [...batch.questions];
        timeLeft = batch.time_limit_minutes * 60;
    });

    onDestroy(() => {
        clearInterval(timerInterval);
    });

    // ── Timer ────────────────────────────────────────────────────────
    function startTimer() {
        clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            timeLeft--;
            timerWarning = timeLeft <= 120; // 2 menit
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                finishExam(true); // waktu habis
            }
        }, 1000);
    }

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60)
            .toString()
            .padStart(2, "0");
        const s = (seconds % 60).toString().padStart(2, "0");
        return `${m}:${s}`;
    }

    // ── Mulai Ujian (dari Intro) ────────────────────────────────────
    function beginExam() {
        phase = "exam";
        currentIndex = 0;
        currentQuestion = questions[0];
        startTimer();
    }

    // ── Load Soal ───────────────────────────────────────────────────
    function loadQuestion(index) {
        currentQuestion = questions[index] || null;
        selectedOption = null;
        fillAnswer = "";
        isEvaluating = false;
    }

    // ── Submit Jawaban ───────────────────────────────────────────────
    async function submitAnswer(answer) {
        if (isEvaluating) return;
        isEvaluating = true;

        // Simpan jawaban (jawab tanpa skip → replace jika sudah ada)
        const existingIdx = userAnswers.findIndex(
            (a) => a.questionId === currentQuestion.id,
        );
        if (existingIdx >= 0) {
            userAnswers[existingIdx] = {
                questionId: currentQuestion.id,
                answer,
            };
        } else {
            userAnswers = [
                ...userAnswers,
                { questionId: currentQuestion.id, answer },
            ];
        }

        // Delay singkat lalu lanjut ke soal berikutnya (NO instant feedback)
        await tick();
        await new Promise((r) => setTimeout(r, 350));

        advanceQuestion();
    }

    // ── Lewati Soal (tandai kosong, lanjut) ─────────────────────────
    function skipQuestion() {
        if (isEvaluating) return;
        advanceQuestion();
    }

    // ── Lanjut ke Soal Berikutnya ────────────────────────────────────
    function advanceQuestion() {
        if (currentIndex < questions.length - 1) {
            currentIndex++;
            loadQuestion(currentIndex);
            isEvaluating = false;
        } else {
            finishExam(false);
        }
    }

    // ── Selesaikan Ujian ─────────────────────────────────────────────
    async function finishExam(timeUp = false) {
        clearInterval(timerInterval);
        examResult = calculateExamScore(userAnswers, batch);
        examResult.timeUp = timeUp;

        // Submit skor ke backend (fire-and-forget)
        if ($user) {
            try {
                await fetch("http://localhost:8000/api/v1/quest/submit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        user_id: $user.id,
                        level_id: `exam_mode_${batchId}`,
                        score: examResult.score,
                        session_stats: {
                            exam_batch: batchId,
                            correct: examResult.correctCount,
                            total: examResult.totalQuestions,
                            passed: examResult.passed,
                            time_up: timeUp,
                        },
                    }),
                });
            } catch (e) {
                console.warn("Failed to submit exam score:", e);
            }
        }

        phase = "review";
        reviewIndex = 0;
    }

    // ── Review ───────────────────────────────────────────────────────
    $: reviewQuestion = questions[reviewIndex] ?? null;
    $: reviewUserAnswer = userAnswers.find(
        (a) => a.questionId === reviewQuestion?.id,
    );
    $: reviewIsCorrect = examResult?.correctIds?.includes(reviewQuestion?.id);

    function getCorrectDisplay(q) {
        if (!q) return "";
        if (q.type === "mcq") return q.options[q.correctIndex];
        if (q.type === "fill") return q.correct[0];
        if (q.type === "translate") return q.acceptedAnswers[0];
        return "";
    }

    function getUserAnswerDisplay(q, ans) {
        if (!ans) return "—";
        if (q.type === "mcq") return q.options[ans.answer] ?? "—";
        return ans.answer || "—";
    }

    // ── Progress bar ─────────────────────────────────────────────────
    $: examProgress = ((currentIndex + 1) / questions.length) * 100;

    // ── Soal type labels ─────────────────────────────────────────────
    const typeLabel = {
        mcq: "Pilihan Ganda",
        fill: "Isian",
        translate: "Terjemahkan",
    };

    // ── Konfirmasi keluar ────────────────────────────────────────────
    let showQuitConfirm = false;
</script>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- PHASE: INTRO SCREEN                                               -->
<!-- ═════════════════════════════════════════════════════════════════ -->
{#if phase === "intro" && batch}
    <div
        class="h-full flex flex-col items-center justify-center p-6 text-slate-200"
        in:fade
    >
        <div class="w-full max-w-xl">
            <!-- Neon glow card -->
            <div
                class="relative rounded-[2.5rem] p-[2px] overflow-hidden exam-card-glow shadow-2xl"
            >
                <div
                    class="bg-slate-900/95 backdrop-blur-2xl rounded-[2.4rem] p-10 relative overflow-hidden"
                >
                    <!-- BG decoration -->
                    <div
                        class="absolute -top-20 -right-20 w-72 h-72 bg-red-500/10 rounded-full blur-[80px] pointer-events-none"
                    ></div>
                    <div
                        class="absolute -bottom-20 -left-20 w-60 h-60 bg-orange-500/10 rounded-full blur-[80px] pointer-events-none"
                    ></div>

                    <!-- Icon & Title -->
                    <div class="text-center mb-8 relative z-10">
                        <div class="text-7xl mb-4 drop-shadow-2xl">
                            {batch.icon}
                        </div>
                        <h2
                            class="text-3xl font-black text-white tracking-tight mb-1"
                        >
                            {batch.title}
                        </h2>
                        <span
                            class="inline-block px-3 py-1 bg-red-500/20 border border-red-400/30 rounded-full text-xs font-black text-red-300 uppercase tracking-widest"
                        >
                            Simulasi Ujian JLPT N5
                        </span>
                    </div>

                    <!-- Description -->
                    <p
                        class="text-white/60 text-sm text-center leading-relaxed mb-8 relative z-10"
                    >
                        {batch.description}
                    </p>

                    <!-- Exam Details Grid -->
                    <div class="grid grid-cols-2 gap-3 mb-8 relative z-10">
                        <div class="exam-info-card">
                            <span class="text-2xl mb-1">⏱️</span>
                            <span
                                class="text-xs text-white/50 font-semibold uppercase tracking-wider"
                                >Durasi</span
                            >
                            <span class="text-white font-black text-lg"
                                >{batch.time_limit_minutes} menit</span
                            >
                        </div>
                        <div class="exam-info-card">
                            <span class="text-2xl mb-1">📝</span>
                            <span
                                class="text-xs text-white/50 font-semibold uppercase tracking-wider"
                                >Jumlah Soal</span
                            >
                            <span class="text-white font-black text-lg"
                                >{questions.length} soal</span
                            >
                        </div>
                        <div class="exam-info-card">
                            <span class="text-2xl mb-1">🎯</span>
                            <span
                                class="text-xs text-white/50 font-semibold uppercase tracking-wider"
                                >Nilai Lulus</span
                            >
                            <span class="text-white font-black text-lg"
                                >≥ {batch.passing_score}%</span
                            >
                        </div>
                        <div class="exam-info-card">
                            <span class="text-2xl mb-1">🚫</span>
                            <span
                                class="text-xs text-white/50 font-semibold uppercase tracking-wider"
                                >Petunjuk</span
                            >
                            <span class="text-red-400 font-black text-lg"
                                >Tidak Ada</span
                            >
                        </div>
                    </div>

                    <!-- Warning Box -->
                    <div
                        class="mb-8 p-5 rounded-2xl bg-amber-500/10 border border-amber-400/25 relative z-10"
                    >
                        <p
                            class="text-amber-300 font-black text-sm mb-3 flex items-center gap-2"
                        >
                            ⚠️ Perhatian Sebelum Memulai
                        </p>
                        <ul
                            class="space-y-2 text-xs text-amber-100/70 font-medium"
                        >
                            <li class="flex items-start gap-2">
                                <span class="text-amber-400 shrink-0 mt-0.5"
                                    >•</span
                                > Tidak ada petunjuk (hint) atau umpan balik instan
                                selama ujian
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-amber-400 shrink-0 mt-0.5"
                                    >•</span
                                > Timer akan berjalan — ujian berakhir otomatis saat
                                waktu habis
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-amber-400 shrink-0 mt-0.5"
                                    >•</span
                                > Kamu bisa mereview semua jawaban setelah ujian
                                selesai
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-amber-400 shrink-0 mt-0.5"
                                    >•</span
                                >
                                Nilai lulus: minimal {batch.passing_score}% dari
                                total soal
                            </li>
                        </ul>
                    </div>

                    <!-- Buttons -->
                    <div class="flex flex-col gap-3 relative z-10">
                        <button
                            on:click={beginExam}
                            class="w-full py-4 bg-gradient-to-r from-red-500 to-orange-600 hover:from-red-400 hover:to-orange-500 text-white font-black rounded-2xl shadow-xl shadow-red-500/30 transition-all active:scale-95 uppercase tracking-widest text-sm"
                        >
                            🚀 Mulai Ujian Sekarang
                        </button>
                        <button
                            on:click={onQuit}
                            class="w-full py-3 bg-white/5 hover:bg-white/10 text-white/50 font-bold rounded-2xl transition text-sm"
                        >
                            Kembali ke Peta Quest
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ═════════════════════════════════════════════════════════════════ -->
    <!-- PHASE: EXAM                                                        -->
    <!-- ═════════════════════════════════════════════════════════════════ -->
{:else if phase === "exam" && currentQuestion}
    <!-- Quit Confirm Modal -->
    {#if showQuitConfirm}
        <div
            class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-md"
            in:fade
        >
            <div
                class="bg-slate-900 border border-white/10 rounded-[2rem] p-8 max-w-xs w-full text-center shadow-2xl"
                in:fly={{ y: 20 }}
            >
                <div class="text-4xl mb-3">⚠️</div>
                <h3 class="text-white font-black text-lg mb-2">
                    Keluar dari Ujian?
                </h3>
                <p class="text-white/50 text-sm mb-6">
                    Progres ujian ini tidak akan disimpan. Kamu harus memulai
                    ulang dari awal.
                </p>
                <div class="flex flex-col gap-2">
                    <button
                        on:click={() => {
                            clearInterval(timerInterval);
                            onQuit();
                        }}
                        class="w-full py-3 bg-rose-500/80 hover:bg-rose-500 text-white font-black rounded-xl transition text-sm uppercase tracking-wider"
                    >
                        Ya, Keluar
                    </button>
                    <button
                        on:click={() => (showQuitConfirm = false)}
                        class="w-full py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl transition text-sm"
                    >
                        Lanjutkan Ujian
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <div
        class="exam-engine h-full flex flex-col items-center justify-center p-4 text-slate-200"
    >
        <div class="w-full max-w-2xl flex flex-col gap-0">
            <!-- ── Exam Header Bar ── -->
            <div class="flex items-center gap-3 mb-4 px-1">
                <!-- Quit -->
                <button
                    on:click={() => (showQuitConfirm = true)}
                    class="w-9 h-9 rounded-xl bg-white/10 hover:bg-rose-500/20 hover:text-rose-400 transition flex items-center justify-center text-slate-400 shrink-0"
                    title="Keluar ujian"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        stroke-width="2.5"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            d="M6 18L18 6M6 6l12 12"
                        />
                    </svg>
                </button>

                <!-- Progress Bar -->
                <div
                    class="flex-grow bg-white/10 h-2 rounded-full overflow-hidden"
                >
                    <div
                        class="bg-gradient-to-r from-red-400 to-orange-500 h-full rounded-full transition-all duration-500"
                        style="width: {examProgress}%"
                    ></div>
                </div>

                <!-- Question counter -->
                <span class="text-xs font-black text-white/60 shrink-0"
                    >{currentIndex + 1}/{questions.length}</span
                >

                <!-- Timer -->
                <div
                    class="shrink-0 px-3 py-1.5 rounded-xl font-black text-sm flex items-center gap-1.5 transition-all duration-500 {timerWarning
                        ? 'bg-red-500/30 text-red-300 border border-red-400/40 timer-pulse'
                        : 'bg-white/10 text-white/80'}"
                >
                    ⏱ {formatTime(timeLeft)}
                </div>
            </div>

            <!-- ── Question Card ── -->
            <div
                class="glass-panel rounded-[2rem] p-8 shadow-2xl relative overflow-hidden min-h-[460px] flex flex-col"
            >
                <!-- BG glow -->
                <div
                    class="absolute -top-16 -right-16 w-52 h-52 bg-red-500/10 rounded-full blur-[60px] pointer-events-none"
                ></div>

                {#key currentQuestion.id + currentIndex}
                    <div
                        in:fly={{ y: 20, duration: 400 }}
                        out:fade={{ duration: 150 }}
                        class="flex flex-col flex-grow"
                    >
                        <!-- Question Meta -->
                        <div class="text-center mb-5">
                            <div
                                class="flex items-center justify-center gap-2 mb-2"
                            >
                                <span
                                    class="inline-block px-3 py-1 bg-red-500/20 border border-red-400/20 text-red-300 rounded-lg text-[10px] font-black uppercase tracking-[0.2em]"
                                >
                                    Ujian • Soal {currentIndex + 1}
                                </span>
                                <span
                                    class="inline-block px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-[0.15em]
                                    {currentQuestion.type === 'translate'
                                        ? 'bg-amber-100/20 text-amber-300'
                                        : currentQuestion.type === 'fill'
                                          ? 'bg-emerald-100/20 text-emerald-300'
                                          : 'bg-slate-700/60 text-slate-300'}"
                                >
                                    {typeLabel[currentQuestion.type]}
                                </span>
                            </div>
                            <!-- Grammar focus (visible) -->
                            <p
                                class="text-[11px] text-indigo-400/80 font-semibold mb-3"
                            >
                                📚 {currentQuestion.grammar_focus}
                            </p>
                            <!-- Question text -->
                            <h3
                                class="text-xl font-black text-white leading-snug whitespace-pre-line"
                            >
                                {@html applyFurigana(currentQuestion.question)}
                            </h3>
                        </div>

                        <!-- ── MCQ ── -->
                        {#if currentQuestion.type === "mcq"}
                            <div class="grid grid-cols-1 gap-3 mt-2">
                                {#each currentQuestion.options as option, i}
                                    <button
                                        on:click={() => {
                                            selectedOption = i;
                                            submitAnswer(i);
                                        }}
                                        disabled={isEvaluating}
                                        class="exam-option group flex items-center gap-4 p-4 text-left rounded-xl transition-all duration-200
                                            {selectedOption === i
                                            ? 'border-indigo-400 bg-indigo-500/20 text-white'
                                            : 'text-slate-300 hover:text-white hover:border-indigo-400/50'}
                                            disabled:opacity-50"
                                    >
                                        <div
                                            class="w-8 h-8 rounded-lg {selectedOption ===
                                            i
                                                ? 'bg-indigo-500 text-white'
                                                : 'bg-white/10 text-white/50 group-hover:bg-indigo-500/20'} flex items-center justify-center text-xs font-black shrink-0 transition-all"
                                        >
                                            {String.fromCharCode(65 + i)}
                                        </div>
                                        <span
                                            class="text-sm font-semibold leading-snug"
                                            >{@html applyFurigana(option)}</span
                                        >
                                    </button>
                                {/each}
                            </div>

                            <!-- ── FILL ── -->
                        {:else if currentQuestion.type === "fill"}
                            <div class="flex flex-col items-center gap-4 mt-4">
                                <input
                                    type="text"
                                    bind:value={fillAnswer}
                                    disabled={isEvaluating}
                                    placeholder="Ketik jawabanmu di sini..."
                                    class="w-full p-4 text-center rounded-2xl bg-white/90 border-2 border-white/40 text-xl font-bold text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10 transition"
                                    on:keydown={(e) =>
                                        e.key === "Enter" &&
                                        fillAnswer.trim() &&
                                        submitAnswer(fillAnswer.trim())}
                                />
                                <div class="flex gap-3 w-full">
                                    <button
                                        on:click={skipQuestion}
                                        disabled={isEvaluating}
                                        class="flex-1 py-3 bg-white/5 hover:bg-white/10 text-white/40 font-bold rounded-xl transition text-sm disabled:opacity-30"
                                    >
                                        Lewati →
                                    </button>
                                    <button
                                        on:click={() =>
                                            submitAnswer(fillAnswer.trim())}
                                        disabled={isEvaluating ||
                                            !fillAnswer.trim()}
                                        class="flex-[2] py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-xl shadow-lg shadow-indigo-500/20 transition disabled:opacity-30 text-sm uppercase tracking-widest"
                                    >
                                        Jawab
                                    </button>
                                </div>
                            </div>

                            <!-- ── TRANSLATE ── -->
                        {:else if currentQuestion.type === "translate"}
                            <div class="flex flex-col items-center gap-4 mt-4">
                                <div
                                    class="w-full p-3 bg-amber-500/10 border border-amber-400/20 rounded-xl text-xs text-amber-300 font-medium text-center"
                                >
                                    ✏️ Tulis dalam romaji atau hiragana. Tidak
                                    perlu tanda baca.
                                </div>
                                <textarea
                                    bind:value={fillAnswer}
                                    disabled={isEvaluating}
                                    placeholder="Ketik terjemahanmu..."
                                    rows="2"
                                    class="w-full p-4 text-center rounded-2xl bg-white/90 border-2 border-white/40 text-lg font-bold text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-amber-400 focus:ring-4 focus:ring-amber-500/10 transition resize-none"
                                    on:keydown={(e) =>
                                        e.key === "Enter" &&
                                        !e.shiftKey &&
                                        (e.preventDefault(),
                                        fillAnswer.trim() &&
                                            submitAnswer(fillAnswer.trim()))}
                                ></textarea>
                                <div class="flex gap-3 w-full">
                                    <button
                                        on:click={skipQuestion}
                                        disabled={isEvaluating}
                                        class="flex-1 py-3 bg-white/5 hover:bg-white/10 text-white/40 font-bold rounded-xl transition text-sm disabled:opacity-30"
                                    >
                                        Lewati →
                                    </button>
                                    <button
                                        on:click={() =>
                                            submitAnswer(fillAnswer.trim())}
                                        disabled={isEvaluating ||
                                            !fillAnswer.trim()}
                                        class="flex-[2] py-3 bg-amber-500 hover:bg-amber-600 text-white font-black rounded-xl shadow-lg shadow-amber-500/20 transition disabled:opacity-30 text-sm uppercase tracking-widest"
                                    >
                                        Kirim
                                    </button>
                                </div>
                            </div>
                        {/if}

                        <!-- No hints label -->
                        <div class="mt-auto pt-6 text-center">
                            <p
                                class="text-[11px] text-white/20 font-medium tracking-wider"
                            >
                                🚫 Ujian — Tanpa Petunjuk
                            </p>
                        </div>
                    </div>
                {/key}
            </div>
        </div>
    </div>

    <!-- ═════════════════════════════════════════════════════════════════ -->
    <!-- PHASE: REVIEW (hasil + pembahasan per soal)                       -->
    <!-- ═════════════════════════════════════════════════════════════════ -->
{:else if phase === "review" && examResult}
    <div
        class="h-full overflow-y-auto custom-scroll p-6 text-slate-200"
        in:fade
    >
        <div class="w-full max-w-2xl mx-auto flex flex-col gap-6">
            <!-- ── Result Card ── -->
            <div
                class="relative rounded-[2rem] p-[2px] overflow-hidden {examResult.passed
                    ? 'result-glow-pass'
                    : 'result-glow-fail'} shadow-2xl"
            >
                <div
                    class="bg-slate-900/95 rounded-[1.9rem] p-8 text-center relative overflow-hidden"
                >
                    <div
                        class="absolute inset-0 {examResult.passed
                            ? 'bg-emerald-500/5'
                            : 'bg-rose-500/5'}"
                    ></div>
                    <div class="relative z-10">
                        <div class="text-6xl mb-3 drop-shadow-2xl">
                            {examResult.passed ? "🏆" : "📖"}
                        </div>
                        <h2 class="text-3xl font-black text-white mb-1">
                            {examResult.passed ? "LULUS!" : "Belum Lulus"}
                        </h2>
                        <p class="text-white/50 text-sm mb-6">
                            {examResult.timeUp
                                ? "⏰ Waktu habis"
                                : "✅ Ujian selesai"}
                            — {batch.title}
                        </p>

                        <!-- Score Circle -->
                        <div
                            class="inline-flex flex-col items-center justify-center w-36 h-36 rounded-full border-4 {examResult.passed
                                ? 'border-emerald-400 bg-emerald-500/10'
                                : 'border-rose-400 bg-rose-500/10'} mb-6 shadow-xl"
                        >
                            <span
                                class="text-4xl font-black {examResult.passed
                                    ? 'text-emerald-300'
                                    : 'text-rose-300'}">{examResult.score}</span
                            >
                            <span
                                class="text-xs text-white/50 font-bold uppercase tracking-widest"
                                >/ 100</span
                            >
                        </div>

                        <!-- Stats grid -->
                        <div class="grid grid-cols-3 gap-3 mb-6">
                            <div
                                class="p-3 rounded-xl bg-white/5 border border-white/10"
                            >
                                <div
                                    class="text-xl font-black text-emerald-400"
                                >
                                    {examResult.correctCount}
                                </div>
                                <div
                                    class="text-[10px] text-white/40 uppercase tracking-wider"
                                >
                                    Benar
                                </div>
                            </div>
                            <div
                                class="p-3 rounded-xl bg-white/5 border border-white/10"
                            >
                                <div class="text-xl font-black text-rose-400">
                                    {examResult.totalQuestions -
                                        examResult.correctCount}
                                </div>
                                <div
                                    class="text-[10px] text-white/40 uppercase tracking-wider"
                                >
                                    Salah
                                </div>
                            </div>
                            <div
                                class="p-3 rounded-xl bg-white/5 border border-white/10"
                            >
                                <div class="text-xl font-black text-white/80">
                                    {examResult.totalQuestions}
                                </div>
                                <div
                                    class="text-[10px] text-white/40 uppercase tracking-wider"
                                >
                                    Total
                                </div>
                            </div>
                        </div>

                        <!-- Pass/Fail message -->
                        <div
                            class="p-4 rounded-2xl {examResult.passed
                                ? 'bg-emerald-500/10 border border-emerald-400/20'
                                : 'bg-amber-500/10 border border-amber-400/20'} text-sm font-medium mb-4"
                        >
                            {#if examResult.passed}
                                <p class="text-emerald-300">
                                    🎉 Selamat! Kamu melewati ujian simulasi
                                    JLPT N5 ini. Terus pertahankan!
                                </p>
                            {:else}
                                <p class="text-amber-300">
                                    💪 Jangan menyerah! Review jawaban di bawah,
                                    pelajari penjelasannya, lalu coba lagi.
                                </p>
                            {/if}
                        </div>

                        <!-- Action Buttons -->
                        <div class="flex gap-3">
                            <button
                                on:click={onQuit}
                                class="flex-1 py-3 bg-white/10 hover:bg-white/20 text-white font-black rounded-xl transition text-sm uppercase tracking-widest"
                            >
                                ← Kembali
                            </button>
                            <button
                                on:click={() => (reviewIndex = 0)}
                                class="flex-[2] py-3 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-black rounded-xl shadow-lg shadow-indigo-500/20 transition text-sm uppercase tracking-widest"
                            >
                                📋 Review Pembahasan
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ── Question Review ── -->
            <div class="flex flex-col gap-4">
                <h3 class="text-white font-black text-lg px-1">
                    📋 Pembahasan Soal
                    <span class="text-white/30 font-medium text-sm ml-2"
                        >({questions.length} soal)</span
                    >
                </h3>

                {#each questions as q, idx}
                    {@const ua = userAnswers.find((a) => a.questionId === q.id)}
                    {@const isCorrect = examResult.correctIds.includes(q.id)}
                    {@const skipped = !ua}
                    <div
                        class="review-card rounded-2xl overflow-hidden border {isCorrect
                            ? 'border-emerald-400/30'
                            : skipped
                              ? 'border-white/10'
                              : 'border-rose-400/30'}"
                    >
                        <!-- Card header -->
                        <div
                            class="flex items-center gap-3 px-5 py-3 {isCorrect
                                ? 'bg-emerald-500/10'
                                : skipped
                                  ? 'bg-white/5'
                                  : 'bg-rose-500/10'}"
                        >
                            <span class="text-lg shrink-0"
                                >{isCorrect
                                    ? "✅"
                                    : skipped
                                      ? "⬜"
                                      : "❌"}</span
                            >
                            <span
                                class="text-xs font-black text-white/50 uppercase tracking-wider"
                                >Soal {idx + 1}</span
                            >
                            <span
                                class="ml-auto text-[10px] px-2 py-0.5 rounded-full {q.type ===
                                'translate'
                                    ? 'bg-amber-500/20 text-amber-300'
                                    : q.type === 'fill'
                                      ? 'bg-emerald-500/20 text-emerald-300'
                                      : 'bg-slate-700 text-slate-300'} font-bold uppercase"
                            >
                                {typeLabel[q.type]}
                            </span>
                        </div>

                        <!-- Card body -->
                        <div class="p-5 bg-slate-900/60">
                            <p
                                class="text-[11px] text-indigo-400 font-semibold mb-2"
                            >
                                📚 {q.grammar_focus}
                            </p>
                            <p
                                class="text-white text-sm font-bold mb-4 whitespace-pre-line leading-snug"
                            >
                                {@html applyFurigana(q.question)}
                            </p>

                            <!-- Answer comparison -->
                            <div class="flex flex-col sm:flex-row gap-3 mb-4">
                                <div
                                    class="flex-1 p-3 rounded-xl {isCorrect
                                        ? 'bg-emerald-500/10 border border-emerald-400/20'
                                        : 'bg-rose-500/10 border border-rose-400/20'}"
                                >
                                    <p
                                        class="text-[10px] font-black uppercase tracking-wider mb-1 {isCorrect
                                            ? 'text-emerald-400'
                                            : 'text-rose-400'}"
                                    >
                                        Jawabanmu
                                    </p>
                                    <p
                                        class="text-sm font-bold {isCorrect
                                            ? 'text-emerald-200'
                                            : 'text-rose-200 line-through opacity-70'}"
                                    >
                                        {@html skipped
                                            ? "— (dilewati)"
                                            : applyFurigana(getUserAnswerDisplay(q, ua))}
                                    </p>
                                </div>
                                {#if !isCorrect}
                                    <div
                                        class="flex-1 p-3 rounded-xl bg-emerald-500/10 border border-emerald-400/20"
                                    >
                                        <p
                                            class="text-[10px] font-black uppercase tracking-wider text-emerald-400 mb-1"
                                        >
                                            Jawaban Benar
                                        </p>
                                        <p
                                            class="text-sm font-bold text-emerald-200"
                                        >
                                            {@html applyFurigana(getCorrectDisplay(q))}
                                        </p>
                                    </div>
                                {/if}
                            </div>

                            <!-- Explanation (always shown in review) -->
                            {#if q.explanation}
                                <div
                                    class="p-4 rounded-xl bg-indigo-500/10 border border-indigo-400/20"
                                >
                                    <p
                                        class="text-[10px] font-black text-indigo-400 uppercase tracking-wider mb-2"
                                    >
                                        💡 Penjelasan
                                    </p>
                                    <p
                                        class="text-sm text-white/80 leading-relaxed font-medium"
                                    >
                                        {@html applyFurigana(q.explanation)}
                                    </p>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/each}

                <!-- Bottom action -->
                <button
                    on:click={onQuit}
                    class="w-full py-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-black rounded-2xl shadow-xl shadow-indigo-500/20 transition uppercase tracking-widest text-sm mt-2 mb-4"
                >
                    ← Kembali ke Peta Quest
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    .exam-card-glow {
        background: linear-gradient(
            135deg,
            rgba(239, 68, 68, 0.5),
            rgba(249, 115, 22, 0.4),
            rgba(239, 68, 68, 0.2)
        );
    }
    .result-glow-pass {
        background: linear-gradient(
            135deg,
            rgba(52, 211, 153, 0.5),
            rgba(16, 185, 129, 0.3)
        );
    }
    .result-glow-fail {
        background: linear-gradient(
            135deg,
            rgba(239, 68, 68, 0.4),
            rgba(251, 146, 60, 0.3)
        );
    }
    .exam-info-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 1rem;
        border-radius: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .exam-option {
        border: 1.5px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 0.875rem;
    }
    .exam-option:hover:not(:disabled) {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(99, 102, 241, 0.1);
    }
    .review-card {
        background: rgba(15, 20, 40, 0.7);
        backdrop-filter: blur(12px);
    }
    .timer-pulse {
        animation: timer-blink 1s ease-in-out infinite;
    }
    @keyframes timer-blink {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.6;
        }
    }
</style>
