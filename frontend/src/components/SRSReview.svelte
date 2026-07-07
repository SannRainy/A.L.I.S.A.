<script>
    import { onMount } from "svelte";
    import { fade, fly, scale } from "svelte/transition";
    import { backOut } from "svelte/easing";
    import { user } from "../stores/auth_store";

    export let onFinish; // Callback ketika ulasan selesai
    export let onQuit; // Callback keluar ke peta quest

    // ── State ──────────────────────────────────────────────────────────────
    let loading = true;
    let dueItems = [];
    let currentIndex = 0;
    let currentDetails = null;
    let loadingDetails = false;
    let isFlipped = false;
    let reviewsCompleted = 0;
    let xpEarned = 0;

    // Load due items
    onMount(async () => {
        if ($user) {
            await loadDueItems();
        }
    });

    async function loadDueItems() {
        loading = true;
        try {
            const res = await fetch(
                `http://localhost:8000/api/v1/srs/due/${$user.id}`,
            );
            const data = await res.json();
            if (data.status === "success" && data.items) {
                dueItems = data.items;
                currentIndex = 0;
                reviewsCompleted = 0;
                xpEarned = 0;
                if (dueItems.length > 0) {
                    await loadCurrentNodeDetails();
                }
            }
        } catch (e) {
            console.error("Gagal memuat due items:", e);
        } finally {
            loading = false;
        }
    }

    // Fetch details of active node from Neo4j exact node API
    async function loadCurrentNodeDetails() {
        const item = dueItems[currentIndex];
        if (!item) return;

        loadingDetails = true;
        currentDetails = null;
        isFlipped = false;

        try {
            const res = await fetch(
                `http://localhost:8000/api/v1/kg/node/${encodeURIComponent(item.node_id)}`,
            );
            const data = await res.json();
            if (data.status === "success" && data.node) {
                currentDetails = data.node;
            }
        } catch (e) {
            console.error("Gagal memuat detail node:", e);
        } finally {
            loadingDetails = false;
        }
    }

    // Submit review and load next card
    async function submitReview(quality) {
        const item = dueItems[currentIndex];
        if (!item || !$user) return;

        // Calculate XP earned: 5 XP for quality >= 3 (correct), 2 XP for incorrect
        const gain = quality >= 3 ? 5 : 2;
        xpEarned += gain;
        reviewsCompleted++;

        try {
            await fetch("http://localhost:8000/api/v1/srs/review", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: $user.id,
                    node_id: item.node_id,
                    node_type: item.node_type,
                    quality: quality,
                }),
            });
        } catch (e) {
            console.error("Gagal merekam ulasan:", e);
        }

        // Move to next card
        if (currentIndex < dueItems.length - 1) {
            currentIndex++;
            await loadCurrentNodeDetails();
        } else {
            // Finished all cards
            dueItems = [];
        }
    }

    function getTypeName(type) {
        const names = {
            vocab: "Kosakata",
            grammar: "Tata Bahasa",
            kanji: "Kanji",
        };
        return names[type?.toLowerCase()] || type;
    }
</script>

<div
    class="h-full overflow-hidden flex flex-col glass-panel rounded-[2.5rem] relative"
