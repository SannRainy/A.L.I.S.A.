<script>
    import { fly, fade, scale } from "svelte/transition";
    import { backOut } from "svelte/easing";

    export let kanji;      // objek kanji saat ini
    export let setIndex;   // index dalam set (0-based)
    export let setTotal;   // total kanji dalam set
    export let onNext;     // callback setelah user selesai dengan kartu ini
    export let onQuit;

    // State kartu
    let phase = "front"; // 'front' | 'reveal'
    let showMnemonic = false;

    function reveal() {
        phase = "reveal";
    }

    function next() {
        phase = "front";
        showMnemonic = false;
        onNext();
    }

    // Hitung jumlah coretan (stars visualization)
    $: strokeDots = Array(Math.min(kanji.strokes || 0, 14)).fill(0);
</script>

<div class="flex flex-col items-center justify-center h-full p-6">

    <!-- Progress mini -->
    <div class="flex items-center gap-3 mb-8">
        <button on:click={onQuit} class="w-9 h-9 rounded-xl bg-white/20 hover:bg-rose-500/10 hover:text-rose-500 text-slate-400 transition flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
        </button>
        <div class="flex-grow bg-slate-200/50 h-2 rounded-full overflow-hidden border border-white/40">
            <div class="bg-gradient-to-r from-amber-400 to-orange-500 h-full rounded-full transition-all duration-500"
                 style="width: {((setIndex) / setTotal) * 100}%"></div>
        </div>
        <span class="text-xs font-black text-slate-400 tabular-nums">{setIndex + 1}<span class="text-slate-300">/</span>{setTotal}</span>
    </div>

    <!-- Kartu Kanji -->
    {#key kanji.id + phase}
        <div
            class="w-full max-w-sm"
            in:fly={{ y: 30, duration: 500, easing: backOut }}
        >
            <!-- FASE DEPAN: Tampilkan Kanji -->
            {#if phase === 'front'}
                <div class="bg-slate-800/80 backdrop-blur-xl rounded-[2.5rem] p-10 shadow-2xl border border-white/30 text-center flex flex-col items-center">
                    <!-- Kanji Besar -->
                    <div class="relative mb-6">
                        <div class="text-[7rem] leading-none font-bold text-white select-none drop-shadow-sm"
                             style="font-family: 'Noto Serif JP', serif;">
                            {kanji.id}
                        </div>
                        <!-- Frekuensi rank -->
                        {#if kanji.frequency}
                            <div class="absolute -top-2 -right-2 bg-indigo-100 text-indigo-600 text-[9px] font-black px-2 py-0.5 rounded-full border border-indigo-200">
                                #{kanji.frequency}
                            </div>
                        {/if}
                    </div>

                    <!-- Coretan -->
                    <div class="flex items-center gap-1 mb-6">
                        <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mr-1">Coretan</span>
                        {#each strokeDots as _, i}
                            <div class="w-1.5 h-1.5 rounded-full bg-amber-400"></div>
                        {/each}
                        <span class="text-[10px] text-amber-500 font-black ml-1">{kanji.strokes}</span>
                    </div>

                    <!-- Tombol Lihat Arti -->
                    <button
                        on:click={reveal}
                        class="w-full py-4 bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-300 hover:to-orange-400 text-white font-black rounded-2xl shadow-xl shadow-amber-500/25 transition-all active:scale-95 uppercase tracking-widest text-sm"
                    >
                        Lihat Arti & Bacaan →
                    </button>
                </div>

            <!-- FASE BELAKANG: Tampilkan Detail -->
            {:else}
                <div class="bg-slate-800/80 backdrop-blur-xl rounded-[2.5rem] p-8 shadow-2xl border border-white/30 text-center flex flex-col items-center gap-5">
                    <!-- Kanji kecil di atas -->
                    <div class="text-5xl leading-none font-bold text-white select-none"
                         style="font-family: 'Noto Serif JP', serif;">
                        {kanji.id}
                    </div>

                    <!-- Arti -->
                    <div>
                        <p class="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">Arti</p>
                        <p class="text-2xl font-black text-white capitalize">{kanji.arti}</p>
                    </div>

                    <!-- Pembacaan -->
                    <div class="w-full grid grid-cols-2 gap-3">
                        <div class="p-3 rounded-2xl bg-indigo-900/40 border border-indigo-400/30">
                            <p class="text-[9px] font-black text-indigo-300 uppercase tracking-wider mb-1">On'yomi</p>
                            <p class="font-black text-indigo-200 text-sm leading-snug">{kanji.onyomi || '—'}</p>
                        </div>
                        <div class="p-3 rounded-2xl bg-emerald-900/40 border border-emerald-400/30">
                            <p class="text-[9px] font-black text-emerald-300 uppercase tracking-wider mb-1">Kun'yomi</p>
                            <p class="font-black text-emerald-200 text-sm leading-snug">{kanji.kunyomi || '—'}</p>
                        </div>
                    </div>

                    <!-- Mnemonic (opsional, bisa di-toggle) -->
                    {#if kanji.mnemonic}
                        <div class="w-full">
                            {#if !showMnemonic}
                                <button
                                    on:click={() => showMnemonic = true}
                                    class="text-xs text-slate-400 hover:text-amber-500 font-semibold transition py-1"
                                >
                                    💡 Lihat Bantuan Mengingat
                                </button>
                            {:else}
                                <div class="w-full p-3 rounded-2xl bg-amber-50 border border-amber-100 text-sm text-amber-800 font-medium text-left leading-relaxed" in:fade>
                                    💡 {kanji.mnemonic}
                                </div>
                            {/if}
                        </div>
                    {/if}

                    <!-- Aksi -->
                    <div class="w-full flex gap-3 mt-1">
                        <button
                            on:click={() => { phase = 'front'; showMnemonic = false; }}
                            class="flex-1 py-3 bg-slate-700 hover:bg-slate-600 text-white font-black rounded-2xl transition text-sm"
                        >
                            ← Lihat Lagi
                        </button>
                        <button
                            on:click={next}
                            class="flex-1 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 text-white font-black rounded-2xl shadow-lg shadow-indigo-500/25 transition-all active:scale-95 text-sm"
                        >
                            Lanjut →
                        </button>
                    </div>
                </div>
            {/if}
        </div>
    {/key}

    <!-- Hint teks -->
    <p class="mt-6 text-xs text-slate-400 font-medium text-center">
        {phase === 'front' ? 'Tebak artinya dulu, baru lihat!' : 'Ingat-ingat baik-baik ya! 🧠'}
    </p>
</div>
