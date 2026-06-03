<script>
    import { profile } from "../stores/profile_store";
    import { fly, fade, scale } from "svelte/transition";
    import MasteryPath from "./MasteryPath.svelte";
    import AchievementBadges from "./AchievementBadges.svelte";
    import { questLevels } from "../lib/data/quest_n5_dataset.js";
    import { kanjiSets } from "../lib/data/kanji_n5_dataset.js";
    
    let activeMapTab = "materi"; // 'materi' | 'kanji'

    // ── Computed Stats ────────────────────────────────────────────────────
    $: completedIds = $profile.completed_quests?.map(q => q.level_id) ?? [];
    $: completedCount = completedIds.length;

    // Hitung Kanji Mastery
    $: masteredKanjiIds = $profile.mastery_path?.filter(n => (n.type === 'Kanji' || n.type === 'kanji') && n.status === 'MASTERED').map(n => n.id) || [];

    // Gabungkan masteredKanjiIds dari Neo4j + kanji yang ada di set yang sudah mastered di localStorage
    $: localMasteredSets = (() => {
        try { return JSON.parse(localStorage.getItem('tvjp_kanji_mastered') || '[]'); }
        catch { return []; }
    })();
    $: localMasteredKanjiIds = kanjiSets
        .filter(set => localMasteredSets.includes(set.id))
        .flatMap(set => set.kanji.map(k => k.id));
    $: allMasteredKanjiIds = [...new Set([...masteredKanjiIds, ...localMasteredKanjiIds])];

    $: masteredKanjiSets = kanjiSets.map(set => {
        // Anggap set mastered jika minimal 80% kanjinya MASTERED di Neo4j
        const masteredInSet = set.kanji.filter(k => masteredKanjiIds.includes(k.id)).length;
        let isMastered = masteredInSet > 0 && (masteredInSet / set.kanji.length) >= 0.8;
        
        // Gabungkan dengan localStorage untuk realtime feel (MVP support)
        if (localMasteredSets.includes(set.id)) isMastered = true;
        
        return { ...set, isMastered };
    });
    $: totalQuests = questLevels.length; // 9

    // XP Progress (sama formula dengan Profile.svelte)
    $: xpForCurrentLevel = ($profile.level - 1) * 100;
    $: xpForNextLevel    = $profile.level * 100;
    $: progressXp        = Math.max(0, $profile.xp - xpForCurrentLevel);
    $: xpNeeded          = xpForNextLevel - xpForCurrentLevel;
    $: xpPct             = Math.min(Math.round((progressXp / xpNeeded) * 100), 100);

    // Rank (sync dengan Profile.svelte)
    const RANKS = [
        { minLevel: 1,  label: "Minarai",  kanji: "見習い" },
        { minLevel: 3,  label: "Ronin",    kanji: "浪人" },
        { minLevel: 5,  label: "Kenshi",   kanji: "剣士" },
        { minLevel: 8,  label: "Samurai",  kanji: "侍" },
        { minLevel: 10, label: "Shogun",   kanji: "将軍" },
    ];
    $: currentRank = [...RANKS].reverse().find(r => $profile.level >= r.minLevel) || RANKS[0];

    // Badge definitions (sinkron dengan AchievementBadges)
    $: badges = [
        {
            id: 'fire_starter',
            emoji: '🔥', label: 'Fire Starter',
            desc: 'Kuasai 5 Kanji',
            unlocked: ($profile.stats?.kanji_mastered ?? 0) >= 5,
            color: 'orange',
        },
        {
            id: 'lightning_brain',
            emoji: '⚡', label: 'Lightning Brain',
            desc: 'Capai Level 3',
            unlocked: ($profile.level ?? 1) >= 3,
            color: 'amber',
        },
        {
            id: 'warrior',
            emoji: '📅', label: '7-Day Warrior',
            desc: 'Kumpulkan 500 XP',
            unlocked: ($profile.xp ?? 0) >= 500,
            color: 'blue',
        },
        {
            id: 'n5_sage',
            emoji: '🌿', label: 'N5 Sage',
            desc: 'Selesaikan semua Quest N5',
            unlocked: completedCount >= 9,
            color: 'emerald',
        },
    ];
    $: unlockedCount = badges.filter(b => b.unlocked).length;

    const colorMap = {
        orange:  { ring: 'border-orange-500/40 bg-orange-500/5',  icon: 'bg-orange-100 border-orange-200',  title: 'text-slate-900', sub: 'text-orange-500' },
        amber:   { ring: 'border-amber-500/40 bg-amber-500/5',    icon: 'bg-amber-100 border-amber-200',    title: 'text-slate-900', sub: 'text-amber-500' },
        blue:    { ring: 'border-blue-500/40 bg-blue-500/5',      icon: 'bg-blue-100 border-blue-200',      title: 'text-slate-900', sub: 'text-blue-500' },
        emerald: { ring: 'border-emerald-500/40 bg-emerald-500/5', icon: 'bg-emerald-100 border-emerald-200', title: 'text-slate-900', sub: 'text-emerald-500' },
    };
