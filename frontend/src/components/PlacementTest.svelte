<script>
    import { onMount } from "svelte";
    import { fade, fly } from "svelte/transition";
    import { backOut } from "svelte/easing";
    import { user } from "../stores/auth_store";
    import { fetchFullProfile } from "../stores/profile_store";

    export let onFinish; // Callback kembali ke QuestMap dan me-reload progress
    export let onQuit; // Callback keluar dari tes tanpa menyimpan hasil

    // ── State ──────────────────────────────────────────────────────────────
    let view = "intro"; // 'intro' | 'loading' | 'quiz' | 'result'
    let questions = [];
    let currentIndex = 0;
    let userAnswers = [];
    let fillInput = "";
    let submitting = false;
    let placementResult = null;

    // Load questions from backend
    async function startTest() {
        view = "loading";
        try {
            const res = await fetch("http://localhost:8000/api/v1/placement/questions");
            const data = await res.json();
            if (data.status === "success" && data.questions) {
                questions = data.questions;
                currentIndex = 0;
                userAnswers = [];
                fillInput = "";
                view = "quiz";
            } else {
                console.error("Gagal memuat soal placement:", data);
                view = "intro";
            }
        } catch (e) {
            console.error("Kesalahan jaringan saat memuat soal:", e);
            view = "intro";
        }
    }

    $: currentQuestion = questions[currentIndex] ?? null;

    // Handle answer submission for current question
    function submitAnswer(selectedOptionIndex = null) {
        if (!currentQuestion) return;

        let isCorrect = false;
        let userAnswerText = "";

        if (currentQuestion.type === "mcq") {
            isCorrect = selectedOptionIndex === currentQuestion.correct;
            userAnswerText = String(selectedOptionIndex);
        } else if (currentQuestion.type === "fill") {
            const userText = fillInput.trim().toLowerCase();
            const correctAns = currentQuestion.correct.toLowerCase().trim();
            isCorrect = userText === correctAns;
            userAnswerText = fillInput.trim();
        }

        userAnswers = [
            ...userAnswers,
            {
                question_id: currentQuestion.id,
                user_answer: userAnswerText,
                is_correct: isCorrect
            }
        ];

        // Move to next question or complete test
        if (currentIndex < questions.length - 1) {
            currentIndex++;
            fillInput = "";
        } else {
            sendResults();
        }
    }

    // Submit all answers to backend
    async function sendResults() {
        if (!$user) return;
        view = "loading";
        submitting = true;

        try {
            const res = await fetch("http://localhost:8000/api/v1/placement/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: $user.id,
                    answers: userAnswers
                })
            });
            const data = await res.json();
            if (data.status === "success") {
                placementResult = data.result;
                // Refresh profile so the skip levels state updates
                await fetchFullProfile($user.id);
                view = "result";
            } else {
                console.error("Gagal mengirim hasil tes:", data);
                view = "intro";
            }
        } catch (e) {
            console.error("Kesalahan jaringan saat mengirim hasil:", e);
            view = "intro";
        } finally {
            submitting = false;
        }
    }

    // Helpers
    function getCategoryName(cat) {
        const names = {
            kanji: "漢字 Kanji",
            vocab: "語彙 Kosakata",
            grammar: "文法 Tata Bahasa"
        };
        return names[cat] || cat;
    }

    function getLevelLabel(level) {
        const labels = {
            absolute_beginner: "Absolute Beginner 🌿",
            N5_low: "N5 Beginner 🛡️ (Skip Level 1-2)",
            N5_mid: "N5 Intermediate ⚔️ (Skip Level 1-5)",
            N5_high: "N5 Expert 👑 (Skip Level 1-7)"
        };
        return labels[level] || level;
    }
</script>

