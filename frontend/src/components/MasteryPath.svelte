<script>
    import { onMount } from "svelte";
    import { fly, fade } from "svelte/transition";
    import { spring } from "svelte/motion";

    export let nodes = []; // e.g. [{ id: 1, label: "Watashi", type: "vocab", status: "MASTERED", last_reviewed: "2026-03-01T00:00:00" }, ...]
    export let isMini = false; // Mode minimap untuk tab Study
    
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

    // Split array into chunks of 3 for the snake path
    $: chunkedNodes = nodes.reduce((resultArray, item, index) => { 
        const chunkIndex = Math.floor(index/3)
        if(!resultArray[chunkIndex]) {
            resultArray[chunkIndex] = [] // start a new chunk
        }
        resultArray[chunkIndex].push(item)
        return resultArray
    }, [])
</script>

<div class="mastery-container {isMini ? 'mini-mode' : ''}">
    {#if !isMini}
        <div class="mb-8 text-center">
            <h2 class="text-2xl font-black text-white px-4">Peta Pembelajaran N5</h2>
            <p class="text-slate-400 text-sm mt-1 mb-4">Teruslah berlatih agar otak keduamu berkembang!</p>
        </div>
    {/if}

    <div class="snake-path w-full max-w-md mx-auto relative px-4 pb-12">
        <!-- Floating XP Popups -->
        {#each popups as pop (pop.id)}
            <div class="absolute text-orange-400 font-bold text-2xl drop-shadow-md z-50 pointer-events-none" 
                 style="left: {pop.x}px; top: {pop.y}px;"
                 in:fly={{ y: 20, duration: 400 }}
                 out:fade>
                +{pop.amount} XP
            </div>
        {/each}

        <!-- The Snake grid -->
        {#each chunkedNodes as chunk, rowIndex}
            <!-- Menggunakan row-reverse pada index ganjil dlm looping menghasilkan S-shape -->
            <div class="flex justify-between items-center w-full relative {rowIndex % 2 !== 0 ? 'flex-row-reverse' : 'flex-row'} mb-16">
                
                {#each chunk as node, colIndex}
                    <!-- Node -->
                    <div class="relative flex flex-col items-center group z-10 w-20">
                        <div class="node-circle
                            {node.status === 'LOCKED' ? 'bg-slate-700 border-slate-600 grayscale' : ''}
                            {node.status === 'LEARNED' ? 'bg-indigo-600 border-indigo-400' : ''}
                            {node.status === 'MASTERED' ? 'bg-yellow-400 border-yellow-200 gold-pulse' : ''}
                            {isRetentionLow(node.last_reviewed, node.status) ? 'retention-warning' : ''}
                            "
                        >
                            {#if node.status === 'MASTERED'}
                                ⭐
                            {:else if node.type === 'kanji'}
                                漢
                            {:else if node.type === 'grammar'}
                                📚
                            {:else}
                                📓
                            {/if}
                        </div>
                        
                        {#if !isMini}
                            <span class="mt-3 text-xs font-bold text-slate-300 text-center max-w-[80px] break-words">
                                {node.label}
                            </span>
                        {/if}

                        <!-- Hover Tooltip -->
                        {#if !isMini}
                            <div class="absolute -top-12 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-xs whitespace-nowrap pointer-events-none z-20 shadow-lg text-white">
                                <span class="font-bold text-slate-300">Status:</span> {node.status}<br>
                                <span class="font-bold text-slate-300">Type:</span> {node.type}
                            </div>
                        {/if}
                    </div>
                    
                    <!-- Line connecting nodes horizontally -->
                    {#if colIndex < chunk.length - 1}
                        <div class="h-1 flex-1 {node.status !== 'LOCKED' ? 'bg-indigo-500' : 'bg-slate-700'} mx-2 transition-colors"></div>
                    {/if}
                {/each}

                <!-- Vertical line connecting rows at the end -->
                {#if rowIndex < chunkedNodes.length - 1}
                    <div class="absolute w-1 h-16 {chunk[chunk.length-1].status !== 'LOCKED' ? 'bg-indigo-500' : 'bg-slate-700'} 
                        {rowIndex % 2 !== 0 ? 'left-10' : 'right-10'} -bottom-16 transition-colors -z-10"></div>
                {/if}
            </div>
        {/each}
    </div>
</div>

<style>
    .mastery-container {
        width: 100%;
        overflow-y: auto;
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
        font-size: 1.5rem;
        font-weight: bold;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        cursor: pointer;
    }

    .node-circle:hover {
        transform: scale(1.15);
    }

    /* Gamification Juicy Glow */
    .gold-pulse {
        color: #78350f; /* dark brown to contrast gold */
        animation: goldPulse 2s infinite ease-in-out;
    }

    @keyframes goldPulse {
        0% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0.7); }
        50% { box-shadow: 0 0 20px 10px rgba(250, 204, 21, 0); }
        100% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0); }
    }

    /* Memory Retention Warning (Vibration + Reddish) */
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
</style>