>
    <!-- Glow Backgrounds -->
    <div
        class="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none"
    ></div>
    <div
        class="absolute bottom-0 left-0 w-80 h-80 bg-teal-500/10 rounded-full blur-[100px] pointer-events-none"
    ></div>

    <!-- HEADER -->
    <div
        class="p-6 border-b border-white/10 flex items-center gap-4 flex-shrink-0 relative z-10"
    >
        <button
            on:click={onQuit}
            class="w-10 h-10 rounded-xl bg-white/20 hover:bg-slate-200/40 text-slate-300 hover:text-white transition flex items-center justify-center shrink-0"
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
                    d="M15 19l-7-7 7-7"
                />
            </svg>
        </button>
        <div>
            <h2 class="text-xl font-black text-white tracking-tight">
                SRS Review Dojo
            </h2>
            <p class="text-xs text-slate-300 mt-0.5">
                Ulas memori materi pelajaran bahasa Jepang Anda
            </p>
        </div>
    </div>

    <!-- MAIN INTERFACE -->
    {#if loading}
        <div
            class="flex-grow flex flex-col items-center justify-center p-6 text-center"
            in:fade
        >
            <div
                class="animate-spin rounded-full h-16 w-16 border-b-2 border-emerald-500 mb-4"
            ></div>
            <p class="text-slate-300 font-bold">Membuka Gulungan Memori...</p>
        </div>
    {:else if dueItems.length === 0}
        <!-- Congratulations / No items screen -->
        <div
            class="flex-grow flex flex-col items-center justify-center p-6 text-center relative z-10"
            in:fly={{ y: 20, duration: 400 }}
        >
            <div class="text-6xl mb-4">✨</div>
            <h3 class="text-2xl font-black text-white mb-2">Dojo Bersih!</h3>

            {#if reviewsCompleted > 0}
                <p class="text-slate-300 text-sm max-w-sm mb-6 leading-relaxed">
                    Kerja bagus! Anda telah menyelesaikan <span
                        class="text-emerald-400 font-bold"
                        >{reviewsCompleted} ulasan</span
                    > kartu memori hari ini.
                </p>
                <div
                    class="bg-slate-800/50 border border-slate-700 rounded-2xl p-5 mb-8 w-full max-w-xs text-center"
                >
                    <span
                        class="text-xs font-black text-slate-400 uppercase tracking-wider block"
                        >XP Diperoleh</span
                    >
                    <span class="text-3xl font-black text-amber-400"
                        >+{xpEarned} XP</span
                    >
                </div>
            {:else}
                <p class="text-slate-300 text-sm max-w-sm mb-8 leading-relaxed">
                    Tidak ada ulasan kartu memori yang jatuh tempo hari ini.
                    Kembali lagi besok untuk mereview materi baru!
                </p>
            {/if}

            <button
                on:click={onFinish}
                class="px-8 py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-black rounded-xl shadow-xl shadow-emerald-500/25 transition active:scale-95 uppercase tracking-widest text-xs"
            >
                Kembali ke Misi
            </button>
        </div>
    {:else if currentDetails}
        <div
            class="flex-grow overflow-y-auto p-6 flex flex-col items-center justify-center relative z-10"
            in:fade
        >
            <!-- Progress Counter -->
            <div class="w-full max-w-sm mb-6 text-center">
                <span
                    class="text-xs font-black text-slate-400 uppercase tracking-widest"
                >
                    Ulasan: {currentIndex + 1} / {dueItems.length}
                </span>
                <div
                    class="w-full bg-slate-700/50 h-2 rounded-full mt-2 overflow-hidden border border-white/5 shadow-inner"
                >
                    <div
                        class="bg-gradient-to-r from-emerald-400 to-teal-500 h-full rounded-full transition-all duration-300"
                        style="width: {((currentIndex + 1) / dueItems.length) *
                            100}%"
                    ></div>
                </div>
            </div>

            <!-- FLASHCARD (Click to Flip) -->
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div
                class="w-full max-w-sm aspect-[4/3] bg-white/95 rounded-[2rem] p-6 md:p-8 border-2 border-white/80 shadow-2xl flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-500 relative select-none hover:shadow-emerald-500/10 {isFlipped
                    ? 'rotate-y-180'
                    : ''}"
                on:click={() => (isFlipped = !isFlipped)}
            >
                {#if !isFlipped}
                    <!-- FRONT SIDE -->
                    <div
                        class="flex flex-col items-center justify-center h-full w-full"
                        in:scale={{ duration: 200 }}
                    >
                        <span
                            class="px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-[9px] font-black text-emerald-600 uppercase tracking-widest mb-4"
                        >
                            {getTypeName(dueItems[currentIndex].node_type)}
                        </span>

                        <!-- Main Card text -->
                        <div
                            class="text-[3rem] font-bold text-slate-900 leading-tight mb-2 font-serif"
                        >
                            {currentDetails.id}
                        </div>

                        {#if currentDetails.romaji}
                            <div
                                class="text-slate-400 text-sm font-semibold italic"
                            >
                                {currentDetails.romaji}
                            </div>
                        {:else if currentDetails.name && currentDetails.name !== currentDetails.id}
                            <div class="text-slate-400 text-sm font-semibold">
                                {currentDetails.name}
                            </div>
                        {/if}

                        <div
                            class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-8"
                        >
                            💡 Klik kartu untuk membalik
                        </div>
                    </div>
                {:else}
                    <!-- BACK SIDE -->
                    <div
                        class="flex flex-col items-center justify-between h-full w-full rotate-y-180"
                        in:scale={{ duration: 200 }}
                    >
                        <div
                            class="flex-grow flex flex-col items-center justify-center"
                        >
                            <!-- Title / Hiragana / Kanji -->
                            <div class="text-xl font-black text-slate-900 mb-1">
                                {currentDetails.id}
                            </div>

                            <!-- Meaning depending on node_type -->
                            {#if dueItems[currentIndex].node_type === "kanji"}
                                <div
                                    class="text-emerald-600 font-black text-lg mb-3"
                                >
                                    {currentDetails.arti}
                                </div>
                                <div
                                    class="space-y-1 text-slate-600 text-xs text-left"
                                >
                                    <p>
                                        <strong>On'yomi:</strong>
                                        {currentDetails.onyomi}
                                    </p>
                                    <p>
                                        <strong>Kun'yomi:</strong>
                                        {currentDetails.kunyomi}
                                    </p>
                                </div>
                            {:else if dueItems[currentIndex].node_type === "vocab"}
                                <div
                                    class="text-emerald-600 font-black text-lg mb-3"
                                >
                                    {currentDetails.indonesian_meaning}
                                </div>
                                {#if currentDetails.pos?.length > 0}
                                    <div
                                        class="text-slate-500 text-[10px] uppercase font-bold tracking-wider mb-2"
                                    >
                                        POS: {currentDetails.pos.join(", ")}
                                    </div>
                                {/if}
                            {:else}
                                <div
                                    class="text-emerald-600 font-bold text-sm mb-3"
                                >
                                    Tata Bahasa N5
                                </div>
                                {#if currentDetails.rules?.length > 0}
                                    <div
                                        class="text-slate-600 text-xs text-center max-w-[280px] leading-relaxed italic mb-2"
                                    >
                                        {currentDetails.rules[0]}
                                    </div>
                                {/if}
                            {/if}

                            <!-- Example sentence -->
                            {#if currentDetails.examples?.length > 0}
                                <div
                                    class="border-t border-slate-200 mt-4 pt-3 text-left w-full max-w-[260px]"
                                >
                                    <p
                                        class="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1"
                                    >
                                        Contoh Kalimat
                                    </p>
                                    <p
                                        class="text-xs text-slate-800 font-semibold"
                                        style="font-family: 'Noto Sans JP', sans-serif;"
                                    >
                                        {currentDetails.examples[0].text}
                                    </p>
                                    <p
                                        class="text-[10px] text-slate-500 mt-0.5"
                                    >
                                        {currentDetails.examples[0].meaning}
                                    </p>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}
            </div>

            <!-- MEMORY QUALITY RATING SCALE (Shown only when card is flipped) -->
            {#if isFlipped}
                <div
                    class="mt-8 w-full max-w-sm"
                    in:fly={{ y: 20, duration: 400 }}
                >
                    <p
                        class="text-xs font-black text-slate-300 text-center uppercase tracking-wider mb-3"
                    >
                        Seberapa baik Anda mengingat?
                    </p>
                    <div class="grid grid-cols-6 gap-1.5">
                        {#each [{ val: 0, label: "Lupa", color: "bg-red-500 hover:bg-red-400 text-white" }, { val: 1, label: "Ragu", color: "bg-orange-500 hover:bg-orange-400 text-white" }, { val: 2, label: "Hampir", color: "bg-amber-500 hover:bg-amber-400 text-white" }, { val: 3, label: "Ingat", color: "bg-lime-500 hover:bg-lime-400 text-slate-900" }, { val: 4, label: "Lancar", color: "bg-emerald-500 hover:bg-emerald-400 text-slate-900" }, { val: 5, label: "Mudah", color: "bg-teal-500 hover:bg-teal-400 text-slate-900" }] as rate}
                            <button
                                on:click={() => submitReview(rate.val)}
                                class="flex flex-col items-center p-2 rounded-xl border border-white/20 {rate.color} transition active:scale-95 shadow-md"
                            >
                                <span class="text-sm font-black leading-none"
                                    >{rate.val}</span
                                >
                                <span
                                    class="text-[8px] font-bold mt-1 tracking-tighter leading-none"
                                    >{rate.label}</span
                                >
                            </button>
                        {/each}
                    </div>
                </div>
            {:else}
                <!-- Tap to flip suggestion when not flipped -->
                <button
                    on:click={() => (isFlipped = true)}
                    class="mt-8 px-8 py-3.5 bg-white/10 hover:bg-white/20 border border-white/20 text-white font-bold rounded-2xl transition active:scale-95 shadow-lg"
                >
                    Tampilkan Jawaban
                </button>
            {/if}
        </div>
    {:else}
        <!-- Fallback if currentDetails fails to load -->
        <div
            class="flex-grow flex flex-col items-center justify-center p-6 text-center relative z-10"
            in:fade
        >
            <div class="text-6xl mb-4">⚠️</div>
            <h3 class="text-xl font-black text-white mb-2">
                Gagal Memuat Detail Kartu
            </h3>
            <p class="text-slate-300 text-sm max-w-sm mb-6 leading-relaxed">
                Materi pelajaran untuk ID <code
                    class="bg-slate-800 px-2 py-1 rounded text-amber-300"
                    >"{dueItems[currentIndex]?.node_id}"</code
                > tidak ditemukan di dalam database Neo4j.
            </p>
            <button
                on:click={async () => {
                    reviewsCompleted++;
                    if (currentIndex < dueItems.length - 1) {
                        currentIndex++;
                        await loadCurrentNodeDetails();
                    } else {
                        dueItems = [];
                    }
                }}
                class="px-6 py-2.5 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition active:scale-95 text-xs uppercase tracking-wider"
            >
                Lewati Kartu Ini
            </button>
        </div>
    {/if}
</div>

<style>
    .rotate-y-180 {
        transform: rotateY(
            0deg
        ); /* handled naturally in Svelte conditional view */
    }
</style>
