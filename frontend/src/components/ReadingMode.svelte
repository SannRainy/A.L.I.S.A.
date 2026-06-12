<script>
    import { onMount, onDestroy } from "svelte";
    import { fade } from "svelte/transition";
    import { user } from "../stores/auth_store";
    import { applyFurigana } from "../lib/furigana";


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

    export let vrmController = null;

    // Audio Playback
    let audioPlayer = null;
    let isPlaying = false;

    function stopAudio() {
        if (audioPlayer) {
            audioPlayer.pause();
            audioPlayer = null;
        }
        isPlaying = false;
        if (vrmController) vrmController.setSpeaking(false);
    }

    function toggleAudio() {
        console.log("[ReadingMode] toggleAudio: vrmController =", vrmController, "isPlaying =", isPlaying);
        if (!selectedPassage) return;
        if (!audioPlayer) {
            audioPlayer = new Audio(`/audio/reading/${selectedPassage.id}.wav`);
            audioPlayer.onended = () => {
                isPlaying = false;
                if (vrmController) vrmController.setSpeaking(false);
            };
        }
        if (isPlaying) {
            audioPlayer.pause();
            isPlaying = false;
            if (vrmController) vrmController.setSpeaking(false);
        } else {
            if (vrmController) vrmController.setSpeaking(true);
            audioPlayer.play().catch(e => {
                console.error("Audio playback failed:", e);
                if (vrmController) vrmController.setSpeaking(false);
                isPlaying = false;
            });
            isPlaying = true;
        }
    }

    onDestroy(() => {
        stopAudio();
    });

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
        stopAudio();
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
        stopAudio();
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
                        <div class="flex gap-2">
                            <button
                                on:click={toggleAudio}
                                class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold rounded-lg transition flex items-center gap-2"
                            >
                                <span>{isPlaying ? "⏸️ Pause" : "🔊 Dengarkan"}</span>
                            </button>
                            <button
                                on:click={() => showTranslation = !showTranslation}
                                class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm rounded-lg transition"
                            >
                                {showTranslation ? "Sembunyikan" : "Tampilkan"} Terjemahan
                            </button>
                        </div>
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
