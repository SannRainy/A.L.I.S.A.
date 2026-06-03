<script>
    import { fly, fade } from "svelte/transition";
    import { questLevels } from "../lib/data/quest_n5_dataset.js";

    export let results; // { score, total, sessionStats, levelId }
    export let levelData = null;
    export let onContinue = () => {};

    // Hitung rank
    $: maxPossibleScore = (results.total || 10) * 10;
    $: percentage = results.score / maxPossibleScore * 100;
    $: rank = percentage >= 90 ? 'S' : percentage >= 70 ? 'A' : percentage >= 50 ? 'B' : 'C';
    $: rankColor = rank === 'S' ? 'from-yellow-400 to-amber-500' :
                   rank === 'A' ? 'from-indigo-500 to-purple-600' :
                   rank === 'B' ? 'from-teal-500 to-cyan-600' :
                   'from-rose-500 to-pink-600';
    $: message = rank === 'S' ? 'Sempurna! Semua grammar dikuasai dengan baik!' :
                 rank === 'A' ? 'Hebat! Kamu hampir sempurna.' :
                 rank === 'B' ? 'Cukup baik, tapi beberapa poin masih perlu latihan.' :
                 'Jangan menyerah! Ulangi misi ini untuk menguasai materinya.';

    // Analisis sessionStats untuk menentukan node lemah
    $: statsEntries = results.sessionStats ? Object.entries(results.sessionStats) : [];
    $: weakNodes = statsEntries
        .filter(([, stat]) => stat.wrong > 0)
        .sort((a, b) => b[1].wrong - a[1].wrong)
        .slice(0, 3);
    $: masteredNodes = statsEntries.filter(([, stat]) => stat.correct > 0 && stat.wrong === 0);

    // Cari grammar_focus dari levelData untuk weak node display
    function getGrammarFocusForNode(nodeId) {
        if (!levelData) return nodeId;
        const q = levelData.questions.find(q => q.node_id === nodeId);
        return q?.grammar_focus || nodeId;
    }

    // Cek apakah ada level berikutnya
    $: nextLevel = results.levelId
        ? questLevels[questLevels.findIndex(l => l.id === results.levelId) + 1]
        : null;

    // Animasi nilai XP
    let displayScore = 0;
    $: {
        if (results.score) {
            const target = results.score;
            const step = Math.max(1, Math.ceil(target / 30));
            const interval = setInterval(() => {
                displayScore = Math.min(displayScore + step, target);
                if (displayScore >= target) clearInterval(interval);
            }, 30);
        }
    }
</script>

<div class="quest-result h-full flex flex-col items-center justify-center p-6 overflow-y-auto">
    <div
        class="w-full max-w-lg bg-white/90 backdrop-blur-md rounded-[2.5rem] p-8 shadow-2xl border border-slate-200"
        in:fly={{ y: 50, duration: 600 }}
    >
        <!-- Header -->
        <div class="text-center mb-8">
            <h2 class="text-3xl font-black text-slate-800 mb-1">Misi Selesai! 🎉</h2>
            <p class="text-slate-500 font-medium text-sm">
                {levelData?.title || 'Level'} — {levelData?.description || ''}
            </p>
        </div>

        <!-- Rank & Score -->
        <div class="flex justify-center items-center gap-8 mb-8">
            <div class="flex flex-col items-center">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Rank</span>
                <div class="w-24 h-24 rounded-full bg-gradient-to-br {rankColor} flex items-center justify-center text-5xl font-black text-white shadow-xl border-4 border-white">
                    {rank}
                </div>
            </div>

            <div class="flex flex-col items-center">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">XP Diperoleh</span>
                <span class="text-5xl font-black text-amber-500">+{displayScore}</span>
                <span class="text-xs text-slate-400 mt-1">dari maks. {maxPossibleScore} XP</span>
            </div>
        </div>

        <!-- Pesan Alisa -->
        <div class="p-4 rounded-2xl bg-indigo-50 border border-indigo-100 mb-6 text-center">
            <p class="text-slate-700 font-medium italic text-sm leading-relaxed">
                "{message}"
            </p>
            <p class="text-xs text-indigo-400 font-bold mt-2">— A.L.I.S.A</p>
        </div>

        <!-- Breakdown Node -->
        {#if statsEntries.length > 0}
            <div class="mb-6">
                <h3 class="text-xs font-black text-slate-500 uppercase tracking-widest mb-3">📊 Analisis Per Materi</h3>

                {#if masteredNodes.length > 0}
                    <div class="mb-3">
                        <p class="text-xs text-emerald-600 font-bold mb-2">✅ Dikuasai Langsung</p>
                        <div class="flex flex-wrap gap-2">
                            {#each masteredNodes as [nodeId]}
                                <span class="px-2 py-1 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold rounded-lg">
                                    {getGrammarFocusForNode(nodeId).split('—')[0].trim()}
                                </span>
                            {/each}
                        </div>
                    </div>
                {/if}

                {#if weakNodes.length > 0}
                    <div>
                        <p class="text-xs text-rose-500 font-bold mb-2">⚠️ Perlu Latihan Lebih</p>
                        <div class="flex flex-col gap-2">
                            {#each weakNodes as [nodeId, stat]}
                                <div class="flex items-center justify-between px-3 py-2 bg-rose-50 border border-rose-100 rounded-xl">
                                    <span class="text-xs font-semibold text-rose-800">
                                        {getGrammarFocusForNode(nodeId).split('—')[0].trim()}
                                    </span>
                                    <span class="text-xs text-rose-500 font-bold">
                                        {stat.wrong}x salah
                                        {stat.hint > 0 ? ` · ${stat.hint}x petunjuk` : ''}
                                    </span>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        {/if}

        <!-- Rekomendasi -->
        {#if rank === 'C' || rank === 'B'}
            <div class="p-4 rounded-2xl bg-amber-50 border border-amber-200 mb-6 text-sm" in:fade>
                <p class="font-black text-amber-800 mb-1">💡 Rekomendasi A.L.I.S.A.</p>
                <p class="text-amber-700 font-medium">
                    {rank === 'C'
                        ? 'Ulangi misi ini dulu sebelum lanjut ke level berikutnya. Gunakan petunjuk jika perlu!'
                        : 'Coba ulangi soal yang salah, atau tanyakan ke A.L.I.S.A. di mode Chat untuk penjelasan lebih dalam.'}
                </p>
            </div>
        {/if}

        <!-- Action Buttons -->
        <div class="flex flex-col gap-3">
            <!-- Tombol utama: lanjut ke peta -->
            <button
                on:click={onContinue}
                class="w-full py-4 bg-slate-800 hover:bg-slate-900 text-white font-black rounded-2xl uppercase tracking-widest shadow-lg shadow-slate-800/20 transition transform hover:-translate-y-1 active:translate-y-0 text-sm"
            >
                {nextLevel ? `Kembali ke Peta →` : '🏆 Selesai! Kembali ke Peta'}
            </button>

            <!-- Info level berikutnya -->
            {#if nextLevel && rank !== 'C'}
                <div class="text-center text-xs text-slate-400 font-medium">
                    Level berikutnya: <span class="text-indigo-500 font-bold">{nextLevel.icon} {nextLevel.title}</span>
                    {#if nextLevel.prerequisites?.length > 0}
                        — {nextLevel.prerequisites.length} prerequisite node
                    {/if}
                </div>
            {/if}
        </div>
    </div>
</div>
