<script>
    import { fly, fade, scale } from "svelte/transition";
    import { backOut } from "svelte/easing";
    import { onMount } from "svelte";
    import { themeStore } from "../stores/theme_store.js";

    export let kanji;      // objek kanji saat ini
    export let setIndex;   // index dalam set (0-based)
    export let setTotal;   // total kanji dalam set
    export let onNext;     // callback setelah user selesai dengan kartu ini
    export let onQuit;

    // State kartu & tab
    let phase = "front"; // 'front' | 'reveal'
    let subMode = "info"; // 'info' | 'write'
    let showMnemonic = false;

    // Canvas drawing state
    let canvas;
    let ctx;
    let isDrawing = false;



    // Confusion pairs mapping
    const CONFUSION_PAIRS = {
        "人": { pair: "入", note: "人 (orang) vs 入 (masuk). Arah goresan atasnya berbeda!" },
        "八": { pair: "人", note: "八 (delapan) vs 人 (orang). Goresan delapan terpisah di atas." },
        "日": { pair: "月", note: "日 (matahari) vs 月 (bulan). Matahari kotak, bulan lonjong." },
        "白": { pair: "百", note: "白 (putih) vs 百 (seratus). Seratus punya atap datar." },
        "見": { pair: "貝", note: "見 (melihat) vs 貝 (kerang). Bagian bawah 見 melengkung keluar." },
        "木": { pair: "本", note: "木 (pohon) vs 本 (buku/asal). 本 memiliki garis horizontal pendek di tengah." },
        "右": { pair: "左", note: "右 (kanan - mulut 口) vs 左 (kiri - kerja 工)." },
        "土": { pair: "士", note: "土 (tanah) vs 士 (ksatria). Tanah garis bawahnya lebih panjang." }
    };

    $: confusion = CONFUSION_PAIRS[kanji.id] || null;
    $: strokeDots = Array(Math.min(kanji.strokes || 0, 14)).fill(0);

    function reveal() {
        phase = "reveal";
    }

    function next() {
        phase = "front";
        showMnemonic = false;
        subMode = "info";
        onNext();
    }


    // Drawing Canvas handlers
    function initCanvas() {
        if (!canvas) return;
        ctx = canvas.getContext("2d");
        clearCanvas();
    }

    function startDrawing(e) {
        isDrawing = true;
        draw(e);
    }

    function stopDrawing() {
        isDrawing = false;
        if (ctx) ctx.beginPath();
    }

    function draw(e) {
        if (!isDrawing || !ctx || !canvas) return;
        const rect = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const x = clientX - rect.left;
        const y = clientY - rect.top;

        ctx.lineWidth = 8;
        ctx.lineCap = "round";
        ctx.strokeStyle = $themeStore === "light" ? "#d97706" : "#fbbf24"; // amber-600 in light mode

        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y);
    }

    function clearCanvas() {
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    $: if (subMode === "write") {
        setTimeout(initCanvas, 50);
    }
</script>

<div class="flex flex-col items-center w-full p-4 md:p-6 flex-1 min-h-0 overflow-y-auto custom-scroll">
    <!-- Progress mini -->
    <div class="flex items-center gap-3 mb-4 w-full max-w-sm flex-shrink-0">
        <button on:click={onQuit} class="w-9 h-9 rounded-xl transition flex items-center justify-center {$themeStore === 'light' ? 'bg-slate-100 hover:bg-rose-100 text-slate-500 hover:text-rose-600 border border-slate-200' : 'bg-white/20 hover:bg-rose-500/10 text-slate-400 hover:text-rose-500'}">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
        </button>
        <div class="flex-grow h-2 rounded-full overflow-hidden border {$themeStore === 'light' ? 'bg-slate-200 border-slate-300' : 'bg-slate-200/50 border-white/40'}">
            <div class="bg-gradient-to-r from-amber-400 to-orange-500 h-full rounded-full transition-all duration-500"
                 style="width: {((setIndex) / setTotal) * 100}%"></div>
        </div>
        <span class="text-xs font-black tabular-nums {$themeStore === 'light' ? 'text-slate-600' : 'text-slate-400'}">{setIndex + 1}<span class={$themeStore === 'light' ? 'text-slate-400' : 'text-slate-300'}>/</span>{setTotal}</span>
    </div>

    <!-- Toggle Sub-Mode (Info vs Tulis) -->
    {#if phase === 'reveal'}
        <div class="flex gap-2 mb-4 p-1.5 rounded-xl border w-full max-w-sm flex-shrink-0 transition-colors duration-300 {$themeStore === 'light' ? 'bg-slate-100/90 border-slate-200 shadow-sm' : 'bg-slate-700/50 border-white/10'}">
            <button on:click={() => subMode = 'info'} class="flex-1 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer {subMode === 'info' ? 'bg-indigo-600 text-white shadow-sm' : ($themeStore === 'light' ? 'text-slate-600 hover:text-slate-900' : 'text-slate-300 hover:text-white')}">ℹ️ Detail</button>
            <button on:click={() => subMode = 'write'} class="flex-1 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer {subMode === 'write' ? 'bg-indigo-600 text-white shadow-sm' : ($themeStore === 'light' ? 'text-slate-600 hover:text-slate-900' : 'text-slate-300 hover:text-white')}">✍️ Latihan Tulis</button>
        </div>
    {/if}

    <!-- Kartu Kanji -->
    {#key kanji.id + phase + subMode}
        <div class="w-full max-w-sm shadow-2xl border rounded-[2.5rem] backdrop-blur-xl p-6 flex flex-col items-center gap-4 flex-shrink-0 transition-colors duration-300 {$themeStore === 'light' ? 'bg-white/95 border-indigo-100 shadow-slate-200' : 'bg-slate-800/80 border-white/30'}" in:fly={{ y: 20, duration: 450, easing: backOut }}>
            {#if phase === 'front'}
                <!-- FASE DEPAN -->
                <div class="text-center flex flex-col items-center w-full">
                    <div class="relative mb-4">
                        <div class="text-[7rem] leading-none font-bold select-none drop-shadow-sm {$themeStore === 'light' ? 'text-slate-900' : 'text-white'}" style="font-family: 'Noto Serif JP', serif;">
                            {kanji.id}
                        </div>
                        {#if kanji.frequency}
                            <div class="absolute -top-2 -right-2 bg-indigo-100 text-indigo-600 text-[9px] font-black px-2 py-0.5 rounded-full border border-indigo-200">
                                #{kanji.frequency}
                            </div>
                        {/if}
                    </div>

                    <div class="flex items-center gap-1 mb-6">
                        <span class="text-[10px] font-bold uppercase tracking-wider mr-1 {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-400'}">Coretan</span>
                        {#each strokeDots as _}
                            <div class="w-1.5 h-1.5 rounded-full bg-amber-400"></div>
                        {/each}
                        <span class="text-[10px] text-amber-500 font-black ml-1">{kanji.strokes}</span>
                    </div>

                    <button on:click={reveal} class="w-full py-3.5 bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-300 text-white font-black rounded-2xl shadow-lg transition active:scale-95 uppercase tracking-widest text-xs cursor-pointer">
                        Lihat Arti & Bacaan →
                    </button>
                </div>
            {:else if subMode === 'info'}
                <!-- DETAIL INFO -->
                <div class="text-center flex flex-col items-center gap-3 w-full">
                    <div class="text-5xl leading-none font-bold select-none {$themeStore === 'light' ? 'text-slate-900' : 'text-white'}" style="font-family: 'Noto Serif JP', serif;">
                        {kanji.id}
                    </div>
                    <div>
                        <p class="text-[9px] font-black uppercase tracking-widest mb-0.5 {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-400'}">Arti</p>
                        <p class="text-xl font-black capitalize {$themeStore === 'light' ? 'text-slate-900' : 'text-white'}">{kanji.arti}</p>
                    </div>
                    <div class="w-full grid grid-cols-2 gap-2 text-left">
                        <div class="p-2.5 rounded-xl border {$themeStore === 'light' ? 'bg-indigo-50 border-indigo-200' : 'bg-indigo-900/40 border-indigo-400/20'}">
                            <p class="text-[9px] font-black uppercase tracking-wider mb-0.5 {$themeStore === 'light' ? 'text-indigo-700' : 'text-indigo-300'}">On'yomi</p>
                            <p class="font-bold text-xs truncate {$themeStore === 'light' ? 'text-indigo-900' : 'text-indigo-200'}">{kanji.onyomi || '—'}</p>
                        </div>
                        <div class="p-2.5 rounded-xl border {$themeStore === 'light' ? 'bg-emerald-50 border-emerald-200' : 'bg-emerald-900/40 border-emerald-400/20'}">
                            <p class="text-[9px] font-black uppercase tracking-wider mb-0.5 {$themeStore === 'light' ? 'text-emerald-700' : 'text-emerald-300'}">Kun'yomi</p>
                            <p class="font-bold text-xs truncate {$themeStore === 'light' ? 'text-emerald-900' : 'text-emerald-200'}">{kanji.kunyomi || '—'}</p>
                        </div>
                    </div>

                    <!-- Mnemonic -->
                    <div class="w-full border-t pt-3 text-left {$themeStore === 'light' ? 'border-slate-200' : 'border-white/10'}">
                        <p class="text-[9px] font-black uppercase tracking-widest mb-1 {$themeStore === 'light' ? 'text-slate-500' : 'text-slate-400'}">Mnemonic</p>
                        <p class="text-xs p-2 rounded-xl {$themeStore === 'light' ? 'text-amber-900 bg-amber-50 border border-amber-200/60 font-medium' : 'text-slate-300 bg-amber-500/10'}">💡 {kanji.mnemonic}</p>
                    </div>

                    <!-- Confusion Pair Detector -->
                    {#if confusion}
                        <div class="w-full border p-2.5 rounded-xl text-left text-xs {$themeStore === 'light' ? 'bg-rose-50 border-rose-200' : 'bg-red-500/10 border-red-500/20'}">
                            <p class="font-bold mb-0.5 {$themeStore === 'light' ? 'text-rose-700' : 'text-red-400'}">⚠️ Hati-hati, Mirip dengan: {confusion.pair}</p>
                            <p class="leading-normal {$themeStore === 'light' ? 'text-slate-700' : 'text-slate-300'}">{confusion.note}</p>
                        </div>
                    {/if}

                    <div class="w-full flex gap-2 pt-2">
                        <button on:click={() => phase = 'front'} class="flex-grow py-2.5 font-black rounded-xl text-xs transition cursor-pointer {$themeStore === 'light' ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-slate-700 hover:bg-slate-600 text-white'}">Kembali</button>
                        <button on:click={next} class="flex-grow py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 text-white font-black rounded-xl text-xs shadow-lg transition active:scale-95 cursor-pointer">Lanjut →</button>
                    </div>
                </div>
            {:else}
                <!-- HANDWRITING CANVAS -->
                <div class="w-full flex flex-col items-center gap-3">
                    <p class="text-xs font-bold {$themeStore === 'light' ? 'text-slate-600' : 'text-slate-400'}">Ikuti bayangan kanji di bawah ini:</p>
                    <div class="relative rounded-2xl w-[240px] h-[240px] flex items-center justify-center overflow-hidden border {$themeStore === 'light' ? 'bg-slate-100 border-slate-300 shadow-inner' : 'bg-slate-900 border-slate-700'}">
                        <!-- Faint guide background -->
                        <div class="absolute inset-0 flex items-center justify-center text-[10rem] font-bold select-none pointer-events-none font-serif {$themeStore === 'light' ? 'text-slate-300 opacity-40' : 'text-slate-800 opacity-30'}">
                            {kanji.id}
                        </div>
                        <!-- Drawing canvas -->
                        <canvas bind:this={canvas} width={240} height={240} class="absolute inset-0 z-10 cursor-crosshair" on:mousedown={startDrawing} on:mousemove={draw} on:mouseup={stopDrawing} on:mouseleave={stopDrawing} on:touchstart|preventDefault={startDrawing} on:touchmove|preventDefault={draw} on:touchend|preventDefault={stopDrawing}></canvas>
                    </div>
                    <div class="flex gap-2 w-full max-w-[240px]">
                        <button on:click={clearCanvas} class="flex-1 py-2 font-bold text-xs rounded-xl transition cursor-pointer {$themeStore === 'light' ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-slate-700 hover:bg-slate-600 text-white'}">Hapus</button>
                        <button on:click={next} class="flex-1 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 text-white font-bold text-xs rounded-xl shadow-lg transition active:scale-95 cursor-pointer">Selesai</button>
                    </div>
                </div>
            {/if}
        </div>
    {/key}
</div>
