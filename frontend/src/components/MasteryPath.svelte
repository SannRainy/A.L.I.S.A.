<script>
    import { onMount } from "svelte";
    import { fly, fade, scale } from "svelte/transition";
    import { spring } from "svelte/motion";
    import { user } from "../stores/auth_store";
    import { backOut } from "svelte/easing";

    export let nodes = []; // default nodes: [{ id, label, type, status, last_reviewed }]
    export let isMini = false; // Mode minimap untuk tab Study
    
    // ── State ──────────────────────────────────────────────────────────────
    let viewMode = "snake"; // 'snake' | 'recommended'
    let recommendedNodes = [];
    let loadingRecommendation = false;

    let selectedNode = null;
    let loadingDetails = false;
    let nodeDetails = null;

    let shortestPathIds = [];
    let loadingPath = false;

    // XP Floating Animation Logic
    let popups = [];
    let popupId = 0;

    export function triggerXpPop(amount, x, y) {
        popups = [...popups, { id: popupId++, amount, x, y }];
        setTimeout(() => {
            popups = popups.slice(1);
        }, 1500);
    }

    function isRetentionLow(lastReviewedStr, status) {
        if (status !== "LEARNED" && status !== "MASTERED") return false;
        if (!lastReviewedStr) return false;
        
        const reviewDate = new Date(lastReviewedStr);
        const diffDays = (new Date() - reviewDate) / (1000 * 60 * 60 * 24);
        return diffDays > 7; // Gemetar kalau tidak direview lebih dari 7 hari
    }

    // Load recommended path (topological sort)
    async function loadRecommendedPath() {
        if (!$user) return;
        loadingRecommendation = true;
        try {
            const res = await fetch(`http://localhost:8000/api/v1/learning-path/${$user.id}`);
            const data = await res.json();
            if (data.status === "success" && data.path) {
                recommendedNodes = data.path;
            }
        } catch (e) {
            console.warn("Gagal memuat learning path rekomendasi:", e);
        } finally {
            loadingRecommendation = false;
        }
    }

    // Toggle view mode
    async function toggleViewMode(mode) {
        viewMode = mode;
        if (viewMode === "recommended" && recommendedNodes.length === 0) {
            await loadRecommendedPath();
        }
    }

    // Select node to show details drawer
    async function selectNode(node) {
        selectedNode = node;
        loadingDetails = true;
        nodeDetails = null;
        shortestPathIds = [];

        try {
            const res = await fetch(`http://localhost:8000/api/v1/kg/node/${encodeURIComponent(node.id)}`);
            const data = await res.json();
            if (data.status === "success" && data.node) {
                nodeDetails = data.node;
            }
        } catch (e) {
            console.error("Gagal mengambil detail node:", e);
        } finally {
            loadingDetails = false;
        }
    }

    // Calculate shortest path to a locked node using Neo4j
    async function findShortestPath() {
        if (!selectedNode || !$user) return;
        loadingPath = true;
        shortestPathIds = [];

        try {
            const res = await fetch(`http://localhost:8000/api/v1/kg/shortest-path/${$user.id}/${encodeURIComponent(selectedNode.id)}`);
            const data = await res.json();
            if (data.status === "success" && data.path) {
                // Simpan id node yang harus dipelajari
                shortestPathIds = data.path.map(n => n.id);
            }
        } catch (e) {
            console.error("Gagal menghitung shortest path:", e);
        } finally {
            loadingPath = false;
        }
    }

    function closeDrawer() {
        selectedNode = null;
        nodeDetails = null;
        shortestPathIds = [];
    }

    function getPopoverClass(colIndex, rowIndex) {
        const isReversed = rowIndex % 2 !== 0;
        if (colIndex === 1) {
            return "left-1/2 -translate-x-1/2";
        }
        if (colIndex === 0) {
            return isReversed ? "right-0" : "left-0";
        }
        // colIndex === 2
        return isReversed ? "left-0" : "right-0";
    }

    // Determine current nodes list based on view mode
    $: activeNodesList = viewMode === "recommended" ? recommendedNodes : nodes;

    // Split array into chunks of 3 for the snake path layout
    $: chunkedNodes = activeNodesList.reduce((resultArray, item, index) => { 
        const chunkIndex = Math.floor(index/3)
        if(!resultArray[chunkIndex]) {
            resultArray[chunkIndex] = [] // start a new chunk
        }
        resultArray[chunkIndex].push(item)
        return resultArray
    }, [])
</script>

