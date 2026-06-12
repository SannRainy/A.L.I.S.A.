<script>
    export let levels = [];
    export let onStart = () => {};
    export let prerequisiteAlert = { show: false }; // { show, levelTitle, missingNodes, source }

    import { profile } from "../stores/profile_store";
    import { fade, fly } from "svelte/transition";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    // ── Kanji Dojo Stats (dari localStorage, sama sumber dengan KanjiStudyMode) ──
    let kanjiMasteredSets = 0;
    try {
        kanjiMasteredSets = JSON.parse(localStorage.getItem('tvjp_kanji_mastered') || '[]').length;
    } catch {}
    $: kanjiProgress = Math.round((kanjiMasteredSets / 13) * 100);

    $: completedIds = $profile.completed_quests ? $profile.completed_quests.map(q => q.level_id) : [];
    $: completedQuests = $profile.completed_quests || [];

    // Level dianggap terbuka jika level sebelumnya sudah diselesaikan dengan nilai >= 90
    function isLevelLocked(index) {
        if (index === 0) return false;
        const prevLevelId = levels[index - 1].id;
        return !completedQuests.some(q => q.level_id === prevLevelId && q.score >= 90);
    }

    function handleStart(levelId) {
        selectedLevelId = levelId;
        showConfirm = true;
    }

    function confirmStart() {
        showConfirm = false;
        onStart(selectedLevelId);
    }

    let showConfirm = false;
    let selectedLevelId = null;
    $: activeLevel = levels.find(l => l.id === selectedLevelId);

    // Warna berdasarkan difficulty_tier
    const tierColors = {
        1: { active: 'from-emerald-400 to-teal-500', shadow: 'shadow-emerald-500/40', badge: 'bg-emerald-100 text-emerald-700', label: 'Beginner' },
        2: { active: 'from-indigo-400 to-purple-600', shadow: 'shadow-indigo-500/40', badge: 'bg-indigo-100 text-indigo-700', label: 'Elementary' },
        3: { active: 'from-rose-400 to-pink-600', shadow: 'shadow-rose-500/40', badge: 'bg-rose-100 text-rose-700', label: 'Pre-Intermediate' },
    };

    function getTierInfo(tier) {
        return tierColors[tier] || tierColors[1];
    }

    // ── Exam Dojo ─────────────────────────────────────────────────────
    // Terbuka setelah semua level quest selesai
    $: examUnlocked = levels.length > 0 && levels.every(l => completedIds.includes(l.id));

    // Meta batch untuk ditampilkan di UI
    const examBatchesMeta = [
        { id: 'exam_1', icon: '📝', title: 'Ujian Pertama',       desc: '25 soal · 15 menit · Grammar Dasar & Menengah',      color: 'from-blue-400 to-indigo-500',    shadow: 'shadow-blue-500/30',   glowBg: 'bg-blue-500/10',   border: 'border-blue-400/30',   badgeColor: 'text-blue-300' },
        { id: 'exam_2', icon: '📋', title: 'Ujian Kedua',         desc: '25 soal · 15 menit · Grammar Menengah & Lanjutan',    color: 'from-violet-400 to-purple-600',  shadow: 'shadow-violet-500/30', glowBg: 'bg-violet-500/10', border: 'border-violet-400/30', badgeColor: 'text-violet-300' },
        { id: 'exam_3', icon: '🏆', title: 'Ujian Final JLPT N5', desc: '25 soal · 20 menit · Komprehensif + Kanji Intensif',  color: 'from-rose-400 to-orange-500',    shadow: 'shadow-rose-500/30',   glowBg: 'bg-rose-500/10',   border: 'border-rose-400/30',   badgeColor: 'text-rose-300' },
    ];

    function portal(node) {
        const target = document.querySelector('.quest-container') || document.body;
        target.appendChild(node);
        return {
            destroy() {
                if (node.parentNode) {
                    node.parentNode.removeChild(node);
                }
            }
        };
    }
</script>