</script>

<div class="h-full overflow-y-auto custom-scroll glass-panel rounded-[2.5rem] relative transition-all duration-500">
    <!-- Ambient Glows -->
    <div class="absolute top-0 right-0 w-80 h-80 bg-amber-200/20 rounded-full blur-[100px] pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-96 h-96 bg-indigo-200/15 rounded-full blur-[120px] pointer-events-none"></div>

    <div class="p-6 md:p-8 relative z-10">

        <!-- ═══════════════════════════════════════════════
             HEADER
        ═══════════════════════════════════════════════ -->
        <div class="text-center mb-8">
            <h2 class="text-2xl font-black text-white tracking-tight">🏆 Pencapaian</h2>
            <p class="text-sm text-slate-300 mt-1 font-medium">Kumpulkan lencana dan kuasai materi N5!</p>
        </div>

        <!-- ═══════════════════════════════════════════════
             LEVEL + XP CARD
        ═══════════════════════════════════════════════ -->
        <div class="glass-card p-5 md:p-6 mb-8">
            <div class="flex flex-col sm:flex-row items-center gap-5">
                <!-- Level Orb -->
                <div class="shrink-0 flex flex-col items-center">
                    <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-fuchsia-500 flex flex-col items-center justify-center shadow-xl shadow-indigo-500/30 border border-white/30">
                        <span class="text-xs font-black text-white/70 uppercase tracking-widest leading-none">Lv.</span>
                        <span class="text-2xl font-black text-white leading-none">{$profile.level}</span>
                    </div>
                    <p class="text-[10px] font-black text-slate-300 uppercase tracking-widest mt-2 text-center">
                        {currentRank.kanji} {currentRank.label}
                    </p>
                </div>

                <!-- XP Detail -->
                <div class="flex-grow w-full">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-black text-white">Total XP: <span class="text-indigo-300">{$profile.xp}</span></span>
                        <span class="text-xs font-bold text-slate-300">{progressXp} / {xpNeeded} XP level ini</span>
                    </div>
                    <div class="w-full bg-slate-700/60 rounded-full h-3.5 p-[2px] border border-white/20 shadow-inner overflow-hidden">
                        <div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-fuchsia-400 h-full rounded-full transition-all duration-1000"
                             style="width: {xpPct}%"></div>
                    </div>
                    <div class="flex justify-between mt-1.5">
                        <span class="text-[10px] text-slate-300 font-semibold">{xpForCurrentLevel} XP</span>
                        <span class="text-[10px] text-indigo-300 font-bold">{xpPct}%</span>
                        <span class="text-[10px] text-slate-300 font-semibold">{xpForNextLevel} XP</span>
                    </div>
                </div>
            </div>

            <!-- Badge Counter -->
            <div class="mt-4 pt-4 border-t border-slate-600/60 flex items-center justify-between">
                <span class="text-xs font-bold text-slate-300">Lencana Terbuka</span>
                <div class="flex items-center gap-1">
                    {#each badges as badge}
                        <span class="text-base {badge.unlocked ? 'opacity-100' : 'opacity-20 grayscale'}" title="{badge.label}">
                            {badge.emoji}
                        </span>
                    {/each}
                    <span class="ml-2 text-xs font-black text-slate-300">{unlockedCount}/{badges.length}</span>
                </div>
            </div>
        </div>

        <!-- ═══════════════════════════════════════════════
             ACHIEVEMENT BADGES
        ═══════════════════════════════════════════════ -->
        <div class="mb-8">
            <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em] mb-5">
                <span class="w-1.5 h-5 bg-amber-400 rounded-full"></span>
                Lencana Langka
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                {#each badges as badge (badge.id)}
                    {@const c = colorMap[badge.color]}
                    <div
                        class="glass-card p-4 flex items-center gap-4 transition-all duration-300
                            {badge.unlocked ? c.ring : 'opacity-60 grayscale hover:opacity-85 hover:grayscale-0'}"
                        in:fly={{ y: 10, duration: 350 }}
                    >
                        <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shrink-0 border
                            {badge.unlocked ? c.icon : 'bg-slate-700/50 border-slate-600/50'}">
                            {badge.emoji}
                        </div>
                        <div class="min-w-0">
                            <h4 class="font-black text-sm {badge.unlocked ? 'text-white' : 'text-slate-400'} truncate">
                                {badge.label}
                            </h4>
                            <p class="text-xs mt-0.5 {badge.unlocked ? c.sub : 'text-slate-400'} leading-snug">
                                {badge.unlocked ? `✓ ${badge.desc}` : `🔒 ${badge.desc}`}
                            </p>
                        </div>
                        {#if badge.unlocked}
                            <div class="ml-auto shrink-0 w-6 h-6 rounded-full bg-emerald-900/50 flex items-center justify-center" in:scale={{ duration: 400 }}>
                                <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>

        <!-- ═══════════════════════════════════════════════
             QUEST PROGRESS (baru — nilai bagi skripsi)
        ═══════════════════════════════════════════════ -->
        <div class="mb-8">
            <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em] mb-5">
                <span class="w-1.5 h-5 bg-rose-400 rounded-full"></span>
                Progress Quest N5
            </h3>

            <div class="glass-card p-5">
                <div class="grid grid-cols-3 gap-2 md:gap-3 mb-4">
                    {#each questLevels as level, i}
                        {@const done = completedIds.includes(level.id)}
                        <div class="flex flex-col items-center p-3 rounded-2xl border transition-all duration-300
                            {done ? 'bg-emerald-900/30 border-emerald-400/30' : 'bg-slate-700/50 border-slate-600/50'}">
                            <span class="text-xl mb-1">{done ? '✅' : level.icon}</span>
                            <span class="text-[9px] font-black text-center leading-tight {done ? 'text-emerald-300' : 'text-slate-300'}">
                                {level.title}
                            </span>
                            <span class="text-[8px] {done ? 'text-emerald-400' : 'text-slate-400'} mt-0.5">
                                {done ? 'Selesai' : `Tier ${level.difficulty_tier}`}
                            </span>
                        </div>
                    {/each}
                </div>
                <div class="text-center">
                    <p class="text-xs font-bold text-slate-300">
                        {completedCount === 0
                            ? 'Mulai Quest pertamamu!'
                            : completedCount < 9
                                ? `${completedCount} dari ${totalQuests} level selesai — terus semangat! 💪`
                                : '🎉 Semua Quest N5 selesai! Kamu adalah N5 Sage!'}
                    </p>
                </div>
            </div>
        </div>

        <!-- ═══════════════════════════════════════════════
             MASTERY PATH (Living Knowledge Graph)
        ═══════════════════════════════════════════════ -->
        <div>
            <div class="flex justify-between items-end mb-5">
                <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em]">
                    <span class="w-1.5 h-5 bg-fuchsia-400 rounded-full"></span>
                    Peta Penguasaan N5
                </h3>
            </div>

            <!-- Tabs -->
            <div class="flex gap-2 mb-4">
                <button 
                    on:click={() => activeMapTab = "materi"}
                    class="flex-1 py-2 px-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300
                        {activeMapTab === 'materi' 
                            ? 'bg-fuchsia-500 text-white shadow-lg shadow-fuchsia-500/30' 
                            : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50'}"
                >
                    Peta Pembelajaran Materi
                </button>
                <button 
                    on:click={() => activeMapTab = "kanji"}
                    class="flex-1 py-2 px-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300
                        {activeMapTab === 'kanji' 
                            ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/30' 
                            : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50'}"
                >
                    Peta Pembelajaran Kanji
                </button>
            </div>

            <div class="bg-slate-800/60 backdrop-blur-sm rounded-3xl p-5 md:p-6 border border-white/20 shadow-sm">
                {#if activeMapTab === "materi"}
                    <!-- Peta Pembelajaran Materi -->
                    {#if $profile.mastery_path && $profile.mastery_path.length > 0}
                        <MasteryPath nodes={$profile.mastery_path} isMini={false} />
                    {:else}
                        <div class="flex flex-col items-center justify-center py-12 opacity-80" in:fade>
                            <span class="text-4xl mb-4">🌱</span>
                            <p class="text-slate-300 font-black text-center">Peta penguasaan masih kosong.</p>
                            <p class="text-xs text-slate-300 text-center mt-2 max-w-xs leading-relaxed">
                                Mulai obrolan dengan A.L.I.S.A. atau kerjakan Quest untuk mengisi Knowledge Graph pertamamu!
                            </p>
                        </div>
                    {/if}
                {:else}
                    <!-- Peta Pembelajaran Kanji -->
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {#each masteredKanjiSets as set, i}
                            <div class="glass-card p-4 flex flex-col items-center text-center relative overflow-hidden transition-all {set.isMastered ? 'border-emerald-400/50 bg-emerald-900/20' : 'border-slate-700/50 bg-slate-800/40'}">
                                {#if set.isMastered}
                                    <div class="absolute top-2 right-2 text-xs">✅</div>
                                {/if}
                                <div class="text-3xl mb-2 {set.isMastered ? 'opacity-100' : 'opacity-70'}">{set.icon}</div>
                                <h4 class="font-black text-white text-sm mb-1">{set.title}</h4>
                                <div class="flex flex-wrap gap-1.5 justify-center mt-2">
                                    {#each set.kanji as kanji}
                                        <span class="w-8 h-8 rounded-lg flex items-center justify-center text-lg font-bold transition-all
                                            {allMasteredKanjiIds.includes(kanji.id) ? 'bg-emerald-500/30 border border-emerald-400/50 text-emerald-100' : 'bg-slate-700/70 border border-slate-600/50 text-white opacity-60'}">
                                            {kanji.id}
                                        </span>
                                    {/each}
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>

    </div>
</div>