<div class="mastery-container {isMini ? 'mini-mode' : ''} h-full flex flex-col">
    <!-- VIEW MODE TOGGLE (Only in full mode) -->
    {#if !isMini}
        <div class="flex justify-center gap-2 mb-6">
            <button
                on:click={() => toggleViewMode("snake")}
                class="px-4 py-2 rounded-xl text-xs font-bold transition {viewMode === 'snake' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}"
            >
                🗺️ Peta Jalur Utama (Snake)
            </button>
            <button
                on:click={() => toggleViewMode("recommended")}
                class="px-4 py-2 rounded-xl text-xs font-bold transition {viewMode === 'recommended' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}"
            >
                🧠 Rekomendasi Urutan Belajar
            </button>
        </div>
    {/if}

    {#if !isMini && viewMode === "recommended" && loadingRecommendation}
        <div class="flex-grow flex flex-col items-center justify-center p-12 text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mb-3"></div>
            <p class="text-slate-400 text-sm">Menyusun urutan belajar kognitif Anda...</p>
        </div>
    {:else}
        <!-- The Snake / Path Grid -->
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="flex-grow overflow-y-auto custom-scroll px-4 pt-12 pb-12 relative" on:click={closeDrawer} role="presentation">
            <!-- Floating XP Popups -->
            {#each popups as pop (pop.id)}
                <div class="absolute text-orange-400 font-bold text-2xl drop-shadow-md z-50 pointer-events-none" 
                     style="left: {pop.x}px; top: {pop.y}px;"
                     in:fly={{ y: 20, duration: 400 }}
                     out:fade>
                    +{pop.amount} XP
                </div>
            {/each}

            <div class="snake-path w-full max-w-md mx-auto relative mt-8">
                {#each chunkedNodes as chunk, rowIndex}
                    {@const hasSelectedNodeInRow = chunk.some(n => selectedNode && n.id === selectedNode.id)}
                    <div class="flex justify-between items-center w-full relative {rowIndex % 2 !== 0 ? 'flex-row-reverse' : 'flex-row'} mb-16 {hasSelectedNodeInRow ? 'z-40' : 'z-10'}">
                        
                        {#each chunk as node, colIndex}
                            {@const isHighlighted = shortestPathIds.includes(node.id)}
                            {@const isSelected = selectedNode && selectedNode.id === node.id}
                            <!-- Node Circle button -->
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div 
                                class="relative flex flex-col items-center group w-20 cursor-pointer {isSelected ? 'z-50' : 'z-10'}"
                                on:click|stopPropagation={() => !isMini && selectNode(node)}
                                role="button"
                                tabindex="0"
                            >
                                <div class="node-circle transition-all duration-300
                                    {node.status === 'LOCKED' ? 'bg-slate-800 border-slate-700 text-slate-500 opacity-60' : ''}
                                    {node.status === 'LEARNED' ? 'bg-indigo-600 border-indigo-400 text-white' : ''}
                                    {node.status === 'MASTERED' ? 'bg-yellow-400 border-yellow-200 text-amber-950 gold-pulse' : ''}
                                    {node.status === 'STRUGGLING' ? 'bg-red-900 border-red-500 text-white font-bold' : ''}
                                    {isRetentionLow(node.last_reviewed, node.status) ? 'retention-warning' : ''}
                                    {isHighlighted ? 'highlighted-node' : ''}
                                    "
                                >
                                    {#if node.status === 'MASTERED'}
                                        ⭐
                                    {:else if node.status === 'STRUGGLING'}
                                        🚨
                                    {:else if node.type?.toLowerCase() === 'kanji'}
                                        漢
                                    {:else if node.type?.toLowerCase() === 'grammar'}
                                        📚
                                    {:else}
                                        📓
                                    {/if}
                                </div>
                                
                                {#if !isMini}
                                    <span class="mt-3 text-xs font-bold text-slate-300 text-center max-w-[80px] break-words group-hover:text-white transition">
                                        {node.label}
                                    </span>
                                {/if}

                                <!-- Hover Tooltip (Desktop) -->
                                {#if !isMini}
                                    <div class="absolute -top-12 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-[10px] whitespace-nowrap pointer-events-none z-20 shadow-lg text-white">
                                        <span class="font-bold text-indigo-400">Status:</span> {node.status}<br>
                                        <span class="font-bold text-indigo-400">Tipe:</span> {node.type}
                                    </div>
                                {/if}

                                <!-- Popover details card (floating right next to the node circle) -->
                                {#if selectedNode && selectedNode.id === node.id}
                                    <div class="absolute top-[80px] z-30 w-72 bg-slate-900 border border-slate-700 rounded-[1.5rem] p-4 shadow-2xl flex flex-col cursor-default {getPopoverClass(colIndex, rowIndex)}"
                                         on:click|stopPropagation
                                         transition:fly={{ y: 10, duration: 250, easing: backOut }}
                                    >
                                        <!-- Close Button -->
                                        <button on:click|stopPropagation={closeDrawer}
                                            class="absolute top-3 right-3 w-6 h-6 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition flex items-center justify-center font-bold text-xs">
                                            ✕
                                        </button>

                                        <!-- Header -->
                                        <div class="flex items-center gap-3 mb-4 pr-4">
                                            <div class="w-10 h-10 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-xl text-white shrink-0">
                                                {#if selectedNode.type?.toLowerCase() === 'kanji'} 漢 {:else if selectedNode.type?.toLowerCase() === 'grammar'} 📚 {:else} 📓 {/if}
                                            </div>
                                            <div class="min-w-0">
                                                <h3 class="text-sm font-black text-white leading-tight truncate text-left">{selectedNode.label}</h3>
                                                <div class="flex gap-1.5 mt-0.5">
                                                    <span class="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[8px] font-bold uppercase">{selectedNode.type}</span>
                                                    <span class="px-1.5 py-0.5 rounded text-[8px] font-bold 
                                                        {selectedNode.status === 'MASTERED' ? 'bg-yellow-500/20 text-yellow-300' : ''}
                                                        {selectedNode.status === 'LEARNED' ? 'bg-indigo-500/20 text-indigo-300' : ''}
                                                        {selectedNode.status === 'STRUGGLING' ? 'bg-red-500/20 text-red-300' : ''}
                                                        {selectedNode.status === 'LOCKED' ? 'bg-slate-800 text-slate-500' : ''}
                                                    ">
                                                        {selectedNode.status}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Content Area -->
                                        <div class="overflow-y-auto max-h-[35vh] pr-1 custom-scroll space-y-3 text-left">
                                            {#if loadingDetails}
                                                <div class="text-center py-4">
                                                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500 mx-auto"></div>
                                                </div>
                                            {:else if nodeDetails}
                                                <!-- Kanji Node details -->
                                                {#if selectedNode.type?.toLowerCase() === "kanji"}
                                                    <div class="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50">
                                                        <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest block mb-1">Detail Kanji</span>
                                                        <div class="grid grid-cols-1 gap-1.5 text-[11px] text-slate-300">
                                                            <p><strong>Arti:</strong> <span class="text-white font-bold">{nodeDetails.arti}</span></p>
                                                            <p><strong>On'yomi:</strong> {nodeDetails.onyomi || '-'}</p>
                                                            <p><strong>Kun'yomi:</strong> {nodeDetails.kunyomi || '-'}</p>
                                                        </div>
                                                    </div>
                                                
                                                <!-- Vocab Node details -->
                                                {:else if selectedNode.type?.toLowerCase() === "vocab"}
                                                    <div class="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50">
                                                        <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest block mb-0.5">Arti Kosakata</span>
                                                        <p class="text-xs font-bold text-white mb-1">{nodeDetails.indonesian_meaning}</p>
                                                        {#if nodeDetails.pos?.length > 0}
                                                            <p class="text-[9px] text-slate-400"><strong>Kelas Kata:</strong> {nodeDetails.pos.join(", ")}</p>
                                                        {/if}
                                                    </div>

                                                <!-- Grammar Node details -->
                                                {:else if selectedNode.type?.toLowerCase() === "grammar"}
                                                    {#if nodeDetails.rules && nodeDetails.rules.filter(r => r && r.trim() !== "").length > 0}
                                                        <div class="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50 space-y-1.5">
                                                            <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest block mb-0.5">Aturan Pemakaian</span>
                                                            {#each nodeDetails.rules.filter(r => r && r.trim() !== "") as rule}
                                                                <p class="text-[11px] text-slate-300 leading-relaxed italic border-l-2 border-indigo-500 pl-1.5">{rule}</p>
                                                            {/each}
                                                        </div>
                                                    {/if}
                                                {/if}

                                                <!-- Example Sentence (shared) -->
                                                {#if nodeDetails.examples?.length > 0}
                                                    <div class="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50">
                                                        <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest block mb-1">Contoh</span>
                                                        <p class="text-xs text-white font-bold" style="font-family: 'Noto Sans JP', sans-serif;">
                                                            {nodeDetails.examples[0].text}
                                                        </p>
                                                        <p class="text-[11px] text-slate-400 mt-0.5">{nodeDetails.examples[0].meaning}</p>
                                                    </div>
                                                {/if}
                                            {:else}
                                                <p class="text-[11px] text-slate-400">Gagal memuat detail.</p>
                                            {/if}

                                            <!-- Last reviewed date -->
                                            {#if selectedNode.last_reviewed}
                                                <p class="text-[9px] text-slate-500 font-semibold uppercase">
                                                    📅 Ulasan: {new Date(selectedNode.last_reviewed).toLocaleDateString("id-ID")}
                                                </p>
                                            {/if}
                                        </div>

                                        <!-- Footer with Shortest Path button -->
                                        {#if selectedNode.status === 'LOCKED'}
                                            <div class="mt-4 pt-3 border-t border-slate-850 flex flex-col gap-2">
                                                <button
                                                    on:click|stopPropagation={findShortestPath}
                                                    disabled={loadingPath}
                                                    class="w-full py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-black rounded-lg shadow-md transition active:scale-95 text-[10px] uppercase tracking-wider disabled:opacity-50"
                                                >
                                                    {loadingPath ? "Mencari..." : "🔍 Jalur Tercepat"}
                                                </button>
                                                
                                                {#if shortestPathIds.length > 0}
                                                    <p class="text-[9px] text-indigo-400 font-bold text-center animate-pulse" in:fade>
                                                        Rute di-highlight!
                                                    </p>
                                                {/if}
                                            </div>
                                        {/if}
                                    </div>
                                {/if}
                            </div>
                            
                            <!-- Line connecting nodes horizontally -->
                            {#if colIndex < chunk.length - 1}
                                <div class="h-1 flex-1 {node.status !== 'LOCKED' ? 'bg-indigo-500' : 'bg-slate-800'} mx-2 transition-colors"></div>
                            {/if}
                        {/each}

                        <!-- Vertical line connecting rows at the end -->
                        {#if rowIndex < chunkedNodes.length - 1}
                            <div class="absolute w-1 h-16 {chunk[chunk.length-1].status !== 'LOCKED' ? 'bg-indigo-500' : 'bg-slate-800'} 
                                {rowIndex % 2 !== 0 ? 'left-10' : 'right-10'} -bottom-16 transition-colors -z-10"></div>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>
    {/if}
</div>

<style>
    .mastery-container {
        width: 100%;
        overflow: hidden;
    }

    .mini-mode .node-circle {
        width: 28px;
        height: 28px;
        font-size: 10px;
        border-width: 2px;
    }

    .mini-mode .mb-16 {
        margin-bottom: 2rem !important;
    }

    .mini-mode .h-16 {
        height: 3rem !important;
        bottom: -3rem !important;
    }

    .node-circle {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        border: 4px solid;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.3rem;
        font-weight: bold;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    .node-circle:hover {
        transform: scale(1.15);
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
    }

    /* Highlighted Shortest Path node */
    .highlighted-node {
        border-color: #22d3ee !important; /* cyan-400 */
        box-shadow: 0 0 20px 5px rgba(34, 211, 238, 0.6) !important;
        animation: glowPulseCyan 1.5s infinite ease-in-out;
    }

    @keyframes glowPulseCyan {
        0%, 100% { box-shadow: 0 0 15px 2px rgba(34, 211, 238, 0.6); }
        50% { box-shadow: 0 0 25px 8px rgba(34, 211, 238, 0.8); }
    }

    /* Gamification Juicy Glow */
    .gold-pulse {
        animation: goldPulse 2s infinite ease-in-out;
    }

    @keyframes goldPulse {
        0% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0.7); }
        50% { box-shadow: 0 0 20px 10px rgba(250, 204, 21, 0); }
        100% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0); }
    }

    /* Memory Retention Warning */
    .retention-warning {
        border-color: #ef4444; /* red-500 */
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
        animation: shake 5s infinite;
    }

    @keyframes shake {
        0%, 95% { transform: translate(0, 0); }
        96% { transform: translate(2px, 0); }
        97% { transform: translate(-2px, 0); }
        98% { transform: translate(2px, 0); }
        99% { transform: translate(-2px, 0); }
        100% { transform: translate(0, 0); }
    }
    :global(body.light) .snake-path .bg-slate-800 {
        background-color: #cbd5e1 !important; /* slate-300 */
    }
    :global(body.light) .node-circle {
        box-shadow: 0 4px 10px rgba(99, 102, 241, 0.08) !important;
    }
</style>