<div class="quest-map h-full overflow-y-auto custom-scroll p-8 flex flex-col items-center relative glass-panel rounded-[2rem]">

    <!-- ── Confirmation Modal ── -->
    {#if showConfirm && activeLevel}
        {@const tier = getTierInfo(activeLevel.difficulty_tier)}
        {@const prevLevel = levels[levels.findIndex(l => l.id === activeLevel.id) - 1]}
        <div use:portal class="absolute inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md" in:fade>
            <div class="bg-white/10 backdrop-blur-2xl rounded-[2.5rem] p-10 max-w-sm w-full shadow-2xl border border-white/20" in:fly={{ y: 20 }}>
                <div class="text-5xl mb-4 text-center drop-shadow-lg">{activeLevel.icon}</div>
                <h3 class="text-2xl font-black text-white text-center mb-1 tracking-tight">{activeLevel.title}</h3>

                <!-- Difficulty badge -->
                <div class="flex justify-center mb-4">
                    <span class="px-3 py-1 rounded-full text-xs font-bold {tier.badge}">
                        Tier {activeLevel.difficulty_tier} — {tier.label}
                    </span>
                </div>

                <p class="text-white/70 text-center text-sm mb-4 leading-relaxed">{activeLevel.description}</p>

                <!-- Prerequisite info -->
                {#if prevLevel}
                    <div class="mb-6 p-3 rounded-xl bg-white/5 border border-white/10 text-center">
                        <p class="text-xs text-white/50 font-semibold uppercase tracking-wider mb-1">Prasyarat Level</p>
                        <p class="text-xs text-indigo-300">Nilai {prevLevel.title} harus ≥ 90</p>
                    </div>
                {:else}
                    <div class="mb-6 p-3 rounded-xl bg-white/5 border border-white/10 text-center">
                        <p class="text-xs text-emerald-400 font-semibold">✅ Tidak ada prasyarat — Level awal!</p>
                    </div>
                {/if}

                <p class="text-indigo-300 font-bold text-sm text-center mb-6">Siap memulai tantangan ini?</p>

                <div class="flex flex-col gap-3">
                    <button
                        on:click={confirmStart}
                        class="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-black py-4 rounded-2xl transition shadow-xl shadow-indigo-500/20 uppercase tracking-widest text-sm"
                    >
                        Mulai Misi!
                    </button>
                    <button
                        on:click={() => showConfirm = false}
                        class="w-full bg-white/5 hover:bg-white/10 text-white/60 font-bold py-3 rounded-2xl transition text-sm"
                    >
                        Nanti Saja
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- ── Prerequisite Alert Modal ── -->
    {#if prerequisiteAlert.show}
        <div use:portal class="absolute inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md" in:fade>
            <div class="bg-white/10 backdrop-blur-2xl rounded-[2.5rem] p-10 max-w-sm w-full shadow-2xl border border-white/20 text-center" in:fly={{ y: 20 }}>
                <div class="text-5xl mb-4">🔒</div>
                <h3 class="text-xl font-black text-white mb-2">Level Terkunci</h3>
                <p class="text-white/70 text-sm mb-6 leading-relaxed">
                    Untuk membuka <span class="text-indigo-300 font-bold">{prerequisiteAlert.levelTitle}</span>,
                    kamu harus menyelesaikan level <span class="text-amber-300 font-bold">{prerequisiteAlert.prevLevelTitle}</span> dengan nilai minimal <span class="text-emerald-400 font-bold">{prerequisiteAlert.requiredScore || 90}</span>.
                </p>

                <button
                    on:click={() => dispatch('dismissAlert')}
                    class="w-full bg-white/10 hover:bg-white/20 text-white font-black py-3 rounded-2xl transition text-sm"
                >
                    Kembali ke Peta
                </button>
            </div>
        </div>
    {/if}

    <!-- ── Header ── -->
    <div class="text-center mb-8">
        <h2 class="text-3xl font-black text-white capitalize tracking-tight drop-shadow-md">N5 Quest Map</h2>
        <p class="text-white/50 font-medium mt-2 text-sm">Selesaikan misi secara berurutan untuk menguasai grammar N5.</p>
        <!-- Tier Legend -->
        <div class="flex justify-center gap-3 mt-4">
            {#each Object.entries(tierColors) as [tier, colors]}
                <span class="px-2 py-1 rounded-full text-[10px] font-bold {colors.badge}">T{tier} {colors.label}</span>
            {/each}
        </div>
    </div>

    <!-- ── KANJI DOJO Entry Card ── -->
    <button
        on:click={() => dispatch('openKanjiDojo')}
        class="w-full max-w-md mx-auto mb-10 group block"
    >
        <div class="relative rounded-[1.5rem] p-[1.5px] overflow-hidden shadow-xl transition-all duration-300 group-hover:scale-[1.02] group-hover:shadow-2xl"
             style="background: linear-gradient(135deg, rgba(251,191,36,0.6), rgba(245,101,39,0.5), rgba(251,191,36,0.3));">
            <div class="bg-slate-900/60 backdrop-blur-xl rounded-[1.4rem] p-5 flex items-center gap-5 relative overflow-hidden">
                <!-- Ambient glow -->
                <div class="absolute inset-0 bg-gradient-to-r from-amber-500/10 to-orange-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                <!-- Icon -->
                <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-2xl shrink-0 shadow-lg shadow-amber-500/30 border border-white/20 z-10">
                    漢
                </div>

                <!-- Info -->
                <div class="flex-grow text-left z-10 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <h3 class="font-black text-white text-base tracking-tight">漢字 Dojo</h3>
                        <span class="px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/30 text-[9px] font-black text-amber-300 uppercase tracking-widest">104 Kanji N5</span>
                    </div>
                    <p class="text-white/50 text-xs font-medium leading-snug">Pelajari semua kanji N5 dengan flashcard terstruktur — 13 set × 8 kanji</p>
                    <!-- Mini progress -->
                    <div class="flex items-center gap-2 mt-2">
                        <div class="flex-grow bg-white/10 h-1.5 rounded-full overflow-hidden">
                            <div class="bg-gradient-to-r from-amber-400 to-orange-500 h-full rounded-full transition-all duration-700"
                                 style="width: {kanjiProgress}%"></div>
                        </div>
                        <span class="text-[10px] font-black text-amber-400 shrink-0">{kanjiMasteredSets}/13 set</span>
                    </div>
                </div>

                <!-- Arrow -->
                <div class="w-8 h-8 rounded-xl bg-white/10 flex items-center justify-center text-amber-400 shrink-0 z-10 group-hover:bg-amber-500/20 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        </div>
    </button>

    <!-- ── Level Nodes ── -->
    <div class="w-full max-w-md relative flex flex-col items-center">
        <!-- Vertical line background -->
        <div class="absolute inset-0 flex justify-center -z-10 pointer-events-none">
            <div class="w-1.5 bg-white/10 h-full rounded-full"></div>
        </div>

        {#each levels as level, index}
            {@const isCompleted = completedIds.includes(level.id)}
            {@const isLocked = isLevelLocked(index)}
            {@const tier = getTierInfo(level.difficulty_tier)}
            {@const questCount = level.questions.length}
            {@const translateCount = level.questions.filter(q => q.type === 'translate').length}

            <div class="relative w-full flex {index % 2 === 0 ? 'justify-start pl-4' : 'justify-end pr-4'} mb-14">
                <button
                    on:click={() => !isLocked && handleStart(level.id)}
                    disabled={isLocked}
                    class="group relative flex flex-col items-center transition-all duration-500 hover:scale-110 active:scale-95"
                >
                    <!-- Node Circle -->
                    <div class="w-24 h-24 rounded-full flex items-center justify-center text-4xl shadow-2xl transition-all duration-500 border-4 z-10
                        {isCompleted ? 'bg-gradient-to-br from-emerald-400 to-teal-500 border-white/40 shadow-emerald-500/30' :
                         isLocked ? 'bg-white/5 border-white/10 opacity-40 grayscale scale-90' :
                         `bg-gradient-to-br ${tier.active} border-white/40 ${tier.shadow} animate-pulse-slow`}">
                        <span class="drop-shadow-md">{isLocked ? '🔒' : isCompleted ? '✅' : level.icon}</span>
                    </div>

                    <!-- Level number -->
                    <div class="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-[10px] font-black text-white z-20">
                        {index + 1}
                    </div>

                    <!-- Completed badge -->
                    {#if isCompleted}
                        <div class="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-yellow-400 flex items-center justify-center text-sm z-20 shadow-md border-2 border-white">
                            ⭐
                        </div>
                    {/if}

                    <!-- Hover Tooltip -->
                    <div class="absolute {index % 2 === 0 ? 'left-full ml-6' : 'right-full mr-6'} top-1/2 -translate-y-1/2 w-64 bg-white/10 backdrop-blur-xl p-5 rounded-[1.5rem] shadow-2xl border border-white/20 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none text-left z-20 {index % 2 === 0 ? '-translate-x-4 group-hover:translate-x-0' : 'translate-x-4 group-hover:translate-x-0'}">
                        <div class="flex items-center gap-2 mb-2">
                            <span class="text-xl">{level.icon}</span>
                            <h4 class="font-black text-white text-sm tracking-tight">{level.title}</h4>
                        </div>
                        <p class="text-xs text-white/60 mb-3 leading-relaxed line-clamp-2">{level.description}</p>

                        <!-- Soal info -->
                        <div class="flex gap-2 mb-3 flex-wrap">
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-white/10 text-white/70">{questCount} soal</span>
                            {#if translateCount > 0}
                                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300">{translateCount}× terjemah</span>
                            {/if}
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {tier.badge}">Tier {level.difficulty_tier}</span>
                        </div>

                        <!-- Prerequisite info -->
                        {#if level.prerequisites?.length > 0}
                            <p class="text-[10px] text-white/40">🔑 {level.prerequisites.length} prasyarat grammar</p>
                        {/if}

                        <!-- Status -->
                        {#if isLocked}
                            <p class="text-[10px] text-rose-400 font-bold mt-2 uppercase tracking-widest">🔒 Terkunci — Nilai Level Sebelumnya Harus ≥ 90</p>
                        {:else if isCompleted}
                            <p class="text-[10px] text-emerald-400 font-bold mt-2 uppercase tracking-widest">✅ Completed</p>
                        {:else}
                            <p class="text-[10px] text-indigo-300 font-bold mt-2 uppercase tracking-widest">▶ Siap Dimainkan</p>
                        {/if}
                    </div>
                </button>
            </div>
        {/each}
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- ── EXAM DOJO Section ── -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div class="w-full max-w-md mt-10 mb-4">
        <!-- Divider with label -->
        <div class="flex items-center gap-3 mb-6">
            <div class="flex-grow h-px bg-white/10"></div>
            <span class="text-[11px] font-black text-white/30 uppercase tracking-[0.25em] shrink-0">
                {examUnlocked ? '🏯 Exam Dojo — Terbuka!' : '🔒 Exam Dojo — Selesaikan Semua Level'}
            </span>
            <div class="flex-grow h-px bg-white/10"></div>
        </div>

        <!-- Locked overlay card -->
        {#if !examUnlocked}
            <div class="relative rounded-[1.5rem] p-[1.5px] overflow-hidden mb-3"
                 style="background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));">
                <div class="bg-slate-900/70 backdrop-blur-xl rounded-[1.4rem] p-6 flex flex-col items-center text-center gap-3 opacity-60">
                    <div class="text-4xl">🔒</div>
                    <h3 class="font-black text-white text-base">Exam Dojo Terkunci</h3>
                    <p class="text-white/40 text-xs leading-relaxed">
                        Selesaikan semua <strong class="text-white/60">{levels.length} Level Quest</strong> terlebih dahulu untuk membuka akses ke Simulasi Ujian Akhir JLPT N5.
                    </p>
                    <!-- Progress meter -->
                    <div class="w-full">
                        <div class="flex justify-between text-[10px] text-white/30 mb-1">
                            <span>Progress</span>
                            <span>{completedIds.filter(id => levels.find(l => l.id === id)).length}/{levels.length} level</span>
                        </div>
                        <div class="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                            <div
                                class="bg-gradient-to-r from-white/30 to-white/20 h-full rounded-full transition-all duration-700"
                                style="width: {Math.round((completedIds.filter(id => levels.find(l => l.id === id)).length / levels.length) * 100)}%"
                            ></div>
                        </div>
                    </div>
                </div>
            </div>

        <!-- Unlocked: Show 3 batch cards -->
        {:else}
            <!-- Intro label -->
            <div class="mb-4 p-4 rounded-2xl bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-400/20 text-center">
                <p class="text-xs text-red-300 font-bold">
                    🎓 Semua level selesai! Kamu siap menghadapi ujian akhir.<br>
                    <span class="text-white/50 font-medium">Pilih batch ujian di bawah ini.</span>
                </p>
            </div>

            {#each examBatchesMeta as batch}
                <button
                    on:click={() => dispatch('openExamDojo', { batchId: batch.id })}
                    class="w-full mb-3 group block"
                >
                    <div class="relative rounded-[1.5rem] p-[1.5px] overflow-hidden shadow-xl transition-all duration-300 group-hover:scale-[1.02] group-hover:shadow-2xl"
                         style="background: linear-gradient(135deg, rgba(239,68,68,0.5), rgba(249,115,22,0.4), rgba(239,68,68,0.2));">
                        <div class="bg-slate-900/80 backdrop-blur-xl rounded-[1.4rem] p-5 flex items-center gap-5 relative overflow-hidden">
                            <!-- Ambient glow -->
                            <div class="absolute inset-0 {batch.glowBg} opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                            <!-- Icon -->
                            <div class="w-14 h-14 rounded-2xl bg-gradient-to-br {batch.color} flex items-center justify-center text-2xl shrink-0 shadow-lg {batch.shadow} border border-white/20 z-10">
                                {batch.icon}
                            </div>

                            <!-- Info -->
                            <div class="flex-grow text-left z-10 min-w-0">
                                <div class="flex items-center gap-2 mb-1">
                                    <h3 class="font-black text-white text-sm tracking-tight">{batch.title}</h3>
                                    <span class="px-2 py-0.5 rounded-full bg-red-500/20 border border-red-400/30 text-[9px] font-black text-red-300 uppercase tracking-widest shrink-0">JLPT N5</span>
                                </div>
                                <p class="text-white/50 text-xs font-medium leading-snug">{batch.desc}</p>
                                <p class="{batch.badgeColor} text-[10px] font-black mt-1.5 uppercase tracking-widest">▶ Mulai Ujian</p>
                            </div>

                            <!-- Arrow -->
                            <div class="w-8 h-8 rounded-xl bg-white/10 flex items-center justify-center text-red-400 shrink-0 z-10 group-hover:bg-red-500/20 transition">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </button>
            {/each}
        {/if}
    </div>
</div>

<style>
    .animate-pulse-slow {
        animation: pulse-ring 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    @keyframes pulse-ring {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
        50% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(99, 102, 241, 0); }
    }
</style>