<div class="h-full overflow-hidden flex flex-col glass-panel rounded-[2.5rem] relative">
    <!-- Glow Backgrounds -->
    <div class="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-80 h-80 bg-fuchsia-500/10 rounded-full blur-[100px] pointer-events-none"></div>

    <!-- VIEW: INTRO -->
    {#if view === "intro"}
        <div class="flex-grow overflow-y-auto p-6 md:p-10 flex flex-col items-center justify-center text-center relative z-10" in:fade>
            <div class="text-6xl mb-4 animate-bounce-slow">🎓</div>
            <h2 class="text-2xl md:text-3xl font-black text-white mb-2 tracking-tight">Tes Penempatan Level</h2>
            <p class="text-slate-300 text-sm max-w-md mb-8 leading-relaxed">
                Uji kemampuan bahasa Jepangmu melalui **30 soal komprehensif** (Kanji, Kosakata, dan Grammar). 
                Hasil tes ini akan membuka level kuis secara otomatis agar Anda tidak perlu mengulang materi yang sudah dikuasai!
            </p>

            <div class="w-full max-w-sm bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 mb-8 text-left space-y-3">
                <div class="flex items-center gap-3">
                    <span class="text-indigo-400 text-lg">📝</span>
                    <span class="text-slate-300 text-xs font-semibold">30 Soal Pilihan Ganda & Isian</span>
                </div>
                <div class="flex items-center gap-3">
                    <span class="text-indigo-400 text-lg">⏳</span>
                    <span class="text-slate-300 text-xs font-semibold">Tanpa batas waktu (kerjakan santai)</span>
                </div>
                <div class="flex items-center gap-3">
                    <span class="text-indigo-400 text-lg">🔓</span>
                    <span class="text-slate-300 text-xs font-semibold">Bisa melompati hingga 7 Level Quest sekaligus</span>
                </div>
            </div>

            <div class="flex gap-3 w-full max-w-xs">
                <button
                    on:click={onQuit}
                    class="flex-1 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-xl transition"
                >
                    Kembali
                </button>
                <button
                    on:click={startTest}
                    class="flex-2 py-3.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-black rounded-xl shadow-xl shadow-indigo-500/25 transition active:scale-95 uppercase tracking-wider text-xs"
                >
                    Mulai Tes
                </button>
            </div>
        </div>

    <!-- VIEW: LOADING -->
    {:else if view === "loading"}
        <div class="flex-grow flex flex-col items-center justify-center p-6 text-center relative z-10" in:fade>
            <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-500 mb-4"></div>
            <p class="text-slate-300 font-bold">Menganalisis Lembar Jawaban...</p>
            <p class="text-xs text-slate-500 mt-1">Harap tunggu sebentar, sistem sedang menyesuaikan tingkat graf kognitif Anda.</p>
        </div>

    <!-- VIEW: QUIZ -->
    {:else if view === "quiz" && currentQuestion}
        <div class="flex-grow overflow-y-auto p-6 md:p-8 flex flex-col items-center justify-center relative z-10" in:fly={{ y: 20, duration: 400 }}>
            <!-- Progress Header -->
            <div class="w-full max-w-md mb-6">
                <div class="flex items-center justify-between mb-2">
                    <span class="px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-black uppercase tracking-wider rounded-lg">
                        {getCategoryName(currentQuestion.category)}
                    </span>
                    <span class="text-xs font-black text-slate-400">
                        {currentIndex + 1} / {questions.length}
                    </span>
                </div>
                <!-- Progress Bar -->
                <div class="w-full bg-slate-700/50 h-2.5 rounded-full overflow-hidden border border-white/5 shadow-inner">
                    <div class="bg-gradient-to-r from-indigo-500 to-purple-600 h-full rounded-full transition-all duration-300"
                         style="width: {((currentIndex + 1) / questions.length) * 100}%"></div>
                </div>
            </div>

            <!-- Question Card -->
            <div class="w-full max-w-md bg-slate-800/50 backdrop-blur rounded-[2rem] p-6 md:p-8 border border-white/10 shadow-2xl">
                <h3 class="text-lg md:text-xl font-bold text-white text-center mb-6 leading-relaxed">
                    {currentQuestion.question}
                </h3>

                <!-- Tipe: MCQ (Pilihan Ganda) -->
                {#if currentQuestion.type === "mcq"}
                    <div class="space-y-3">
                        {#each currentQuestion.options as option, i}
                            <button
                                on:click={() => submitAnswer(i)}
                                class="w-full text-left p-4 rounded-xl border-2 border-slate-700 bg-slate-700/30 hover:border-indigo-500 hover:bg-indigo-500/10 transition active:scale-[0.98]"
                            >
                                <span class="text-indigo-400 font-black mr-2">{String.fromCharCode(65 + i)}.</span>
                                <span class="text-white font-medium">{option}</span>
                            </button>
                        {/each}
                    </div>

                <!-- Tipe: Fill-in-the-blank (Isian) -->
                {:else if currentQuestion.type === "fill"}
                    <div class="space-y-4">
                        <input
                            type="text"
                            bind:value={fillInput}
                            placeholder="Ketik jawaban Anda..."
                            class="w-full p-4 rounded-xl bg-slate-700/30 border-2 border-slate-700 text-white font-bold text-center placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none transition"
                            on:keydown={(e) => e.key === "Enter" && fillInput.trim() && submitAnswer()}
                        />
                        <button
                            on:click={() => submitAnswer()}
                            disabled={!fillInput.trim()}
                            class="w-full py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-black rounded-xl shadow-lg disabled:opacity-40 uppercase tracking-widest text-xs transition active:scale-95"
                        >
                            Jawab & Lanjut
                        </button>
                    </div>
                {/if}
            </div>

            <!-- Quit button -->
            <button
                on:click={onQuit}
                class="mt-6 text-xs text-slate-500 hover:text-slate-300 font-bold transition uppercase tracking-wider"
            >
                Keluar dari Tes
            </button>
        </div>

    <!-- VIEW: RESULT -->
    {:else if view === "result" && placementResult}
        <div class="flex-grow overflow-y-auto p-6 md:p-10 flex flex-col items-center justify-center text-center relative z-10" in:fly={{ y: 30, duration: 500, easing: backOut }}>
            <div class="text-6xl mb-4">🏆</div>
            <h2 class="text-2xl md:text-3xl font-black text-white mb-2 tracking-tight">Hasil Tes Penempatan</h2>
            <p class="text-slate-300 text-sm mb-6 max-w-sm">Selamat! Anda telah menyelesaikan tes kognitif onboarding.</p>

            <!-- Placed Level Result Box -->
            <div class="w-full max-w-md bg-gradient-to-br from-indigo-900/30 to-fuchsia-900/20 border-2 border-indigo-500/30 rounded-[2rem] p-6 mb-8 text-center shadow-xl">
                <span class="text-[10px] font-black text-indigo-300 uppercase tracking-widest block mb-1">Hasil Evaluasi Tingkat</span>
                <span class="text-2xl font-black text-white block mb-4">
                    {getLevelLabel(placementResult.estimated_level)}
                </span>

                <div class="w-20 h-20 rounded-full border-4 border-indigo-400 bg-indigo-500/10 flex flex-col items-center justify-center mx-auto mb-6 shadow-lg shadow-indigo-500/20">
                    <span class="text-xl font-black text-indigo-300 leading-none">{placementResult.total_score}</span>
                    <span class="text-[9px] font-bold text-slate-400 uppercase tracking-wider mt-1">/{placementResult.total_questions} Benar</span>
                </div>

                <!-- Category breakdown -->
                <div class="grid grid-cols-3 gap-3 border-t border-slate-700/50 pt-4">
                    {#each Object.entries(placementResult.category_scores) as [cat, score]}
                        <div class="text-center">
                            <span class="text-[9px] font-black text-slate-400 uppercase tracking-wider block">{cat}</span>
                            <span class="text-lg font-black text-white block mt-0.5">{score} <span class="text-xs text-slate-400">/{placementResult.category_totals[cat]}</span></span>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Congratulations Text -->
            <p class="text-xs text-slate-400 mb-8 max-w-xs leading-relaxed">
                {#if placementResult.mastered_levels.length > 0}
                    Berdasarkan tes, level kuis yang dilewati ({placementResult.mastered_levels.join(", ")}) telah ditandai sebagai dikuasai pada peta materi kognitif Anda.
                {:else}
                    Anda ditempatkan di tingkat awal. Semangat belajarnya dari awal ya untuk membangun fondasi yang solid! 🌟
                {/if}
            </p>

            <button
                on:click={onFinish}
                class="w-full max-w-xs py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 text-white font-black rounded-xl shadow-xl shadow-emerald-500/25 transition active:scale-95 uppercase tracking-widest text-xs"
            >
                Masuk ke Quest Map
            </button>
        </div>
    {/if}
</div>

<style>
    .animate-bounce-slow {
        animation: bounce-slow 3s infinite ease-in-out;
    }
    @keyframes bounce-slow {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .flex-2 {
        flex: 2 2 0%;
    }
</style>
